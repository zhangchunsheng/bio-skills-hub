#!/usr/bin/env bash
# 将前端构建产物部署到 Laravel public/ 目录：
#   server/public/        ← web/dist（用户端）
#   server/public/admin/  ← admin/dist（管理端）
# 之后 php artisan serve（或 Nginx/Apache 指向 server/public）即可同时提供
# 用户端、管理端和 /api 接口。
set -euo pipefail
cd "$(dirname "$0")/.."

PUBLIC=server/public

# 用户端：清空 public 下除 admin/ 与 index.php 之外的文件后拷贝
find "$PUBLIC" -mindepth 1 -maxdepth 1 ! -name 'admin' ! -name 'index.php' ! -name '.htaccess' ! -name 'favicon.ico' -exec rm -rf {} +
cp -r web/dist/. "$PUBLIC/"

# 管理端
rm -rf "$PUBLIC/admin"
cp -r admin/dist "$PUBLIC/admin"

echo "部署完成：用户端 /  管理端 /admin/  API /api/"
