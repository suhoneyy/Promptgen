from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from transformers import pipeline

app = Flask(__name__)
CORS(app)  


gpt2_pipeline = pipeline('text-generation', model='gpt2')

@app.route('/execute-sp/', methods=['POST'])
def execute_sp():
    data = request.get_json()
    
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400
    
    prompt = """You are a prompt generating agent tasked to help users with writing a prompt that will help them achieve the expected result. The current prompt is -' {} ' which is generating the result - '{}'. The user wants to obtain the following result - ' {} '. Rewrite the current prompt to get the desired values.""".format(data['prompt'], data['curr_result'], data['exp_result'])
    

    response = gpt2_pipeline(prompt, max_length=100, num_return_sequences=1)
    

    generated_prompt = response[0]['generated_text']
    
    return jsonify({"prompt": generated_prompt})

if __name__ == '__main__':
    app.run(debug=True)
