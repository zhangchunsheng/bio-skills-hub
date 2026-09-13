---
name: "在SEO发布前，从路由清单生成XML网站地图和robots.txt"
slug: "generate-xml-sitemaps-and-robots-txt-from-route-inventories-before-seo-launch"
version: "1.0.0"
displayName: "在SEO发布前，从路由清单生成XML网站地图和robots.txt"
summary: "当代理已经知道网站路由或内容URL，并且在启动前需要有效的sitemap XML、sitemap索引或robots.txt引用时，请使用sitemap。这是一个发布构件技能，而不是爬虫或SEO平台。"
license: "MIT"
description: "当代理已经知道网站路由或内容URL，并且在启动前需要有效的sitemap XML、sitemap索引或robots.txt引用时，请使用sitemap。这是一个发布构件技能，而不是爬虫或SEO平台。"
github_stars: 1708
verification: "security_reviewed"
source: "https://github.com/1991513ccie-png/skills"
author: "1991513ccie-png"
category: "Content Writing & SEO"
framework: "Multi-Framework"
tool_ecosystem:
  github_repo: "1991513ccie-png/skills"
  github_stars: 1708
  npm_package: "sitemap"
  npm_weekly_downloads: 12536444
---

# 在SEO发布前，从路由清单生成XML网站地图和robots.txt

Use sitemap when an agent already knows the site routes or content URLs and needs valid sitemap XML, sitemap indexes, or robots.txt references before launch. This is a publishing-artifact skill, not a crawler or SEO platform.

## Prerequisites

Node.js, npm

## Installation

Use the upstream install or setup path that matches your environment:
- npm install --save sitemap
- npx sitemap < listofurls.txt # npx sitemap -h for more examples and a list of options.

Requirements and caveats from upstream:
- # sitemap ![MIT License](https://img.shields.io/npm/l/sitemap)[![Build Status](https://github.com/1991513ccie-png/skills)](https://github.com/1991513ccie-png/skills)![Monthly Downloads]...
- const { SitemapStream, streamToPromise } = require('sitemap')
- const { Readable } = require('stream')

Basic usage or getting-started notes:
- [Example of using sitemap.js with](#serve-a-sitemap-from-a-server-and-periodically-update-it) [express](https://expressjs.com/)
- sh
- ## Generate a one time sitemap from a list of urls

- Source: https://github.com/1991513ccie-png/skills
- Extracted from upstream docs: https://raw.githubusercontent.com/ekalinin/sitemap.js/HEAD/README.md

## Documentation

- https://github.com/1991513ccie-png/skills
