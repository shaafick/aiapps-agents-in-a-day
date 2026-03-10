# GitHub Copilot SDK

GitHub Copilot SDK is an event-capable framework for building AI agents with either GitHub Copilot credentials or BYOK (Bring Your Own Key) provider credentials.

For this lab, the default path is BYOK with Azure Foundry endpoint and API key, using the sample at `labs/40-AIAgents/game_agent_v3_copilot.py`.

**Package**: `github-copilot-sdk`  
**Import module**: `copilot`

## Default Lab Path

Use this section for the workshop flow. It matches `labs/40-AIAgents/game_agent_v3_copilot.py`.

### 1) Go to the lab folder

```bash
cd labs/40-AIAgents
```

### 2) Install and imports

Package/import mapping for this lab:

- Install package: `github-copilot-sdk`
- Import module: `copilot`

Recommended path (matches lab dependencies):

```bash
pip install -r requirements.txt
```

Fallback path (Copilot SDK only):

```bash
pip install github-copilot-sdk python-dotenv
```

### 3) Configure environment variables

The sample requires these variables:

| Variable | Required | Used by sample |
| --- | --- | --- |
| `AZURE_FOUNDRY_PROJECT_ENDPOINT` | Yes | Endpoint passed to provider `base_url` |
| `AZURE_FOUNDRY_API_KEY` | Yes | BYOK `api_key` for provider |
| `AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME` | Optional | Model name, defaults to `gpt-4o` |
| `DEV_Name` | Optional | Player name, defaults to `default-player` |

If your environment uses `AZURE_OPENAI_API_ENDPOINT` and `AZURE_OPENAI_API_KEY`, map them into the sample variable names before running.

### 4) Run the sample

```bash
python3 game_agent_v3_copilot.py
```

Expected shape of output:

```text
Q: What is 15 + 27?
A: 42
```

## Provider Configuration (Lab Default)

The sample uses `SessionConfig` and an Azure provider:

```python
from copilot import CopilotClient, SessionConfig, MessageOptions, PermissionHandler

client = CopilotClient()
await client.start()

session = await client.create_session(
    SessionConfig(
        model="gpt-4o",
        provider={
            "type": "azure",
            "base_url": "https://<foundry-project-endpoint>",
            "api_key": "<AZURE_FOUNDRY_API_KEY>",
            "azure": {"api_version": "2024-10-21"},
        },
        on_permission_request=PermissionHandler.approve_all,
    )
)

response = await session.send_and_wait(MessageOptions(prompt="What is 15 + 27?"))
print(response.data.content)
```

## Sessions

The session persists conversation context across turns:

```python
await session.send_and_wait(MessageOptions(prompt="My name is Alice."))
result = await session.send_and_wait(MessageOptions(prompt="What is my name?"))
print(result.data.content)
```

## Authentication Patterns

Copilot SDK supports two broad auth approaches.

### 1) GitHub Copilot credentials

Use Copilot-authenticated flows via logged-in user state, OAuth token, or token environment variables (`COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`).

### 2) BYOK provider credentials (Lab default)

Use provider credentials directly in session config, typically API keys:

```python
provider = {
    "type": "azure",
    "base_url": "https://<endpoint>",
    "api_key": "<api-key>",
}
```

Important limitation for BYOK: credentials are treated as static values. If you use short-lived bearer tokens, your app must refresh them and recreate or update sessions.

## Optional Advanced Patterns

These are optional and not required for this lab.

### Event callback flow (optional)

Use this when you need reactive event handling instead of `send_and_wait`.

```python
done = asyncio.Event()
response_text = ""


def on_event(event):
    nonlocal response_text
    if event.type.value == "assistant.message":
        response_text = event.data.content
    elif event.type.value == "session.idle":
        done.set()


session.on(on_event)
await session.send({"prompt": "What is 15 + 27?"})
await done.wait()
```

### OpenAI-compatible provider shape (optional)

Use this when your endpoint is configured for OpenAI-compatible routing.

```python
session = await client.create_session(
    {
        "model": "gpt-5",
        "provider": {
            "type": "openai",
            "base_url": "https://<resource>.openai.azure.com/openai/v1/",
            "api_key": "<AZURE_OPENAI_API_KEY>",
            "wire_api": "responses",
        },
    }
)
```

## Learn More

- [GitHub Copilot SDK - BYOK Guide](https://github.com/github/copilot-sdk/blob/main/docs/auth/byok.md)
- [GitHub Copilot SDK - Authentication Overview](https://github.com/github/copilot-sdk/blob/main/docs/auth/index.md)
- [Provider Configuration Reference](https://github.com/github/copilot-sdk/blob/main/docs/auth/byok.md#provider-configuration-reference)
- [Getting Started](https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md)
- [GitHub Repository](https://github.com/github/copilot-sdk)
