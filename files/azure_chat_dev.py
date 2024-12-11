# what is the facebook company?

import json
import os
from openai import AzureOpenAI
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

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

def download_report_from_blob(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    download_stream = blob_client.download_blob()
    report_content = download_stream.readall()
    return report_content.decode('utf-8')

def analyze_report(report_content, query):
    # Assuming the report is a CSV or text file, you can process it accordingly
    # Here's an example of processing a CSV file
    df = pd.read_csv(pd.compat.StringIO(report_content))
    
    # Implement your analysis logic here based on the query
    if query == "summary":
        return df.describe().to_string()
    elif query == "specific_column":
        return df['YourColumnName'].value_counts().to_string()
    else:
        return "Query not recognized"


def get_stock_price(ticker):
    return str(yf.Ticker(ticker).history(period='1y').iloc[-1].Close)

def calculate_SMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y')
    return str(data.rolling(window=window).mean().iloc[-1])

def calculate_EMA(ticker, window):
    data = yf.Ticker(ticker).history(period='1y')
    return str(data.ewm(span=window, adjust=False).mean().iloc[-1])

def calculate_RSI(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    delta = data.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=14-1, adjust=False).mean()
    ema_down = down.ewm(com=14-1, adjust=False).mean()
    rs = ema_up / ema_down
    return str(100 - 100 / (1 + rs)).iloc[-1]

def calculate_MACD(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    ema_12 = data.ewm(span=12, adjust=False).mean()
    ema_26 = data.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - signal
    return f'{macd.iloc[-1]}, {signal.iloc[-1]}, {macd_histogram.iloc[-1]}'

def plot_stock_price(ticker):
    data = yf.Ticker(ticker).history(period='1y')
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Close')
    plt.title(f'{ticker} Stock Price over Last Year')
    plt.xlabel('Date')
    plt.ylabel('Stock Price ($)')
    plt.grid(True)
    plt.savefig('Stock.png')
    plt.show()

functions = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a given ticker symbol of a company.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol of the company (for example AAPL for Apple)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_SMA",
        "description": "Calculate the simple moving average (SMA) for a given ticker symbol of a company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol of the company (for example AAPL for Apple)."
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the SMA."
                }
            },
            "required": ["ticker", "window"]
        }
    },
    {
        "name": "calculate_EMA",
        "description": "Calculate the exponential moving average (EMA) for a given ticker symbol of a company and for a window",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "  The stock ticker symbol of the company (for example AAPL for Apple)."
                },
                "window": {
                    "type": "integer",
                    "description": "The timeframe to consider when calculating the EMA."
                }
            },
            "required": ["ticker", "window"]
        }
    },
    {
        "name": "calculate_RSI",
        "description": "Calculate the relative strength index (RSI) for a given ticker symbol of a company and for a window",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "  The stock ticker symbol of the company (for example AAPL for Apple)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_MACD",
        "description": "Calculate the Moving Average Convergence Divergence (MACD) for a given ticker symbol of a company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol of the company (for example AAPL for Apple)."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "plot_stock_price",
        "description": "Plot the stock price for the last year for a given ticker symbol of a company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker symbol of the company (for example AAPL for Apple)."
                }
            }
        }
    },
    {
        "name": "analyze_report",
        "description": "Analyze a report stored in Azure Blob Storage based on the user's query",
        "parameters": {
            "type": "object",
            "properties": {
                "blob_name": {
                    "type": "string",
                    "description": "The name of the blob (report) to be analyzed."
                },
                "query": {
                    "type": "string",
                    "description": "The query to analyze the report with."
                }
            },
            "required": ["blob_name", "query"]
        }
    }
]

available_functions = {
    'get_stock_price': get_stock_price,
    'calculate_SMA': calculate_SMA,
    'calculate_EMA': calculate_EMA,
    'calculate_RSI': calculate_RSI,
    'calculate_MACD': calculate_MACD,
    'plot_stock_price': plot_stock_price,
    'analyze_report': lambda blob_name, query: analyze_report(download_report_from_blob(blob_name), query)
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
        if function_name in ['get_stock_price', 'calculate_RSI', 'calculate_MACD', 'plot_stock_price']:
            args_dict = {'ticker': function_args.get('ticker')}
        elif function_name in ['calculate_SMA', 'calculate_EMA']:
            args_dict = {'ticker': function_args.get('ticker'), 'window': function_args.get('window')}

        function_result = available_functions[function_name](**args_dict)
        messages.append({'role': 'function', 'name': function_name, 'content': function_result})

        if function_name == 'plot_stock_price':
            plt.show()
        else:
            second_response = client.chat.completions.create(
                model=azure_deployment_name,
                messages=messages,
                functions=functions,
                function_call='auto'
            )
            second_response_dict = second_response.to_dict() 
            return second_response_dict['choices'][0]['message']['content']
            print(function_result)
    else:
        return response_message['content']
