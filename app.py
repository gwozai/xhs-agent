from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common import NoSuchElementException, ElementNotInteractableException
import os
import json
from local import LocalStorage
from ai import AI
import requests
from PIL import Image
import base64

class App:
    def __init__(self):
        self.currentPosts  = []
        self.currentPost = None
        self.mainPage = 'https://www.xiaohongshu.com/explore?channel_id=homefeed.cosmetics_v3'
        self.ai = AI()

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
        # self.driver.add_cookie({
        #     'name': "webId",
        #     'value': "xxx777",
        #     'domain': ".xiaohongshu.com",
        #     'path': "/"
        # })
        self.driver.get(self.mainPage)
        self.storage = LocalStorage(self.driver)

    def run(self):
        time.sleep(3)
        if not self.getSession():
            self.login()
            self.saveSession()
        print("登录完成，即将开始执行任务")
        run = True
        while True:
            try:
                time.sleep(3)
                if run or True: #如果要控制翻页，则把run改成False
                    posts = self.findPostList()
                    for post in posts:
                        postEl = self.clickPostDetail(post)
                        if postEl:
                            print("开始操作内容")
                            if not postEl.is_displayed():
                                print("元素丢失")
                                continue
                            print("获取内容详情")
                            postDetail = self.getCurrentPostDetail(postEl)
                            print(postDetail)
                            try: 
                                ai_result = self.ai.chat(postDetail)
                            except Exception as e: 
                                print("AI请求异常: %s" % e)
                                time.sleep(10)
                                continue
                            print(ai_result)
                            ai_result = json.loads(ai_result)
                            if ai_result['status'] == 'success': # input("是否操作本篇笔记？(y): "):
                                if ai_result['is_like']: # input("是否点赞本篇笔记？(y/n): ") == "y":
                                    self.like(postEl)
                                    time.sleep(2)
                                if ai_result['is_fav']: # input("是否收藏本篇笔记？(y/n): ") == 'y':
                                    self.fav(postEl)
                                    time.sleep(2)
                                if ai_result['is_comment']:
                                    comment = ai_result['comment']
                                    # comment = input("请输入评论内容：")
                                    if comment:
                                        self.comment(postEl, comment)
                                        time.sleep(2)
                                print("本篇笔记已操作完成")
                                self.driver.back()
                            else:
                                if self.driver.current_url != self.mainPage:
                                    self.driver.back()
                                print("本篇笔记已跳过")

                            # time.sleep(3)
                            # return last page
                        else:
                            print("没有展开笔记详情，稍后重试")
                        time.sleep(3)

            except Exception as e:
                print("发生异常: %s" % e)
                print(e.__traceback__)
            finally:
                print("本轮任务结束，等待5秒后刷新")
                run = False
                time.sleep(5)
                if self.driver.current_url != self.mainPage:
                    self.driver.get(self.mainPage)
                else:
                    reloadEl = self.driver.find_elements(By.CLASS_NAME, "reload")
                    if reloadEl:
                        reloadEl = reloadEl[0]
                        reloadEl.click()    
                    else:
                        self.driver.refresh()
                        
    def getSession(self):
        if os.path.isfile("cookie"):
            with open("cookie", "r") as f:
                cookies = f.read()
                if cookies:
                    json_cookies = json.loads(cookies)
                    for cookie_item in json_cookies:
                        self.driver.add_cookie(cookie_item)
        
        if os.path.isfile("localstorage"):
            with open("localstorage", "r") as f:
                localstorage = f.read()
                if localstorage:
                    json_storage = json.loads(localstorage)
                    for k in json_storage:
                        self.driver.execute_script("localStorage.setItem('%s', '%s')" % (k, json_storage[k]))

        # self.driver.refresh()
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

        local_storage = self.storage.items()
        with open("localstorage", "w") as f:
            f.write(json.dumps(local_storage))

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
        print(post)
        is_video = post.find_elements(By.CLASS_NAME, "play-icon")
        if is_video:
            print("下一个操作笔记是视频，即将跳过")
            return None
        post.click()
        time.sleep(3)
        currentUrl = self.driver.current_url
        print("点击帖子, url: %s" % currentUrl)
        self.currentPost = post
        parent_el = self.driver.find_elements(By.CLASS_NAME, "note-detail-mask")
        if parent_el:
            print("找到帖子详情")
            return parent_el[0]
        else:
            print("未找到帖子详情")
        return None
            
    def getCurrentPostDetail(self, parent_el): 
        titleEl = parent_el.find_elements(By.ID, "detail-title")
        title = ""
        if titleEl:
            title = titleEl[0].text
            print("找到帖子标题, title: %s" % title)
        
        authorEl = self.driver.find_elements(By.CLASS_NAME, "username")
        author = ""
        if authorEl:
            author = authorEl[1].text
            print("找到作者昵称, title: %s" % author)
        
        contentEl = parent_el.find_elements(By.ID, "detail-desc")
        content = ""
        if contentEl:
            # 会风险警告
            inner_text = self.driver.execute_script("return arguments[0].innerText;", contentEl[0])
            content = inner_text
            # for contentItemEl in contentEl:
            #     content += contentItemEl.text
            #     for contentItemItem in contentItemEl.find_elements():
            #         content += contentItemItem.text
            print("找到帖子内容, content: %s" % content)

        mediaEL = parent_el.find_elements(By.CLASS_NAME, "note-slider-img")
        media = []
        if mediaEL:
            print("找到帖子媒体, 数量: %d" % len(mediaEL))
            try:
                for mediaItemEl in mediaEL:
                    if mediaItemEl.is_displayed():
                        print("找到媒体, url: %s" % mediaItemEl.get_attribute("src"))
                        media.append(mediaItemEl.get_attribute("src"))
            except Exception as e:
                print("媒体获取发生异常: %s" % e)
        
        dataEl = parent_el.find_elements(By.CLASS_NAME, "interact-container")
        if not dataEl:
            print("未找到帖子互动数据")
            return {
                "title": title,
                "content": content,
                "media": media
            }
        dataEl = dataEl[0]
        
        like_total_text = ''
        like_totalEl = dataEl.find_elements(By.CLASS_NAME, "like-active")
        if like_totalEl:
            like_total = like_totalEl[0].find_elements(By.CLASS_NAME, "count")
            if like_total:
                like_total_text = like_total[0].text
                print("找到点赞总数, total: %s" % like_total_text)

        fav_total_text = ''
        fav_totalEl = dataEl.find_elements(By.CLASS_NAME, "collect-wrapper")
        if fav_totalEl:
            fav_total = fav_totalEl[0].find_elements(By.CLASS_NAME, "count")
            if fav_total:
                fav_total_text = fav_total[0].text
                print("找到收藏总数, total: %s" % fav_total_text)

        com_total_text = ''
        com_totalEl = dataEl.find_elements(By.CLASS_NAME, "chat-wrapper")
        if com_totalEl:
            com_total = com_totalEl[0].find_elements(By.CLASS_NAME, "count")
            if com_total:
                com_total_text = com_total[0].text
                print("找到评论总数, total: %s" % com_total_text)

        media_path = ""
        if media:
            media_path = self.downloadMedia(media[0])
            with open(media_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        return [
            {
                'type': "image_url",
                "image_url": {
                    "url": f"data:image/webp;base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": json.dumps({
                    "title": title,
                    "author": author,
                    "content": content,
                    # "media": media,
                    "like_count": like_total_text,
                    "fav_count": fav_total_text,
                    "comment_count": com_total_text,
                    "channel": "彩妆"
                })
            }
        ]

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
        dataEl = postDivEl.find_elements(By.CLASS_NAME, "interact-container")
        if not dataEl:
            print("未找到帖子互动数据")
            return False
        dataEl = dataEl[0]
        likeEl = dataEl.find_elements(By.CLASS_NAME, "like-active")
        if likeEl:
            likeEl[0].click()
            print("点赞完成")
            return True
        else: 
            print("没有找到点赞按钮")
        return True
    
    def fav(self, postDivEl):
        dataEl = postDivEl.find_elements(By.CLASS_NAME, "interact-container")
        if not dataEl:
            print("未找到帖子互动数据")
            return False
        dataEl = dataEl[0]
        favEl = dataEl.find_elements(By.CLASS_NAME, "collect-wrapper")
        if favEl:
            favEl[0].click()
            print("收藏完成")
            return True
        else: 
            print("没有找到收藏按钮")
        return True
   
    def comment(self, postDivEl, comment):
        dataEl = postDivEl.find_elements(By.CLASS_NAME, "interact-container")
        if not dataEl:
            print("未找到帖子互动数据")
            return False
        dataEl = dataEl[0]
        comEl = dataEl.find_elements(By.CLASS_NAME, "chat-wrapper")
        if comEl:
            comEl[0].click()
            time.sleep(1)
            print("展开评论")
            try:
                inputEl = postDivEl.find_element(By.ID, "content-textarea")
                inputEl.click()
                # self.driver.execute_script("arguments[0].innerHtml = 'arguments[1]'", inputEl, comment)
                inputEl.send_keys(comment)
                print("输入评论")
                time.sleep(3)
                sendEl = postDivEl.find_element(By.CLASS_NAME, "submit")
                sendEl.click()
                print("发送评论,评论完成")
                return True
            except Exception as e:
                print("评论发生异常: %s" % e)
                return False
        else: 
            print("没有找到评论按钮")
            return False

    def flushPostList(self):
        #todo
        return True

    def downloadMedia(self, media_url, resize = True):
        if not os.path.isdir('media'):
            os.path.mkdir('media')
        file_name = media_url.split('/')[-1]
        media_path = os.path.join('media', file_name)
        if os.path.isfile(media_path):
            print("媒体已存在, 跳过下载")
        else:
            print("开始下载媒体, url: %s" % media_url)
            response = requests.get(media_url)
            with open(media_path, 'wb') as f:
                f.write(response.content)
            print("媒体下载完成, 保存路径: %s" % media_path)

        if not os.path.isfile(media_path):
            print("媒体下载失败")
            return None
        if resize:
            resize_path = self._resizeMedia(media_path)
            if resize_path:
                return resize_path
            else:
                print("媒体缩放失败，用原图")            
        return media_path

    def _resizeMedia(self, media_path):
        image = Image.open(media_path)
        image.save("%s.new.webp" % media_path)
        return "%s.new.webp" % media_path

    def close(self):
        self.driver.close()

app = App()
app.run()
