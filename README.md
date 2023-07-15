# TableBotty - A Data Table Management Assistant

TableBotty is a powerful data table management assistant that leverages OpenAI's GPT models and custom tools via GPT function calling. It provides a user-friendly, lightweight interface to help with displaying, analyzing, and manipulating tables. TableBotty is capable of editing CSV files (for now, more filetypes to come), making it a perfect tool for tasks like data cleaning and pre-processing.  Current abilities include:

- Reading and understanding general table info like column names, layout and expected values
- Adding and dropping columns
- Condensing tables with multiple entries per object
- Dropping rows via plain english conditionals
- Applying GPT-generated functions to columns, using other columns, to pwrform operations 

# Installation
1. Install Python (version 3.6 or higher is recommended).

2. Clone this repository:

git clone https://github.com/maquenneville/TableBotty.git

3. Navigate to the TableBotty directory:

cd TableBotty

4. Install the required packages:

pip install -r requirements.txt

# Usage
Ensure all relevant .csv files are copied to the gpt_workspace folder before engaging with the bot.

WARNING: Any files in the gpt_workspace folder are subject to change if requested by the user. Ensure you have backup copies elsewhere.

Start the TableBotty program:

python tablebotty.py

Interact with the bot using the provided commands or by describing tasks related to CSV files and data tables. The bot will attempt to execute the requested tasks to the best of its abilities.

# Notes
The functions available to the bot are declared in the tool_calls dictionary and their corresponding descriptions in the tool_descriptions list. If you wish to expand the functionality of the bot, you can add more functions and their descriptions.  So far there are only a few (but powerful) tools, and I will be expanding them over time.

# License
This project is licensed under the terms of the MIT license.
