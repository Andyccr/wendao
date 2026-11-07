# 问道

Andy Chen 的个人博客。站点基于 [Hugo](https://gohugo.io/)，版式参考 Journal / hugo-theme-diary：左侧栏 + 标题/日期列表。界面字体为 Montserrat，文章标题与正文为 Lora / 中文衬线。

GitHub Pages（合并到 `main` 并打开 Pages 之后）：<https://andyccr.github.io/wendao/>

This is Andy Chen’s personal blog, built with Hugo. The layout follows the Journal / hugo-theme-diary sidebar + title/date list. UI type is Montserrat; titles and article body use Lora with CJK serif fallbacks. After `main` is deployed: <https://andyccr.github.io/wendao/>

## 语言 / Languages

三种语言，URL 与 BYVoid 同类：

Three locales, Journal-style prefixes under the Pages base:

| | URL |
|---|---|
| 简体中文 | `/wendao/zhs/` |
| 正體中文 | `/wendao/zht/` |
| English | `/wendao/en/` |

`/wendao/` 会跳转到 `/wendao/zhs/`（Hugo `defaultContentLanguageInSubdir`）。

`/wendao/` redirects to `/wendao/zhs/`.

正體版由简体正文经 OpenCC `s2t` 逐字转换，不改写。英文版只收录原文为英文的文章，不机翻中文。

Traditional pages are OpenCC `s2t` character conversion only. The English locale lists posts originally written in English; Chinese posts are not machine-translated.

RSS：`/wendao/zhs/index.xml`、`/wendao/zht/index.xml`、`/wendao/en/index.xml`

## 本地预览 / Local preview

需要 Hugo Extended 0.151.2 或相近版本。

```bash
hugo server
```

打开 <http://localhost:1313/wendao/>（会进入简体）。

Open <http://localhost:1313/wendao/> (redirects to Simplified Chinese).

生产构建 / production:

```bash
hugo --gc --minify
```

## 写新文章 / Add a post

在 `content/zhs/posts/` 新增 Markdown，然后生成另外两种语言树：

Add Markdown under `content/zhs/posts/`, then regenerate the other locales:

```bash
hugo new content/zhs/posts/my-new-post.md
python3 scripts/generate_locales.py
```

`generate_locales.py` 需要 `opencc-python-reimplemented`。Front matter 示例：

```yaml
---
title: "标题"
date: 2026-11-07T12:00:00+08:00
---
```

图片放在 `static/images/`：

```markdown
![](images/example.jpg)
```

## 部署 / Deploy

不要改其他仓库的 `CNAME`，也不要给本站绑定自定义域名。`andychen.net` 仍指向旧站 `Andyccr/Blog`。

1. 推送到 `main`。
2. `.github/workflows/pages.yml` 构建 Hugo 并发布 GitHub Pages。
3. 仓库 Settings → Pages → Source = **GitHub Actions**。

## 从旧站导入 / Import notes

旧文章来自 <https://andychen.net/> 与 [Andyccr/Blog](https://github.com/Andyccr/Blog)。

```bash
python3 scripts/migrate_posts.py
python3 scripts/generate_locales.py
```

每篇文章保留原标题、日期、正文和 `original_url`。`blog.andyccr.com` 与 `192.144.164.198` 上的附件目前打不开；Wayback 能取回的图在 `static/images/`，其余保留原链接。
