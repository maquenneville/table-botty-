# TableBotty - A Data Table Management Assistant

TableBotty is a powerful data table management assistant that leverages OpenAI's GPT models and custom tools via GPT function calling. It provides a user-friendly, plain english, lightweight interface to help with displaying, analyzing, and manipulating tables. TableBotty at its base uses a specified csv or excel file in the gpt_workspace folder to perform edits and display info.  You can also switch to a database mode for interacting with database tables.  These features make it a perfect tool for tasks like data exploration, data cleaning, and pre-processing, with no coding or SQL knowledge required.  Current abilities include:

- Reading and understanding general table info like column names, number of rows and data types
- Adding rows using either user-provided or gpt-provided values
- Gathering and using row-specific data
- Get basic column stats for use in analysis
- Adding, dropping and renaming columns
- Condensing tables with multiple entries per object
- Dropping rows via plain english conditionals
- Applying GPT-generated functions to columns, using other columns, to perform operations
- When switched to the "database" mode, can create and execute any sql command in the specified database (using the "database" command) based on plain english

# Installation
1. Install Python (version 3.8 or higher is recommended).

2. Clone this repository:

git clone https://github.com/maquenneville/TableBotty.git

3. Update the config.ini file with your personal OpenAI API key and optional database credentials (ensure you set the database type)

4. Navigate to the TableBotty directory:

cd TableBotty

5. Install the required packages:

pip install -r requirements.txt

# Usage
Ensure all relevant .csv and/or .xlsx files are copied to the gpt_workspace folder before engaging with the bot.

WARNING: Any files in the gpt_workspace folder are subject to change if requested by the user. Ensure you have backup copies elsewhere.  Also, if a database is specified in the config.ini file, that database is also subject to change by the bot.

Start the TableBotty program:

python tablebotty.py

Interact with the bot using the provided commands or by describing tasks related to csv/excel files and database tables. The bot will attempt to execute the requested tasks to the best of its abilities.

# Notes
The functions available to the bot are declared in the tool_calls dictionary and their corresponding descriptions in the tool_descriptions list. If you wish to expand the functionality of the bot, you can add more functions and their descriptions.  So far there are only a few (but powerful) tools, and I will be expanding them over time.  If using the "database" mode, it will use the truncated list of database-specific tools in db_tool_descriptions and db_tool_calls.

# License
This project is licensed under the terms of the MIT license.
