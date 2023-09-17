import streamlit as st
from st_pages import Page, add_page_title, show_pages
from streamlit_extras.switch_page_button import switch_page
from PIL import Image

# Declaring the pages in your app

show_pages(
    [   Page("pages/post-summarizer.py", "Summarizer"),
        Page("pages/home.py", "Home"),
    ]
)
add_page_title()  # Optional method to add title and icon to current page

try:
    switch_page('Summarizer')
except:
    switch_page('summarizer')