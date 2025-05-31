# Context7 MCP Server Test

## Test Instructions

### For Claude Code
Try this prompt in Claude Code:
```
How do I create a simple FastAPI application with error handling? use context7
```

### For VSCode with GitHub Copilot
Try asking in Copilot Chat:
```
@workspace How can I implement async/await in Python with proper error handling?
```

## Expected Behavior

Context7 should:
1. Fetch up-to-date documentation from official sources
2. Provide current code examples
3. Include version-specific information
4. Show best practices and common patterns

## Verification

- Claude Code: Should show "use context7" triggers fetching external docs
- VSCode: Should enhance Copilot responses with current documentation
- Both: Should provide more accurate, up-to-date code examples

## Configuration Status

✅ Claude Code: Context7 MCP server configured with SSE transport
✅ VSCode: MCP configuration files created
✅ Package: @upstash/context7-mcp installed globally
✅ Logs: Context7 activity visible in VSCode logs

Delete this file after testing is complete.