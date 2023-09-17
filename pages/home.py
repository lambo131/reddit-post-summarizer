import streamlit as st
from streamlit_extras.switch_page_button import switch_page

page_text = """### How the app works (step by step)

#### 1.0. API key!
Enter your **OpenAI API** key on the side pannel. Sorry or else I will be broke!!!

#### 1.1. Load reddit post
Find your interested reddit page, and paste the url into the "Reddit post url" field

Then, press **"Load Reddit Post"** to scrape the post with a Reddit praw api integration

#### 2. Set discussion filter
you can specify the discussion you want to select explicity by using
- **"select by author":** choose the discussion branches by the commentor's name
- **"select by range":** choose a range of discussions

*note: One Discussion refers to all the content in a first layer/parent comment.*

You can also just choose "all comments", which will select all the discussions (32 max)

#### 3. Check selected Discussions
This isn't necessary, but you can check if the comments loaded are really what you chosed.

#### 4. Generate summary
It is as simple as pressing the **"Generate Summary"** button!

you can view the reponse after the generation process, which is about fifteen seconds

#### 5. Change work bench
You can read and analyze multiple Reddit posts at once!

From the side panel, you can move from post to post in the **"Summarized post"** section

The **work bench** will only save:
- the content you have generated 
- the post you have loaded

#### 6. debug
This is for me hahaha >_<. You can use this if you are contributing to this project on github.

#### 7. change prompt(advanced)
You can change the prompt for the llm inside the web tool core function. 
This means you can customize how the summary is generated. Actually, you can do much more!

!!! you can change anything, but you must keep **{title}** and **{discussion}** in the prompt, as they are the prompt template variable.

For example (will work):

    Write a 500 word satirical news article called:"{title}" 
    based on the following text:{discussion}

For example (will not work):

    Write a 500 word satirical news article based on the following 
    text:{something else}

#### Use you imagination and have fun!!!
"""
contributors = """Team: Adeline Li
      Alexandra Wang
      David Wu
      Jennifer Zhang
"""
cols1 = st.columns(3)
cols1[1].text("creator: Lambo Qin")
cols1[1].text(contributors)
st.markdown("""### Word from creator
This is a summarizer tool for reddit. You can understand the main points of a discussion with one click of a button!
The problem this tool is trying to solve is that some post has thousands of comments, which is impossible for us to read.
This means we cannot get a full picture of the discussion, and only see limited view points.
As a tool to promote information literacy, I hope you to become a better consumer of information and a smarter reader.
""")
if st.button("Try now", type="primary", key="boo"):
    switch_page('summarizer')  

st.markdown(page_text)

cols2 = st.columns(7)
if cols2[3].button("Try now", type="primary",key="foo"):
    switch_page('summarizer')   
