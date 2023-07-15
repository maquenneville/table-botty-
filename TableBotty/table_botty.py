# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 00:21:10 2023

@author: marca
"""

from function_bot import FunctionBot
from gpt_tools import get_columns, populate_column_by_function, drop_rows_by_condition, condense_table, add_csv_column, delete_csv_column, read_csv_file, script_dir, gpt_workspace
import os
import threading
import sys
import time
import shutil

tool_calls = {'get_columns': get_columns, 'populate_column_by_function': populate_column_by_function, 'drop_rows_by_condition': drop_rows_by_condition, 'condense_table': condense_table, 'read_csv_file': read_csv_file, 'delete_csv_column': delete_csv_column, 'add_csv_column': add_csv_column}

tool_descriptions = [
    
    {
        "name": "read_csv_file",
        "description": "Read the first 5 rows from a CSV file and return them as CSV text. The CSV file is located in the directory specified by the 'gpt_workspace' global variable.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
            },
            "required": ["filename"],
        }
    },
    {
        "name": "delete_csv_column",
        "description": "Deletes a specified column from a CSV file located in the directory specified by the 'gpt_workspace' global variable and resaves the CSV file with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "column_name": {
                    "type": "string",
                    "description": "The name of the column to be deleted."
                },
            },
            "required": ["filename", "column_name"],
        }
    },
    {
        "name": "add_csv_column",
        "description": "Adds a specified column filled with NaN values to a CSV file located in the directory specified by the 'gpt_workspace' global variable and resaves the CSV file with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "column_name": {
                    "type": "string",
                    "description": "The name of the column to be added."
                },
            },
            "required": ["filename", "column_name"],
        }
    },
    {
        "name": "condense_table",
        "description": "Condenses a CSV file located in the directory specified by the 'gpt_workspace' global variable based on a target column. For each unique value in the target column, it sums the values in numeric columns and concatenates the values in non-numeric columns. The condensed CSV file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "column_name": {
                    "type": "string",
                    "description": "The name of the column to be used as the basis for condensation."
                },
            },
            "required": ["filename", "column_name"],
        }
    },
    {
        "name": "drop_rows_by_condition",
        "description": "Drops rows from a CSV file located in the directory specified by the 'gpt_workspace' global variable based on a condition applied to a target column. The CSV file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "column_name": {
                    "type": "string",
                    "description": "The name of the column to be used as the basis for the condition."
                },
                "condition": {
                    "type": "string",
                    "description": "The condition to be applied to the target column, expressed as a string. For example, '> 50' means 'drop rows where the value in the target column is greater than 50'."
                },
            },
            "required": ["filename", "column_name", "condition"],
        }
    },
    {
        "name": "populate_column_by_function",
        "description": "Applies a function to one or more target columns of a CSV file located in the directory specified by the 'gpt_workspace' global variable, creating a new results column. The CSV file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV file, including the .csv extension."
                },
                "target_columns": {
                    "type": ["string", "array"],
                    "description": "The name(s) of the column(s) to be used as the input to the function. It can be a single string (for one column) or a list of strings (for multiple columns)."
                },
                "result_column": {
                    "type": "string",
                    "description": "The name of the new column to be created as the output of the function."
                },
                "func_definition": {
                    "type": "string",
                    "description": "The definition of the function to be applied to the target column(s), expressed as a string. This should be a full lambda function definition. If there's only one target column, 'x' should be used as the variable, e.g., 'lambda x: (x - 32) * 5.0/9.0' to convert degrees Fahrenheit to Celsius. If there are multiple target columns, use multiple variables, e.g., 'lambda x, y: x + y' to add two columns together."
                },
            },
            "required": ["filename", "target_columns", "result_column", "func_definition"],
        }
    },
    {
        "name": "get_columns",
        "description": "Read a CSV file and return the names of its columns",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the CSV file",
                }
            },
            "required": ["file_name"],
        }
    }

]


class Spinner:
    def __init__(self, message="Thinking..."):
        self._message = message
        self._running = False
        self._spinner_thread = None

    def start(self):
        self._running = True
        self._spinner_thread = threading.Thread(target=self._spin)
        self._spinner_thread.start()

    def stop(self):
        self._running = False
        self._spinner_thread.join()

    def _spin(self):
        spinner_chars = "|/-\\"
        index = 0

        while self._running:
            sys.stdout.write(
                f"\r{self._message} {spinner_chars[index % len(spinner_chars)]}"
            )
            sys.stdout.flush()
            time.sleep(0.1)
            index += 1

        # Clear the spinner line
        sys.stdout.write("\r" + " " * (len(self._message) + 2))
        sys.stdout.flush()
        
        
        
        
def main():
    print("Welcome to TableBotty!\n")
    
    spinner = Spinner()
    
    
    print('\nEnsure all relevant .csv files are copied to the gpt_workspace folder before engaging with the bot\n')
    print('\n Warning: any files in the gpt_workspace folder are subject to change if requested by the user, ensure you have backup copies elsewhere\n')

    bot_primer = "You are my Data Table Management Assistant.  Your job is to help the user by displaying, analyzing, manipulating tables and anything else the user might need regarding tables.  When necessary, you will use the function tools provided to you to perform the user requests to the best of your ability.  If instructions are unclear at any point, clarify with the user before proceeding.  You have permission to view, analyze and edit the files specified by the user and ONLY those files."
    # Instantiate the bot
    bot = FunctionBot(primer=bot_primer, function_desc=tool_descriptions, function_calls=tool_calls)

    print(f"\nYou can now chat with your table agent, and give it tasks.")
    print("\nEnter 'exit' at any time to end the chat.")
    print("\nEnter 'help' to see a list of commands.\n")
    print("\nEnter 'tools' to see the tools the agent can use.\n")

    while True:
        user_input = input("You: ")
        # Check if the user wants to exit
        if user_input.lower() == "exit":
            print("Ending the chat. Goodbye!")
            break

        # If user needs help, display commands
        elif user_input.lower() == "help":
            print("\nList of Commands:")
            print("'exit' - End the chat.")
            print("'smart agent' - Switch to GPT-4 model for responses.")
            print("'fast agent' - Switch back to GPT-3.5 Turbo model for responses.\n")
            continue
        
        elif user_input.lower() == "tools":
            print("Tools:\n")
            tool_list_string = "\n\n".join(f"{tool['name']}: {tool['description']}" for tool in tool_descriptions)
            print(tool_list_string)
            continue
        
        # If user wants to switch to 'gpt-4'
        elif user_input.lower() == "smart agent":
            bot.smart_agent()
            print("Switched to smart agent (GPT-4) for responses.")
            continue

        # If user wants to switch back to 'gpt-3.5-turbo'
        elif user_input.lower() == "fast agent":
            bot.long_agent()
            print("Switched back to fast agent (GPT-3.5 Turbo) for responses.")
            continue

        spinner.start()
        # Generate a response and display it
        bot_response = bot.chat(user_input)
        spinner.stop()
        print(f"\nAgent: {bot_response}\n")


if __name__ == "__main__":
    main()