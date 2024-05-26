# -*- coding: utf-8 -*-
"""
Created on Tue May 21 23:51:01 2024

@author: marca
"""

import configparser
import os

# Create a ConfigParser instance
config = configparser.ConfigParser()
config.read('config.ini')

# Extract API key
OPENAI_API_KEY = config.get('API_KEYS', 'OpenAI_API_KEY')

# Extract database type
DATABASE_TYPE = config.get('database', 'type').lower()

# Extract database configurations based on the type
if DATABASE_TYPE == 'postgresql':
    DB_USER = config.get('postgresql', 'user')
    DB_PASSWORD = config.get('postgresql', 'password')
    DB_NAME = config.get('postgresql', 'dbname')
    DB_HOST = config.get('postgresql', 'host')
    DB_PORT = config.get('postgresql', 'port')
elif DATABASE_TYPE == 'mysql':
    DB_USER = config.get('mysql', 'user')
    DB_PASSWORD = config.get('mysql', 'password')
    DB_NAME = config.get('mysql', 'dbname')
    DB_HOST = config.get('mysql', 'host')
    DB_PORT = config.get('mysql', 'port')
elif DATABASE_TYPE == 'sqlite':
    DB_NAME = config.get('sqlite', 'dbname')


# Get the directory of the main script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the full, system-independent path to the workspace
GPT_WORKSPACE = os.path.join(script_dir, "gpt_workspace")

