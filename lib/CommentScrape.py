import praw
from typing import List
import json
import streamlit as st

from lib.Functions import str_token_count
from lib.Functions import*

class CommentScrapper:
    def __init__(self):
        try:
            with open("secrets.txt", "r") as file:
                secrets = json.load(file)
        except:
            secrets = {
                'reddit_secret': st.secrets['openai_api_key'],
                'client_id': st.secrets['client_id'],
                'user_agent': st.secrets['user_agent'],
            }
        self.secrets = secrets['reddit_secret']
        self.client_id = secrets['client_id']
        self.user_agent = secrets['user_agent']

        self.num_comment_layer = [10,10,3,3,3,3,10,10,10,10]
        self.max_depth = 7
        self.token_limit = 7000

        self.submission = None
        self.discussions = []
        # self.selected_discussions = []
        self.post_title = None

        self.debug = False
    
    # interface methods
    def get_post_id(self, url:[str]):
        chunks = url.split('/')
        found = False
        for chunk in chunks:
            if found:
                return chunk
            if chunk == 'comments':
                found = True
        return ""
    def view_selected_discussions(self, discussions):
        output = ""
        for discussion in discussions:
            output+=f"discussion #{discussion.discussion_num}---------------"
            output+=f"author: {discussion.author}\n"
            for comment in discussion.grouped_comments:
                text = f"comment:\n {comment.comment.body}"
                output+=f"{print_str_as_blocks(remove_extra_lines(text), char_limit = 70, indent=1)}\n\n"
            output+="\n\n"+"#"*30+"\n"
        return output

    def extract_text(self, discussions):
        all_content = ""
        for i, discussion in enumerate(discussions):
            block_of_comments = ""
            discussion_num = discussion.discussion_num
            for comment in discussion.grouped_comments:
                comment_str=comment.comment.body
                block_of_comments+=remove_extra_lines("{"+comment_str)+"}\n\n"
            seperator_a = f"**Begining discussion {discussion_num}\n"
            seperator_b = f"**End of discussion {discussion_num}\n\n"
            all_content+=seperator_a+block_of_comments+seperator_b
        return all_content
    
    def scrape_post(self, post_id):
        # ------get post submission
        reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.secret,
            user_agent=self.user_agent
        )
        self.submission = reddit.submission(id=post_id)
        return self.submission
    
    def extract_discussions(self, post_id):
        self.scrape_post(post_id)
        self.discussions = self.group_comments(self.scrape_comments())
        return self.discussions
    
    def get_all_discussions(self):
        return self.discussions
    
    def get_discussions_by_author(self, authors:List[str]):
        # returns scrapped discussions of the list of authors
        selected_discussions = []
        discussions = self.discussions
        for discussion in discussions:
            if discussion.author in authors:
                selected_discussions.append(discussion)
        return selected_discussions

    def get_discussions_by_range(self, range:List[int]):
        # returns scrapped discussions of selected index
        selected_discussions = self.discussions[range[0]-1:range[1]]
        return selected_discussions
    
    def get_discussions_by_index(self, indexes:List[int]):
        selected_discussions = []
        discussions = self.discussions
        for i, discussion in enumerate(discussions):
            if i+1 in indexes:
                selected_discussions.append(discussion)
        return selected_discussions

    # private methods
    
    def scrape_comments(self):
        dp = DebugPrinter(working=self.debug)
        submission = self.submission
        if type(submission) == None:
            return "No post submittion retrieved!"
        self.post_title = submission.title

        # ------scrape post
        terminate = False
        total_token_count = 0
        # token_limit = 7000 # leave room for the ~8000 token limit
        queue = []
        queue_set_pointer = 1 # scrape first layer comments by sets of 10s
        back_up_queue = []
        scraped_comments = []
        # num_comment_layer = [10,10,3,3,3,3,10,10,10,10]
        # max_depth = 7
        depth = 0

        while not terminate:
            dp.dprint(f"depth: {depth}, queue len: {len(queue)}")
            indent = "| "*depth
            next_queue = []

            if len(queue) == 0:
                if len(back_up_queue) > 0:
                    dp.dprint("#\n"*3+"."*10+f"scraping backup queue #{len(back_up_queue)}")
                    queue = back_up_queue
                    back_up_queue = []
                else:
                    depth = 0
                    indent = "| "*depth
                    for i in range((queue_set_pointer-1)*self.num_comment_layer[0],
                                (queue_set_pointer)*self.num_comment_layer[0]):
                        if i >= len(submission.comments):
                            terminate = True
                            break
                        comment = self.MyComment(submission.comments[i], [i+1], depth)
                        queue.append(comment)
                    queue_set_pointer+=1

            for i, que in enumerate(queue):
                # scrape queued comments
                try:
                    body = que.comment.body
                except:
                    dp.dprint("")
                    continue

                this_comment = que.comment
                dp.dprint(f"{indent} this comment pos: {que.pos}, total_token_before: {total_token_count}")  
                dp.dprint(f"{indent} comment: {body[:20]}...")
                scraped_comments.append(que)
                token_count = str_token_count(this_comment.body)
                total_token_count+=token_count

                if total_token_count > self.token_limit:
                    terminate = True
                    break
                try:
                    replies = this_comment.replies
                except:
                    dp.dprint("")
                    continue
                if depth>=self.max_depth:
                    dp.dprint("")
                    continue
                
                # add new comments to queue
                for j, reply in enumerate(this_comment.replies):
                    dp.dprint(f"{indent} reply # {j}") 
                    reply_pos = que.pos.copy()
                    reply_pos.append(j+1)
                    queued_comment = self.MyComment(reply, reply_pos, depth)
                    if j+1 <= self.num_comment_layer[depth+1]:
                        dp.dprint(" *queued")
                        next_queue.append(queued_comment)
                    else:
                        dp.dprint("")
                        back_up_queue.append(queued_comment)
                dp.dprint("")

            queue = next_queue
            depth+=1
        return scraped_comments
        

    def group_comments(self, group, depth=0):
        dp = DebugPrinter(working=self.debug)
        discussions = []
        seen_discussion = []
        dp.dprint(f"\n\ndepth: {depth}")
        indent = "| "*depth
        this_group = []
        added_comments = [] # ones no need to sort anymore
        for comment in group:
            this_group = []
            if depth >= len(comment.pos):
                dp.dprint("...... adding comment to discussion, depth > len(comment.pos)")
                dp.dprint(f"{indent}added comment pos: {comment.pos}")
                added_comments.append(comment)
                discussions.append(comment)
                continue

            discussion_num = comment.pos[depth]
            if discussion_num in seen_discussion:
                continue

            dp.dprint(f"\n{indent}####searching for group #{discussion_num} pos: {comment.pos}")
            for comment in group:
                if depth >= len(comment.pos):
                    continue
                if comment.pos[depth] == discussion_num:
                    dp.dprint(f"{indent}appending discussion: {comment.pos}")
                    this_group.append(comment)
            
            dp.dprint("this group:")
            for skipped_comment in added_comments:
                dp.dprint(skipped_comment.pos)
            for comment in this_group:
                dp.dprint(comment.pos)
            if depth == 0:
                grouped_comments = self.group_comments(this_group, depth=depth+1)
                discussion = self.Discussion(grouped_comments)
                discussions.append(discussion)
            else:
                discussions.extend(self.group_comments(this_group, depth=depth+1))
            seen_discussion.append(discussion_num) 
            dp.dprint(f"discussion len {len(discussions)}")

            # force break (testing only)
            if depth == 0:
                dp.dprint("*"*20+"finished a first layer comment")
                # break
        
        dp.dprint("*"*20+f"\nend of discussion branch {depth}\
            discussion num #{len(discussions)}")
        if len(discussions) == 0:
            for comment in group:
                dp.dprint(f"this_group: {comment.pos}")
            return group
        
        return discussions
    

    # Sub Classes

    class MyComment:
        def __init__(self, comment, pos, depth):
            self.comment = comment
            self.pos = pos
            self.depth = depth
        
    class Discussion:
        def __init__(self, grouped_comments):
            self.grouped_comments = grouped_comments
            self.author = str(grouped_comments[0].comment.author)
            self.discussion_num = grouped_comments[0].pos[0]
            self.num_comments = len(grouped_comments)
            self.char_count = self.get_char_count()

        def get_char_count(self):
            count = 0
            for my_comment in self.grouped_comments:
                str = my_comment.comment.body
                count+=len(str)
            return count