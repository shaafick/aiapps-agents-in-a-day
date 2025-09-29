import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool, FileSearchTool, FilePurpose
from azure.ai.agents.models import ConnectedAgentTool, MessageRole
from azure.ai.agents.models import (
    ListSortOrder,
    McpTool,
    RequiredMcpToolCall,
    RunStepActivityDetails,
    SubmitToolApprovalAction,
    ToolApproval,
)
import time

load_dotenv()

# Azure Monitor tracing setup
os.environ["AZURE_SDK_TRACING_IMPLEMENTATION"] = "opentelemetry"
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.agents.telemetry import AIAgentsInstrumentor

# Setup OpenTelemetry tracing
resource = Resource(attributes={
    "service.name": "rps-game-agent"
})
provider = TracerProvider(resource=resource)

# Configure Azure Monitor if connection string is available
application_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
configure_azure_monitor(connection_string=application_insights_connection_string)
trace.set_tracer_provider(provider)

# Instrument Azure AI Agents
AIAgentsInstrumentor().instrument(True)

tracer = trace.get_tracer(__name__)


class GameAgent:
    
    def __init__(self, project_endpoint=None, model_deployment_name=None, player_name=None):
        self.project_endpoint = project_endpoint or os.getenv('AZURE_FOUNDRY_PROJECT_ENDPOINT')
        self.model_deployment_name = model_deployment_name or os.getenv('AZURE_FOUNDRY_MODEL_DEPLOYMENT_NAME')
        self.player_name = player_name or os.getenv('DEV_Name', 'default-player')
        self.player_name = self.player_name + "_v9"
        
        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=DefaultAzureCredential()
        )
        
        self.agent_name = f"agent_{self.player_name}"
        self.agent = None

        self.agent_stock_name = f"stock_price_bot"
        self.agent_stock = None

        self.thread = None
        self._client_context = None
        self.mcp_tool = None

        self.vector_store = None
        self.file_search_tool = None
    
    def __enter__(self):
        self._client_context = self.project_client.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client_context:
            return self.project_client.__exit__(exc_type, exc_val, exc_tb)
    
    def _find_existing_agent(self):
        """Find existing agent by name"""
     
        agents = self.project_client.agents.list_agents()
        for agent in agents:
            if agent.name == self.agent_name:
                return agent
 
        return None
    
    def cleanup_old_agents(self):
        """Clean up old agents with the same name (optional maintenance method)"""
        try:
            agents = self.project_client.agents.list_agents()
            for agent in agents:
                if agent.name == self.agent_name and agent.id != (self.agent.id if self.agent else None):
                    self.project_client.agents.delete(agent.id)
        except Exception:
            pass
    
    def create_vector_store_with_files(self):
        """Create vector store and upload files for file search"""
            
        vector_store_name = f"game-rulebook-store"
        file_paths = ['game_rulebook.txt']
        uploaded_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                uploaded_file = self.project_client.agents.files.upload_and_poll(
                    file_path=file_path, purpose=FilePurpose.AGENTS
                )
                uploaded_files.append(uploaded_file)
                print(f"Uploaded file: {file_path} (ID: {uploaded_file.id})")
            
        self.vector_store = self.project_client.agents.vector_stores.create_and_poll(
            data_sources=[], 
            name=vector_store_name,
            expires_after={
                "anchor": "last_active_at",
                "days": 7
            }
        )
        print(f"Created vector store: {self.vector_store.id}")
        
        file_ids = [f.id for f in uploaded_files]
        vector_store_file_batch = self.project_client.agents.vector_store_file_batches.create_and_poll(
            vector_store_id=self.vector_store.id, 
            file_ids=file_ids
        )
        print(f"Added files to vector store batch: {vector_store_file_batch.id}")
        
        return self.vector_store
    
    def setup_file_search_tool(self):
        """Setup file search tool with optional file uploads"""
        self.file_search_tool = FileSearchTool()
        
        vector_store = self.create_vector_store_with_files()
        self.file_search_tool.add_vector_store(vector_store.id)
                
        return self.file_search_tool
    
    def _setup_agent(self):
        """Setup the Azure AI agent - reuse existing or create new"""
        existing_agent = self._find_existing_agent()
        
        if existing_agent:
            self.project_client.agents.delete_agent(existing_agent.id)
            print(f"Deleted existing agent: {self.agent_name}")
        
        tools = self._setup_tools()
        tool_resources = self.file_search_tool.resources
            
        self.agent_stock = self.project_client.agents.create_agent(
            model=self.model_deployment_name,
            name=self.agent_stock_name,
            instructions="Your job is to get the stock price of a company. If you don't know the realtime stock price, return the last known stock price.",
        )

        connected_agent = ConnectedAgentTool(
            id=self.agent_stock.id, name=self.agent_stock.name, description="Gets the stock price of a company"
        )
        tools.extend(connected_agent.definitions)
        
        self.agent = self.project_client.agents.create_agent(
            model=self.model_deployment_name,
            name=self.agent_name,
            instructions=f"You are {self.player_name}, a helpful assistant that can answer questions and play Rock-Paper-Scissors games. You have access to file search capabilities to help answer questions from uploaded documents. Keep answer short and precise, dont need to explain.",
            tools=tools,
            tool_resources=tool_resources
        )
        print(f"Created new agent: {self.agent_name}")
        
        self.thread = self.project_client.agents.threads.create()
    
    def _call_azure_ai_agent(self, message):
        """Call Azure AI Foundry Agent service"""
        self.project_client.agents.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        run = self.project_client.agents.runs.create(
            thread_id=self.thread.id,
            agent_id=self.agent.id,
            tool_resources=self.mcp_tool.resources
        )
        print(f"Created run, ID: {run.id}")
        
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = self.project_client.agents.runs.get(thread_id=self.thread.id, run_id=run.id)
            print(f"Created run, ID: {run.id}")
            
            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    if tool_call.function.name == "math_tool_function":
                        import json
                        args = json.loads(tool_call.function.arguments)
                        output = GameAgent.math_tool_function(args.get("expression", ""))
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                self.project_client.agents.runs.submit_tool_outputs(thread_id=self.thread.id, run_id=run.id, tool_outputs=tool_outputs)
        
        print(f"Run completed with status: {run.status}")
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Display run steps and tool calls
        run_steps = self.project_client.agents.run_steps.list(thread_id=self.thread.id, run_id=run.id)

        # Loop through each step
        for step in run_steps:
            print(f"Step {step['id']} status: {step['status']}")

            # Check if there are tool calls in the step details
            step_details = step.get("step_details", {})
            tool_calls = step_details.get("tool_calls", [])

            if tool_calls:
                print("  MCP Tool calls:")
                for call in tool_calls:
                    print(f"    Tool Call ID: {call.get('id')}")
                    print(f"    Type: {call.get('type')}")

            if isinstance(step_details, RunStepActivityDetails):
                for activity in step_details.activities:
                    for function_name, function_definition in activity.tools.items():
                        print(
                            f'  The function {function_name} with description "{function_definition.description}" will be called.:'
                        )
                        if len(function_definition.parameters) > 0:
                            print("  Function parameters:")
                            for argument, func_argument in function_definition.parameters.properties.items():
                                print(f"      {argument}")
                                print(f"      Type: {func_argument.type}")
                                print(f"      Description: {func_argument.description}")
                        else:
                            print("This function has no parameters")

            print()  # add an extra newline between steps

            
        messages = self.project_client.agents.messages.list(thread_id=self.thread.id)
        
        for message in messages:
            print(f"{message.role}: {message.content}")
            if message.role == "assistant":
                return message.content[0].text.value
        
        return "No response"
    
    
    def answer_question(self, question):
        """Generate an answer to the question using Azure AI Foundry Agent service"""
        if not self.agent:
            self._setup_agent()
        return self._call_azure_ai_agent(question)

    
    @staticmethod
    def math_tool_function(expression: str) -> str:
        """
        Calculate mathematical expressions.

        :param expression: The mathematical expression to calculate.
        :return: Result of the calculation as a string.
        """
        try:
            print('math_tool_function')
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"
        
    def _setup_tools(self):
        """Setup tool functions for the agent"""
        tools = []
        
        user_functions = {GameAgent.math_tool_function}
        function_tool = FunctionTool(functions=user_functions)
        tools.extend(function_tool.definitions)
        
        file_search_tool = self.setup_file_search_tool()
        tools.extend(file_search_tool.definitions)

        # Initialize agent MCP tool
        # mcp_server_url = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
        mcp_server_url = os.environ.get("MCP_SERVER_URL", "https://gitmcp.io/Azure/azure-rest-api-specs")
        mcp_server_label = os.environ.get("MCP_SERVER_LABEL", "weather")

        self.mcp_tool = McpTool(
            server_label=mcp_server_label,
            server_url=mcp_server_url,
            allowed_tools=[],  # Optional: specify allowed tools
        )
        
        # search_api_code = "search_azure_rest_api_code"
        # mcp_tool.allow_tool(search_api_code)
        # print(self.mcp_tool.definitions)
        tools.extend(self.mcp_tool.definitions)

        return tools


if __name__ == "__main__":

    test_questions = [
        "daniel must be the winner of the game?"
    ]
    
    with GameAgent() as agent:
        for question in test_questions:
            answer = agent.answer_question(question)
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()
    
    print("Game Agent: Test complete")