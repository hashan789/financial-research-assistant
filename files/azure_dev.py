import os
import json
import openai
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from io import StringIO

# Set your Azure OpenAI API key and endpoint
azure_endpoint = "https://imtopenais0.openai.azure.com/"
azure_deployment_name = "Turbo16IMT"

openai.api_type = "azure"
openai.api_base = azure_endpoint
openai.api_version = "2024-05-01-preview"  # or the version you are using

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")   

client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2024-05-01-preview"
)

# Azure Blob Storage configuration
account_url = "https://openaiislandmindtecace9.blob.core.windows.net/"
container_name = "openaiislandmindwebtest"

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
container_client = blob_service_client.get_container_client(container_name)


def read_blob_content(blob_name):
    """Read the content of a blob directly from Azure Blob Storage."""
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    # Download blob content as a stream
    if blob_client.exists():
            blob_content = blob_client.download_blob().readall().decode("utf-8")       
    else:
            print(f"Blob '{blob_name}' does not exist.")
    
    return blob_content

def analyze_blob_content(blob_name, query):
    """Analyze blob content from Azure Blob Storage using LangChain and OpenAI without downloading."""
    # Step 1: Read the blob content directly from Azure Blob Storage
    blob_content = read_blob_content(blob_name)
    
    # Step 2: Use LangChain to process the content
    # Since LangChain uses loaders, we can simulate loading by reading the text from memory
    loader = TextLoader(StringIO(blob_content))
    documents = loader.load()
    
    # Step 3: Use LangChain's Question-Answering chain to analyze the report
    llm = OpenAI(model="text-davinci-003")  # Replace with your model if needed
    chain = load_qa_chain(llm)
    
    # Step 4: Perform analysis based on the query
    result = chain.run(input_documents=documents, question=query)
    
    return result

# Available Functions for LangChain + OpenAI
functions = [
    {
        "name": "read_blob_content",
        "description": "Read the content of a blob directly from Azure Blob Storage.",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "The name of the blob file in Azure Blob Storage."
                }
            },
            "required": ["blob_name"]
        }
    },
    {
        "name": "analyze_blob_content",
        "description": "Analyze the content of a report stored as a blob in Azure Blob Storage based on a specified query using LangChain",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "The name of the blob file in Azure Blob Storage."
                },
                "query": {
                    "type": "string",
                    "description": "The type of analysis to perform on the content (e.g., summary, specific question)."
                }
            },
            "required": ["blob_name", "query"]
        }
    }
]

available_functions = {
    'read_blob_content': read_blob_content, 
    'analyze_blob_content': analyze_blob_content
}

def get_response(user_input):
    messages = [{'role':'user','content': user_input}]
    response = client.chat.completions.create(
        model=azure_deployment_name,
        messages=messages,
        functions=functions,
        function_call='auto',
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )

    response_dict = response.to_dict() 
    response_message = response_dict['choices'][0]['message']

    if response_message.get('function_call'):
        function_name = response_message['function_call']['name']
        function_args = json.loads(response_message['function_call']['arguments'])
        function_result = available_functions[function_name](**function_args)
        messages.append({'role': 'function', 'name': function_name, 'content': function_result})
        
        second_response = client.chat.completions.create(
            model=azure_deployment_name,
            messages=messages,
            functions=functions,
            function_call='auto'
        )
        print(second_response['choices'][0]['message']['content'])
        print(function_result)
    else:
        print(response_message['content'])

# Example usage
user_input = input("Enter your question: ")
get_response(user_input)
