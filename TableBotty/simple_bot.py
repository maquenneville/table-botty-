# -*- coding: utf-8 -*-
"""
Created on Thu May 18 12:22:23 2023

@author: marca
"""

import openai
from openai import OpenAI
import time
import configparser
import tiktoken
import json

class SimpleBot:
    
    def __init__(self, primer, model="gpt-4-turbo-preview"):
        self.openai_api_key = self._get_api_keys("config.ini")
        openai.api_key = self.openai_api_key
        self.model = model
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.client = OpenAI(api_key=self.openai_api_key)
        if isinstance(primer, list):
            self.primer = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
            for message in primer:
                self.primer.append({"role": "user", "content": message})
        else:
            self.primer = [
                {"role": "system", "content": primer},
            ]

    def _get_api_keys(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        openai_api_key = config.get("API_KEYS", "OpenAI_API_KEY")
        return openai_api_key

    def _count_tokens(self, text):
        tokens = len(self.encoding.encode(text))
        return tokens

    def _generate_response(
        self,
        messages,
        function_desc=None,
        temperature=0.5,
        n=1,
        max_tokens=4000,
        frequency_penalty=0,
        stream=False
    ):
        token_ceiling = 4096
# =============================================================================
#         if self.model == "gpt-4":
#             max_tokens = 8000
#             token_ceiling = 8000
#         if self.model == "gpt-3.5-turbo-16k" or self.model == "gpt-3.5-turbo-0125" or self.model == "gpt-3.5-turbo-1106":
#             max_tokens = 16000
#             token_ceiling = 16000
#         if self.model == "gpt-4-turbo-preview":
#             max_tokens = 100000
#             token_ceiling = 100000
# =============================================================================
    
        tokens_used = sum([self._count_tokens(msg["content"]) for msg in messages])
        tokens_available = token_ceiling - tokens_used
    
        max_tokens = min(max_tokens, (tokens_available - 100))
    
        if tokens_used + max_tokens > token_ceiling:
            max_tokens = token_ceiling - tokens_used - 10
    
        if max_tokens < 1:
            max_tokens = 1
    
        max_retries = 10
        retries = 0
        backoff_factor = 1  # Initial sleep time factor
    
        while retries < max_retries:
            
            try:
                completion_params = {
                    "model": self.model,
                    "messages": messages,
                    "n": n,
                    "temperature": temperature,
                    #"max_tokens": max_tokens,
                    "frequency_penalty": frequency_penalty,
                    "stream": stream
                }
                if function_desc is not None:
                    completion_params["functions"] = function_desc
    
                completion = self.client.chat.completions.create(**completion_params)
    
                response = completion
                return response
            except Exception as e:
                print(e)
                retries += 1
                sleep_time = backoff_factor * (2 ** retries)  # Exponential backoff
                print(f"Server overloaded, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
        print("Failed to generate prompt after max retries")
        return



    def smart_agent(self):
        self.model = "gpt-4"

    def fast_agent(self):
        self.model = "gpt-3.5-turbo-0125"
        
    def long_agent(self):
        self.model = "gpt-3.5-turbo-16k"

    def add_primer(self, primer_text):
        self.primer.append({"role": "user", "content": primer_text})

    def chat(self, input_string: str, context_chunks: list=None):
        # Create a local copy of self.primer
        messages = self.primer.copy()

        # Append new user message
        messages.append({"role": "user", "content": f"{input_string}"})
        
        if context_chunks:
            
            memories = [{"role": "user", "content": f"Context:\n{context}"} for context in context_chunks]
            messages.extend(memories)
            
        response = self._generate_response(messages, temperature=0.1)

        return response
    
    def stream_chat(self, input_string: str, context_chunks: list=None):
        
        # Create a local copy of self.primer
        messages = self.primer.copy()

        # Append new user message
        messages.append({"role": "user", "content": f"{input_string}"})
        
        if context_chunks:
            
            memories = [{"role": "user", "content": f"Context:\n{context}"} for context in context_chunks]
            messages.extend(memories)
            
        response = self._generate_response(messages, temperature=0.1, stream=True)

        return response

# =============================================================================
# normal_summary = "You are my Policy Document Summary Assistant.  Your job is to take all or part of a policy document, and trim it down into a summary.  Maintain all important details, while attempting to keep the summary as short as possible.  You must respond with a summary, and only a summary, no explanatory text or pleasantries."
# detailed_summary = "You are my Court Document Summary Assistant.  Your job is to take all or part of a policy document, and to create a highly detailed summary.  Do not worry about length. Maintain all details, including all findings, evidence and arguments, all actions by the defendant and important events and dates.  You must respond with a summary, and only a summary, no explanatory text or pleasantries."
# evidence_summary = "You are my Court Document Findings Assistant.  Your job is to take all or part of a legal document, and to create a highly detailed summary of the findings of fact and actions taken by the subject of the investigation on the day in question.  Do not worry about length. Maintain all details pertaining to the actions of the subject on on Jan. 6th and the days surrounding it.  You must respond with a summary, and only a summary, no explanatory text or pleasantries."
# 
# class ProjSummaryBot(SimpleBot):
#     
#     def __init__(self, page_texts_file, model="gpt-4-turbo-preview"):
#         super().__init__( primer=evidence_summary, model=model)
#         print("Initializing project pages and summary groups...")
#         self.page_texts = self._read_array_from_file_json(page_texts_file)
#         self.groups = self.group_doc_pages()
#         self.group_summaries = []
#         print("Initialization complete")
# 
#     def group_doc_pages(self, max_token_length=2000):
#         """
#         Groups an array of page text values into text blocks based on a maximum token length.
#         
#         Args:
#             page_texts (list): An array of page text values.
#             max_token_length (int): The maximum token length for a text block.
#             
#         Returns:
#             list: An array of text blocks, each within the specified token limit.
#         """
#         grouped_pages = []
#         current_group = ""
#         
#         for page_text in self.page_texts:
#             # Check if adding the current page to the current group would exceed the token limit
#             if self._count_tokens(current_group + page_text) > max_token_length:
#                 # If so, and the current group isn't empty, add it to the groups and start a new one
#                 if current_group:
#                     grouped_pages.append(current_group.strip())
#                     current_group = page_text
#                 else:
#                     # If the current group is empty (a single page exceeds the limit), add the page directly
#                     grouped_pages.append(page_text)
#             else:
#                 # If not, add the current page to the current group
#                 current_group += " " + page_text
#         
#         # Add the last group if it's not empty
#         if current_group:
#             grouped_pages.append(current_group.strip())
#         
#         return grouped_pages
#     
#     def _read_array_from_file_json(self, file_path):
#         """
#         Reads a text file back into an array using JSON format.
#         
#         Args:
#             file_path (str): The path to the file to read from.
#             
#         Returns:
#             list: An array where each element is a line from the file.
#         """
#         with open(file_path, 'r', encoding='utf-8') as file:
#             array = json.load(file)
#         return array
#     
#     def _save_array_to_file_json(self, array, file_path):
#         """
#         Saves an array to a text file using JSON format.
#         
#         Args:
#             array (list): The array to save.
#             file_path (str): The path to the file where the array should be saved.
#         """
#         with open(file_path, 'w', encoding='utf-8') as file:
#             json.dump(array, file)
# 
#     def _summarize_text(self, input_string: str):
#         # Create a local copy of self.primer
#         messages = self.primer.copy()
#         
#         # Append new user message
#         messages.append({"role": "user", "content": f"Text to summarize: {input_string}"})
#         
#         response = self._generate_response(messages, temperature=0.1)
#         print(response)
#         
#         return response.choices[0].message.content
# 
#     def summarize_page_groups(self):
#         """
#         Summarizes each group of page texts in self.summary_groups.
#         
#         Returns:
#             list: An array of summaries, one for each group in self.summary_groups.
#         """
#         summaries = []
#         for group in self.groups:
#             print("Summarizing group...")
#             summary = self._summarize_text(group)
#             summaries.append(summary)
#             print("Summary complete")
#             
#         self.group_summaries = summaries
#         self._save_array_to_file_json(self.group_summaries, file_path='summary_groups.json')
#         print("Summaries saved to 'summary_groups.json'")
#         return summaries
# =============================================================================


# =============================================================================
# simple = SimpleBot("You are a helpful assistant")
# 
# print(simple.chat("""You are an expert marketing strategist. You're helping someone who works in brand strategy and specialises in helping solopreneurs find a market positioning that's both pragmatic and fulfilling. 
# 
# They are building the following offer. 
# 
# Offer name: Strategy Sounding Boards
# Offer type: 1-1 Consultation
# Offer transformation: Clients go from confused, fed up and unsure of how to move forwards, to having clarity on their offers, a clear understanding of their brand positioning, as well as a renewed sense of purpose, energy and inspiration in their business. 
# Offer process: This is a 90-min call. Before the call, clients fill out some answers to a few questions about their business. This is really about them sharing their thoughts and feelings, as well as some practical info on their current brand presence as well as key competitors. On the call, we discuss their business from a pragmatic sense first (is their offer strategy feasible for them, the market and their earnings goals) and we move through an understanding of their audience through to how they might compete and position themselves to stand out. 
# Offer features: A brand strategy doing (light) market research for your business; a transcript and recording of the call; a summary of outcomes and action points as a follow up. 
# Offer benefits: Clarity, inspiration, ideation fun and renewed hope - it's great for business owners to just be able to talk full bore about their business without the other person glazing over! Instead, they get a brand strategist who loves learning about small businesses, and helps them analyse, brainstorm and ideate away so we can unravel some of the knottiest issues and questions they're facing. 
# 
# For the following audience: 
# 'Building stage' service business owners who have had some success with selling their offers, but are struggling to turn that success into consistent, financially meaningful success or are struggling to scale successfully. 
# 
# It solves these problems for them: 
# Indecision about their next steps
# Confusion at the amount of directions they might go in
# Inability to see their business with clear eyes
# Struggling to be consistent, confident or efficient with their marketing
# 
# And meets these desires: 
# 
# Feeling like they have a sense of purpose and direction in their business
# Matching their goals and dreams with the market to create a compelling and sustainable business direction and positioning strategy
# Getting clear direction for their marketing and content creation
# Feeling more confident and inspired in their business
# 
# But they might have these objections to taking up the offer: 
# 
# They don't think their business can really be fixed in 90 mins
# They don't want to spend money if they don't feel like they're growing already
# They don't think they'll get anything tangible from it. 
# 
# 
# 
# AWARENESS
# You are currently putting together their buyer journey. The first stage of this journey is awareness, where the potential audience becomes aware that they have a problem related to the above offer.
# 
# Please use your marketing expertise to create a buyer journey overview for the Awareness stage. 
# The format is below: 
# 
# ***Format***
# 
# Begin your response with: 
# 
# In the Awareness part of their buyer journey, your buyers are...
# 
# and then complete it with the answers to the following questions in the sections & format suggested:
# 
# ***Feeling***
# Question: What are they feeling when they become problem aware? 
# *Experiential Overview*: A brief experiential overview of their feelings
# *Emotions* a short list of key emotions at this stage. 
# 
# ***Doing***
# Question: What are they doing when they become problem aware? 
# *Experiential Overview*: A brief experiential overview of what they might be doing to become problem aware *Actions*: a short list of key actions at this stage. 
# 
# ***Thinking***
# Question: What are they thinking when they become problem aware? 
# *Experiential Overview* A brief experiential overview of what they might be thinking as they become problem aware 
# *Thoughts*: a short list of key questions, thoughts or ideas at this stage. 
# 
# ***What they need to move to the next stage***
# *Overview* Please explain what would need to happen for this audience to feel ready to move to the next stage, which is  'Consideration' (e.g. searching for and researching solutions). 
# 
# ******OUTPUT TONE******
# Our tone of voice is conversational and relatable. We aim to connect with our audience on a personal level, sharing stories and memories that resonate with them. We sprinkle our language with humor and use specific, vivid descriptions to make our point. While we don't shy away from expressing our opinions, we do so in a friendly and approachable manner. We seek to engage with our audience and provide practical advice or recommendations. Our tone is efficient and straightforward, without wasting time on unnecessary fluff. We value authenticity and aim to build trust with our readers through genuine experiences and recommendations.
# 
# Consider perplexity and burstiness when creating the buyer journey, ensuring consistent levels of both without losing specificity or context. Write in a conversational style as written by a human: use an informal tone, use personal pronouns, use the active voice, keep language simple and avoid latinate words and jargon if there is a more simple alternative. Use sentence case for any titles. Do not make things up. Do not include any other information.
# 
# 
# CONSIDERATION
# You are currently putting together their buyer journey. The second stage of this journey is consideration, where the potential audience becomes solution aware in terms of the problem related to the above offer.
# 
# Please use your marketing expertise to create a buyer journey overview for the Consideration stage. 
# The format is below: 
# 
# ***Format***
# 
# Begin your response with: 
# 
# In the Consideration part of their buyer journey, your buyers are...
# 
# and then complete it with the answers to the following questions in the sections & format suggested:
# 
# ***Feeling***
# Question: What are they feeling when they become solution aware? 
# *Experiential Overview*: A brief experiential overview of their feelings
# *Emotions* a short list of key emotions at this stage. 
# 
# ***Doing***
# Question: What are they doing when they become solution aware? 
# *Experiential Overview*: A brief experiential overview of what they might be doing to become solution aware *Actions*: a short list of key actions at this stage. 
# 
# ***Thinking***
# Question: What are they thinking when they become solution aware? 
# *Experiential Overview* A brief experiential overview of what they might be thinking as they become solution aware 
# *Thoughts*: a short list of key questions, thoughts or ideas at this stage. 
# 
# ***What they need to move to the next stage***
# *Overview* Please explain what would need to happen for this audience to feel ready to move to the next stage, which is  'Decision' (e.g. choosing to purchase a solution). 
# 
# ******OUTPUT TONE******
# Our tone of voice is conversational and relatable. We aim to connect with our audience on a personal level, sharing stories and memories that resonate with them. We sprinkle our language with humor and use specific, vivid descriptions to make our point. While we don't shy away from expressing our opinions, we do so in a friendly and approachable manner. We seek to engage with our audience and provide practical advice or recommendations. Our tone is efficient and straightforward, without wasting time on unnecessary fluff. We value authenticity and aim to build trust with our readers through genuine experiences and recommendations.
# 
# Consider perplexity and burstiness when creating the buyer journey, ensuring consistent levels of both without losing specificity or context. Write in a conversational style as written by a human: use an informal tone, use personal pronouns, use the active voice, keep language simple and avoid latinate words and jargon if there is a more simple alternative. Use sentence case for any titles. Do not make things up. Do not include any other information.
# 
# DECISION
# You are currently putting together their buyer journey. The third stage of this journey is decision, where the potential audience becomes ready to make a decision to solve the problem related to the above offer.
# 
# Please use your marketing expertise to create a buyer journey overview for the Decision stage. 
# The format is below: 
# 
# ***Format***
# 
# Begin your response with: 
# 
# In the Decision part of their buyer journey, your buyers are...
# 
# and then complete it with the answers to the following questions in the sections & format suggested:
# 
# ***Feeling***
# Question: What are they feeling as they make their decision? 
# *Experiential Overview*: A brief experiential overview of their feelings
# *Emotions* a short list of key emotions at this stage. 
# 
# ***Doing***
# Question: What are they doing as they make their decision? 
# *Experiential Overview*: A brief experiential overview of what they might be doing to make their decision
#  *Actions*: a short list of key actions at this stage. 
# 
# ***Thinking***
# Question: What are they thinking as they make their decision? 
# *Experiential Overview* A brief experiential overview of what they might be thinking as they make their decision 
# *Thoughts*: a short list of key questions, thoughts or ideas at this stage. 
# 
# ***What they need to move to the next stage***
# *Overview* Please explain what would need to happen for this audience to feel ready to move to the next stage, which is Service (e.g. they are ready to use the service).
# 
# ******OUTPUT TONE******
# Our tone of voice is conversational and relatable. We aim to connect with our audience on a personal level, sharing stories and memories that resonate with them. We sprinkle our language with humor and use specific, vivid descriptions to make our point. While we don't shy away from expressing our opinions, we do so in a friendly and approachable manner. We seek to engage with our audience and provide practical advice or recommendations. Our tone is efficient and straightforward, without wasting time on unnecessary fluff. We value authenticity and aim to build trust with our readers through genuine experiences and recommendations.
# 
# Consider perplexity and burstiness when creating the buyer journey, ensuring consistent levels of both without losing specificity or context. Write in a conversational style as written by a human: use an informal tone, use personal pronouns, use the active voice, keep language simple and avoid latinate words and jargon if there is a more simple alternative. Use sentence case for any titles. Do not make things up. Do not include any other information.
# 
# SERVICE
# You are currently putting together their buyer journey. The fourth stage of this journey is service, where the potential audience becomes ready to use the provided surface.
# 
# Please use your marketing expertise to create a buyer journey overview for the Service stage. 
# The format is below: 
# 
# ***Format***
# 
# Begin your response with: 
# 
# In the Service part of their buyer journey, your buyers are...
# 
# and then complete it with the answers to the following questions in the sections & format suggested:
# 
# ***Feeling***
# Question: What are they feeling as they use this service? 
# *Experiential Overview*: A brief experiential overview of their feelings
# *Emotions* a short list of key emotions at this stage. 
# 
# ***Doing***
# Question: What are they doing as they use this service? 
# *Experiential Overview*: A brief experiential overview of what they might be doing as they use this service
#  *Actions*: a short list of key actions at this stage. 
# 
# ***Thinking***
# Question: What are they thinking as they use this service? 
# *Experiential Overview* A brief experiential overview of what they might be thinking as they use this service 
# *Thoughts*: a short list of key questions, thoughts or ideas at this stage.
# 
# ***What they need to move to the next stage***
# *Overview* Please explain what would need to happen for this audience to feel ready to move to the next stage, which is Retention (e.g. they are ready to be nurtured into becoming a loyal customer and advocate).
# 
# ******OUTPUT TONE******
# Our tone of voice is conversational and relatable. We aim to connect with our audience on a personal level, sharing stories and memories that resonate with them. We sprinkle our language with humor and use specific, vivid descriptions to make our point. While we don't shy away from expressing our opinions, we do so in a friendly and approachable manner. We seek to engage with our audience and provide practical advice or recommendations. Our tone is efficient and straightforward, without wasting time on unnecessary fluff. We value authenticity and aim to build trust with our readers through genuine experiences and recommendations.
# 
# Consider perplexity and burstiness when creating the buyer journey, ensuring consistent levels of both without losing specificity or context. Write in a conversational style as written by a human: use an informal tone, use personal pronouns, use the active voice, keep language simple and avoid latinate words and jargon if there is a more simple alternative. Use sentence case for any titles. Do not make things up. Do not include any other information.
# 
# RETENTION
# You are currently putting together their buyer journey. The last stage of this journey is Retention, where the potential audience becomes ready to be nurtured into becoming a loyal customer and advocate.
# 
# Please use your marketing expertise to create a buyer journey overview for the Retention stage. 
# The format is below: 
# 
# ***Format***
# 
# Begin your response with: 
# 
# In the Retention part of their buyer journey, your buyers are...
# 
# and then complete it with the answers to the following questions in the sections & format suggested:
# 
# ***Feeling***
# Question: What are they feeling as they become a loyal customer? 
# *Experiential Overview*: A brief experiential overview of their feelings
# *Emotions* a short list of key emotions at this stage. 
# 
# ***Doing***
# Question: What are they doing as they become a loyal customer? 
# *Experiential Overview*: A brief experiential overview of what they might be doing as they become a retained, loyal customer
#  *Actions*: a short list of key actions at this stage. 
# 
# ***Thinking***
# Question: What are they thinking as they become a loyal customer? 
# *Experiential Overview* A brief experiential overview of what they might be thinking as they become a loyal customer 
# *Thoughts*: a short list of key questions, thoughts or ideas at this stage. 
# 
# ******OUTPUT TONE******
# Our tone of voice is conversational and relatable. We aim to connect with our audience on a personal level, sharing stories and memories that resonate with them. We sprinkle our language with humor and use specific, vivid descriptions to make our point. While we don't shy away from expressing our opinions, we do so in a friendly and approachable manner. We seek to engage with our audience and provide practical advice or recommendations. Our tone is efficient and straightforward, without wasting time on unnecessary fluff. We value authenticity and aim to build trust with our readers through genuine experiences and recommendations.
# 
# Consider perplexity and burstiness when creating the buyer journey, ensuring consistent levels of both without losing specificity or context. Write in a conversational style as written by a human: use an informal tone, use personal pronouns, use the active voice, keep language simple and avoid latinate words and jargon if there is a more simple alternative. Use sentence case for any titles. Do not make things up. Do not include any other information."""))
# 
# =============================================================================
