# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 20:16:18 2023

@author: marca
"""

from simple_bot import SimpleBot
import time
import openai
from openai.error import RateLimitError, InvalidRequestError, APIError
import json

class FunctionBot(SimpleBot):
    def __init__(self, primer, model='gpt-3.5-turbo-16k', function_desc=None, function_calls=None):
        super().__init__(primer, model)
        self.function_desc = function_desc if function_desc else []
        self.function_calls = function_calls if function_calls else {}
        
        self.messages = self.primer.copy()
        
        
    def _execute_function(self, function_name, function_args):
        if function_name in self.function_calls:
            try:
                print(function_args)
                return self.function_calls[function_name](**function_args)
            except Exception as e:
                print(f"Function execution failed due to invalid arguments")
                print(f"Error message: {e}")
                raise
        else:
            raise Exception("Function does not exist and cannot be called")

    def _generate_function_response(self, *args, **kwargs):
        messages = args[0]
        response = None
    
        while True:
            response = super()._generate_response(messages, **kwargs)
            
            if response.choices[0]["finish_reason"] != "function_call":
                break
            
            full_message = response.choices[0]
            function_call = full_message["message"]["function_call"]
            function_name = function_call["name"]
            function_args = json.loads(function_call["arguments"])
            
            print(f'Using {function_name}...')
            result = self._execute_function(function_name, function_args)
            
            messages.append({"role": "function", "content": f"Finished executing function {function_name}. Result: {result}", 'name': function_name})

        
        return response

        
    def smart_agent(self):
        
        self.model = 'gpt-4-0613'
        
    def fast_agent(self):
        
        self.model = 'gpt-3.5-turbo-0613'

    
    def chat(self, input_string: str):
        # Append new user message
        self.messages.append({"role": "user", "content": input_string})

        response = self._generate_function_response(self.messages, temperature=0.1, function_desc=self.function_desc)
        
        if response is not None:
            self.messages.append({"role": "assistant", "content": str(response.choices[0].message.content)})
        
        return response.choices[0].message.content if response else None
    

