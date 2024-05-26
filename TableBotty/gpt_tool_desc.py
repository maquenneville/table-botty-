# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:03:19 2024

@author: marca
"""

from gpt_tools import xlsx_to_sql, sql_to_xlsx, sql_to_csv, execute_sql, csv_to_sql
from constants import DATABASE_TYPE



db_tool_calls = {'sql_to_csv': sql_to_csv, 'execute_sql': execute_sql, 'csv_to_sql': csv_to_sql, 'sql_to_xlsx': sql_to_xlsx, 'xlsx_to_sql': xlsx_to_sql}

db_tool_descriptions = [    {
        "name": "csv_to_sql",
        "description": f"Saves a CSV file as a table in a {DATABASE_TYPE} database. The SQL table is created or replaced if it already exists.",
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
            "name": "xlsx_to_sql",
            "description": f"Saves a .xlsx file as a table in a {DATABASE_TYPE} database. The SQL table is created or replaced if it already exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the .xlsx file, including the .xlsx extension."
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
        "description": f"Reads data from a specified table of a {DATABASE_TYPE} database and writes it to a CSV file in the 'gpt_workspace' directory.",
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
        "name": "sql_to_xlsx",
        "description": f"Reads data from a specified table of a {DATABASE_TYPE} database and writes it to a .xlsx file in the 'gpt_workspace' directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "The name of the table from which the data is to be read."
                },
                "filename": {
                    "type": "string",
                    "description": "The name of the .xlsx file to be created, including the .xlsx extension."
                },
            },
            "required": ["table_name", "filename"]
        }
    },
    {
        "name": "execute_sql",
        "description": f"Executes a SQL query on a specified table of a {DATABASE_TYPE} database. If the SQL query returns data, the result set is returned as a dictionary. Otherwise, a success message is returned.",
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
    }


]