# AI Apps and Agents in a day (Lab)

## Lab Structure

### Part 1: Build a Basic Agent
- Introduction to agentic AI concepts (prompt → plan → act → reflect loop)
- Use Azure OpenAI for chat, planning, and coding
- Hands-on: Build a simple agent that can play Rock Paper Scissor via prompt-response
- Explore Semantic Kernel for basic agent memory

**tech**
connect to foundry project 
consume different llm
ingest document to ai search
query ai search + rag
create tools to perform api call
SK lib

### Part 2: Make the Agent Smarter with Data & Tools
- Integrate Azure AI Search (RAG) for intelligent data retrieval
- Use Azure Functions for serverless tool integration
- Store agent state in Azure Storage or Cosmos DB
- Hands-on: Enhance the agent to learn from previous matches and use external data/tools to improve gameplay

**tech**
ingest image to cosmos db
query cosmos db + image vector rag
create multiple tools to perform local actions
tool to query webapi and response
langchain lib (use previous lab)

### Tournament A:
15 minutes: Rock Paper Scissor Rookie Tournament

For each round:
- agent to enrol the game by following instructions (say the magic word)
- agent to call api to retrieve question (text / based on KB)
- agent to resolve and find the right answer before submitting its move (answer must be correct otherwise timeout)
- agent to submit its move to the API server
- server checks the answer and decides the winner
- next round starts
- first to 3 wins

Agent
- prompt to guide strategy
- query knowledge base (RAG DB)
- tool to resolve the question
- tool to invoke api and understand json output


### Part 3: Orchestrate, Multi-Agent Collaboration
- Orchestrate agent workflows with Azure Logic Apps
- Host the agent using App Service, AKS, or Azure Container Apps
- Secure APIs with Azure API Management and manage secrets with Key Vault
- Hands-on: Deploy the agent, enable secure API interactions, and automate tournament workflows

**tech**
consume vision api
consume doc intelelligence
consume voice api
sequential orcheistration 
connect agent to logic app


### Part 4: MCP, Deploy, Competition
- Enable multi-agent orchestration (agents collaborate, compete, or strategize in Rock Paper Scissor Tournament)
- Implement strategies for agents to adapt and learn from opponents
- Prepare the app for production: security, scaling, monitoring, and operational excellence
- Hands-on: Agents interact and compete in the tournament, demonstrating orchestration and monitoring
- deploy to website 

**tech**
azure static web
human in the loop (human based random question)
local llm trace
llm evaluation local
build a local mcp server
build github action /ci/cd deployment (no bicep, az resource are provisioned in advance)



### Tournament B:
15 minutes: Rock Paper Scissor Championship

For each round:
- agent to enrol the game by following instructions (say the magic word)
- agent to call api to retrieve question (question could be an image, text, word doc, question random, speech)
- agent to resolve and find the right answer before submitting its move (answer must be correct otherwise timeout)
- agent to submit its move to the API server
- connected agent to receive backdoor tips
- server checks the answer and decides the winner
- next round starts
- first to 3 wins
- special advantage: past result win/loss pattern
- online deployed agent only (github static page or azure swa using token only)
- existing speach agent
- existing doc agent
- sequencial and handoff pattern


Agent
- prompt to guide strategy
- query knowledge base (RAG DB)
- tool to resolve the question
- tool to perform calcuation, image detection, or OCR or word doc
- tool to invoke api and understand json output
- tool to query the internet
- connection agent to receive backdoor tips
- 


# Rock Paper Scissor Tournament:

## API Server Design

Create an API server (Azure Functions or App Service) to manage tournament logic, player registration, and match orchestration.
Endpoints: register agent, start match, submit move, get results.

Each agent (player) connects to the API server, registers, and participates in matches.
Agents can be implemented as scripts or services (e.g., Python, Node.js).
Tournament Logic

## 8 players per group.
Each match: best of 3 rounds (first to 2 wins).
Winners advance to play other winners until a final winner is determined.
Azure Integration

Use Azure Functions for serverless API endpoints.
Store tournament state in Azure Storage or Cosmos DB.



# These topics to be covered in the lab:

Azure Resource Types
Microsoft Foundry (Model Catalog, Playground, Agent Service)
Azure OpenAI (LLMs for chat, planning, coding, summarization)
Azure AI Search (RAG, intelligent data layer)
Azure Functions (serverless tool integration)
Azure Logic Apps (workflow orchestration)
App Service / AKS / ACA (app hosting: web, container, Kubernetes)
Azure API Management (APIM) (secure API exposure)
Azure Key Vault (secrets management)
Azure Storage / Cosmos DB (agent state, knowledge storage)
Azure Monitor / Application Insights (logging, monitoring)
Technologies to Cover
Semantic Kernel (agent memory, planning, tool integration)
GitHub Copilot (coding assistant, automation)
Jupyter Notebooks (interactive exploration, model testing)
GitHub Codespaces (cloud dev environment)
Bicep (Infrastructure as Code for Azure)
Azure CLI / PowerShell (management, automation)
CI/CD (GitHub Actions, Azure DevOps for deployment)
Multi-Agent Orchestration (agent collaboration, perception → planning → action loop)
Security & Compliance (auth, rate limits, monitoring, cost controls)
Lab Focus Areas
Building agentic AI apps with prompt → plan → act → reflect loop
Integrating and orchestrating Azure AI services and tools
Deploying and operationalizing with containerization and CI/CD
Implementing security, monitoring, and production readiness




