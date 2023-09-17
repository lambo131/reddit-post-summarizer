
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
# from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import textwrap
import streamlit as st

import json
from lib.Functions import*

class Generator:
    def __init__(self):
        self.llm = None
        self.active_template = template_2 # just a string
        self.using_admin = False

    def initialize_llm(self, api_key):
        try:
            with open("secrets.txt", "r") as file:
                secrets = json.load(file)
        except:
            secrets = {
                'openai_api_key': st.secrets['openai_api_key'],
                'admin_name': st.secrets['admin_name'],
            }
        if api_key == secrets['admin_name']:
            openai_api_key = secrets['openai_api_key']
            self.using_admin = True
        else:
            openai_api_key = api_key
            self.using_admin = False
        self.llm = OpenAI(temperature = 0.7, model_name="gpt-3.5-turbo-16k",openai_api_key=openai_api_key)
    
    def get_summary(self, title, text):
        text = text[:7500] # set token limit
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=10)
        docs = text_splitter.create_documents([text])
        prompt_template = PromptTemplate(
            input_variables=["discussion","title"],
            template=self.active_template,
        )              
        prompt = prompt_template.format(discussion=docs, title=title)
        try:
            response = self.llm(prompt)
            response = print_str_as_blocks(response, char_limit = 70)
        except:
            return "error with OpenAI API, maybe due to wrong API key entered..."
        return response

    def reset_active_template(self):
        self.active_template = template_2


template_1 = """
Write a summary of the following reddit discussion. 
Highlight differnt opinions and perspectives.
Here are the discussions:
{discussion}
"""
template_2 = """Generate a overview of a Reddit post called "{title}" based on all the comments. 
The overview should include a summary and an reflection
description for the summary: A point-form list summary of the discussion in detail. 
Write another paragraph to highlight different opinions and diverse voices.
descrption for the reflection: Write a reflection on the discussion you just read. 
Think critically and elaborate on your thoughts on the arguments.
Format your response in markdown.
Here are the comments:
{discussion}
Again, output the following:
- summary:
- paragraph highlighting different opinions:
- reflection:"""

template_3 ="""Generate a one sentence overview of a Reddit post called "{title}" based on all the comments. 
Here are the comments:
{discussion}
"""