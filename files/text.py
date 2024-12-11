import csv
import os
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import openai
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient
import azure.core.exceptions
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import logging

import requests

reports_url = "https://cse.lk/pages/financial-reports/financial-reports.component.html"

blob_name = "HCV FOODS PLC.pdf"

def download_specific_annual_reports_to_blob(base_url,blob_name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.62 Safari/537.36',  
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9,application/pdf'
        }

        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  #Exception for HTTP errors
        if response.status_code != 200:
            logging.warning(f"Failed to fetch the web page at {base_url}.")
            return "Failed to fetch the web page."

        soup = BeautifulSoup(response.content, 'html.parser')
        financial_reports_block = soup.find('div',class_='financial-reports-block').find('ul')
        # financial_reports_lists = financial_reports_block.find_all("li")

        # for year in years_to_download:
        # for financial_reports_list in financial_reports_lists:
        #         report_li = financial_reports_list.find('div', class_="rules-block").find('div', class_="row")
        #         report_li_link = report_li.find('div', class_="col-lg-8")
        #         if blob_name in report_li_link.text:
        #             report_url = report_li.find('div', class_="col-lg-3").find('div', class_="rule-block-inner").find('div', class_="rule-download").find('a').get("href")
                    
        #             print(report_url)

        #         else:
        #             logging.warning(f"No valid PDF reports found.")

        # return "Annual reports uploaded to Azure Blob Storage."
        print(financial_reports_block)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

def file_path():
    # Get the current working directory
    current_folder = os.getcwd()

    print(current_folder)

file_path()

# download_specific_annual_reports_to_blob(reports_url, blob_name)
