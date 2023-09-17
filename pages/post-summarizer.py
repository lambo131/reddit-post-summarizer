import streamlit as st
try:
    import sys
    sys.path.insert(0, ".\lib")
    from Bench import Bench
    from CommentScrape import CommentScrapper
    from OutputGeneration import Generator
    from Functions import *
except:
    from lib.Bench import Bench
    from lib.CommentScrape import CommentScrapper
    from lib.OutputGeneration import Generator
    from lib.Functions import *

if "scrapper" not in st.session_state:
    st.session_state.scrapper = CommentScrapper()
if "generator" not in st.session_state:
    st.session_state.generator = Generator()
if "benches" not in st.session_state:
    st.session_state.benches = []
if "current_bench" not in st.session_state:
    st.session_state.current_bench = None
if "seen_post" not in st.session_state:
    st.session_state.seen_post = []
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""


try:
    scrapper = st.session_state.scrapper
except: "no scrapper"
generator = st.session_state.generator
selected_discussions = []
benches = st.session_state.benches
current_bench = st.session_state.current_bench


st.header("-Post Summarizer-")

#--------------url enter
preload_link = ""
if current_bench != None:
    preload_link = current_bench.url
url = st.text_input("Reddit post url",preload_link)


l2_1, l2_2,l2_3 = st.columns(3)
if l2_1.button("Load Reddit Post"):
    scrapper = CommentScrapper()
    post_id = scrapper.get_post_id(url)
    scrapper.get_post_id(url)
    scrapper.extract_discussions(post_id)
    l2_2.text("done!")
    if post_id not in st.session_state.seen_post:
        new_bench = Bench(url, post_id, scrapper.submission.title, scrapper)
        benches.append(new_bench)
        st.session_state.seen_post.append(post_id)
        current_bench = new_bench


#--------------filter settings

if current_bench != None:
    filter_options = [":rainbow[All comments]", "***Select by author***", "Select by range :one:~:eight:"]
    comment_filter = st.radio(
    "**comment filer**",
    filter_options,
    # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."],
    horizontal=True
    )  
    if comment_filter == filter_options[0]:
        pass
    elif comment_filter == filter_options[1]:
        all_authors = []
        deleted_count = 1
        for i, comment in enumerate(current_bench.scrapper.submission.comments):
            if str(comment.author) != "None":
                all_authors.append(f"#{i+1} "+ str(comment.author))
            else:
                all_authors.append(f"#{i+1} Deleted_{deleted_count}")
                deleted_count+=1
        selected_authors = st.multiselect(
                        'Select comment authors',
                        all_authors[:30],[])
    elif comment_filter == filter_options[2]:
        comment_range = st.slider(
                    'Select a range of comments',
                    1, min(30,len(current_bench.scrapper.submission.comments)), (1, 2))

    if comment_filter == filter_options[0]:
        selected_discussions = scrapper.get_all_discussions()
    elif comment_filter == filter_options[1]:
        authors_index_list = []
        for author in selected_authors:
            index = int(author.split(" ")[0][1:])
            authors_index_list.append(index)
        selected_discussions = scrapper.get_discussions_by_index(authors_index_list)
    elif comment_filter == filter_options[2]:
        selected_discussions = scrapper.get_discussions_by_range(comment_range)
else:
    st.write("**comment filer**")
    st.text("   Load Reddit post first!")
#--------------See selected discussions
st.write("**See selected discussion**")
selected_discussions_view = scrapper.view_selected_discussions(selected_discussions)
expander = st.expander("See selected discussions/comments")
expander.text(selected_discussions_view)
# selected_discussions_view = f'<p style="color:white;">{selected_discussions_view}</p>'


#--------------Generate summary
st.divider()
@st.cache_data
def get_summary(title, text, api_key, prompt):
    # api_key for preventing caching skip method on when user change key
    temp = st.empty()
    temp.text("Wait for up to 20 seconds... >.<")
    summary = generator.get_summary(title, text)
    temp.empty()
    return summary

l1_1, l1_2,l1_3 = st.columns(3)
l1_1.subheader("Response:")
if l1_3.button("Generate Summary"):
    if generator.llm != None:
        current_bench.selected_discussions = selected_discussions
        title = scrapper.post_title
        text = scrapper.extract_text(selected_discussions)
        current_bench.summary = get_summary(title, text, st.session_state.user_api_key,generator.active_template)
    else:
        st.write("Please enter your OpenAI API key!!!")

if current_bench != None:    
    summary_text = current_bench.summary
else:
    summary_text = ""

st.markdown(summary_text)

#--------------sidebar api key enter
api_key = st.sidebar.text_input("Your api key")
if api_key != st.session_state.user_api_key:
    generator.initialize_llm(api_key)
    st.session_state.user_api_key = api_key


#--------------sidebar workbench select
buttons_list = {}
st.sidebar.subheader("Summarized posts")
for i, bench in enumerate(benches):
    button = st.sidebar.button(f"#{i+1} {bench.post_title[:50]}...")
    buttons_list[bench.post_id] = button


for i, name in enumerate(buttons_list):
    if buttons_list[name]:
        st.sidebar.write(f"{i} button was clicked, id={name}")
        current_bench = benches[i]
        st.session_state.current_bench = current_bench
        st.experimental_rerun()


#--------------dev options
st.divider()
l3_1, l3_2,l3_3 = st.columns(3)
if l3_1.checkbox("debug"):
    st.write(f"@seen post id: {st.session_state.seen_post}")
    
    #st.text("scrapper.secrets")
    #st.text(f"reddit_secret: {scrapper.secret}")
    #st.text(f"client_id: {scrapper.client_id}")
    #st.text(f"user_agent: {scrapper.user_agent}")
    
    st.write(f"@using admin: {generator.using_admin}")

    st.write(f"@apikey: {st.session_state.user_api_key}")
    st.write("generator.active_template:")
    st.text(generator.active_template)
    expander = st.expander("view comment scrape tree")
    if current_bench != None:  
        expander.text(f"post title: {current_bench.scrapper.post_title}")
        expander.text(f"discussion len: {len(selected_discussions)}")
        for discussion in selected_discussions:
            expander.text(f"new discussion---------------")
            expander.text(f"author: {discussion.author} | "+
                f"Discussion #: {discussion.discussion_num} | "+
                f"char count: {discussion.char_count} | "+
                f"num comments: {discussion.num_comments} | "
            )
            for comment in discussion.grouped_comments:
                pos = "   comment hierarchy: "
                for index in comment.pos:
                    pos += str(index)+" "
                expander.text(pos)

if l3_2.checkbox("change prompt(resets to defualt when turned off)"):
    user_prompt = st.text_area('modify the prompt here:', generator.active_template,height=200)
    if user_prompt != generator.active_template:
        generator.active_template = user_prompt
        st.session_state.generator = generator
        st.experimental_rerun()
else:
    generator.reset_active_template()

if scrapper != None:
    st.session_state.scrapper = scrapper
if generator != None:
    st.session_state.generator = generator
if benches != None:
    st.session_state.benches = benches
if current_bench != None:
    st.session_state.current_bench = current_bench