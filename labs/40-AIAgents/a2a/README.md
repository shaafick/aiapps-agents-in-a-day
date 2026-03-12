# Rock-Paper-Scissors Game Agent - A2A Architecture

A clean Agent-to-Agent (A2A) implementation for the Rock-Paper-Scissors game, using the official a2a-sdk.

## Architecture

This implementation demonstrates **Agent-to-Agent (A2A) Protocol** using the official a2a-sdk:

### Game Tools Agent Server (A2A Service)
A specialized agent providing three capabilities via A2A protocol:
- `calculate` - Safe mathematical expression evaluation
- `rps_rules` - Rock-Paper-Scissors game rules
- `get_tournament_info` - Tournament format, scoring, and rules from rulebook

Implemented using:
- `A2AStarletteApplication` - Official A2A server framework
- `AgentExecutor` - Task-based execution pattern
- `DefaultRequestHandler` - Handles A2A message protocol
- `InMemoryTaskStore` - Task state management

Exposes A2A endpoints:
- `/.well-known/agent-card` - Discovery endpoint
- Standard A2A message endpoints

### Game Agent Client (A2A Consumer)
The client that interfaces with users and demonstrates A2A communication:
- Discovers agent capabilities via `A2ACardResolver`
- Creates `A2AClient` to communicate with remote agent
- Sends messages via `SendMessageRequest` and receives `SendMessageResponse`
- Handles user interaction and presents results

## Structure

```
a2a/
├── game_tools_agent/      # A2A Server
│   ├── agent_executor.py  # AgentExecutor with game logic
│   ├── agent.py           # Legacy (kept for reference)
│   └── server.py          # Starlette server with A2AStarletteApplication
├── game_agent.py          # A2A Client (demonstrates A2A communication)
├── main.py                # Orchestrates server and client
├── requirements.txt       # Python dependencies (includes a2a-sdk)
├── .env.example           # Environment variable template
└── README.md              # This file
```

## Setup

1. **Activate virtual environment and install dependencies:**
   ```bash
   # CRITICAL: Activate .venv FIRST
   source .venv/bin/activate  # macOS/Linux
   # OR
   .venv\Scripts\activate     # Windows
   
   # Then install packages
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Required environment variables in `.env`:**
   ```
   SERVER_URL=localhost
   GAME_TOOLS_AGENT_PORT=8088
   DEV_Name=YourName (optional)
   ```
   
   Note: Azure OpenAI credentials are no longer required as the agent logic doesn't use LLM - it directly executes tool functions.

## Usage

### Option 1: Run Everything Together (Recommended)

```bash
python main.py
```

This will:
1. Start the Game Tools Agent server
2. Wait for it to be healthy
3. Start the interactive client
4. Clean up servers on exit

### Option 2: Run Components Separately (to see A2A in action)

**Terminal 1 - Start Game Tools Agent Server:**
```bash
python -m uvicorn game_tools_agent.server:app --host localhost --port 8088
```

**Terminal 2 - Run Game Agent Client:**
```bash
python game_agent.py
```

This clearly shows the Agent-to-Agent communication happening between two separate processes.

## A2A Protocol Communication Flow

This example demonstrates the full A2A protocol:

### 1. Server Setup
Game Tools Agent Server:
- Exposes `/.well-known/agent-card` - Discovery endpoint with skills
- Provides `/health` - Health check
- Uses `A2AStarletteApplication` for standard A2A protocol

### 2. Agent Discovery
Game Agent Client:
- Uses `A2ACardResolver` to fetch agent card
- Discovers available skills and capabilities
```python
# Discovery
resolver = A2ACardResolver(httpx_client, base_url)
agent_card = await resolver.get_agent_card()

# Create proxy
tools_agent_proxy = A2AAgent(name=agent_card.name, agent_card=agent_card, url=url)

# Convert to tool
game_tools = tools_agent_proxy.as_tool()
```

### 3. Agent-to-Agent Communication
Agent #2 delegates requests to Agent #1 via:
- `POST /v1/message` - Message endpoint (with streaming support)

The Game Agent automatically calls the Game Tools Agent whenever tools are needed.

## Example Interactions

```
You: What is 15 * 23?
Agent: 345

You: If I play Rock and opponent plays Scissors, who wins?
Agent: Rock wins

You: What is the tournament scoring system?
Agent: [Returns detailed scoring from rulebook]
```

## Key Features

- **Clean separation**: Tools agent only handles tool execution, game agent handles user interaction
- **A2A protocol**: Standard discoverability via agent cards
- **Streaming support**: Server-sent events for responses
- **Health checks**: Server readiness detection
- **Graceful shutdown**: Proper cleanup of resources
- **Pure A2A focus**: Demonstrates Agent-to-Agent communication patterns

## Troubleshooting

**Connection errors:**
- Ensure Game Tools Agent server is running on the configured port
- Check firewall settings
- Verify environment variables are set correctly

**Tool not executing:**
- Check server logs for errors
- Verify Azure OpenAI credentials
- Ensure game_rulebook.txt exists in parent directory

**Import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.9+
