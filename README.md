# Simple LangChain Document Summarizer

A minimal LangChain application that reads a DOCX file and summarizes it using GPT-4o-mini.

## Features

- Reads DOCX files using python-docx
- Summarizes content using OpenAI's GPT-4o-mini model
- Built with LangGraph for workflow management
- Uses uv for dependency management

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. Ensure the input file exists at `./data/input/B.docx`

## Usage

Run the application:
```bash
uv run main.py
```

The application will:
1. Read the DOCX file from `./data/input/B.docx`
2. Extract text content from the document
3. Generate a summary using GPT-4o-mini
4. Display the results in the console
5. Save the summary to `./data/results/summary.txt`

## Project Structure

```
├── main.py                 # Main entry point
├── graph.py               # LangGraph workflow definition
├── state.py               # State type definitions
├── nodes/
│   └── extract_answers.py # Document processing node
├── data/
│   ├── input/
│   │   └── B.docx        # Input document
│   └── results/
│       └── summary.txt   # Generated summary
├── pyproject.toml        # Dependencies
└── .env.example          # Environment variables template
```

## Dependencies

- `langchain` - LangChain framework
- `langchain-openai` - OpenAI integration
- `langgraph` - Graph-based workflows
- `python-docx` - DOCX file reading
- `python-dotenv` - Environment variable management
- `openai` - OpenAI API client

## Requirements

- Python 3.13+
- OpenAI API key
- uv package manager
