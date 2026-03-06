# GitHub Copilot SDK

GitHub Copilot SDK is an event-driven framework for building AI agents. It supports both GitHub Copilot credentials and BYOK (Bring Your Own Key) provider credentials. For GitHub Copilot credentials, the SDK can use a logged-in Copilot user session, OAuth user tokens, or supported GitHub token environment variables. For BYOK, callers supply provider API keys or static bearer tokens directly.

Copilot SDK excels in scenarios requiring **event-based messaging**, **multi-provider flexibility**, and **explicit credential management**. It's ideal for environments where automatic CLI or managed-identity auth is not available or where you need fine-grained control over API keys, bearer tokens, and custom authentication flows.

**Package**: `github-copilot-sdk`

**Use Cases**: Event-driven agent workflows, GitHub Copilot credential-based apps, BYOK provider integrations (OpenAI, Azure, Anthropic, Ollama), custom authentication patterns, environments without Azure CLI access.

**Why GitHub Copilot SDK?**
- **Event-Driven Architecture**: Reactive messaging patterns with `session.on()` event handlers
- **Direct API Control**: Use API keys and bearer tokens without CLI dependencies
- **Multi-Provider Flexibility**: Unified interface for OpenAI, Azure, Anthropic, Ollama, custom endpoints
- **Wire API Options**: Supports both "completions" and "responses" API formats
- **Custom Authentication**: Full control over authentication tokens and credential management
- **No CLI Dependencies**: Works in environments without Azure CLI or GitHub CLI

Let's cover some core components:

Let's cover some core components:

## Create GitHub Copilot Agent

- navigate to `labs/40-AIAgents` folder, open `game_agent_v3_copilot.py` file.

```python
cd labs/40-AIAgents
```

- run the agent and see the console output.

```python
python game_agent_v3_copilot.py
```

Expected output:

```
GitHub Copilot SDK (BYOK) agent initialized: default-player
Testing agent: default-player
Q: What is 15 + 27?
A: 42
Game Agent: Test complete
```

- GitHub Copilot SDK uses API keys (BYOK) from Azure Foundry with event-based messaging patterns.

## Provider Configuration

Copilot SDK uses provider configurations to connect to AI services with explicit API credentials:

  ```python
  from copilot import CopilotClient
  import os

  client = CopilotClient()
  await client.start()
  
  # BYOK with Azure Foundry
  session = await client.create_session({
      "model": "gpt-5",
      "provider": {
          "type": "openai",  # For Azure Foundry with /openai/v1/ endpoint
          "base_url": "https://your-resource.openai.azure.com/openai/v1/",
          "api_key": os.environ["AZURE_OPENAI_API_KEY"],
          "wire_api": "responses",  # Use "responses" for GPT-5, "completions" for older
      },
  })
  ```

  Providers support multiple types: `"openai"` for OpenAI-compatible endpoints, `"azure"` for native Azure endpoints, `"anthropic"` for Claude models. The `wire_api` setting chooses between Chat Completions API (`"completions"`) and Responses API (`"responses"`).

## Event-Based Messaging

Copilot SDK uses reactive event handlers instead of direct method calls:

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

  This event-driven pattern enables reactive agent architectures where responses are handled asynchronously through callbacks rather than blocking method calls.

## Sessions

Sessions maintain stateful conversations with automatic history tracking:

  ```python
  # First message
  await session.send({"prompt": "My name is Alice."})
  await done.wait()
  
  # Second message - session remembers context
  await session.send({"prompt": "What is my name?"})
  await done.wait()
  # Response will reference "Alice"
  ```

  Unlike request-response patterns, sessions handle conversation state automatically across multiple interactions.

## Authentication Patterns

Copilot SDK supports two primary auth models:

**1) GitHub Copilot credentials**

- **Logged-in user credentials (default)**: `CopilotClient()` can use stored credentials from `copilot` CLI sign-in.
- **OAuth GitHub App token**: pass `github_token` / `githubToken` to authenticate on behalf of a user.
- **Environment variable tokens** (priority in docs): `COPILOT_GITHUB_TOKEN`, then `GH_TOKEN`, then `GITHUB_TOKEN`.

These modes use GitHub Copilot authentication and typically require a Copilot subscription.

**2) BYOK provider credentials**

For BYOK sessions, supply explicit provider credentials in the provider config. Typical options include API keys and bearer tokens:

  **API Keys**:
  ```python
  provider: {
    "api_key": os.environ["AZURE_OPENAI_API_KEY"]
  }
  ```

  **Bearer Tokens** (custom flows):
  ```python
  provider: {
    "bearer_token": os.environ["MY_BEARER_TOKEN"]
  }
  ```

  **Important Limitation (BYOK)**: Credentials passed to BYOK provider configs are treated as static values; the SDK does not automatically refresh short-lived tokens (for example, tokens obtained via Azure Entra ID or managed identity). If you rely on short-lived tokens you must acquire/refresh them in your application code and recreate or update sessions accordingly.

## Learn More

**Official Documentation**:
- [GitHub Copilot SDK - BYOK Guide](https://github.com/github/copilot-sdk/blob/main/docs/auth/byok.md)
- [GitHub Copilot SDK - Authentication Overview](https://github.com/github/copilot-sdk/blob/main/docs/auth/index.md)
- [Provider Configuration Reference](https://github.com/github/copilot-sdk/blob/main/docs/auth/byok.md#provider-configuration-reference)
- [Getting Started](https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md)
- [GitHub Repository](https://github.com/github/copilot-sdk)

**Installation**:
```bash
pip install github-copilot-sdk
```

**Environment Variables**:
- `AZURE_OPENAI_API_ENDPOINT` - Azure Foundry endpoint (must end with `/openai/v1/`)
- `AZURE_OPENAI_API_KEY` - API key (BYOK - not Azure CLI)
- `AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME` - Model deployment name

**GitHub Copilot Token Environment Variables**:
- `COPILOT_GITHUB_TOKEN` - Recommended explicit token variable for Copilot SDK auth
- `GH_TOKEN` - GitHub CLI-compatible token variable
- `GITHUB_TOKEN` - GitHub Actions-compatible token variable
