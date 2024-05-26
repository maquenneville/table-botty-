# TableBotty - A Data Table Management Assistant

TableBotty is a powerful data table management assistant that leverages OpenAI's GPT models and custom tools via GPT function calling. It provides a user-friendly, plain english, lightweight interface to help with displaying, analyzing, and manipulating tables. TableBotty at its base can use csv or excel files in the gpt_workspace folder to perform edits and display info, which will be loaded into your choaen database upon initialization.  All querying and editing is then performed on the db tables, and can be exported into new csv or excel files to the gpt_workspace folder.   These features make it an effective tool for tasks like data exploration, data cleaning, and pre-processing, with no coding or SQL knowledge required.  Current abilities include:

- Can create and execute any SQL command in the specified database (using the "database" command) based on plain english (can handle SQLite, PostgreSQL and MySQL dbs)
- Can chain together SQL commands and queries to perform complex edits, or to answer queries that require digging into multiple tables/performing operations
- Can export any of these tables into tabular files for use elsewhere

# Installation
1. Install Python (version 3.8 or higher is recommended).

2. Clone this repository:

git clone https://github.com/maquenneville/TableBotty.git

3. Update the config.ini file with your personal OpenAI API key and database credentials (ensure you set the database type)

4. Navigate to the TableBotty directory:

cd TableBotty

5. Install the required packages:

pip install -r requirements.txt

# Usage
Ensure any and all necessary .csv and/or .xlsx files are copied to the gpt_workspace folder before engaging with the bot.

WARNING: Any files in the gpt_workspace folder are subject to change if requested by the user. Ensure you have backup copies elsewhere.  Also, if a database is specified in the config.ini file, that database is also subject to change by the bot.

Start the TableBotty program:

python tablebotty.py

Interact with the bot using the provided commands or by describing tasks related to csv/excel files and database tables. The bot will attempt to execute the requested tasks to the best of its abilities.

# Notes
The functions available to the bot are declared in the db_tool_calls dictionary and their corresponding descriptions in the db_tool_descriptions list. If you wish to expand the functionality of the bot, you can add more functions and their descriptions.  So far there are only a few (but powerful) tools, leveraging the high functionality of SQL commands.

# License
This project is licensed under the terms of the MIT license.
