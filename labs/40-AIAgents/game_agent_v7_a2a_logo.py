"""
Logo Recognition Agent - A2A Service Implementation
===================================================
FastAPI-based A2A protocol service (avoids azure.ai.agentserver version issues)

Prerequisites:
    pip install agent-framework agent-framework-azure-ai fastapi uvicorn

Usage:
    python game_agent_v7_a2a_logo.py
"""

import os
import asyncio
from typing import AsyncIterable
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Any
from agent_framework import Agent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity.aio import DefaultAzureCredential
import uvicorn

load_dotenv()

app = FastAPI()
agent = None
credential = None


class MessageRequest(BaseModel):
    message: Optional[str] = None
    content: Optional[str] = None
    text: Optional[str] = None
    
    def get_message(self) -> str:
        """Extract message from various possible fields"""
        return self.message or self.content or self.text or ""


def create_logo_agent():
    """Create the logo recognition agent"""
    global credential
    
    endpoint = os.getenv('AZURE_OPENAI_API_ENDPOINT')
    # Use gpt-4o for vision capabilities instead of gpt-4.1
    deployment_name = 'gpt-4o'
    
    credential = DefaultAzureCredential()
    
    chat_client = AzureOpenAIChatClient(
        endpoint=endpoint,
        deployment_name=deployment_name,
        credential=credential
    )
    
    return Agent(
        name="LogoDetectionAgent",
        client=chat_client,
        instructions="""You are a logo detection specialist with vision capabilities. 
        When given an image URL, analyze the image and identify the company or brand logo. 
        Look at the image carefully and return only the name of the logo/brand (e.g., "Python", "Microsoft", "Google"). 
        If you cannot analyze the image, try to infer from the URL."""
    )


@app.on_event("startup")
async def startup():
    global agent
    agent = create_logo_agent()
    print("✓ Logo Detection Agent started on http://localhost:8088")
    print("  Agent card: http://localhost:8088/.well-known/agent-card")
    print("  Ready to accept A2A requests")


@app.on_event("shutdown")
async def shutdown():
    if credential:
        await credential.close()


@app.get("/.well-known/agent-card")
@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """A2A protocol: Agent discovery endpoint"""
    return JSONResponse({
        "name": "LogoDetectionAgent",
        "description": "Detects and identifies logos from image URLs",
        "version": "1.0.0",
        "url": "http://localhost:8088",
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "skills": [
            {
                "name": "logo-detection",
                "id": "logo-detection-v1",
                "description": "Detect and identify logos from images",
                "tags": ["vision", "logos", "branding"]
            },
            {
                "name": "image-analysis",
                "id": "image-analysis-v1",
                "description": "Analyze images for brand identification",
                "tags": ["vision", "analysis"]
            }
        ],
        "capabilities": {
            "streaming": True
        },
        "tools": [
            {
                "name": "detect_logo",
                "description": "Detect the name of a logo or brand from an image URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the image containing the logo"
                        }
                    },
                    "required": ["image_url"]
                }
            }
        ]
    })


async def stream_response(text: str) -> AsyncIterable[str]:
    """Stream response in SSE format for A2A protocol"""
    import json
    
    # Send chunks
    for chunk in text.split():
        data = json.dumps({"type": "text", "content": chunk + " "})
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.01)
    
    # Send done signal
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/")
@app.post("/v1/message")
@app.post("/v1/message:stream")
async def message_stream(request: Request):
    """A2A protocol: Message endpoint (supports both streaming and non-streaming)"""
    if not agent:
        return JSONResponse(
            {"error": "Agent not initialized"}, 
            status_code=500
        )
    
    try:
        # Parse JSON body flexibly
        body = await request.json()
        print(f"Received request body: {body}")
        
        # Extract message from A2A JSON-RPC structure
        message = None
        
        # Try A2A JSON-RPC format: params.message.parts[].text
        if 'params' in body and 'message' in body['params']:
            msg_obj = body['params']['message']
            if 'parts' in msg_obj and len(msg_obj['parts']) > 0:
                # Get text from all parts and concatenate
                texts = [part.get('text', '') for part in msg_obj['parts'] if part.get('kind') == 'text']
                message = ' '.join(texts) if texts else None
        
        # Fallback to simple message field
        if not message:
            message = body.get('message') or body.get('content') or body.get('text') or body.get('prompt')
        
        if not message:
            print(f"No message found in body keys: {list(body.keys())}")
            return JSONResponse(
                {"error": "No message content provided", "received_keys": list(body.keys())}, 
                status_code=400
            )
        
        print(f"Extracted message: {message}")
        result = await agent.run(message)
        
        return StreamingResponse(
            stream_response(result.text),
            media_type="text/event-stream"
        )
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": str(e)}, 
            status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088)
