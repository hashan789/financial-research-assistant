from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
from typing_extensions import Concatenate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default") 

os.environ["OPENAI_API_TYPE"] = "azure"  
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://finastmodel.openai.azure.com/"
# os.environ["AZURE_OPENAI_BASE"] = "https://finastmodel.openai.azure.com/openai/deployments/text-embedding/embeddings?api-version=2023-05-15"
os.environ["AZURE_OPENAI_API_KEY"] = "f7aac3553ac4423eacfcae0a167d3e24" 
os.environ["OPENAI_API_VERSION"] = "2023-03-15-preview" 

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

current_folder = os.getcwd()
report_path = os.path.join(current_folder, "download_files", "agstar.pdf")

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

query = "who is chairman of agstar?"

docs = document_search.similarity_search(query)

# print(docs)

input_data = {
    'input_documents': docs,
    'question': query,
}

result = chain.invoke(input=input_data)

print(result['output_text'])


