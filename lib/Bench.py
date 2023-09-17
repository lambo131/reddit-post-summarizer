class Bench:
    def __init__(self, url, post_id, post_title, scrapper):
        self.post_id = post_id
        self.post_title = post_title
        self.url = url
        self.scrapper = scrapper
        self.submission = None
        self.selected_discussions = []
        self.summary = ""