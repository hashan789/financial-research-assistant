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
from langchain.llms import AzureOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from typing_extensions import Concatenate
import logging
import urllib.request
import requests
from dotenv import load_dotenv, dotenv_values

# loading variables from .env file
load_dotenv()

reports_url = os.getenv("REPORTS_URL")

open_api_type = os.getenv("OPENAI_API_TYPE")
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv
open_api_version_embeddings = os.getenv("OPENAI_API_VERSION_EMBEDDINGS")
open_api_version_llm = os.getenv("OPENAI_API_VERSION_LLM")
open_api_version_chat = os.getenv("OPENAI_API_VERSION_CHAT")
azure_deployment_name_embeddings = os.getenv("AZURE_DEPLOYMENT_NAME_EMBEDDINGS")
azure_deployment_name_llm = os.getenv("AZURE_DEPLOYMENT_NAME_LLM")
azure_deployment_name_chat = os.getenv("AZURE_DEPLOYMENT_NAME_CHAT")
account_url = os.getenv("ACCOUNT_URL")
container_name = os.getenv("CONTAINER_NAME")

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
      
client_llm = openai.AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    azure_ad_token_provider=token_provider,
    api_version=open_api_version_llm
)

client_chat = openai.AzureOpenAI(
    azure_endpoint=azure_openai_endpoint,
    azure_ad_token_provider=token_provider,
    api_version=open_api_version_chat
)


# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
container_client = blob_service_client.get_container_client(container_name)


def upload_to_blob_storage(file_content, container_name, blob_name):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=financeresearchstore;AccountKey=GLrMzbCR8Oxy6U9Lv6+GzgFohLw9LCpD76k4/jpC8LnxN96XmPGYGE1x74L3rrbSlydaii+NKrOu+AStgVbxBg==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    # Convert bytes to file-like object (using io.BytesIO)
    # file_like_object = Document(io.BytesIO(file_content))
    blob_client.upload_blob(file_content, overwrite=True)


def download_file(file_url):
    """Download a file from a given URL and return the content."""
    try:
        with urllib.request.urlopen(file_url) as response:
            return response.read()  # Return the file content
    except Exception as e:
        raise RuntimeError(f"Failed to download file from URL: {str(e)}")



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
                text_list = blob_name.split(".")[0]
                for text in text_list.split("_"):
                    if text in report_name.lower():
                        report_url = lc.locator("div.rules-block").locator("div.col-lg-3").locator("a").get_attribute("href")
                        print(report_url)
                        # Extract the original file name from the URL
                        file_name = os.path.basename(report_url)

                        new_file_name = str(blob_name)

                        blob = blob_name.split(".")[0]

                        download_file_name = f"{blob}_download_file.pdf"

                        # Download the PDF file into memory
                        file_content = download_file(report_url)

                        # os.rename(file_name,new_file_name)

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


def read_blob_from_azure(blob_name):
    """Read blob content directly into memory without downloading."""
    try:
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Download blob
        blob_client = container_client.get_blob_client(blob_name)
        if not blob_client.exists():
            download_specific_annual_reports_to_blob(reports_url,blob_name)
            read_blob_from_azure(blob_name)
            # raise FileNotFoundError(f"Blob '{blob_name}' not found in container '{container_name}'.")

        # Read blob content into memory
        blob_content = blob_client.download_blob().readall()
        return blob_content
    except Exception as e:
        raise RuntimeError(f"Failed to read blob: {str(e)}")


def extract_text_from_pdf(file_path):
    with io.BytesIO(file_path) as file_like:
        pdf_reader = PyPDF2.PdfReader(file_like)

        #Extract text from each page
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()

    return text_content


def load_and_analyze_report(blob_name, query):
    """Load and analyze report using LangChain and OpenAI."""
    try:
        report_path = read_blob_from_azure(blob_name)

        text_content = extract_text_from_pdf(report_path)

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        texts = text_splitter.split_text(text_content)

        # print(len(texts))

        embeddings = AzureOpenAIEmbeddings(deployment = azure_deployment_name_embeddings, openai_api_version = open_api_version_embeddings)

        # print(embeddings)

        document_search = FAISS.from_texts(texts,embeddings)

        # print(document_search)

        llm = AzureOpenAI(deployment_name = azure_deployment_name_llm, api_version = open_api_version_llm)

        # print(llm)

        chain = load_qa_chain(llm=llm, chain_type="stuff")


        docs = document_search.similarity_search(query)

        # print(docs)

        prompt = f"Report: {docs}\n\nQuestion: {query}\nAnswer:"

        # # Send the prompt to Azure OpenAI and get the response
        response = client_llm.completions.create(
            model=azure_deployment_name_llm,
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        response_dict = response.to_dict()
        result = response_dict['choices'][0]['text']

        # return result

        return result.split("Question")[0]
    
    except Exception as e:
        print(f"Error loading or analyzing the report: {e}")
        return "An error occurred during report analysis."
    
    

def get_response(user_input, company):
    content = f"name for a PDF file based on the unrecognized word of the question '{user_input}' (e.g. Question: 'who is chairman of facebook?'  Answer: 'facebook.pdf')"

    messages = [{'role':'user','content': content}]

    # # Send the prompt to Azure OpenAI and get the response
    response = client_chat.chat.completions.create(
        model=azure_deployment_name_chat,
        messages=messages,
        max_tokens=500,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    
    response_dict = response.to_dict() 
    response_message = response_dict['choices'][0]['message']

    blob_name = f'{company}.pdf'

    print(blob_name)

    result = load_and_analyze_report(blob_name,user_input)

    print(result)

    return result

# user_input = input("Enter a question: ")
# get_response(user_input)