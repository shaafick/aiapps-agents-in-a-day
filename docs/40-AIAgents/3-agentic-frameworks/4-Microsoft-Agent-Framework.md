# Microsoft Agent Framework

Microsoft Agent Framework is an SDK for building production-ready AI agents in application code. It gives you a consistent programming model for providers, sessions, tools, and orchestration.

For this lab, the sample in `labs/40-AIAgents/ms-agent-foundry/game_agent_v3_maf.py` runs a console agent against Azure OpenAI Responses through Agent Framework using Entra ID credentials.

## Framework vs Service

- **Microsoft Agent Framework**: SDK and orchestration patterns in your app code.
- **Azure AI Foundry Agent Service**: Managed agent runtime and operations in Azure.

Use Agent Framework when you want code-level control over behavior and integration. Use Foundry Agent Service when you want more service-managed lifecycle and operations.

## Current Sample Behavior

The current `game_agent_v3_maf.py` sample does the following:

- Creates `AzureOpenAIResponsesClient` with `project_endpoint`, deployment name, and `DefaultAzureCredential`.
- Creates one agent with `client.as_agent(...)`.
- Creates one session with `agent.create_session()` and reuses it for the full chat loop.
- Sends every non-empty user message with `await agent.run(user_input, session=session)`.
- Exits on `exit` or `quit`.

## Create Microsoft Agent Framework Agent

- navigate to `labs/40-AIAgents/ms-agent-foundry`.

```bash
cd labs/40-AIAgents/ms-agent-foundry
```

- Create and activate a virtual environment.

```bash
python -m venv .maf
```
```bash
# Windows
source .maf/Scripts/activate
```
```bash
# macOs/linux
source .maf/bin/activate
```

- install the requirements:

```bash
pip install -r requirements.txt
```

- Run the sample.

```bash
python game_agent_v3_maf.py
```

Expected startup:

```text
============================================================
Microsoft Agent Framework - Game Agent
============================================================
You can:
  - Ask math questions (e.g., 'What is 15 + 27?')
  - Play Rock-Paper-Scissors (e.g., 'I choose rock')
  - Type 'exit' or 'quit' to end
============================================================

Using endpoint: <your endpoint>
Using model: gpt-4o

You:
```

## Provider Setup

This is the pattern used by the current sample:

```python
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential

client = AzureOpenAIResponsesClient(
    project_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    deployment_name=os.getenv("AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
    credential=DefaultAzureCredential(),
)

agent = client.as_agent(
    name="GameAgent",
    instructions="You are a helpful game assistant.",
)
```

## Sessions

Session continuity is built in when you pass the same session object on each turn:

```python
session = agent.create_session()

await agent.run("My name is Alex.", session=session)
result = await agent.run("What is my name?", session=session)
print(result)
```

## Extension A: Add Tools/Functions

Research validation: Agent Framework supports tool-enabled agents in code (official docs and package examples show `tools=[...]` usage).

Use this extension to let learners add helper functions for math and game resolution.

Paste this snippet at marker `INSERT-TOOLS-HERE` in `labs/40-AIAgents/ms-agent-foundry/game_agent_v3_maf.py`.

```python
from random import choice


def evaluate_math(
    expression: Annotated[str, Field(description="Simple arithmetic expression")],
) -> str:
    return str(eval(expression, {"__builtins__": {}}, {}))


def evaluate_rps(
    player_move: Annotated[str, Field(description="rock, paper, or scissors")],
) -> str:
    options = ("rock", "paper", "scissors")
    server_move = choice(options)
    winning_pairs = {
        ("rock", "scissors"),
        ("paper", "rock"),
        ("scissors", "paper"),
    }
    pm = player_move.lower().strip()
    if pm not in options:
        return "Invalid move. Use rock, paper, or scissors."
    if pm == server_move:
        winner = "tie"
    elif (pm, server_move) in winning_pairs:
        winner = "player"
    else:
        winner = "server"
    return f"player={pm}, server={server_move}, winner={winner}"


agent = client.as_agent(
    name="GameAgent",
    instructions=INSTRUCTIONS,
    tools=[evaluate_math, evaluate_rps],
)
```

After pasting, prompts like `Use evaluate_rps with my move scissors` can trigger tool usage with a random server move and a tool-calculated winner.

## Extension B: New Session Tool (Restart Game)

Research validation: `create_session()` and reusing `session=` in `run(...)` are supported and already used by this sample.

Paste this snippet at marker `INSERT-SESSION-CONTINUITY-HERE` in `labs/40-AIAgents/ms-agent-foundry/game_agent_v3_maf.py`.

```python
active_session_id = 1


def new_session():
    return agent.create_session()


def reset_session(current_id):
    return new_session(), current_id + 1
```

Then replace the existing session initialization line with:

```python
session = new_session()
```

Paste this snippet at marker `INSERT-NEW-SESSION-TOOL-HERE` in `labs/40-AIAgents/ms-agent-foundry/game_agent_v3_maf.py`.

```python
restart_requested = False


def new_session_tool() -> str:
    nonlocal restart_requested
    restart_requested = True
    return "New game requested. I will start a fresh session after this response."


agent = client.as_agent(
    name="GameAgent",
    instructions=INSTRUCTIONS,
    tools=[evaluate_math, evaluate_rps, new_session_tool],
)
```

Paste this snippet at marker `INSERT-NEW-SESSION-RESTART-HOOK-HERE` in `labs/40-AIAgents/ms-agent-foundry/game_agent_v3_maf.py`.

```python
if restart_requested:
    session, active_session_id = reset_session(active_session_id)
    restart_requested = False
    print(f"Started new game session #{active_session_id}")
    print()
```

With this flow, the user can ask the agent to call `new_session_tool` to restart the game without slash commands.

## Learn More

**Official Documentation**:
- [Microsoft Agent Framework Overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)
- [Azure OpenAI Provider](https://learn.microsoft.com/agent-framework/agents/providers/azure-openai)
- [Your First Agent Tutorial](https://learn.microsoft.com/agent-framework/get-started/your-first-agent)
- [Azure AI Foundry Hosted Agents](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents?view=foundry)
- [Foundry Agent Runtime Components](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/runtime-components?view=foundry)
