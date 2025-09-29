---
title: Getting Started
---

:::info LAB PRE-REQUISITES

- VS Code
- Node.js 18.x or later
- Azure OpenAI API Key
- Azure Cosmos DB

  :::

## Introduction

For this lab, you will be building a chatbot for a bicycle store that can answer queries about bicycles and accessories for you.

### Chatbot Demo

Hosted RAG chatbot example is here: https://aiaaa-s2-chatbot.azurewebsites.net

![alt text](images/chatbot-image.png)

The product catalog for the bicycle store is stored in an Azure Cosmos DB database. The solution will use Azure Cosmos DB vector search capabilities to retrieve relevant documents from the database based on the user's query. It will generate the final response using Chat Completion API from Azure OpenAI.

### Data Ingestion

![RAG](images/rag_design_data_ingestion.png)

### Query Processing

![RAG](images/rag_design.png)

## Lab Outline

1. [Loading Product Catalog](/docs/Chatbot/Load-Product-Catalog): The first step in building the chatbot is to load some sample data into the Azure Cosmos DB database to build a product catalog.

2. [Vector Search with Azure Cosmos DB](/docs/Chatbot/Vector-Search): Use text embeddings to perform vector search in Azure Cosmos DB.

3. [Workflow Orchestration using LangChain](/docs/Chatbot/Using-Langchain): Use LangChain to orchestrate the workflow of querying Azure Cosmos DB and Azure OpenAI services.

4. [Chatbot Backend API](/docs/Chatbot/Chatbot-Backend): Build the Node.js backend API to expose the Azure OpenAI functionality.

5. [Chatbot Frontend](/docs/Chatbot/Chatbot-Frontend): Connect Chatbot Frontend with the Backend API.

## Deployment Architecture

![Solution Architecture Diagram](images/architecture.jpg)

The Front-end Web App is a static SPA application written in React. Since React is outside the scope of this guide, the source code for the Front-end Web App is provided for you. The Front-end Web App communicates with the Node.js backend API, which you will build in this lab.

The Node.js backend API is responsible for generating responses to user queries. It queries Azure Cosmos DB to extract relevant documents using vector search and then uses Azure OpenAI services to generate responses to user queries.

Let's get started by clicking the Next button below.