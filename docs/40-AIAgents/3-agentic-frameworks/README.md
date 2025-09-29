
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

- **Azure AI Agent Service**: Is a platform and deployment service in Azure Foundry for agents. It offers building connectivity to services support by Azure Found like Azure OpenAI, Azure AI Search, Bing Search and code execution.
- **Semantic Kernel**: Is a production-ready agent library for building enterprise agentic applications. Focuses on event-driven, distributed agentic applications, enabling multiple LLMs and SLMs, tools, and single/multi-agent design patterns.
- **AutoGen**: Is an experimentation framework focused on leading-edge research on multi-agent systems. It is the best place to experiment and prototype sophisticated multi-agent systems.
- **LangChain**: Is a widely adopted open-source framework for building applications powered by language models. It provides a suite of tools and abstractions to facilitate the development of AI-driven applications. 

There are many ways to compare these frameworks, we can look at some key differences in terms of their design, capabilities, and target use cases. It does sound like there is a lot of overlap between these frameworks, but there are some key differences in terms of their design, capabilities, and target use cases.

Let's summarize the key differences in a table:

| Framework | Focus | Core Concepts | Use Cases |
| --- | --- | --- | --- |
| LangChain | Understanding and generating human-like text content | Agents, Modular Components, Collaboration | Natural language understanding, content generation |
| AutoGen | Event-driven, distributed agentic applications | Agents, Personas, Functions, Data | Code generation, data analysis tasks |
| Semantic Kernel | Understanding and generating human-like text content | Agents, Modular Components, Collaboration | Natural language understanding, content generation |
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
> A: A great choice is to build your application in Semantic Kernel first and then use Azure AI Agent Service to deploy your agent. This approach allows you to easily persist your agents while leveraging the power to build multi-agent systems in Semantic Kernel. Additionally, Semantic Kernel has a connector in AutoGen, making it easy to use both frameworks together.
 

## Integrate existing Azure ecosystem tools

The answer is yes, you can integrate your existing Azure ecosystem tools directly with Azure AI Agent Service especially, this because it has been built to work seamlessly with other Azure services. You could for example integrate Bing, Azure AI Search, and Azure Functions. There's also deep integration with Azure AI Foundry.

For AutoGen and Semantic Kernel, you can also integrate with Azure services, but it may require you to call the Azure services from your code. Another way to integrate is to use the Azure SDKs to interact with Azure services from your agents. Additionally, like was mentioned, you can use Azure AI Agent Service as an orchestrator for your agents built in AutoGen or Semantic Kernel which would give easy access to the Azure ecosystem.
