import os
import json
import random
import numpy as np
import torch
from colorama import init, Fore, Style
from configparser import ConfigParser
from groq import Groq

from ..utils.api_utils import make_api_request, load_prompt_options, get_prompt_content
from ..utils.chat_utils import ChatHistoryManager

init()  # Initialize colorama

class GroqAPILLM:
    DEFAULT_PROMPT = "Use [system_message] and [user_input]"
    
    LLM_MODELS = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "llama-guard-3-8b",
        "llama3-groq-8b-8192-tool-use-preview",
        "llama3-groq-70b-8192-tool-use-preview",
        "mixtral-8x7b-32768",
        "gemma-7b-it",
        "gemma2-9b-it",
        "llama-3.2-1b-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-11b-text-preview",
        "llama-3.2-90b-text-preview",
    ]
    
    def __init__(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        groq_directory = os.path.join(current_directory, 'groq')
        config_path = os.path.join(groq_directory, 'GroqConfig.ini')
        self.config = ConfigParser()
        self.config.read(config_path)
        self.api_key = self.config.get('API', 'key')
        self.client = Groq(api_key=self.api_key)
        
        # Load prompt options
        prompt_files = [
            os.path.join(groq_directory, 'DefaultPrompts.json'),
            os.path.join(groq_directory, 'UserPrompts.json')
        ]
        self.prompt_options = load_prompt_options(prompt_files)
        
        # Initialize chat history manager
        self.chat_history_manager = ChatHistoryManager()
    
    @classmethod
    def INPUT_TYPES(cls):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            groq_directory = os.path.join(current_directory, 'groq')
            prompt_files = [
                os.path.join(groq_directory, 'DefaultPrompts.json'),
                os.path.join(groq_directory, 'UserPrompts.json')
            ]
            prompt_options = load_prompt_options(prompt_files)
        except Exception as e:
            print(Fore.RED + f"Failed to load prompt options: {e}" + Style.RESET_ALL)
            prompt_options = {}
    
        return {
            "required": {
                "model": (cls.LLM_MODELS, {"tooltip": "Select the Large Language Model (LLM) to use."}),
                "preset": ([cls.DEFAULT_PROMPT] + list(prompt_options.keys()), {"tooltip": "Select a preset or custom prompt for guiding the LLM."}),
                "system_message": ("STRING", {"multiline": True, "default": "", "tooltip": "Optional system message to guide the LLM's behavior."}),
                "user_input": ("STRING", {"multiline": True, "default": "", "tooltip": "User input or prompt to generate a response from the LLM."}),
                "temperature": ("FLOAT", {"default": 0.85, "min": 0.1, "max": 2.0, "step": 0.05, "tooltip": "Controls randomness in responses."}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 131072, "step": 1, "tooltip": "Maximum number of tokens to generate in the response."}),
                "top_p": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 1.0, "step": 0.01, "tooltip": "Limits the pool of words the model can choose from based on their combined probability."}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 4294967295, "tooltip": "Seed for random number generation, ensuring reproducibility."}),
                "max_retries": ("INT", {"default": 2, "min": 1, "max": 10, "step": 1, "tooltip": "Maximum number of retries in case of request failure."}),
                "stop": ("STRING", {"default": "", "tooltip": "Stop generation when the specified sequence is encountered."}),
                "json_mode": ("BOOLEAN", {"default": False, "tooltip": "Enable JSON mode for structured output."}),
                "conversation_id": ("STRING", {"default": "", "tooltip": "Unique identifier for the conversation. Leave empty for a new conversation."}),
            }
        }
    
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("api_response", "success", "status_code", "conversation_id", "chat_history")
    OUTPUT_TOOLTIPS = ("The API response. This is the text generated by the model", "Whether the request was successful", "The status code of the request", "The unique identifier for the conversation", "The complete chat history")
    FUNCTION = "process_completion_request"
    CATEGORY = "⚡ MNeMiC Nodes"
    DESCRIPTION = "Uses Groq API to generate text from language models with conversation context."
    
    def process_completion_request(self, model, preset, system_message, user_input, temperature, max_tokens, top_p, seed, max_retries, stop, json_mode, conversation_id):
        # Set the seed for reproducibility
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
    
        if preset == self.DEFAULT_PROMPT:
            system_message = system_message
        else:
            system_message = get_prompt_content(self.prompt_options, preset)
    
        url = 'https://api.groq.com/openai/v1/chat/completions'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        # Get or create conversation history
        if not conversation_id:
            conversation_id = self.chat_history_manager.create_new_conversation()
        
        conversation_history = self.chat_history_manager.get_history(conversation_id)
        
        # Add system message if it's a new conversation
        if not conversation_history:
            conversation_history.append({"role": "system", "content": system_message})
        
        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        data = {
            'model': model,
            'messages': conversation_history,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': top_p,
            'seed': seed
        }
        
        if stop:  # Only add stop if it's not empty
            data['stop'] = stop
        
        print(f"Sending request to {url} with data: {json.dumps(data, indent=4)} and headers: {headers}")
        
        assistant_message, success, status_code = make_api_request(data, headers, url, max_retries)
        
        # Add assistant's response to conversation history
        if success:
            conversation_history.append({"role": "assistant", "content": assistant_message})
            self.chat_history_manager.update_history(conversation_id, conversation_history)
        
        chat_history = json.dumps(self.chat_history_manager.get_all_conversations(), indent=2)
        return assistant_message, success, status_code, conversation_id, chat_history

    def get_chat_history(self):
        all_conversations = self.chat_history_manager.get_all_conversations()
        return json.dumps(all_conversations, indent=2)