from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from transformers import GPT2Tokenizer, GPT2Model, pipeline, set_seed # Replace with your LLM library
from azure_llm import get_response

app = Flask(__name__)
cors = CORS(app)

@app.route('/process',methods=['POST'])
@cross_origin()
def process_query():
  data = request.get_json()
  company = data['dataQuery']['company']
  query = data['dataQuery']['query']

  response = get_response(query, company)

  print(query,company)

  return jsonify({'response' : response})

if __name__ == '__main__':
  app.run(debug = True)  # Replace with your desired port
