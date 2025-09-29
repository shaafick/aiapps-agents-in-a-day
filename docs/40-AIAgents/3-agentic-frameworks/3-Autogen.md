
# AutoGen

AutoGen is an open-source framework developed by Microsoft Research's AI Frontiers Lab. It focuses on event-driven, distributed *agentic* applications, enabling multiple LLMs and SLMs, tools, and advanced multi-agent design patterns.

AutoGen is built around the core concept of agents, which are autonomous entities that can perceive their environment, make decisions, and take actions to achieve specific goals. Agents communicate through asynchronous messages, allowing them to work independently and in parallel, enhancing system scalability and responsiveness.

<a href="https://en.wikipedia.org/wiki/Actor_model" target="_blank">Agents are based on the actor model</a>. According to Wikipedia, an actor is _the basic building block of concurrent computation. In response to a message it receives, an actor can: make local decisions, create more actors, send more messages, and determine how to respond to the next message received_.

**Use Cases**: Automating code generation, data analysis tasks, and building custom agents for planning and research functions.

Here are some important core concepts of AutoGen we will cover in this lab.



## Create Autogen Agent

- navigate to `labs/40-AIAgents` folder, open `game_agent_v3_autogen.py` file.

```python
cd labs/40-AIAgents
```

- run the agent and see the console output.

```python
python game_agent_v3_autogen.py
```

![Azure AI Foundry Project](./images/autogen.png)

## Agents

An agent is a software entity that:
  - **Communicates via messages**, these messages can be synchronous or asynchronous.
  - **Maintains its own state**, which can be modified by incoming messages.
  - **Performs actions** in response to received messages or changes in its state. These actions may modify the agent’s state and produce external effects, such as updating message logs, sending new messages, executing code, or making API calls.
    
  Here you have a short code snippet in which you create your own agent with Chat capabilities:

    ```python
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient


    class MyAssistant(RoutedAgent):
        def __init__(self, name: str) -> None:
            super().__init__(name)
            model_client = OpenAIChatCompletionClient(model="gpt-4o")
            self._delegate = AssistantAgent(name, model_client=model_client)
    
        @message_handler
        async def handle_my_message_type(self, message: MyMessageType, ctx: MessageContext) -> None:
            print(f"{self.id.type} received message: {message.content}")
            response = await self._delegate.on_messages(
                [TextMessage(content=message.content, source="user")], ctx.cancellation_token
            )
            print(f"{self.id.type} responded: {response.chat_message.content}")
    ```
    
    In the previous code, `MyAssistant` has been created and inherits from `RoutedAgent`. It has a message handler that prints the content of the message and then sends a response using the `AssistantAgent` delegate. Especially note how we assign to `self._delegate` an instance of `AssistantAgent` which is a pre-built agent that can handle chat completions.


    Let's let AutoGen know about this agent type and kick off the program next:

    ```python
    
    # main.py
    runtime = SingleThreadedAgentRuntime()
    await MyAgent.register(runtime, "my_agent", lambda: MyAgent())

    runtime.start()  # Start processing messages in the background.
    await runtime.send_message(MyMessageType("Hello, World!"), AgentId("my_agent", "default"))
    ```

    In the previous code the agents are registered with the runtime and then a message is sent to the agent resulting in the following output:

    ```text
    # Output from the console:
    my_agent received message: Hello, World!
    my_assistant received message: Hello, World!
    my_assistant responded: Hello! How can I assist you today?
    ```

## Multi agents

AutoGen supports the creation of multiple agents that can work together to achieve complex tasks. Agents can communicate, share information, and coordinate their actions to solve problems more efficiently. To create a multi-agent system, you can define different types of agents with specialized functions and roles, such as data retrieval, analysis, decision-making, and user interaction. Let's see how such a creation looks like so we get a sense of it:

    ```python
    editor_description = "Editor for planning and reviewing the content."

    # Example of declaring an Agent
    editor_agent_type = await EditorAgent.register(
    runtime,
    editor_topic_type,  # Using topic type as the agent type.
    lambda: EditorAgent(
        description=editor_description,
        group_chat_topic_type=group_chat_topic_type,
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o-2024-08-06",
            # api_key="YOUR_API_KEY",
        ),
        ),
    )

    # remaining declarations shortened for brevity

    # Group chat
    group_chat_manager_type = await GroupChatManager.register(
    runtime,
    "group_chat_manager",
    lambda: GroupChatManager(
        participant_topic_types=[writer_topic_type, illustrator_topic_type, editor_topic_type, user_topic_type],
        model_client=OpenAIChatCompletionClient(
            model="gpt-4o-2024-08-06",
            # api_key="YOUR_API_KEY",
        ),
        participant_descriptions=[
            writer_description, 
            illustrator_description, 
            editor_description, 
            user_description
        ],
        ),
    )
    ```

    In the previous code we have a `GroupChatManager` that is registered with the runtime. This manager is responsible for coordinating the interactions between different types of agents, such as writers, illustrators, editors, and users.

## Agent Runtime

The framework provides a runtime environment, enabling communication between agents, manages their identities and lifecycles, and enforce security and privacy boundaries. This means that you can run your agents in a secure and controlled environment, ensuring that they can interact safely and efficiently. There are two runtimes of interest:

  - **Stand-alone runtime**. This is a good choice for single-process applications where all agents are implemented in the same programming language and run in the same process. Here's an illustration of how it works: <a href="https://microsoft.github.io/autogen/stable/_images/architecture-standalone.svg" target="_blank">Stand-alone runtime</a>

  - **Distributed agent runtime**, is suitable for multi-process applications where agents may be implemented in different programming languages and running on different machines. Here's an illustration of how it works:     <a href="https://microsoft.github.io/autogen/stable/_images/architecture-distributed.svg" target="_blank">Distributed runtime</a>
