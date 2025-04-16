"""
Smart Importer Agent implementation using Azure AI Projects SDK for intelligent file importing and CSV generation.
"""
from typing import Dict, Any, List
import os
import logging
from pathlib import Path
import pandas as pd
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from ...base import BaseAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartImporterAgent(BaseAgent):
    def __init__(self, project_connection_string: str):
        """Initialize the Smart Importer Agent.
        
        Args:
            project_connection_string: Azure AI Project connection string
        """
        self.project_connection_string = project_connection_string
        self.project_client = None
        self.agent = None
        
        self.system_message = """You are a smart importing agent that processes various file formats and generates clean CSV files.
You can handle multiple input formats including Excel files, text files, JSON, and XML.
You intelligently:
- Detect and infer data types and structures
- Identify and standardize date formats
- Recognize and handle different numerical representations
- Clean and normalize data
- Handle missing or malformed values
- Identify and merge related columns
- Suggest optimal column names and data structures
- Detect and handle outliers
- Identify potential data quality issues

Here are examples of the transformations you should suggest:

1. Date Standardization Example:
   Input columns: ["purchase_date", "shipping_date", "return_date"]
   Input values: ["01/23/24", "2024.01.15", "Jan 20 2024"]
   Suggested transformation: Standardize to ISO format "YYYY-MM-DD"
   Output values: ["2024-01-23", "2024-01-15", "2024-01-20"]

2. Name Column Merging Example:
   Input columns: ["first_name", "middle_initial", "last_name"]
   Input values: ["John", "M", "Smith"]
   Suggested transformation: Merge into "full_name" with proper spacing
   Output: "John M Smith"

3. Phone Number Normalization Example:
   Input values: ["(555) 123-4567", "555.123.4567", "5551234567"]
   Suggested transformation: Standardize format to "(XXX) XXX-XXXX"
   Output: All numbers in "(555) 123-4567" format

4. Address Field Splitting Example:
   Input: "123 Main St, Apt 4B, New York, NY 10001"
   Suggested transformation: Split into components
   Output columns: ["street_number", "street_name", "unit", "city", "state", "zip"]
   Output values: ["123", "Main St", "Apt 4B", "New York", "NY", "10001"]

5. Currency Standardization Example:
   Input values: ["$1,234.56", "1234.56", "USD 1,234.56"]
   Suggested transformation: Standardize to decimal number
   Output: 1234.56 (as float)

6. Missing Value Handling Example:
   Input values: ["", "N/A", "null", "unknown", None]
   Suggested transformations:
   - For numeric columns: Replace with statistical measure (mean/median)
   - For categorical columns: Replace with mode or "Unknown"
   - For dates: Replace with previous/next valid date or null

7. Column Name Standardization Example:
   Input names: ["First Name", "LAST_NAME", "email_address", "PHONE_NUM"]
   Suggested transformation: Convert to snake_case
   Output: ["first_name", "last_name", "email_address", "phone_number"]

8. Data Type Inference Example:
   Input column: "age"
   Input values: ["25", "thirty", "35", "40"]
   Suggested transformations:
   - Convert text numbers to integers
   - Flag invalid values
   - Suggest data type as integer

9. Outlier Detection Example:
   Input column: "transaction_amount"
   Input values: [10.50, 25.00, 15.75, 1000000.00, 20.25]
   Suggested actions:
   - Flag unusual values
   - Suggest validation rules
   - Provide statistical summary

10. Related Column Detection Example:
    Input columns: ["latitude", "longitude", "geo_coordinates"]
    Suggested transformation:
    - Merge lat/long into geo_coordinates if empty
    - Split geo_coordinates into lat/long if those are empty
    - Validate coordinate pairs

Your goal is to convert input data into well-structured, clean CSV files while preserving data integrity and meaning.
When suggesting transformations, always consider:
- The semantic meaning of the data
- The relationships between columns
- The intended use of the data
- Data validation rules
- Best practices for data storage and analysis

Provide your suggestions in a clear, structured format that can be programmatically processed."""

    async def initialize(self) -> None:
        """Initialize the agent with necessary configurations."""
        try:
            # Initialize Azure credentials
            credential = DefaultAzureCredential()
            logger.info("Initialized Azure credentials")
            
            # Initialize Azure AI Project client
            self.project_client = AIProjectClient.from_connection_string(
                conn_str=self.project_connection_string,
                credential=credential,
            )
            logger.info("Initialized Azure AI Project client")
            
            # Create and initialize the agent
            await self.create()
            logger.info("Successfully created and initialized the agent")
            
        except Exception as e:
            logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to initialize agent: {str(e)}")

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a message using the agent."""
        return await self.process_request({"message": message})

    async def create(self) -> None:
        """Create and initialize the agent with necessary tools."""
        # Create an instance of the CodeInterpreterTool
        code_interpreter = CodeInterpreterTool()
        
        # Create the agent
        self.agent = self.project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="SmartImporterAgent",
            instructions=self.system_message,
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )

    async def process_request(self, request: Dict[str, Any], thread_id: str | None = None) -> Dict[str, Any]:
        """Process an import request."""
        try:
            # If a thread ID is provided, use it, otherwise create a new thread
            if thread_id:
                logger.info(f"Using existing thread ID to process request: {thread_id}")
                thread = self.project_client.agents.get_thread(thread_id=thread_id)
            else:
                logger.info("Creating new thread to process request")
                thread = self.project_client.agents.create_thread()
            
            # Add user message to thread
            self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=str(request)
            )
            
            # Run the agent
            run = self.project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=self.agent.id
            )
            
            if run.status == "failed":
                return {
                    "error": run.last_error,
                    "status": run.status.value
                }
            
            # Get the agent's response
            messages = self.project_client.agents.list_messages(
                thread_id=thread.id,
                order="asc"
            )

            # Get the last message from the sender
            last_msg = messages.get_last_text_message_by_role("assistant")

            if last_msg is None:
                return {
                    "error": "No response from agent",
                    "status": run.status.value
                }
            
            # Generate an image file for the bar chart
            for image_content in messages.image_contents:
                logger.info(f"Image File ID: {image_content.image_file.file_id}")
                file_name = f"{image_content.image_file.file_id}_image_file.png"
                self.project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
                logger.info(f"Saved image file to: {Path.cwd() / file_name}")

            # Print the file path(s) from the messages
            for file_path_annotation in messages.file_path_annotations:
                logger.info(f"File Paths: Type: {file_path_annotation.type}, Text: {file_path_annotation.text}, File ID: {file_path_annotation.file_path.file_id}, Start Index: {file_path_annotation.start_index}, End Index: {file_path_annotation.end_index}")
                self.project_client.agents.save_file(file_id=file_path_annotation.file_path.file_id, file_name=Path(file_path_annotation.text).name)

            # Return the last message from the agent
            return {
                "response": last_msg.text.value,
                "status": run.status.value,
                "agent_id": self.agent.id,
                "thread_id": thread.id,
                "run_id": run.id
            }

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    async def evaluate(self) -> Dict[str, Any]:
        """Evaluate agent performance."""
        return {
            "metrics": {
                "file_processing": "Measures successful file imports",
                "data_quality": "Tracks data cleaning effectiveness",
                "format_handling": "Analyzes support for different file formats"
            }
        }

    async def process_file(self, file_path: str, original_filename: str, thread_id: str | None = None) -> Dict[str, Any]:
        """Process an uploaded file and return the analysis results."""
        try:
            logger.info(f"Processing file: {original_filename}")
            
            # Read the file based on its extension
            file_ext = Path(original_filename).suffix.lower()
            
            if file_ext in ['.csv', '.txt']:
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # If a thread ID is provided, use it, otherwise create a new thread
            if thread_id:
                logger.info(f"Using existing thread ID to process file: {thread_id}")
                thread = self.project_client.agents.get_thread(thread_id=thread_id)
            else:
                logger.info("Creating new thread to process file")
                thread = self.project_client.agents.create_thread()
            
            # Create a message with file analysis request
            analysis_request = f"""Please analyze this data and suggest improvements:
            
            File: {original_filename}
            Columns: {', '.join(df.columns)}
            Data Types: {df.dtypes.to_dict()}
            Sample Data: {df.head().to_dict()}
            
            Please provide:
            1. Data quality analysis
            2. Suggested transformations
            3. Potential issues and how to fix them
            4. Optimal column structure
            """
            
            self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=analysis_request
            )
            
            # Run the agent
            run = self.project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=self.agent.id
            )
            
            if run.status == "failed":
                return {
                    "error": run.last_error,
                    "status": run.status.value
                }
            
            # Get the agent's response
            messages = self.project_client.agents.list_messages(
                thread_id=thread.id,
                order="asc"
            )
            
            # Get the last message from the agent
            last_msg = messages.get_last_text_message_by_role("assistant")
            
            if last_msg is None:
                return {
                    "error": "No response from agent",
                    "status": run.status.value
                }
            
            # Save any generated visualizations
            visualization_paths = []
            for image_content in messages.image_contents:
                file_name = f"{image_content.image_file.file_id}_analysis.png"
                self.project_client.agents.save_file(
                    file_id=image_content.image_file.file_id,
                    file_name=file_name
                )
                visualization_paths.append(str(Path.cwd() / file_name))
            
            return {
                "response": last_msg.text.value,
                "filename": original_filename,
                "columns": list(df.columns),
                "row_count": len(df),
                "analysis": last_msg.text.value,
                "visualizations": visualization_paths,
                "status": run.status.value,
                "agent_id": self.agent.id,
                "thread_id": thread.id
            }
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed"
            }
