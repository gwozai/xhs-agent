<h1 align="center">
    小红薯🍠Agent
</h1>
<p align="center">
    <img src="/static/logo.jpeg" alt="logo" style="margin: 0 auto;width:200px;">
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Python-3.9%2B-blue" alt="Python Version">
    <img src="https://img.shields.io/badge/Selenium-blue" alt="Selenium Version">
    <img src="https://img.shields.io/badge/OpenAI-blue" alt="OpenAI Version">
</p>

## 简介

基于 selenium + openai 的小红书自动化网页操作，访问探索频道帖子进行AI代理操作，仅作学习用途，请勿用于商业用途，任何商业化行为以仓库作者无关。

## 基本功能

- 缓存账户登录
- 访问探索频道指定板块
- 浏览帖子，跳过视频笔记
- 获取小红书封面，下载并重置大小
- 点赞
- 收藏
- 评论

## AI功能

可接入Google Gemini，DeepSeek，OpenAI等AI模型进行操作处理，传递帖子的首图，标题内容，帖子数据，由AI参考而决定是否点赞，收藏，评论以及评论内容。

## 使用

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 运行

```bash
python app.py
```

运行后将会自动打开ChromeDrive，首次需要手动登录，登录完成后存储cookie，启动若为过期自动登录，操作过程中不可以对手动对页面进行操作，包括但不限于修改窗口大小，手动点入其他页面，打开开发者工具等，否则会导致程序异常。

## 注意事项

- 请勿用于商业用途，任何商业化行为与仓库作者无关
- 请勿用于违法用途，包括但不限于违法内容，违法操作等
- 请勿使用自己常用账户操作，脚本虽做了反检测，但仍存在被封号风险，作者不承担任何责任

## 鸣谢

- [Google Gemini](https://gemini.google.com/) 提供的该项目icon生成，感谢慷慨的免费调试额度用于开发和调试

## 联系

- 邮箱: abigeater@163.com