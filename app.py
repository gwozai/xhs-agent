from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common import NoSuchElementException, ElementNotInteractableException

class App:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.currentPosts  = []
        self.driver.get("https://www.xiaohongshu.com/explore?channel_id=homefeed.fitness_v3")

    def run(self):
        self.login()

    def login(self):
        while True:
            users = self.driver.find_elements(By.CLASS_NAME, "user")    
            if users:
                user = users[0]
                profile_url = user.find_element(By.TAG_NAME, "a")
                print("登录成功，用户主页:", profile_url.get_attribute("href"))
                break
            time.sleep(3)

    def findPostList(self):
        postContainer = self.driver.find_elements(By.ID, "exploreFeeds")
        if not postContainer:
            print("未找到帖子列表")
            return []
        posts = postContainer[0].find_elements(By.CLASS_NAME, "note-item")
        print("找到帖子列表, 数量: %d" % len(posts))
        self.currentPosts = posts
        return posts

    def readPostDetail(self, id):
        post = None
        for postEl in self.currentPosts:
            first_div = postEl.find_element(By.TAG_NAME, "div")
            first_a = first_div.find_element(By.TAG_NAME, 'a')
            if first_a.get_attribute("href").find(id) != -1:
                print("找到帖子, id: %s" % id)
                post = first_div
                break
        
        if not post:
            print("未找到帖子, id: %s" % id)
            return {}
        post.click()
        return post

    def like(self, postDivEl):

        #todo
        return True
    
    def comment(self, id):
        #todo
        return True

    def closePostDetail(self, id):
        #todo
        return True

    def flushPostList(self):
        #todo
        return True

    def close(self):
        self.driver.close()

app = App()
app.run()
