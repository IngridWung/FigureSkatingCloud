# 冰上四重奏 · 花样滑冰课程项目

一个介绍男单、女单、双人滑和冰舞的网站。访客可观看节目视频、回答四道趣味题；Python 后端评分，并把最近成绩存到本地 SQLite 数据库。

## 在 VS Code 中运行

1. 用 VS Code 打开 `figure skating` 文件夹。
2. 打开终端，运行 `python server.py`。
3. 浏览器打开 <http://localhost:8000>。
4. 完成问答后刷新页面；最近成绩应仍然显示。

也可以用 VS Code Live Server 打开 `web/index.html`。建议在浏览器地址栏使用 `http://localhost:5500/web/index.html`：目前嵌入的 YouTube 视频在 `127.0.0.1:5500` 下可能显示无法观看，而同一页面在 `localhost:5500` 下已验证可以播放。页面样式在两种地址下都能加载。若要使用问答和历史记录，仍需在另一个终端运行 `python server.py`，因为 Live Server 只提供静态文件，不运行 Python API。

不需要安装 Python 扩展包或单独安装数据库。Python 自带 SQLite，首次答题时自动建立 `data/skating.db`。请勿把此文件上传到 Git。

## 当前结构

- `web/`：静态网页（HTML、CSS、JavaScript）。
- `server.py`：网页服务器、问答接口和 SQLite 数据读写。

## 下一阶段

页面现在展示四张 Wikimedia Commons 运动员照片。每张照片下方都有作者、许可和原始文件页链接；图片目前由 Wikimedia 远程加载，需要联网。你拍的照片可以在上传后放进 `web/assets/`。之后将前端部署为静态网站、Python API 放入容器，并把 SQLite 换成云端托管 PostgreSQL，以满足课堂作业的三部分部署要求。当前 SQLite 仅供本地开发，不能当作最终要求的云端托管资源。

答题记录不需要注册登录：浏览器生成随机编号，API 按编号查询历史。清除浏览器本地数据后，原记录不会再显示；这不是账户系统，也不适合存私人信息。
