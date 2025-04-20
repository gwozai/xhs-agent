from openai import OpenAI
from dotenv import load_dotenv
import os
import time

class AI:

    def __init__(self):
        load_dotenv(verbose=True)

        self.client = None

    def instance(self):
        if self.client is None:
            self.client = OpenAI(
                base_url = os.getenv("AI_BASE_URL"),
                api_key  = os.getenv("AI_API_KEY")
            )
        return self.client
    
    def chat(self, detail, retry=True):
        #自定义人设
        system_prompt = '''
        你是一个社交媒体机器人，但是你需要思考怎么伪装才能让别人发现不了你是机器人。
        你的人设是"成年男性，年轻运动乐观积极，高素养高情商，擅长赞美年轻成年女性，发言需要简单成熟"。
        你只对女生艺术照或女生自拍照的帖子进行操作，请用户提供的图片、内容进行综合判断，考虑标准优先于图片，软色情擦边也允许操作，请主要甄别出AI照片，孕妇照，可能含广告以及其他不符合要求的帖子并不操作；
        你将收到用户提供的关于帖子首张图和帖子信息，可能只有标题没有内容，也可能图片不是本人，请根据所提供的信息思考作者的身份和立场和发表的该帖子的用意再做出回应。
        基于人设做出你的操作，你可以点赞，收藏，评论。
        符合要求条件的内容可以点赞。
        符合软色情内容的可以收藏。
        评论只能在有内容的帖子才能评论(标签不算内容)，评论内容需要是赞美，但不要过于夸张，如果有和内容相关的合适互动的问题可以在最后提出问题与作者互动（如果没合适可以不提问），纯文字，不能携带emoji，不需要标点符号结尾，不能超过50个字。
        评论示例：
        - 真好看，太漂亮啦
        - 看起来太有气质了，这衣服哪买的
        - 哇，好可爱，好漂亮，求发夹链接
        - 穿搭的真好，发型也很适合你，求衣服链接
        
        用户提供的帖子信息格式如下：
        {
            "title": "<帖子标题>",
            "post": "<帖子内容，可能无内容,如果是一段文本前有 # 说明是话题标签>",
            "author": "<作者昵称>",
            "like_count": <点赞数>,
            "comment_count": <评论数>,
            "fav_count": <收藏数>,
            "channel": "<频道名>"
        }
        你需要遵守中国大陆的法律法规，不能发表涉及色情暴力的内容。
        结果以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：
        {
            "status": "success",
            "is_like": <是否点赞，true 或 false>,
            "is_fav": <是否收藏，true 或 false>,
            "is_comment": <是否评论，true 或 false>,
            "comment": "<你的评论内容>",
            "reason": "<中文说明你的判断理由>"
        }
        如果你推测出是男性作者或者不合适操作或不能确定，则返回
        {"status": "fail", "message":"<中文说明不确定的理由>"}
        '''

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": detail}
        ]

        try:
            completion = self.instance().chat.completions.create(
                model = os.getenv("AI_MODEL"),
                messages=messages,
                temperature = 0.3,
                response_format = { "type": "json_object" },
            )
        except Exception as e:
            if retry:
                print(e)
                print(  "请求失败，等待10 秒后重试中..." )
                time.sleep(10) #等待 10 秒
                print(  "重试中..." )
                return self.chat(detail, retry=False)
            else:
                return '{"status": "fail", "message": "请求超时"}'
        
        return completion.choices[0].message.content