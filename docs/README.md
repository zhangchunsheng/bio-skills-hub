```shell
开发一个用于生物分析的skillshub网站，skills从互联网获取，比如：https://www.skillhub.cn/，将skills下载到本地，使用vue+vite+tailwindcss开发
生成claude.md
项目部署后不应该再使用https://www.skillhub.cn，项目应直接包含生物分析相关skills，从互联网检索并保存到本地，数据库可以使用sqlite，后端接口可以使用php
重构系统，前端仍然使用vue+vite+tailwind，后端管理使用vue+vite+element，后端接口使用laravel，php版本为8.2，数据库仍然使用sqlite
admin需要登录才能访问，用户可以上传skills，上传skills也需要登录
后台缺少用户管理
允许用户修改密码
优化seo
https://biohub.luomor.com/skill/org-whlskj/biomed-rd-procurement-intelligence-assistant，显示有两个keywords

chmod 777 public
chmod 777 storage
chmod 777 storage/app
chmod 777 storage/app/public
chmod 777 storage/framework
chmod 777 storage/framework/cache
chmod 777 storage/framework/cache/data
chmod 777 storage/framework/sessions
chmod 777 storage/framework/testing
chmod 777 storage/framework/views
chmod 777 storage/logs
chmod -R 777 storage/logs/laravel.log
chmod 777 bootstrap/cache/
chmod 777 storage/app/private/
chmod 777 storage/app/public/
chmod 777 database
chmod 777 database/skills.db

https://biohub.luomor.com/
管理员账号：admin@bio-skills.local / admin123456 
```