This is a repository to test different scenarios of MCP Servers. [Resources](https://modelcontextprotocol.io/quickstart/server)

## Get Started

Create a new directory for our project

```bash
uv init weather
cd weather
```

Create virtual environment and activate it

```bash
uv venv
.venv\Scripts\activate
```

Install dependencies

```bash
uv add mcp[cli] httpx fastapi asyncio aiohttp
```
