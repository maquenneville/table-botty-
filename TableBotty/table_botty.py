# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 00:21:10 2023

@author: marca
"""

from function_bot import FunctionBot
from gpt_tools import find_rows_by_value, aggregate_dataframe_operations, get_cell_info_excel, adjust_column_width_excel, change_font_excel_cells, sql_to_csv, execute_sql, csv_to_sql, add_row_with_values, get_column_stats, rename_columns, get_rows_by_index, get_basic_table_info, get_columns, populate_column_by_function, drop_rows_by_condition, condense_table, add_column, delete_column, read_file_sample, script_dir, gpt_workspace
import os
import threading
import sys
import time
import shutil

tool_calls = {'find_rows_by_value': find_rows_by_value, 'aggregate_dataframe_operations': aggregate_dataframe_operations, 'get_cell_info_excel': get_cell_info_excel, 'adjust_column_width_excel': adjust_column_width_excel, 'change_font_excel_cells': change_font_excel_cells, 'add_row_with_values': add_row_with_values, 'get_column_stats': get_column_stats, 'rename_columns': rename_columns, 'get_rows_by_index': get_rows_by_index, 'get_basic_table_info': get_basic_table_info, 'get_columns': get_columns, 'populate_column_by_function': populate_column_by_function, 'drop_rows_by_condition': drop_rows_by_condition, 'condense_table': condense_table, 'read_file_sample': read_file_sample, 'delete_column': delete_column, 'add_column': add_column}

tool_descriptions = [
    
    {
        "name": "read_file_sample",
        "description": "Read the first 5 rows from a CSV or Excel file and return them as CSV text. The file is located in the directory specified by the 'gpt_workspace' global variable.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
            },
            "required": ["filename"],
        }
    },
    {
        "name": "delete_column",
        "description": "Deletes a specified column from a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable and resaves the file with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
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
        "name": "add_column",
        "description": "Adds a specified column filled with NaN values to a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable and resaves the file with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
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
        "description": "Condenses a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable based on a target column. For each unique value in the target column, it sums the values in numeric columns and concatenates the values in non-numeric columns. The condensed file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
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
        "description": "Drops rows from a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable based on a condition applied to a target column. The file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
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
        "description": "Applies a function to one or more target columns, or all columns if none is specified, of a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable, creating a new results column. The file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "target_columns": {
                    "type": ["string", "array", "null"],
                    "description": "The name(s) of the column(s) to be used as the input to the function. It can be a single string (for one column), a list of strings (for multiple columns), or null for all columns."
                },
                "result_column": {
                    "type": "string",
                    "description": "The name of the new column to be created as the output of the function."
                },
                "func_definition": {
                    "type": "string",
                    "description": "The definition of the function to be applied to the target column(s), expressed as a string. This should be a full lambda function definition. If there's only one target column, 'x' should be used as the variable, e.g., 'lambda x: (x - 32) * 5.0/9.0' to convert degrees Fahrenheit to Celsius. If there are multiple target columns, use multiple variables, e.g., 'lambda x, y: x + y' to add two columns together. If 'target_columns' is null, the function should be defined to accept a Series object and work row-wise against axis=1."
                }
            },
            "required": ["filename", "result_column", "func_definition"]
        }
    },
    {
        "name": "get_columns",
        "description": "Get the list of column names from a file. The file should be in CSV or Excel format and located in the 'gpt_workspace' directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the file, including the file extension (.csv or .xlsx)."
                }
            },
            "required": ["file_name"]
        }
    },
    {
        "name": "get_basic_table_info",
        "description": "Get basic information about the table in a file. The file should be in CSV or Excel format and located in the 'gpt_workspace' directory. The information includes the list of column names, the number of rows, the number of columns, and the data types of each column.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file, including the file extension (.csv or .xlsx)."
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "get_rows_by_index",
        "description": "Returns a subset of rows from a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable. The rows are selected based on their index values and are returned as a single string in CSV format.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "A list of index values specifying which rows to return. Indices start from 0."
                }
            },
            "required": ["filename", "rows"]
        }
    },
    {
        "name": "rename_columns",
        "description": "Renames selected columns in a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable. The file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "old_names": {
                    "type": "array",
                    "items": { "type": "string" },
                    "description": "A list of old column names to be replaced."
                },
                "new_names": {
                    "type": "array",
                    "items": { "type": "string" },
                    "description": "A list of new column names to replace the old ones."
                }
            },
            "required": ["filename", "old_names", "new_names"]
        }
    },
    {
        "name": "get_column_stats",
        "description": "Extracts basic statistics from a specified column in a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable. If the column is numeric, the statistics include count, mean, standard deviation, minimum, 25th percentile, median, 75th percentile, and maximum. If the column is text-based, the statistics include the number of unique values, the most frequent value, frequency of the most frequent value, shortest length, longest length, and average length.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "column_name": {
                    "type": "string",
                    "description": "The name of the column from which to extract statistics."
                },
            },
            "required": ["filename", "column_name"],
        }
    },
    {
        "name": "add_row_with_values",
        "description": "Appends a row with specified values to a CSV or Excel file located in the directory specified by the 'gpt_workspace' global variable. The file is then resaved with the same name.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "row_values": {
                    "type": "array",
                    "items": { "type": ["integer", "string", "number"] },
                    "description": "A list of values to be appended as a new row. The list must have the same number of elements as there are columns in the CSV file."
                }
            },
            "required": ["filename", "row_values"]
        }
    },
    {
        "name": "aggregate_dataframe_operations",
        "description": "Performs a chain of aggregate operations on a pandas DataFrame loaded from a CSV or Excel file. The operations are performed by executing a snippet of Python code supplied by the user. The final DataFrame after all operations are performed is saved as a new CSV or Excel file, with the filename format '{filename}_pandas_working.{csv or xlsx}'.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "agg_operations": {
                    "type": "string",
                    "description": "A snippet of Python code representing a chain of aggregate operations to be performed on the DataFrame. The code should be formatted as if it were to be appended directly to a DataFrame variable named 'df', e.g., 'groupby('column').agg({'other_column': 'mean'})'."
                }
            },
            "required": ["filename", "agg_operations"]
        }
    },
    {
        "name": "find_rows_by_value",
        "description": "Finds the rows in a DataFrame loaded from a CSV or Excel file where the value of a specified comparison column is equal to a given value. The filename of the data file, the target column, the comparison column, and the value must be specified. Returns the values of the target column for these rows.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the CSV or Excel file, including the .csv or .xlsx extension."
                },
                "target_column": {
                    "type": "string",
                    "description": "The name of the target column, the values of which will be returned for the rows that match the condition."
                },
                "comparison_column": {
                    "type": "string",
                    "description": "The name of the comparison column, the values of which will be checked against the specified value."
                },
                "value": {
                    "type": ["string", "number"],
                    "description": "The value to compare against the values in the comparison column."
                }
            },
            "required": ["filename", "target_column", "comparison_column", "value"]
        }
    },
    {
        "name": "change_font_excel_cells",
        "description": "Changes the font, size, and color of specific cells in an Excel file. The new font and color are applied to all cells specified in the 'cell_positions' list. The file is saved after the changes.",
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
                    "description": "A list of cell positions (e.g., 'A1', 'B2') where the font should be changed."
                },
                "font_name": {
                    "type": "string",
                    "description": "The name of the font to apply to the cells."
                },
                "font_size": {
                    "type": "integer",
                    "description": "The size of the font to apply to the cells."
                },
                "font_color": {
                    "type": "string",
                    "description": "The color of the font to apply to the cells. Must be an RGB string (e.g., 'FFFFFF' for white)."
                }
            },
            "required": ["filename", "cell_positions", "font_name", "font_size", "font_color"]
        }
    },
    {
        "name": "adjust_column_width_excel",
        "description": "Adjusts the width of specified columns in an Excel file. The new widths are applied to all columns specified in the 'columns' list. The file is saved after the changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the Excel file, including the .xlsx extension."
                },
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of column names (e.g., 'A', 'B') where the width should be adjusted."
                },
                "widths": {
                    "type": ["array", "integer"],
                    "items": {
                        "type": "integer"
                    },
                    "description": "The new width(s) to apply to the column(s). Can be a single integer (applies to all) or a list of integers corresponding to each column."
                }
            },
            "required": ["filename", "columns", "widths"]
        }
    }




]

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
                    "description": "The SQL query to be executed, which can be a single or multiline string."
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
    db_bot_primer = "You are my Database Management Assistant.  Your job is to help the user by displaying, analyzing, manipulating tables and anything else the user might need regarding tables in a database.  When necessary, you will use the function tools provided to you to perform the user requests to the best of your ability.  If instructions are unclear at any point, clarify with the user before proceeding.  You have permission to view, analyze and edit the database specified by the user and ONLY that database."
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
            print("'database' - Switch to using tools for interacting with the SQL database specified in the config.ini file.\n")
            print("\n")
            continue
        
        elif user_input.lower() == "tools":
            print("Tools:\n")
            tool_list_string = "\n\n".join(f"{tool['name']}: {tool['description']}" for tool in tool_descriptions)
            print(tool_list_string)
            print("\n")
            continue
        
        # If user wants to switch to 'gpt-4'
        elif user_input.lower() == "smart agent":
            bot.smart_agent()
            print("Switched to smart agent (GPT-4) for responses.")
            print("\n")
            continue

        # If user wants to switch back to 'gpt-3.5-turbo'
        elif user_input.lower() == "fast agent":
            bot.long_agent()
            print("Switched back to fast agent (GPT-3.5 Turbo) for responses.")
            print("\n")
            continue
        
        elif user_input.lower() == "database":
            bot = FunctionBot(primer=db_bot_primer, function_desc=db_tool_descriptions, function_calls=db_tool_calls)
            print("Activated new bot specifically for interacting with your database")
            print("\n")
            continue
        spinner.start()
        # Generate a response and display it
        bot_response = bot.chat(user_input)
        spinner.stop()
        print(f"\nTable Botty: {bot_response}\n")

# =============================================================================
# import sqlite3
# from sqlite3 import Error
# 
# def create_connection():
#     conn = None;
#     try:
#         conn = sqlite3.connect('gpt.db')  # This will create a database file named 'my_database.db' if it doesn't exist
#         print(sqlite3.version)
#     except Error as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()
# =============================================================================


    
if __name__ == "__main__":
    main()
    #create_connection()