# mcp-imdb MCP server

A Model Context Protocol (MCP) server for accessing IMDB data

## Components

### Resources

The server implements a simple note storage system with:
- Custom note:// URI scheme for accessing individual notes
- Each note resource has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements one tool:
- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resource changes

## Configuration

The server supports multiple transport protocols that can be selected via the
`MCP_TRANSPORT` environment variable:

- `STDIO` (default) – communicate over standard input/output. This is the
  transport used when running the server locally or via the included tests.
- `HTTP` – start the server as a Streamable HTTP service. When enabled the
  server listens on the port specified by the `PORT` environment variable
  (default `8000`).
- `SSE` – expose a Server-Sent Events endpoint at `/sse` with a companion
  `/messages/` POST endpoint. The server listens on the `PORT` environment
  variable (default `8000`).

Example for running the server over HTTP:

```bash
MCP_TRANSPORT=HTTP PORT=8000 uv run mcp-imdb
```

Example for running the server over SSE:

```bash
MCP_TRANSPORT=SSE PORT=8000 uv run mcp-imdb
```

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "mcp-imdb": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/git/mcp-imdb",
        "run",
        "mcp-imdb"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "mcp-imdb": {
      "command": "uvx",
      "args": [
        "mcp-imdb"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory <dir_to>/git/mcp-imdb run mcp-imdb
```
Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
