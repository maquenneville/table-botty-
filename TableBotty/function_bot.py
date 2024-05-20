# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 20:16:18 2023

@author: marca
"""

from simple_bot import SimpleBot
import time
import openai
from openai import OpenAI
#from openai.error import RateLimitError, InvalidRequestError, APIError
import json

class FunctionBot(SimpleBot):
    def __init__(self, primer, model='gpt-4-turbo-preview', function_desc=None, function_calls=None):
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

# =============================================================================
#     def _generate_function_response(self, *args, **kwargs):
#         messages = args[0]
#         response = None
#     
#         while True:
#             response = super()._generate_response(messages, **kwargs)
#             
#             print(response)
#             
#             if response.choices[0].finish_reason != "function_call":
#                 break
#             
#             full_message = response.choices[0]
#             #function_call = full_message["message"]["function_call"]
#             tool_calls = full_message.message.tool_calls
#             
#             for call in tool_calls:
#                 #function_name = function_call["name"]
#                 function_name = call.name
#                 #function_args = json.loads(function_call["arguments"])
#                 function_args = json.loads(call.arguments)
#                 
#                 print(f'Using {function_name}...')
#                 result = self._execute_function(function_name, function_args)
#             
#                 messages.append({"role": "function", "content": f"Finished executing function {function_name}. Result: {result}", 'name': function_name})
# 
#         
#         return response
# =============================================================================


    def _generate_function_response(self, *args, **kwargs):
        messages = args[0]
        response = None
    
        while True:
            response = super()._generate_response(messages, **kwargs)
            
            print(response)
            
            if response.choices[0].finish_reason != "function_call":
                break
            
            full_message = response.choices[0]
            function_call = full_message.message.function_call
            
            if function_call:  # Check if function_call is present
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                print(f'Using {function_name}...')
                result = self._execute_function(function_name, function_args)
            
                messages.append({"role": "function", "content": f"Finished executing function {function_name}. Result: {result}", 'name': function_name})
    
            # Handle tool_calls if they exist and are not None
            tool_calls = full_message.message.tool_calls
            if tool_calls:  # Add this check to ensure tool_calls is not None
                for call in tool_calls:
                    function_name = call.name
                    function_args = json.loads(call.arguments)
                    
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
    

from gpt_tools import find_rows_by_value, aggregate_dataframe_operations, get_cell_info_excel, adjust_column_width_excel, change_font_excel_cells, sql_to_csv, execute_sql, csv_to_sql, add_row_with_values, get_column_stats, rename_columns, get_rows_by_index, get_basic_table_info, get_columns, populate_column_by_function, drop_rows_by_condition, condense_table, add_column, delete_column, read_file_sample, script_dir, gpt_workspace




db_tool_calls = {'sql_to_csv': sql_to_csv, 'execute_sql': execute_sql, 'csv_to_sql': csv_to_sql}

db_tool_descriptions = [    {
        "name": "csv_to_sql",
        "description": "Saves a CSV file as a table in a SQL database. The type of the database ('sqlite', 'mysql', or 'postgresql') and the database credentials are read from a 'config.ini' file in the working directory. The SQL table is created or replaced if it already exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "table_name": {
                    "type": "string",
                    "description": "The name of the SQL table to create or replace."
                }
            },
            "required": ["filename", "table_name"]
        }
    },
    {
        "name": "sql_to_csv",
        "description": "Reads data from a specified table of a SQL database and writes it to a CSV file in the 'gpt_workspace' directory. The database details and credentials are read from a 'config.ini' file. The database type can be 'SQLite', 'MySQL', or 'PostgreSQL'.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "The name of the table from which the data is to be read."
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file to be created, including the .csv extension."
                },
            },
            "required": ["table_name", "filename"]
        }
    },
    {
        "name": "execute_sql",
        "description": "Executes a SQL query on a specified table of a database. The database details and credentials are read from a 'config.ini' file. The database type can be 'SQLite', 'MySQL', or 'PostgreSQL'. If the SQL query returns data, the result set is returned as a dictionary. Otherwise, a success message is returned.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "The name of the table on which the SQL query is to be executed."
                },
                "sql": {
                    "type": "string",
                    "description": "The SQL query to be executed, which can be a single or multiline string. Only use traditional SQL, do not use PRAGMA or any other special database command types."
                },
            },
            "required": ["table_name", "sql"]
        }
    },
    {
        "name": "get_cell_info_excel",
        "description": "Retrieves information about specific cells in an Excel file. For each cell specified in the 'cell_positions' list, it returns the font, font size, font color, width, and height.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the Excel file, including the .xlsx extension."
                },
                "cell_positions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of cell positions (e.g., 'A1', 'B2') for which information should be retrieved."
                }
            },
            "required": ["filename", "cell_positions"]
        }
    }


]

db_bot_primer = "You are my Database Management Assistant.  Your job is to help the user by displaying, analyzing, manipulating tables and anything else the user might need regarding tables in a SQLite database.  When necessary, you will use the function tools provided to you to perform the user requests to the best of your ability.  If instructions are unclear at any point, clarify with the user before proceeding.  You have permission to view, analyze and edit the database specified by the user and ONLY that database."
    


bot = FunctionBot(primer=db_bot_primer, function_desc=db_tool_descriptions, function_calls=db_tool_calls)


bot.chat("What tables are in the database?")