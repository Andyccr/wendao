# 问道

Andy Chen 的个人博客。站点基于 [Hugo](https://gohugo.io/)，版式参考 Journal / hugo-theme-diary 一类的左侧栏 + 标题/日期列表，而不是卡片式首页。

GitHub Pages 地址（合并到 `main` 并打开 Pages 之后）：<https://andyccr.github.io/wendao/>

This is Andy Chen’s personal blog, built with Hugo. The layout follows the quiet sidebar + title/date list pattern (Journal / hugo-theme-diary), not a card grid. After `main` is deployed to GitHub Pages: <https://andyccr.github.io/wendao/>

## 本地预览 / Local preview

需要 Hugo Extended 0.151.2 或相近版本。

You need Hugo Extended 0.151.2 or a nearby version.

```bash
hugo server
```

浏览器打开 <http://localhost:1313/wendao/>。

Then open <http://localhost:1313/wendao/>.

生产构建：

Production build:

```bash
hugo --gc --minify
```

生成结果在 `public/`。

Output is written to `public/`.

## 写新文章 / Add a post

在 `content/posts/` 新增 Markdown 文件，文件名用英文或原有短名：

Create a Markdown file in `content/posts/`. Keep the filename in ASCII when you can:

```bash
hugo new posts/my-new-post.md
```

Front matter 示例 / example:

```yaml
---
title: "标题"
date: 2026-11-07T12:00:00+08:00
---
```

正文用 Markdown 写。图片可以放在 `static/images/`，在文章里写成：

Write the body in Markdown. Put images in `static/images/` and reference them without a leading slash:

```markdown
![](images/example.jpg)
```

保存后 `hugo server` 会热更新。

`hugo server` reloads on save.

## 部署 / Deploy

不要改其他仓库的 `CNAME`，也不要给本站绑定自定义域名。`andychen.net` 仍指向旧站 `Andyccr/Blog`。

Do not add a custom domain, and do not edit another repo’s `CNAME`. `andychen.net` still points at the old site (`Andyccr/Blog`).

1. 把更改推送到 `main`。
2. GitHub Actions 工作流 `.github/workflows/pages.yml` 会构建 Hugo 并发布到 GitHub Pages。
3. 在仓库 Settings → Pages 中，Source 选 **GitHub Actions**。

Steps:

1. Push to `main`.
2. `.github/workflows/pages.yml` builds Hugo and publishes GitHub Pages.
3. In the repo Settings → Pages, set Source to **GitHub Actions**.

RSS：`/wendao/index.xml`

## 从旧站导入 / Import notes

旧文章来自 <https://andychen.net/> 与公开仓库 [Andyccr/Blog](https://github.com/Andyccr/Blog)。转换脚本：

Old posts came from <https://andychen.net/> and the public repo [Andyccr/Blog](https://github.com/Andyccr/Blog). Converter:

```bash
python3 scripts/migrate_posts.py
```

脚本默认读取 `/tmp/old-blog`。每篇文章保留原标题、日期、正文和 `original_url`。

`blog.andyccr.com` 与旧 IP `192.144.164.198` 上的附件目前已经打不开。能从 Wayback Machine 取回的本地图会放进 `static/images/`；其余仍保留原文链接。维基共享资源上的图继续指向原 URL。

The script reads `/tmp/old-blog` by default. Each post keeps its original title, date, body, and `original_url`.

Attachments hosted on `blog.andyccr.com` and `192.144.164.198` are currently unreachable. Files recovered from the Wayback Machine live in `static/images/`; the rest keep the original URL. Wikimedia images stay as remote links.
