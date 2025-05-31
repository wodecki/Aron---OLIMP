import os
import tomllib
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    if tools:
      return prompt | llm.bind_tools(tools)
    else:
      return prompt | llm


# Load environment variables
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# Initialize tools
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
arxiv = load_tools(["arxiv"])[0]
tavily = TavilySearchResults(max_results=5)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# Load prompt templates from TOML file
with open("config/prompts.toml", "rb") as f:
    prompts = tomllib.load(f)

search_template = prompts["search"]["template"]
outliner_template = prompts["outliner"]["template"]
writer_template = prompts["writer"]["template"]
editor_template = prompts["editor"]["template"]

tools = [tavily, wikipedia, arxiv]

search_agent = create_agent(
    llm,
    tools,
    system_message=search_template,
)

outliner_agent = create_agent(
    llm,
    [],
    system_message=outliner_template,
)

writer_agent = create_agent(
    llm,
    [],
    system_message=writer_template,
)

editor_agent = create_agent(
    llm,
    [],
    system_message=editor_template,
)

# Node definitions - each agent defined separately using Command for routing
def search_node(state) -> Command[Literal["tools", "outliner"]]:
    """Search agent node for finding information."""
    result = search_agent.invoke(state)
    
    # Check if the result has tool calls to determine routing
    if result.tool_calls:
        return Command(
            update={"messages": [result]},
            goto="tools"
        )
    else:
        return Command(
            update={"messages": [result]},
            goto="outliner"
        )

def outliner_node(state):
    """Outliner agent node for creating document structure."""
    result = outliner_agent.invoke(state)
    return {
        "messages": [result]
    }

def writer_node(state):
    """Writer agent node for content creation."""
    result = writer_agent.invoke(state)
    return {
        "messages": [result]
    }

def editor_node(state) -> Command[Literal["writer", END]]:
    """Editor agent node for content review and iteration tracking."""
    result = editor_agent.invoke(state)
    iteration_count = state.get("no_of_iterations", 0) + 1
    
    # Check completion criteria to determine routing
    # Look for DONE in the content (case insensitive) or if max iterations reached
    content_lower = result.content.lower() if result.content else ""
    if 'done' in content_lower or iteration_count >= 3:
        return Command(
            update={
                "messages": [result],
                "no_of_iterations": iteration_count
            },
            goto=END
        )
    else:
        return Command(
            update={
                "messages": [result],
                "no_of_iterations": iteration_count
            },
            goto="writer"
        )



# Define state structure
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    no_of_iterations: int

# Configuration
MAX_ITERATIONS = 3

# Build the workflow graph
workflow = StateGraph(AgentState)

# Add nodes to the graph
workflow.add_node("search", search_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("outliner", outliner_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

# Set entry point
workflow.set_entry_point("search")

# Add edges between nodes - simplified since routing is handled by Commands
workflow.add_edge("tools", "outliner")  # After tools, go directly to outliner to prevent loops
workflow.add_edge("outliner", "writer")
workflow.add_edge("writer", "editor")

# Compile the graph
graph = workflow.compile()

#Execution
# if __name__ == "__main__":
#     thread = {"configurable": {"thread_id": "1"}}
    
#     question = "Jaki jest potencjał wykorzystania technologii generatywnych w bankowości? Zaproponuj scenariusze użycia i przykładowe uzasadnienia biznesowe."
#     input_message = HumanMessage(content=question)
    
#     for event in graph.stream({"messages": [input_message], "no_of_iterations": 0}, thread, stream_mode="values"):
#         event["messages"][-1].pretty_print()
