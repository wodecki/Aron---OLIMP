# Context7 MCP Server Configuration

This directory contains configuration files for the Context7 MCP (Model Context Protocol) server integration with both Claude Code and VSCode.

## Installed Components

✅ **Context7 MCP Server for Claude Code**
- Transport: SSE (Server-Sent Events)
- URL: https://mcp.context7.com/sse
- Status: Configured and active

✅ **Context7 MCP Server for VSCode**
- Configuration: HTTP transport via `.vscode/mcp.json`
- Alternative: Local stdio via `.vscode/mcp-local.json`
- Package: @upstash/context7-mcp (installed globally)

## Files Created

- `.vscode/mcp.json` - HTTP transport configuration
- `.vscode/mcp-local.json` - Local stdio configuration  
- `.vscode/settings.json` - VSCode settings with MCP integration
- `.vscode/README_MCP.md` - This documentation

## Usage

### With Claude Code
Simply add "use context7" to your prompts when asking for code assistance:

```
How do I implement error handling in Python? use context7
```

### With VSCode
1. Ensure GitHub Copilot extension is installed and enabled
2. Use GitHub Copilot Chat with Context7 integration
3. The MCP server will automatically provide up-to-date documentation

## Context7 Features

- **Up-to-date Documentation**: Fetches current docs from official sources
- **Code Examples**: Provides real, working code samples
- **Version-Specific**: Matches documentation to specific library versions
- **Multiple Languages**: Supports various programming languages and frameworks

## Verification

To verify the installation:

### Claude Code
```bash
claude mcp list
```
Should show: `context7: https://mcp.context7.com/sse (SSE)`

### VSCode
Check that the MCP configuration loads properly when opening the workspace.

## Troubleshooting

If you encounter issues:

1. **Claude Code**: Try restarting Claude Code after configuration
2. **VSCode**: Reload the window (Cmd+R) to refresh MCP connections
3. **Network**: Ensure internet connectivity for remote MCP servers
4. **Local fallback**: Use `mcp-local.json` if HTTP transport fails

## Alternative Configurations

If the HTTP transport doesn't work, rename `mcp-local.json` to `mcp.json` to use the local stdio transport instead.