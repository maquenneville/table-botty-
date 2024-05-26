# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:01:33 2024

@author: marca
"""

from constants import DATABASE_TYPE
from function_bot import FunctionBot
from gpt_tools import initial_file_store
import os
import threading
import sys
import time
import shutil
from gpt_tool_desc import db_tool_calls, db_tool_descriptions


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
    
    print('\nEnsure all relevant .csv/.xlsx files, if needed, are copied to the gpt_workspace folder before engaging with the bot\n')
    print('\n Warning: any files in the gpt_workspace folder are subject to change if requested by the user, ensure you have backup copies elsewhere\n')

    db_bot_primer = f"You are my Database Management Assistant.  Your job is to help the user by displaying, analyzing, manipulating tables and anything else the user might need regarding tables in a {DATABASE_TYPE} database.  When helpful and/or necessary, you will use the function tools provided to you to perform the user requests to the best of your ability.  If the task/query requires multiple SQL commands in a row, perform as many as are needed to complete the full task/answer the query.  Try to answer questions using the least amount of data, to keep token counts low.  If instructions are unclear at any point, clarify with the user before proceeding.  You have permission to view, analyze and edit the database specified by the user and ONLY that database."
    
    # Instantiate the bot
    bot = FunctionBot(primer=db_bot_primer, function_desc=db_tool_descriptions, function_calls=db_tool_calls)
    initial_file_store()

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
            print("\n")
            continue
        
        elif user_input.lower() == "tools":
            print("Tools:\n")
            tool_list_string = "\n\n".join(f"{tool['name']}: {tool['description']}" for tool in db_tool_descriptions)
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
        
        spinner.start()
        # Generate a response and display it
        bot_response = bot.chat(user_input)
        spinner.stop()
        print(f"\nTable Botty: {bot_response}\n")



    
if __name__ == "__main__":
    main()
    #create_connection()