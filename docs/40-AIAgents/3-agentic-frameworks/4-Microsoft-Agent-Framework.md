# Microsoft Agent Framework

Microsoft Agent Framework is an official SDK from Microsoft for building production-ready AI agents with standardized patterns across multiple AI providers. It provides enterprise-grade agent development with built-in support for Azure OpenAI Responses API, tool integration, session management, and streaming capabilities.

Agent Framework is designed for **cloud-native enterprise deployments** where security, compliance, and scalability are paramount. Documentation examples show `AzureCliCredential` for local development, while production and managed-identity scenarios should use `DefaultAzureCredential` or `ManagedIdentityCredential` from `azure-identity` to integrate with Entra ID and managed identities.

**Package**: `agent-framework`

**Use Cases**: Enterprise AI agents requiring Azure Entra ID authentication, production deployments with managed identities, agents using Responses API tools (code interpreter, file search, web search), multi-provider agent architectures.

**Why Microsoft Agent Framework?**
- **Enterprise Security**: Azure CLI authentication with managed identity and Entra ID support
- **Official Microsoft SDK**: Production-ready with ongoing support and updates
- **Multi-Provider**: Standardized patterns work across Azure OpenAI, OpenAI, Anthropic, GitHub Copilot
- **Rich Tooling**: Native integration with Responses API tools and MCP servers
- **Cloud-Native**: Built for Azure deployments (App Service, Functions, Container Apps)
- **Async-First**: Modern Python async architecture for scalability

Let's cover some core components:

## Create Microsoft Agent Framework Agent

- navigate to `labs/40-AIAgents` folder, open `game_agent_v3_maf.py` file.

```python
cd labs/40-AIAgents
```

- run the agent and see the console output.

```python
python game_agent_v3_maf.py
```

Expected output:

```
Microsoft Agent Framework agent initialized: default-player
Testing agent: default-player
Q: What is 15 + 27?
A: 42
Game Agent: Test complete
```

- Microsoft Agent Framework uses async patterns and Azure CLI authentication for secure, production-ready deployments.

## Providers

Agent Framework abstracts AI providers through a unified interface. The Azure OpenAI provider uses `AzureOpenAIResponsesClient` to connect to Azure's Responses API:

    ```python
    from agent_framework.azure import AzureOpenAIResponsesClient
    from azure.identity import AzureCliCredential, DefaultAzureCredential

    # Local development: Azure CLI. Production: DefaultAzureCredential or ManagedIdentityCredential.
    client = AzureOpenAIResponsesClient(
      azure_endpoint=os.getenv('AZURE_OPENAI_API_ENDPOINT'),
      deployment_name=os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME'),
      credential=AzureCliCredential()
    )
  
  agent = client.as_agent(
      name="MyAgent",
      instructions="You are a helpful assistant."
  )
  ```

  The Responses API provides comprehensive tool support including code interpreter, file search, web search, and hosted MCP servers. Use `AzureCliCredential()` for local development (requires `az login`). For production and managed identity scenarios prefer `DefaultAzureCredential()` or `ManagedIdentityCredential()` which integrate with Entra ID and managed identities.

## Agents

Agents are created using the `.as_agent()` method, which transforms a provider client into an autonomous agent with instructions:

  ```python
  agent = client.as_agent(
      name="GameAgent",
      instructions="You are a helpful assistant for playing games."
  )
  ```

  Agents automatically handle conversation history, tool invocation, and response generation. The async `run()` method executes agent logic:

  ```python
  result = await agent.run("What is 15 + 27?", session=session)
  ```

## Sessions

Sessions maintain conversation state across multi-turn interactions:

  ```python
  session = agent.create_session()
  
  # First interaction
  await agent.run("My name is Alice.", session=session)
  
  # Second interaction - agent remembers context
  result = await agent.run("What is my name?", session=session)
  # Returns: "Alice"
  ```

  Sessions enable stateful conversations with automatic history management, critical for building conversational AI applications.

## Async Architecture

Agent Framework is built on modern Python async patterns for scalability and performance:

  ```python
  async with client.as_agent(name="AsyncAgent", instructions="...") as agent:
      session = agent.create_session()
      result = await agent.run("Hello!", session=session)
  ```

  Async context managers ensure proper resource cleanup. All agent operations are async, enabling concurrent execution and efficient I/O handling.

## Learn More

**Official Documentation**:
- [Microsoft Agent Framework Overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)
- [Azure OpenAI Provider](https://learn.microsoft.com/agent-framework/agents/providers/azure-openai)
- [Your First Agent Tutorial](https://learn.microsoft.com/agent-framework/get-started/your-first-agent)
- [GitHub Repository](https://github.com/microsoft/agent-framework)

**Installation**:
```bash
pip install agent-framework --pre
pip install azure-identity
```

**Environment Variables**:
- `AZURE_OPENAI_API_ENDPOINT` - Your Azure Foundry endpoint
- `AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME` - Model deployment name
- Authentication: use `az login` for local development; in production use Managed Identity or `DefaultAzureCredential` for managed-identity/Entra ID scenarios