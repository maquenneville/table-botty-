# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:12:14 2023

@author: marca
"""


import pandas as pd
import numpy as np
import configparser
from constants import OPENAI_API_KEY, DATABASE_TYPE, DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT, GPT_WORKSPACE
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os



### DATABASE TOOLS ###

def get_engine_string():
    if DATABASE_TYPE == 'sqlite':
        return f'sqlite:///{DB_NAME}.db'
    elif DATABASE_TYPE == 'mysql':
        return f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    elif DATABASE_TYPE == 'postgresql':
        return f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    else:
        raise ValueError(f"Unsupported database type: {DATABASE_TYPE}")

def csv_to_sql(filename, table_name):
    conn_str = get_engine_string()
    
    # Create a SQLAlchemy engine
    try:
        engine = create_engine(conn_str)
    except OperationalError:
        return f"Unable to create the engine due to an Operational Error. Please check your connection details and try again."

    filepath = os.path.join(GPT_WORKSPACE, filename)
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Save the DataFrame to the SQL database
        data.to_sql(table_name, engine, if_exists='replace')

        return f"CSV file '{filename}' was saved as table '{table_name}' in the {DATABASE_TYPE} database successfully!"
    except Exception as e:
        return f"An error occurred: {e}"
    
    
def xlsx_to_sql(filename, table_name):
    conn_str = get_engine_string()

    # Create a SQLAlchemy engine
    try:
        engine = create_engine(conn_str)
    except OperationalError:
        return f"Unable to create the engine due to an Operational Error. Please check your connection details and try again."

    filepath = os.path.join(GPT_WORKSPACE, filename)
    try:
        # Load the DataFrame from the Excel file
        data = pd.read_excel(filepath)

        # Save the DataFrame to the SQL database
        data.to_sql(table_name, engine, if_exists='replace')

        return f"Excel file '{filename}' was saved as table '{table_name}' in the {DATABASE_TYPE} database successfully!"
    except Exception as e:
        return f"An error occurred: {e}"



def sql_to_csv(table_name, filename):
    conn_str = get_engine_string()
    
    try:
        # Creating the engine
        engine = create_engine(conn_str)

        # Reading the data from the SQL table into a DataFrame
        data = pd.read_sql_table(table_name, engine)

        # Writing the DataFrame to a CSV file in the GPT_WORKSPACE
        filepath = os.path.join(GPT_WORKSPACE, filename)
        data.to_csv(filepath, index=False)

        # Closing the connection
        engine.dispose()

        return f"Table '{table_name}' from the database has been successfully saved as '{filename}' in the 'GPT_WORKSPACE'!"
    except Exception as e:
        return f"An error occurred: {e}"
    
    
def sql_to_xlsx(table_name, filename):

    conn_str = get_engine_string()
    
    try:
        # Creating the engine
        engine = create_engine(conn_str)

        # Reading the data from the SQL table into a DataFrame
        data = pd.read_sql_table(table_name, engine)

        # Writing the DataFrame to an Excel file in the GPT_WORKSPACE
        filepath = os.path.join(GPT_WORKSPACE, filename)
        data.to_excel(filepath, index=False)

        # Closing the connection
        engine.dispose()

        return f"Table '{table_name}' from the database has been successfully saved as '{filename}' in the 'GPT_WORKSPACE'!"
    except Exception as e:
        return f"An error occurred: {e}"


    
def execute_sql(table_name, sql):

    conn_str = get_engine_string()
    
    try:
        # Creating the engine
        engine = create_engine(conn_str)

        # Executing the SQL block
        with engine.connect() as connection:
            result = connection.execute(text(sql))
            
            # Handling the results
            if result.returns_rows:
                # Convert the result to a list of dictionaries
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result]
            else:
                return f"SQL block executed successfully on table '{table_name}'!"
    except Exception as e:
        print(e)
        return f"An error occurred: {e}"



def initial_file_store():
    # Folder containing the files
    workspace_folder = 'GPT_WORKSPACE'
    
    # Ensure the workspace folder exists
    if not os.path.exists(workspace_folder):
        os.makedirs(workspace_folder)
    
    # List all files in the workspace folder
    files = os.listdir(workspace_folder)
    print(files)

    # Check if the folder is empty
    if not files:
        return "The GPT_WORKSPACE folder is empty. No files to process."

    # Process each file in the workspace folder
    results = []
    for file in files:
        file_path = os.path.join(workspace_folder, file)
        if file.lower().endswith('.csv'):
            table_name = os.path.splitext(file)[0]
            result = csv_to_sql(file, table_name)
            print(result)
            results.append(result)
        elif file.lower().endswith('.xlsx'):
            table_name = os.path.splitext(file)[0]
            result = xlsx_to_sql(file, table_name)
            print(result)
            results.append(result)
    
    # Join the results into a single string
    results_str = "\n".join(results)
    return results_str
