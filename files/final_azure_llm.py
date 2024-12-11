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

import requests

reports_url = "https://cse.lk/pages/financial-reports/financial-reports.component.html"

os.environ["OPENAI_API_TYPE"] = "azure"  
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://finastmodel.openai.azure.com/"
# os.environ["AZURE_OPENAI_BASE"] = "https://finastmodel.openai.azure.com/openai/deployments/text-embedding/embeddings?api-version=2023-05-15"
os.environ["AZURE_OPENAI_API_KEY"] = "f7aac3553ac4423eacfcae0a167d3e24" 
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview" 

azure_endpoint = "https://finastmodel.openai.azure.com/"
azure_deployment_name = "gpt-35-turbo"

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
      
client = openai.AzureOpenAI(
    azure_endpoint=azure_endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2023-03-15-preview"
)

# Azure Blob Storage configuration
account_url = "https://openaiislandmindtecace9.blob.core.windows.net/"
container_name = "openaiislandmindwebtest"

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
container_client = blob_service_client.get_container_client(container_name)


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


def download_blob(blob_name):
    """Download a file from Azure Blob Storage."""
    try:
        blob_service_client = BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        current_folder = os.getcwd()
        download_file_path = os.path.join(current_folder, "download_files", blob_name)

        if blob_client.exists():
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            print(f"Blob '{blob_name}' downloaded successfully.")
            return download_file_path
        else:
            print(f"Blob '{blob_name}' not found.")
            if blob_name.lower().endswith(".pdf"):
                # Download specific annual reports if needed
                result = download_specific_annual_reports_to_blob(reports_url, blob_name)
                if result.startswith("Annual reports uploaded"):
                    return download_blob(blob_name)  # Retry download after attempting to upload
            return None
    except azure.core.exceptions.ResourceNotFoundError:
        print(f"Blob '{blob_name}' not found in container '{container_name}'.")
    except azure.core.exceptions.HttpResponseError as e:
        print(f"Error occurred: {e.message}")


def load_and_analyze_report(blob_name, query):
    """Load and analyze report using LangChain and OpenAI."""
    try:
        report_path = download_blob(blob_name)

        pdfreader = PdfReader(report_path)

        raw_text = ""

        for i , page in enumerate(pdfreader.pages):
            content = page.extract_text()
            if content:
                raw_text += content

        # print(raw_text)

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        texts = text_splitter.split_text(raw_text)

        # print(len(texts))

        embeddings = AzureOpenAIEmbeddings(deployment="text-embedding", openai_api_version="2023-05-15")

        # print(embeddings)

        document_search = FAISS.from_texts(texts,embeddings)

        # print(document_search)

        llm = AzureOpenAI(deployment_name="gpt-35-turbo")

        # print(llm)

        chain = load_qa_chain(llm=llm, chain_type="stuff")


        docs = document_search.similarity_search(query)

        # print(docs)

        prompt = f"Report: {docs}\n\nQuestion: {query}\nAnswer:"

        # # Send the prompt to Azure OpenAI and get the response
        response = client.completions.create(
            model=azure_deployment_name,
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
    
    

def get_response(user_input):
    content = f"name for a PDF file based on the unrecognized word of the question '{user_input}' (e.g. Question: 'who is chairman of facebook?'  Answer: 'facebook.pdf')"

    messages = [{'role':'user','content': content}]

    # # Send the prompt to Azure OpenAI and get the response
    response = client.chat.completions.create(
        model=azure_deployment_name,
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

    blob_name = response_message['content']

    result = load_and_analyze_report(blob_name,user_input)

    print(result)

    return result
