import subprocess
from subprocess import CompletedProcess, Popen
import time
from typing import List
import ollama
import requests
import httpx
from ollama import ChatResponse, GenerateResponse, ListResponse, chat, generate, list, Client


BASE_URL = "http://localhost:11434"
LLM_SERVER = "ollama-serve"
SYSTEM_PROMPT = "You are a helpful assistant."
MODELS_LIST = ['wizard-math:latest', 'codellama:13b-code-q8_0', 'llama3.1:latest', 'qwen2.5-coder:latest']

#   Useful parsing
def get_response_text(response: dict) -> str:
    return response["message"]["content"]

def get_models_names(models)-> List[str]:
    return [model.model for model in models.models]


#  Ollama interactions

def get_ollama_client()-> Client:
    client = Client(host="http://localhost:11434")
    return client

def ollama_llms_available(client: Client)->ListResponse:
    response = client.list()
    return response


def check_ollama_server()-> bool:
    try:
        list()
        return True
    except:
        return False
    
def run_ollama()-> Popen|None:
    if not check_ollama_server():
        p = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        return p

def ollama_generate(client: Client, prompt: str, model: str)->GenerateResponse:

    response = client.generate(
        model=model,
        prompt=prompt
    )
    return response


def ollama_chat(client: Client, user_text: str, history=None) -> ChatResponse:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages += history

    messages.append({"role": "user", "content": user_text})

    response = client.chat(
        model="llama3.1:latest",
        messages=messages
    )

    return response

def download_model(client: Client, model_name: str):
    try:
        client.pull(model_name)
    except:
        print(f"Error downloading model {model_name}")
