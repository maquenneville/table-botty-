# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:12:14 2023

@author: marca
"""


import pandas as pd
import numpy as np
import configparser
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

# Get the directory of the main script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the full, system-independent path to the workspace
gpt_workspace = os.path.join(script_dir, "GPTworkspace")



### TABULAR DATA TOOLS ###

def get_columns(file_name):
    file_path = os.path.join(gpt_workspace, file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return columns
    else:
        return f"File {file_name} does not exist."
    


def get_basic_table_info(filename):
    # Construct the full filepath
    filepath = os.path.join(gpt_workspace, filename)

    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Get basic info
        info_dict = {
            'columns': list(data.columns),
            'num_rows': len(data),
            'num_columns': len(data.columns),
            'dtypes': dict(data.dtypes)
        }

        return info_dict
    except Exception as e:
        return str(e)
    
# Let's define the function "get_column_stats" that will take a filename and column name as input and return a dictionary with basic stats of the column.

def get_column_stats(filename, column_name):
    # Construct the full filepath
    filepath = os.path.join(gpt_workspace, filename)

    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Check if the column exists in the DataFrame
        if column_name not in data.columns:
            return f"Column '{column_name}' not found in the CSV file."

        # Check if the column is numeric or text-based
        if pd.api.types.is_numeric_dtype(data[column_name]):
            # Get basic stats for numeric columns
            stats = data[column_name].describe().to_dict()
        else:
            # Get basic stats for text-based columns
            stats = {
                'unique_values': data[column_name].nunique(),
                'most_frequent_value': data[column_name].mode().iloc[0] if not data[column_name].mode().empty else None,
                'freq_most_frequent_value': data[column_name].value_counts().iloc[0] if not data[column_name].value_counts().empty else None,
                'shortest_length': data[column_name].str.len().min(),
                'longest_length': data[column_name].str.len().max(),
                'average_length': data[column_name].str.len().mean()
            }

        return stats
    except Exception as e:
        return f"An error occurred: {e}"



def get_rows_by_index(filename, rows):
    # Construct the full filepath
    filepath = os.path.join(gpt_workspace, filename)

    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Select only the rows with indices in the rows list
        selected_rows = data.iloc[rows]

        # Convert the selected rows back into CSV format
        csv_output = selected_rows.to_csv(index=False)

        return csv_output
    except Exception as e:
        return str(e)

def add_row_with_values(filename, row_values):
    filepath = os.path.join(gpt_workspace, filename)
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Check if the number of values matches the number of columns
        if len(row_values) != len(data.columns):
            return "Error: The number of values provided does not match the number of columns in the CSV file."

        # Append the new row
        data.loc[len(data)] = row_values

        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)

        return f"Row with values {row_values} was added to '{filename}' successfully!"
    except Exception as e:
        return f"An error occurred: {e}"


def rename_columns(filename, old_names, new_names):
    # Check if both lists have the same length
    if len(old_names) != len(new_names):
        return "Error: Old names and new names lists must have the same length."

    # Create a dictionary from the lists of old and new names
    column_dict = dict(zip(old_names, new_names))

    filepath = os.path.join(gpt_workspace, filename)
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Rename the columns
        data.rename(columns=column_dict, inplace=True)

        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)

        return f"Columns {old_names} were renamed to {new_names} in '{filename}' successfully!"
    except Exception as e:
        return f"An error occurred: {e}"



def read_csv_file(filename):
    
    filepath = gpt_workspace + "\\" + filename
    try:
        data = pd.read_csv(filepath, nrows=5)
        csv_text = data.to_csv(index=False)
        return csv_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def delete_csv_column(filename, column_name):
    filepath = gpt_workspace + "\\" + filename
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)
        
        # Check if the column exists in the DataFrame
        if column_name in data.columns:
            # Drop the column from the DataFrame
            data = data.drop(columns=[column_name])
            
            # Write the DataFrame back to the CSV file
            data.to_csv(filepath, index=False)
            return f"Column '{column_name}' deleted successfully!"
        else:
            return f"Column '{column_name}' not found in the CSV file."
    except Exception as e:
        return f"An error occurred: {e}"
    
def add_csv_column(filename, column_name):
    filepath = gpt_workspace + "\\" + filename
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)
        
        # Add the new column to the DataFrame
        data[column_name] = pd.Series([np.nan]*len(data))
            
        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)
        return f"Column '{column_name}' added successfully!"
    except Exception as e:
        return f"An error occurred: {e}"
    
def condense_table(filename, column_name):
    filepath = gpt_workspace + "\\" + filename
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)
        
        # Check if the column exists in the DataFrame
        if column_name not in data.columns:
            return f"Column '{column_name}' not found in the CSV file."

        # Process each group of rows that have the same target column value
        def process_group(group):
            # Detect the data types of the columns
            column_is_numeric = group.dtypes.apply(lambda dtype: np.issubdtype(dtype, np.number))

            # Sum numeric columns, concatenate string columns
            return group.agg({column: 'sum' if is_numeric else ' '.join for column, is_numeric in column_is_numeric.iteritems()})
        
        data = data.groupby(column_name).apply(process_group).reset_index()

        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)
        return f"Table condensed successfully using column '{column_name}'!"
    except Exception as e:
        return f"An error occurred: {e}"
    
def drop_rows_by_condition(filename, column_name, condition):
    filepath = gpt_workspace + "\\" + filename
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)
        
        # Check if the column exists in the DataFrame
        if column_name not in data.columns:
            return f"Column '{column_name}' not found in the CSV file."

        # Apply the condition to the DataFrame
        # Invert the condition with '~' to keep rows where the condition is False
        data = data.query(f'~({column_name} {condition})')

        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)
        return f"Rows dropped successfully using condition '{condition}' on column '{column_name}'!"
    except Exception as e:
        return f"An error occurred: {e}"
    


def populate_column_by_function(filename, target_columns, result_column, func_definition):
    # Create the global scope for the exec function
    global_scope = {"pd": pd}

    # Use exec to define the function in the global scope
    exec(f"global func; func = {func_definition}", global_scope)

    # Get the function from the global scope
    func = global_scope["func"]

    filepath = gpt_workspace + "\\" + filename
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Check if the target_columns exist in the DataFrame
        missing_columns = [col for col in target_columns if col not in data.columns]
        if missing_columns:
            return f"Target columns '{missing_columns}' not found in the CSV file."
        
        # Apply the function to the target columns to create the result column
        # If there's only one target column, we apply the function directly
        if len(target_columns) == 1:
            data[result_column] = data[target_columns[0]].apply(func)
        else:  # If there are multiple target columns, we need to apply function row-wise
            data[result_column] = data[target_columns].apply(lambda row: func(*row), axis=1)

        # Write the DataFrame back to the CSV file
        data.to_csv(filepath, index=False)
        
        return f"Column '{result_column}' created successfully using function '{func_definition}' on column(s) '{target_columns}'!"
    except Exception as e:
        return f"An error occurred: {e}"

### DATABASE TOOLS ###



def csv_to_sql(filename, table_name):
    # Parsing the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Ensure the database type is in lowercase
    database_type = config.get('database', 'type').lower()
    
    db_config = config[database_type]

    # Create the appropriate connection string
    if database_type == 'sqlite':
        conn_str = f"{database_type}:///{db_config['dbname']}.db"
    else:
        conn_str = f"{database_type}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"

    # Create a SQLAlchemy engine
    try:
        engine = create_engine(conn_str)
    except OperationalError:
        return f"Unable to create the engine due to an Operational Error. Please check your connection details and try again."

    filepath = os.path.join(gpt_workspace, filename)
    try:
        # Load the DataFrame from the CSV file
        data = pd.read_csv(filepath)

        # Save the DataFrame to the SQL database
        data.to_sql(table_name, engine, if_exists='replace')

        return f"CSV file '{filename}' was saved as table '{table_name}' in the {database_type} database successfully!"
    except Exception as e:
        return f"An error occurred: {e}"



def sql_to_csv(table_name, filename):
    # Parsing the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Getting the database type from the configuration
    database_type = config.get('database', 'type').lower()

    # Setting up the engine string based on the database type
    if database_type == 'sqlite':
        engine_string = f'sqlite:///{config.get("sqlite", "dbname")}.db'
    elif database_type == 'mysql':
        engine_string = f'mysql+pymysql://{config.get("mysql", "user")}:{config.get("mysql", "password")}@{config.get("mysql", "host")}:{config.get("mysql", "port")}/{config.get("mysql", "dbname")}'
    elif database_type == 'postgresql':
        engine_string = f'postgresql://{config.get("postgresql", "user")}:{config.get("postgresql", "password")}@{config.get("postgresql", "host")}:{config.get("postgresql", "port")}/{config.get("postgresql", "dbname")}'

    try:
        # Creating the engine
        engine = create_engine(engine_string)

        # Reading the data from the SQL table into a DataFrame
        data = pd.read_sql_table(table_name, engine)

        # Writing the DataFrame to a CSV file in the gpt_workspace
        filepath = os.path.join(gpt_workspace, filename)
        data.to_csv(filepath, index=False)

        # Closing the connection
        engine.dispose()

        return f"Table '{table_name}' from the database has been successfully saved as '{filename}' in the 'gpt_workspace'!"
    except Exception as e:
        return f"An error occurred: {e}"


def execute_sql(table_name, sql):
    # Parsing the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Getting the database type from the configuration
    database_type = config.get('database', 'type').lower()

    # Setting up the engine string based on the database type
    if database_type == 'sqlite':
        engine_string = f'sqlite:///{config.get("sqlite", "dbname")}.db'
    elif database_type == 'mysql':
        engine_string = f'mysql+pymysql://{config.get("mysql", "user")}:{config.get("mysql", "password")}@{config.get("mysql", "host")}:{config.get("mysql", "port")}/{config.get("mysql", "dbname")}'
    elif database_type == 'postgresql':
        engine_string = f'postgresql://{config.get("postgresql", "user")}:{config.get("postgresql", "password")}@{config.get("postgresql", "host")}:{config.get("postgresql", "port")}/{config.get("postgresql", "dbname")}'

    try:
        # Creating the engine
        engine = create_engine(engine_string)

        # Executing the SQL block
        result = engine.execute(sql)
        

        # Closing the connection
        engine.dispose()

        # Handling the results
        if result.returns_rows:
            return [dict(row) for row in result]
        else:
            return f"SQL block executed successfully on table '{table_name}'!"
    except Exception as e:
        return f"An error occurred: {e}"





