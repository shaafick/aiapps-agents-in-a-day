
# AI Agent Frameworks

AI agent frameworks are software platforms designed to simplify the creation, deployment, and management of AI agents. These frameworks provide developers with pre-built components, abstractions, and tools that streamline the development of complex AI systems.

These frameworks help developers focus on the unique aspects of their applications by providing standardized approaches to common challenges in AI agent development. They enhance scalability, accessibility, and efficiency in building AI systems.

## What are AI Agent Frameworks and what do they enable developers to do?

Traditional AI Frameworks can help you integrate AI into your apps and make these apps better in the following ways:

- **Personalization**: AI can analyze user behavior and preferences to provide personalized recommendations, content, and experiences.
Example: Streaming services like Netflix use AI to suggest movies and shows based on viewing history, enhancing user engagement and satisfaction.
- **Automation and Efficiency**: AI can automate repetitive tasks, streamline workflows, and improve operational efficiency.
Example: Customer service apps use AI-powered chatbots to handle common inquiries, reducing response times and freeing up human agents for more complex issues.
- **Enhanced User Experience**: AI can improve the overall user experience by providing intelligent features such as voice recognition, natural language processing, and predictive text.
Example: Virtual assistants like Siri and Google Assistant use AI to understand and respond to voice commands, making it easier for users to interact with their devices.

### Why do we need the AI Agent Framework?

AI Agent frameworks represent something more than just AI frameworks. They are designed to enable the creation of intelligent agents that can interact with users, other agents, and the environment to achieve specific goals. These agents can exhibit autonomous behavior, make decisions, and adapt to changing conditions. Let's look at some key capabilities enabled by AI Agent Frameworks:

- **Agent Collaboration and Coordination**: Enable the creation of multiple AI agents that can work together, communicate, and coordinate to solve complex tasks.
- **Task Automation and Management**: Provide mechanisms for automating multi-step workflows, task delegation, and dynamic task management among agents.
- **Contextual Understanding and Adaptation**: Equip agents with the ability to understand context, adapt to changing environments, and make decisions based on real-time information.

So in summary, agents allow you to do more, to take automation to the next level, to create more intelligent systems that can adapt and learn from their environment.

### How to prototype, iterate, and improve the agent’s capabilities?

This is a fast-moving landscape, but there are some things that are common across most AI Agent Frameworks that can help you quickly prototype and iterate namely module components, collaborative tools, and real-time learning. Let's dive into these:

- **Use Modular Components**: AI SDKs offer pre-built components such as AI and Memory connectors, function calling using natural language or code plugins, prompt templates, and more.
- **Leverage Collaborative Tools**: Design agents with specific roles and tasks, enabling them to test and refine collaborative workflows.
- **Learn in Real-Time**: Implement feedback loops where agents learn from interactions and adjust their behavior dynamically.

## AI Agent Frameworks

 - **[Azure AI Agent Service](./1-Azure-AI-Agent-Service.md)**: A Microsoft platform for agent deployment and orchestration with integrations into the Azure ecosystem. Use the linked page for details on how it integrates with Azure services.
	 - Official docs (Azure AI overview): https://learn.microsoft.com/azure/ai-services/
 - **[Semantic Kernel](./2-Semantic-Kernel.md)**: A Microsoft SDK for building agentic applications, focused on prompt orchestration, memory, plugins and extensibility. It is well-suited for production-ready agents that require SDK-level control.
	 - Official docs: https://learn.microsoft.com/semantic-kernel/
 - **[AutoGen](./3-Autogen.md)**: An experimentation and research-oriented framework (GitHub project) for multi-agent orchestration and advanced multi-agent patterns. Good for prototyping and research; treat some parts as experimental.
	 - Official repo: https://github.com/microsoft/autogen
 - **[Microsoft Agent Framework](./4-Microsoft-Agent-Framework.md)**: The repository's lightweight framework and guidance for local-first agents (ties to Azure OpenAI in examples). Use the local doc for implementation details.
 - **[Microsoft Agent Framework](./4-Microsoft-Agent-Framework.md)**: The repository's lightweight framework and guidance for local-first agents (ties to Azure OpenAI in examples). Use the local doc for implementation details.
	 - Official docs: https://learn.microsoft.com/agent-framework/overview/
 - **[GitHub Copilot SDK](./5-GitHub-Copilot-SDK.md)**: Tooling and SDKs to build Copilot-style integrations; supports enterprise BYOK patterns for Copilot workflows. This is oriented to Copilot-style extensions rather than a general LLM framework.
	 - Official repo/docs: https://github.com/github/copilot-sdk
 - **[LangChain](./5-LangChain.md)**: A widely adopted open-source framework providing chains, agents, connectors and integrations (large community and rich Python/JS ecosystems). Best when you want rapid prototyping with many pre-built connectors.
	 - Official docs: https://python.langchain.com/en/latest/

There are many ways to compare these frameworks. They overlap in capabilities, but differ in origin, primary language/SDK, and typical deployment targets. The short notes below add nuance and soften absolute recommendations.

Let's summarize the key differences in a table:

| Framework | Focus | Core Concepts | Use Cases |
| --- | --- | --- | --- |
| LangChain | Understanding and generating human-like text content | Agents, Modular Components, Collaboration | Natural language understanding, content generation |
| AutoGen | Event-driven, distributed agentic applications | Agents, Personas, Functions, Data | Code generation, data analysis tasks |
| Semantic Kernel | Understanding and generating human-like text content | Agents, Modular Components, Collaboration | Natural language understanding, content generation |
| Microsoft Agent Framework | Lightweight local/hybrid agent development | Conversation Management, Direct Azure OpenAI Integration | Simple agents, edge deployments, full control scenarios |
| GitHub Copilot SDK | BYOK agent development with Copilot patterns | BYOK Credentials, Custom Deployments, Enterprise Control | Custom Copilot extensions, enterprise security, cost management |
| Azure AI Agent Service | Flexible models, enterprise security, Code generation, Tool calling | Modularity, Collaboration, Process Orchestration | Secure, scalable, and flexible AI agent deployment |


Common use cases:
 
> Q: I'm experimenting, learning and building proof-of-concept agent applications, and I want to be able to build and experiment quickly
>

>A: AutoGen would be a good choice for this scenario, as it focuses on event-driven, distributed agentic applications and supports advanced multi-agent design patterns.

> Q: What makes AutoGen a better choice than Semantic Kernel and Azure AI Agent Service for this use case?
>
> A: AutoGen is specifically designed for event-driven, distributed agentic applications, making it well-suited for automating code generation and data analysis tasks. It provides the necessary tools and capabilities to build complex multi-agent systems efficiently.

>Q: Sounds like Azure AI Agent Service could work here too, it has tools for code generation and more?

>
> A: Yes, Azure AI Agent Service is a platform service for agents and add built-in capabilities for multiple models, Azure AI Search, Bing Search and Azure Functions. It makes it easy to build your agents in the Foundry Portal and deploy them at scale.
 
> Q: I'm still confused just give me one option
>
> A: A great choice is to build your application in Semantic Kernel first and then use Foundry Agent Service to deploy your agent. This approach allows you to easily persist your agents while leveraging the power to build multi-agent systems in Semantic Kernel. Additionally, Semantic Kernel has a connector in AutoGen, making it easy to use both frameworks together.
 

## Integrate existing Azure ecosystem tools

The answer is yes, you can integrate your existing Azure ecosystem tools directly with Azure AI Agent Service especially, this because it has been built to work seamlessly with other Azure services. You could for example integrate Bing, Azure AI Search, and Azure Functions. There's also deep integration with Microsoft Foundry.

For AutoGen and Semantic Kernel, you can also integrate with Azure services, but it may require you to call the Azure services from your code. Another way to integrate is to use the Azure SDKs to interact with Azure services from your agents. Additionally, like was mentioned, you can use Azure AI Agent Service as an orchestrator for your agents built in AutoGen or Semantic Kernel which would give easy access to the Azure ecosystem.

**Microsoft Agent Framework — research notes**

- Agent Framework is a Microsoft-authored successor that combines concepts from Semantic Kernel and AutoGen; it is designed to provide unified, production-ready agent abstractions and explicit multi-agent workflows. (source: Microsoft docs)
- Status: public preview; expect API and features to evolve — validate production readiness and licensing for your scenario. (source: Microsoft docs)
- Key features:
	- Multi-agent orchestration patterns (sequential, concurrent, group chat, handoff, magentic lead/worker patterns).
	- Session-based state management and long-running/human-in-the-loop support.
	- Workflow/graph-based execution to express explicit multi-agent execution paths.
	- Provider-agnostic chat client abstractions (`IChatClient` / `ChatClientAgent`) supporting OpenAI, Azure OpenAI, Foundry, and other providers.
	- Enterprise features: OpenTelemetry observability, Microsoft Entra (Azure AD) integration for security, and responsible AI controls.
	- Standards interoperability: support for A2A/MCP and other agent-to-agent protocols where applicable.
- Language/SDK support: packages and examples exist for Python and .NET (C#); installation is via `agent-framework` packages (preview builds). See migration guides for Semantic Kernel and AutoGen.
- Foundry integration: can create persistent Foundry/Foundry Agent Service-backed agents with service-managed chat history and deployment-managed resources; requires Foundry project configuration. (see Azure Foundry docs)
- Migration & guides: Microsoft provides migration guides from Semantic Kernel and AutoGen to Agent Framework — consult them when porting existing agents.
- Cautions: preview status means some components are experimental; data flow to third-party agents/services should be reviewed for compliance and governance.

Links (primary Microsoft sources):
- Agent Framework overview: https://learn.microsoft.com/agent-framework/overview/
- Migration guide (from Semantic Kernel): https://learn.microsoft.com/agent-framework/migration-guide/from-semantic-kernel/
- Migration guide (from AutoGen): https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/
- Azure AI / Foundry agent docs: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview
- .NET AI ecosystem reference (Agent Framework section): https://learn.microsoft.com/dotnet/ai/dotnet-ai-ecosystem#microsoft-agent-framework

If you want, I can also update the per-framework pages (e.g., `4-Microsoft-Agent-Framework.md`) with matching notes and code examples from the official docs.
