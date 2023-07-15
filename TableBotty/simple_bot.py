# -*- coding: utf-8 -*-
"""
Created on Thu May 18 12:22:23 2023

@author: marca
"""

import openai
from openai.error import RateLimitError, InvalidRequestError, APIError
import time
import configparser
import tiktoken


class SimpleBot:
    
    def __init__(self, primer, model="gpt-3.5-turbo-16k"):
        self.openai_api_key = self._get_api_keys("config.ini")
        openai.api_key = self.openai_api_key
        self.model = model
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        if isinstance(primer, list):
            self.primer = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            for message in primer:
                self.primer.append({"role": "user", "content": message})
        else:
            self.primer = [
                {"role": "system", "content": primer},
            ]

    def _get_api_keys(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        openai_api_key = config.get("API_KEYS", "OpenAI_API_KEY")
        return openai_api_key

    def _count_tokens(self, text):
        tokens = len(self.encoding.encode(text))
        return tokens

    def _generate_response(
        self,
        messages,
        function_desc=None,
        temperature=0.5,
        n=1,
        max_tokens=4000,
        frequency_penalty=0,
    ):
        token_ceiling = 4096
        if self.model == "gpt-4":
            max_tokens = 8000
            token_ceiling = 8000
        if self.model == "gpt-3.5-turbo-16k":
            max_tokens = 15000
            token_ceiling = 15000
    
        tokens_used = sum([self._count_tokens(msg["content"]) for msg in messages])
        tokens_available = token_ceiling - tokens_used
    
        max_tokens = min(max_tokens, (tokens_available - 100))
    
        if tokens_used + max_tokens > token_ceiling:
            max_tokens = token_ceiling - tokens_used - 10
    
        if max_tokens < 1:
            max_tokens = 1
    
        max_retries = 10
        retries = 0
        backoff_factor = 1  # Initial sleep time factor
    
        while retries < max_retries:
            
            try:
                completion_params = {
                    "model": self.model,
                    "messages": messages,
                    "n": n,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "frequency_penalty": frequency_penalty,
                }
                if function_desc is not None:
                    completion_params["functions"] = function_desc
                
    
                completion = openai.ChatCompletion.create(**completion_params)
    
                response = completion
                return response
            except Exception as e:
                print(e)
                retries += 1
                sleep_time = backoff_factor * (2 ** retries)  # Exponential backoff
                print(f"Server overloaded, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
        print("Failed to generate prompt after max retries")
        return



    def smart_agent(self):
        self.model = "gpt-4"

    def fast_agent(self):
        self.model = "gpt-3.5-turbo"
        
    def long_agent(self):
        self.model = "gpt-3.5-turbo-16k"

    def add_primer(self, primer_text):
        self.primer.append({"role": "user", "content": primer_text})

    def chat(self, input_string: str):
        # Create a local copy of self.primer
        messages = self.primer.copy()

        # Append new user message
        messages.append({"role": "user", "content": f"{input_string}"})

        response = self._generate_response(messages, temperature=0.1)

        return response
    

