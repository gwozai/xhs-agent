from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common import NoSuchElementException, ElementNotInteractableException
import os
import json

class App:
    def __init__(self):
        self.currentPosts  = []
        self.currentPost = None

        stealth_path = "stealth.min.js"
        with open(stealth_path) as f:
            js = f.read()


        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('lang=zh-CN,zh')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")#就是这一行告诉chrome去掉了webdriver痕迹
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
        self.driver.add_cookie({
            'name': "webId",
            'value': "xxx777",
            'domain': ".xiaohongshu.com",
            'path': "/"
        })
        self.driver.get("https://www.xiaohongshu.com/explore?channel_id=homefeed.fitness_v3")

    def run(self):
        if not self.getSession():
            self.login()
            self.saveSession()
        print("登录完成，即将开始执行任务")
        time.sleep(3)
        run = True
        while True:
            try:
                if run:
                    posts = self.findPostList()
                    for post in posts:
                        self.clickPostDetail(post)
                        self.getCurrentPostDetail()

                        print("本篇笔记已操作完成")
                        time.sleep(3)
                        # return last page
                        self.driver.back()
            except Exception as e:
                print("发生异常: %s" % e)
            finally:
                print("本轮任务结束，等待3秒后刷新")
                run = False
                time.sleep(3)
        
    def getSession(self):
        return False
        if os.path.isfile("cookie"):
            with open("cookie", "r") as f:
                cookies = f.read()
                if cookies:
                    json_cookies = json.loads(cookies)
                    for cookie_item in json_cookies:
                        self.driver.add_cookie(cookie_item)
                    self.driver.refresh()
        return False

    def login(self):
        while True:
            users = self.driver.find_elements(By.CLASS_NAME, "user")    
            if users:
                user = users[0]
                profile_url = user.find_element(By.TAG_NAME, "a")
                print("登录成功，用户主页:", profile_url.get_attribute("href"))
                break
            time.sleep(3)

    def saveSession(self):
        cookies = self.driver.get_cookies()
        with open("cookie", "w") as f: 
            f.write(json.dumps(cookies))

        return True

    def findPostList(self):
        postContainer = self.driver.find_elements(By.ID, "exploreFeeds")
        if not postContainer:
            print("未找到帖子列表")
            return []
        posts = postContainer[0].find_elements(By.CLASS_NAME, "note-item")
        print("找到帖子列表, 数量: %d" % len(posts))
        self.currentPosts = posts
        return posts

    def clickPostDetail(self, post):
        post.click()
        currentUrl = self.driver.current_url
        print("点击帖子, url: %s" % currentUrl)
        self.currentPost = post
        return True

    def getCurrentPostDetail(self):
        titleEl = self.driver.find_elements(By.ID, "detail-title")
        title = ""
        if titleEl:
            title = titleEl[0].text
            print("找到帖子标题, title: %s" % title)
        
        contentEl = self.driver.find_elements(By.ID, "detail-desc")
        content = ""
        if contentEl:
            # 会风险警告
            # inner_text = self.driver.execute_script("return arguments.innerText;", contentEl[0])
            for contentItemEl in contentEl:
                content += contentItemEl.text
                for contentItemItem in contentItemEl.find_elements():
                    content += contentItemItem.text
            print("找到帖子内容, content: %s" % content)

        mediaEL = self.driver.find_elements(By.CLASS_NAME, "note-slider-img")
        media = []
        if mediaEL:
            print("找到帖子媒体, 数量: %d" % len(mediaEL))
            for mediaItemEl in mediaEL:
                if mediaItemEl.is_displayed():
                    print("找到媒体, url: %s" % mediaItemEl.get_attribute("src"))
                    media.append(mediaItemEl.get_attribute("src"))

        return {
            "title": title,
            "content": content,
            "media": media
        }

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
