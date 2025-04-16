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

基于 selenium + openai 的小红薯自动化网页操作，访问探索频道帖子进行AI代理操作，仅作学习用途，请勿用于商业用途，任何商业化行为与仓库作者无关。

## 基本功能

- 缓存账户登录
- 访问探索频道指定板块、搜索页面浏览
- 浏览帖子
- 获取封面，下载并重置大小
- 点赞
- 收藏
- 评论

## AI功能

可接入Google Gemini，DeepSeek，OpenAI等AI模型进行操作处理，传递帖子的首图，标题内容，帖子数据，由AI参考而决定是否点赞，收藏，评论以及评论内容。请在 `ai.py` 中配置提示词。

最少使用20 RPM（每分钟请求数）的模型才能不间断运行，免费用户下使用<b>gemini-2.0-flash</b>模型的15 RPM也是能勉强跑满，中途可能会出发限流自动等待10秒。

强烈推荐使用: gemini-2.0-flash模型, 免费且更像人类了

## 使用

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 修改 `.env` 环境变量

3. 运行

```bash
python app.py
```

运行后将会自动打开ChromeDrive，首次需要手动登录，登录完成后存储cookie，启动若为过期自动登录，操作过程中不可以对手动对页面进行操作，包括但不限于修改窗口大小，手动点入其他页面，打开开发者工具等，否则会导致程序异常。

## 注意事项

- 项目仅用于学习用途
- 请勿用于商业用途，任何商业化行为与仓库作者无关
- 请勿用于违法用途，包括但不限于违法内容，违法操作，尊重平台的版权和隐私，不得侵犯该平台合法权益，不得从事任何违法或不道德的行为，下载的临时文件请24小时内删除等
- 请勿使用自己常用账户操作，可能存在被封号风险，作者不承担任何责任
- 不对本项目的安全性、完整性、可靠性、有效性、正确性或适用性做任何明示或暗示的保证，也不对本工具的使用或滥用造成的任何直接或间接的损失、责任、索赔、要求或诉讼承担任何责任
- 保留随时修改、更新、删除或终止本工具的权利，无需事先通知或承担任何义务
- 使用者在下载、安装、运行或使用本工具时，即表示已阅读并同意本免责声明。如有异议，请立即停止使用本工具，并删除所有相关文件

## 鸣谢

- [Google Gemini](https://gemini.google.com/) 提供的该项目icon生成，感谢慷慨的免费调试额度用于开发和调试

## 联系

- 邮箱: abigeater@163.com

