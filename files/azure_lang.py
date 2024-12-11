import csv
import io
import os
import json
from urllib.parse import urljoin
from PyPDF2 import PdfReader
import PyPDF2
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import time
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient
import azure.core.exceptions
from langchain_community.document_loaders import TextLoader , UnstructuredFileLoader
from langchain_unstructured import UnstructuredLoader
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureOpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
import logging

import requests

reports_url = "https://cse.lk/pages/financial-reports/financial-reports.component.html"

# Set your Azure OpenAI API key and endpoint
azure_endpoint = "https://imtopenais0.openai.azure.com/"
azure_deployment_name = "Turbo16IMT"
azure_api_key = "e2ac277a12e34cb69b7e8aa52a610ca1"
azure_api_version = "2024-05-01-preview"  # or the version you are using

openai.api_type = "azure"
openai.api_key = "e2ac277a12e34cb69b7e8aa52a610ca1"
openai.api_base = azure_endpoint
openai.api_version = "2024-05-01-preview"  # or the version you are using

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
      
client = openai.AzureOpenAI(
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

def document_to_dict(document):
    """Convert a Document object to a dictionary that is JSON serializable."""
    return {
        "text": document.page_content,
        "metadata": document.metadata
    }


def upload_to_blob_storage(file_content, container_name, blob_name):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=openaiislandmindtecace9;AccountKey=RYnrLvvl//cCvsSs7fOx4CN7PbVvRkk9jHVhyr1MKlOM05c7TLgiG3u1A7vyqhSrFIUp3VsLlFOS+ASturRNMA==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(file_content, overwrite=True)


def download_file(url, file_name):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  #Exception for HTTP errors
        with open(file_name, 'wb') as file:
            file.write(response.content)
            print(f"File downloaded as {file_name}")
        if response.status_code == 200:
            return response.content
    except requests.exceptions.RequestException as e:
        logging.error("Error downloading file: %s", e)  
        return None
    

def download_specific_annual_reports_to_blob(base_url,blob_name):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=50)
            page = browser.new_page()
            page.goto(base_url)
            time.sleep(200)

            link_locators = page.locator("div.financial-reports-block").locator("ul").locator("li").all()
            # .get_by_role("table").get_by_role("tbody").get_by_role("tr").all()

            for lc in link_locators:
                report_name = lc.locator("div.rules-block").locator("div.col-lg-8").locator("div.rule").inner_text()
                if blob_name.split(".")[0] in report_name.lower():
                    report_url = lc.locator("div.rules-block").locator("div.col-lg-3").locator("a").get_attribute("href")
                    print(report_url)
                    # Extract the original file name from the URL
                    file_name = os.path.basename(report_url)

                    download_file_name = "download_file.pdf"

                    new_file_name = str(blob_name)

                    # Download the PDF file into memory
                    file_content = download_file(report_url, download_file_name)

                    os.rename(download_file_name,new_file_name)

                    if file_content:
                        # Upload the downloaded file content to Azure Blob Storage
                        upload_to_blob_storage(file_content, container_name, new_file_name)

                        logging.info(f"Report uploaded to Azure Blob Storage: {new_file_name}")
                    else:
                        logging.warning(f"Failed to download the report.")

        return "Annual reports uploaded to Azure Blob Storage."

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"


def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_pdf(file_path):
    with io.BytesIO(file_path) as file_like:
        pdf_reader = PyPDF2.PdfFileReader(file_like)

        #Extract text from each page
        text_content = ""
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text_content += page.extract_text()

    return text_content

def download_blob(blob_name):
    """Download a file from Azure Blob Storage."""
    # container_client = blob_service_client.get_container_client(container_name)
    # blob_client = container_client.get_blob_client(blob_name)
    
    # download_file_path = f"./download_files/{blob_name}"
    # with open(download_file_path, "wb") as download_file:
    #     download_file.write(blob_client.download_blob().readall())
    
    # return download_file_path

    try:
        # Create the BlobServiceClient object which will be used to interact with the blob service.
        blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Download blob
        blob_client = container_client.get_blob_client(blob_name)

        current_folder = os.getcwd()

        download_file_path = f"{current_folder}\download_files\{blob_name}"

        if blob_client.exists():
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall()) 
                print(f"Blob '{blob_name}' downloaded successfully.")          
        else:
            if blob_name.lower().endswith(".pdf"):
                # print(f"Blob '{blob_name}' doesn't exists.")
                result = download_specific_annual_reports_to_blob(reports_url, blob_name)
                download_file_path = download_blob(blob_name)

        return download_file_path 
    
    except azure.core.exceptions.ResourceNotFoundError:
        print(f"Blob '{blob_name}' not found in container '{container_name}'.")
    except azure.core.exceptions.HttpResponseError as e:
        print(f"Error occurred: {e.message}")


def load_and_analyze_report(blob_name, query):
    """Load and analyze report using LangChain and OpenAI."""
    # Step 1: Download the report from Azure Blob Storage
    # report_path = download_blob(blob_name)
    
    # # Step 2: Use LangChain to load the document
    # loader = TextLoader(report_path)
    # documents = loader.load()

    try:
        print(blob_name)
        report_path = download_blob(blob_name)
        # loader = TextLoader(report_path)
        # documents = loader.load()

        # Assume the report is a PDF file
        loader = PyPDFLoader(report_path)  # Replace with the path to your PDF file
        document = loader.load()
        # document = extract_text_from_pdf(report_path)
        print("File loaded successfully.")
    except Exception as e:
        print(f"Error loading the file: {e}")

    
    # # Step 3: Use LangChain's Question-Answering chain to analyze the report
    # llm = OpenAI(openai_api_key="e2ac277a12e34cb69b7e8aa52a610ca1",model="text-davinci-003")  # You can replace with your model if needed
    # # llm = ChatOpenAI()
    # chain = load_qa_chain(llm)
    
    # # Step 4: Perform analysis based on the query
    # result = chain.run(input_documents=documents, question=query)
    # print(document)
    documents = [Document(page_content=str(document))]
    # print(documents)

    # # Step 3: Split the text into manageable chunks (if the document is large)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    split_documents = text_splitter.split_documents(documents)

    embeddings = AzureOpenAIEmbeddings(api_key=openai.api_key, azure_endpoint=azure_endpoint)
    doc_search = Chroma.from_documents(split_documents,embeddings)

    # # # Step 4: Initialize OpenAI language model
    llm = AzureOpenAI(model_name=azure_deployment_name,api_key=azure_api_key, azure_endpoint=azure_endpoint, api_version=azure_api_version)

    # # # Step 5: Set up a prompt template for asking questions
    # prompt_template = PromptTemplate.from_template("Based on the report, answer the following question: {query}")

    # # # Step 6: Create a question-answering chain
    # # qa_chain = load_qa_chain(llm=llm, chain_type="map_reduce")  # You can use "stuff" for smaller docs or "map_reduce" for large ones
    chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=doc_search.as_retriever(search_kwargs={'k': 1}))

    # # # Step 7: Ask a question
    result = chain.invoke(query)

    # Step 3: Ask a question about the report
    # report_text = load_pdf(report_path)

    # Step 4: Send the report text and the question to Azure OpenAI
    prompt = f"Report: {document}\n\nQuestion: {query}\nAnswer:"

    # # Send the prompt to Azure OpenAI and get the response
    response = client.chat.completions.create(
        model=azure_deployment_name,
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    
    return result

# Available Functions for LangChain + OpenAI
functions = [
    {
        "name": "download_blob",
        "description": "Download a blob (file) from Azure Blob Storage.",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "The name of the blob file with company name in Azure Blob Storage (e.g., keells.pdf, cargills.pdf)."
                }
            },
            "required": ["blob_name"]
        }
    },
    {
        "name": "load_and_analyze_report",
        "description": "Analyze a report uploaded to Azure Blob Storage based on the specified query using LangChain",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "The name of the blob file with company name in Azure Blob Storage (e.g., keells.pdf, cargills.pdf)."
                },
                "query": {
                    "type": "string",
                    "description": "The type of analysis to perform on the report (e.g., summary, specific question)."
                }
            },
            "required": ["blob_name", "query"]
        }
    }
]

available_functions = {
    'download_blob': download_blob,
    'load_and_analyze_report': load_and_analyze_report
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
        second_response_dict = second_response.to_dict() 
        print(second_response_dict['choices'][0]['message']['content'])
        print(function_result)
    else:
        print(response)

# Example usage
user_input = input("Enter your question: ")
get_response(user_input)
