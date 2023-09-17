import tiktoken

def print_str_as_blocks(str, char_limit=70, indent=0) -> str:
    line = "  "*indent
    output = ""
    for char in str:
        if char == "\n":
            output+=line+'\n'
            line = "  "*indent
            continue
                
        if len(line) > char_limit and char == " ":
            output+=line+"\n"
            line = "  "*indent
            continue
        line+=char
    if len(line) > 0:
        output+=line
    # print(output)
    return output

def remove_extra_lines(str):
        temp = ""
        repeat_nline = 0
        # remove extra lines
        for i in str:
            if i == "\n":
                if repeat_nline <= 1:
                    repeat_nline+=1
                    temp += i
                else:
                    continue
            else:
                if i != " ":
                    repeat_nline = 0
                temp += i
                continue
        return temp

def str_token_count(str):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(str))

class DebugPrinter:
    def __init__(self, working=False):
        self.working = working

    def dprint(self, str, end='\n'):
        if self.working:
            print(str, end=end)