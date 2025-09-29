---
title: "Automation"
---

:::info TUTORIAL OVERVIEW
In this tutorial, you'll learn how to implement intelligent automation using LLM function calling to streamline store operations.

**What you'll build:** An automation system that can control various store functions through natural language commands.

**What you'll learn:**
- LLM function calling mechanisms
- Workflow automation design
- Integration with business systems
- Conversational automation interfaces
:::

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Implement LLM function calling for automation
2. Design automation workflows for business processes
3. Create conversational interfaces for system control
4. Integrate automation with existing business systems

## Scenario

Your store operations involve many repetitive manual tasks that could be automated to improve efficiency and reduce errors. The goal is to leverage LLM function-calling mechanisms to automate repetitive in-store tasks, improving accuracy, reducing labor-intensive efforts, and streamlining overall operations.

## Goal

Build an intelligent automation system that can understand natural language commands and execute appropriate business functions, similar to a smart assistant for store operations.

## Step-by-Step Implementation

### Step 1: Understanding Function Calling

Function calling allows LLMs to:
- Understand user intent from natural language
- Map requests to specific functions
- Execute functions with appropriate parameters
- Provide feedback about actions taken
- Chain multiple functions for complex workflows

### Step 2: Design Your Automation Functions

Start by identifying common store operations that can be automated. Let's write a program to control the light automation.

### Step 3: Code Solution

<details>
    <summary>Code snippet for above challenge</summary>
    <details>
    <summary>Don't Look! Have you tried to solve it yourself?</summary>
    <details>
    <summary>Your solution will be better than our sample answer!</summary>

    The basic solution is provided below. Feel free to expand on it to make it more interesting!
    Go to `labs/30-AIApps` in terminal, run `npm install`, then run `node 6-Automation.js` to see it in action.
    
    ```
    const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
    const prompt = require("prompt-sync")({ sigint: true });

    async function main() {
      let livinRoomLight = "off";
      let bedroomLight = "off";
      let kitchenLight = "off";

      const client = new OpenAIClient(
        "https://aiaaa-s2-openai.openai.azure.com/",
        new AzureKeyCredential("<AZURE_OPENAI_API_KEY>")
      );

      const deploymentId = "gpt-4o";
      console.log("The chatbot is ready. Type 'exit' to quit.");

      const getLightStatus = {
        name: "get_light_status",
        description: "Retrieves the status of a light",
        parameters: {
          type: "object",
          properties: {
            roomName: {
              type: "string",
              description: "The room where the light is located",
            },
          },
          required: ["roomName"],
        },
      };

      const setLightStatus = {
        name: "set_light_status",
        description: "Sets the status of a light",
        parameters: {
          type: "object",
          properties: {
            roomName: {
              type: "string",
              description: "The room where the light is located",
            },
            status: {
              type: "string",
              description: "The status of the light",
            },
          },
          required: ["roomName", "status"],
        },
      };

      const options = {
        tools: [
          {
            type: "function",
            function: getLightStatus,
          },
          {
            type: "function",
            function: setLightStatus,
          },
        ],
      };

      function applyToolCall({ function: call, id }) {
        if (call.name === "get_light_status") {
          const { room_name } = JSON.parse(call.arguments);
          let status = "off";
          if (room_name === "Living Room") {
            status = livinRoomLight;
          } else if (room_name === "Bedroom") {
            status = bedroomLight;
          } else if (room_name === "Kitchen") {
            status = kitchenLight;
          }

          return {
            role: "tool",
            content: status,
            toolCallId: id,
          };
        } else if (call.name === "set_light_status") {
          const { room_name, status } = JSON.parse(call.arguments);
          if (room_name === "Living Room") {
            livinRoomLight = status;
          } else if (room_name === "Bedroom") {
            bedroomLight = status;
          } else if (room_name === "Kitchen") {
            kitchenLight = status;
          }

          return {
            role: "tool",
            content: "ok",
            toolCallId: id,
          };
        }

        throw new Error(`Unknown tool call: ${call.name}`);
      }

      while (true) {
        var userInput = prompt("User:");
        if (userInput === "exit") {
          break;
        }

        const chatResponse = await client.getChatCompletions(
          "gpt-4o",
          [
            {
              role: "system",
              content:
                "You are a home assistant that can control lights at home. The available lights are Living Room Light`, `Bedroom Light`, and `Kitchen Light. Before changing the lights, you may need to check their current state. Avoid telling the user numbers like the saturation, brightness,and hue; instead, use adjectives like 'bright' or 'dark'.",
            },
            { role: "user", content: userInput },
          ],
          options
        );

        // console.log(chatResponse.choices);
        for (const choice of chatResponse.choices) {
          const responseMessage = choice.message;
          if (responseMessage?.role === "assistant") {
            const requestedToolCalls = responseMessage?.toolCalls;
            if (requestedToolCalls?.length) {
              const toolCallResolutionMessages = [
                responseMessage,
                ...requestedToolCalls.map(applyToolCall),
              ];

              const result = await client.getChatCompletions(
                deploymentId,
                toolCallResolutionMessages
              );

              console.log(result.choices[0].message.content);
            } else {
              console.log(responseMessage.content);
            }
          }
        }
      }
    }

    main().catch((err) => {
      console.error("The sample encountered an error:", err);
    });
    ```

    </details>
    </details>
</details>

### Step 4: Testing it out

- Replace `<AZURE_OPENAI_API_KEY>` placeholder value by looking up  https://aiaaa-s2-setting.azurewebsites.net
- Go to `labs\30-AIApps` folder in terminal windows and run `npm install`
- Start the code by running `node automation.js`
- Try to control light on and off in different rooms

```
User: how many lights?
There are three lights available: Living Room Light, Bedroom Light, and Kitchen Light.

User: turn off living room
I've turned off the lights in the living room for you. If you need anything else, feel free to ask!
```

## Real-World Automation Examples

### Inventory Management
- **Automatic Reordering**: Monitor stock levels and create purchase orders
- **Demand Forecasting**: Predict inventory needs based on sales patterns
- **Expiry Management**: Track and alert on products nearing expiration

### Customer Service
- **Ticket Routing**: Automatically assign support tickets to appropriate staff
- **Response Templates**: Generate personalized customer responses
- **Follow-up Automation**: Schedule and send follow-up communications

### Operations Management
- **Staff Scheduling**: Optimize staff schedules based on demand patterns
- **Energy Management**: Control lighting, HVAC based on occupancy
- **Security Monitoring**: Automated alert systems for unusual activity

### Financial Operations
- **Invoice Processing**: Automated invoice generation and processing
- **Expense Tracking**: Categorize and approve routine expenses
- **Report Generation**: Create daily, weekly, and monthly reports

## Integration Opportunities

### Business Systems
- **ERP Integration**: Connect with enterprise resource planning systems
- **CRM Integration**: Sync with customer relationship management tools
- **POS Systems**: Integrate with point-of-sale terminals
- **Accounting Software**: Automate financial data synchronization

### Communication Platforms
- **Slack/Teams**: Enable automation through chat interfaces
- **Email Systems**: Automated email campaigns and notifications
- **SMS Gateways**: Text message automation for urgent alerts
- **Mobile Apps**: Push notifications and in-app automation
