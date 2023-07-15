# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 22:12:14 2023

@author: marca
"""


import pandas as pd
import numpy as np

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


    






