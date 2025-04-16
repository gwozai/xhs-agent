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
import signal
import sys
import random

class App:
    def __init__(self):
        self.currentPosts  = []
        self.currentPost = None
        self.actionDo = True #是否真实操作 还是模拟测试
        self.doVideoNote = True #视频笔记是否操作
        self.runPage = [
            'https://www.xiaohongshu.com/explore',  
        ]
        self.pageRunTime = 10 #每个页面运行次数
       
        self.ai = AI()
        self.session = requests.session()

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
        self.driver.get('https://www.xiaohongshu.com/explore')
        self.storage = LocalStorage(self.driver)

    def run(self):
        time.sleep(5)
        print("开始从缓存获取数据")
        if not self.getSession():
            print("已调用完毕自动登录，如果长时间没动静，请手动刷新页面，还没有登录状态则手动登录或重新运行程序...")
            self.login()
            self.saveSession()

        print("登录完成，即将开始执行任务")
        run = True
        while True:
            for page in self.runPage:
                self.driver.get(page)
                time.sleep(5)
                for i in range(self.pageRunTime):
                    print("开始第%s次操作: %s" % (i+1, page))
                    try:
                        time.sleep(random.randint(3, 10)) #单篇笔记操作间隔
                        if run or True: #如果要控制翻页，则把run改成False
                            posts = self.findPostList()
                            for post in posts:
                                id = self.getCurrentPostId(post)
                                if id and self.isHistoryNote(id):
                                    print("本篇笔记已操作过，跳过")
                                    continue
                                else:
                                    print("本篇笔记未操作过，开始操作")
                                postEl = self.clickPostDetail(post)
                                if postEl:
                                    print("开始操作内容")
                                    if not postEl.is_displayed():
                                        print("元素丢失")
                                        continue
                                    
                                    print("获取内容详情")
                                    postDetail = self.getCurrentPostDetail(postEl)
                                    # print(postDetail)
                                    try: 
                                        ai_result = self.ai.chat(postDetail)
                                    except Exception as e: 
                                        print("AI请求异常: %s" % e)
                                        time.sleep(10)
                                        continue
                                    print("AI返回结果: %s" % ai_result)
                                    self.saveHistoryNote({"id":id, "ai_result": ai_result})
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
                                        time.sleep(3)
                                    else:
                                        if self.driver.current_url != page:
                                            self.driver.back()
                                        print("本篇笔记已跳过")

                                    # time.sleep(3)
                                    # return last page
                                else:
                                    print("没有展开笔记详情，稍后重试")
                                
                                time.sleep(0.01)

                    except Exception as e:
                        print("发生异常: %s" % e)
                        print(e.__traceback__)
                    finally:
                        print("本轮任务结束，等待5秒后刷新")
                        run = False
                        time.sleep(5)
                        print("当前页面url: %s" % self.driver.current_url)
                        if self.driver.current_url.find(page) == -1: 
                            self.driver.get(page)
                        else:
                            if self.driver.current_url.find("search_result") != -1: # search result
                                # 往下拉到底部加载更多
                                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                print("至底部等待5秒加载完毕")
                                time.sleep(5) #等5秒加载完毕
                            else:
                                try:
                                    reloadEl = self.driver.find_elements(By.CLASS_NAME, "reload")
                                    if reloadEl:
                                        reloadEl = reloadEl[0]
                                        reloadEl.click()    
                                    else:
                                        self.driver.refresh()
                                except Exception as e:
                                    print("点击刷新失败，刷新页面，%s" % e)
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
        time.sleep(3)
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
        for cookie in cookies:
            self.session.cookies[cookie['name']] = cookie['value']
        self.session.headers['User-Agent'] = self.driver.execute_script("return navigator.userAgent")

        with open("cookie", "w") as f: 
            f.write(json.dumps(cookies))

        local_storage = self.storage.items()
        with open("localstorage", "w") as f:
            f.write(json.dumps(local_storage))

        return True

    def findPostList(self):
        postContainer = None
        if self.driver.current_url.find("explore") != -1:
            print("发现页面的列表")
            postContainer = self.driver.find_elements(By.ID, "exploreFeeds")
        if self.driver.current_url.find("search_result") != -1:
            print("搜索页面的列表")
            filter_el = self.driver.find_elements(By.CLASS_NAME, "filter")
            if filter_el:
                filter_el = filter_el[0]
                try_time = 10
                while True:
                    filter_panel_el = filter_el.find_elements(By.CLASS_NAME, "filter-panel")
                    if filter_panel_el:
                        filter_tag_el =  filter_panel_el[0].find_elements(By.TAG_NAME, "span")
                        for el in filter_tag_el:
                            if el.text == "未看过":
                                el.click()
                                time.sleep(1)
                                filter_el.click()
                                time.sleep(5) #等待页面重新加载
                                break
                        break
                    else:
                        filter_el.click()
                        time.sleep(3)
                        try_time -= 1
                        if try_time == 0:
                            print("未找到筛选面板")
                            break

            postContainer = self.driver.find_elements(By.CLASS_NAME, "feeds-container")
        if not postContainer:
            print("未找到帖子列表")
            return []
        posts = postContainer[0].find_elements(By.CLASS_NAME, "note-item")
        print("找到帖子列表, 数量: %d" % len(posts))
        self.currentPosts = posts
        newPosts = []
        for post in posts:
            id = self.getCurrentPostId(post)
            if id and not self.isHistoryNote(id):
                newPosts.append(post)
        return newPosts

    def getCurrentPostId(self, post):
        id = post.find_elements(By.TAG_NAME, "a")
        # print(id)
        if id:
            id = id[0].get_attribute("href")
            return id.split("/")[-1]
        else:
            print("未找到帖子id")
            return None

    def clickPostDetail(self, post):
        # print(post)
        is_video = post.find_elements(By.CLASS_NAME, "play-icon")
        if self.doVideoNote == False and is_video:
            print("下一个操作笔记是视频，即将跳过")
            time.sleep(1)
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
        
        if not media:
            ogMetaEL = self.driver.find_elements(By.XPATH, "//meta[@name='og:image']");
            if ogMetaEL:
                print("找到帖子媒体, url: %s" % ogMetaEL[0].get_attribute("content"))
                media.append(ogMetaEL[0].get_attribute("content"))

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
            if self.actionDo:
                likeEl[0].click()
            print("点赞完成")
            return True
        else: 
            print("没有找到点赞按钮")
        return False
    
    def fav(self, postDivEl):
        dataEl = postDivEl.find_elements(By.CLASS_NAME, "interact-container")
        if not dataEl:
            print("未找到帖子互动数据")
            return False
        dataEl = dataEl[0]
        favEl = dataEl.find_elements(By.CLASS_NAME, "collect-wrapper")
        if favEl:
            if self.actionDo:
                favEl[0].click()
            print("收藏完成")
            return True
        else: 
            print("没有找到收藏按钮")
        return False
   
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
                if self.actionDo:
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
            os.mkdir('media')
        file_name = "%s.webp" % media_url.split('/')[-1]
        media_path = os.path.join('media', file_name)
        if os.path.isfile(media_path):
            print("媒体已存在, 跳过下载")
        else:
            print("开始下载媒体, url: %s" % media_url)
            response = self.session.get(media_url)
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

    def isHistoryNote(self, id):
        with open('history.json', 'r') as f:
            data = json.loads(f.read())
            for note in data['notes']:
                if note['id'] == id: 
                    return True
        return False
    
    def saveHistoryNote(self, info_data):
        with open('history.json', 'r') as f:
            data = json.loads(f.read())
        data['notes'].append(info_data)
        with open('history.json', 'w') as f:
            f.write(json.dumps(data))

def sign_handler(signal, frame):
    print('请再次按下退出操作!')
    app.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sign_handler)
    app = App()
    try:
        app.run()
    except Exception as e:
        print("程序退出: %s" % e)