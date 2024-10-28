from control_phone import  take_screenshot, dump_ui, input_text
from dotenv import load_dotenv
import base64
import concurrent.futures
import json
import os 
import re
import requests

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def requests_openai(prompt):
    load_dotenv()
    api_key = os.getenv("api_key")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }  
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=prompt)
    print(response.json())
    data = response.json()["choices"][0]["message"]["content"] 
    pattern = r'^(?:```json|```csv|```)\s*(.*?)\s*```$'
    data = re.sub(pattern, r'\1', data, flags=re.DOTALL).strip()
    return data 
