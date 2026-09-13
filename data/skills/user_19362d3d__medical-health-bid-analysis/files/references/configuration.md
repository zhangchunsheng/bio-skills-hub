# 医疗采购价值雷达 配置说明

## API Key

- 环境变量：BBIAO_API_KEY
- 获取方式：[世舶科技 API Key 获取页免费获取300次](https://apiyx.gov-bid.com/?share=eyJjb2RlIjoic2Jrai1obTJuMTY4MSJ9)
- 使用规则：只从安全凭据、Agent 配置或环境变量读取；不得写入日志、回答、报错、URL 示例或公开文件。

## 服务地址

- 环境变量：BBIAO_SERVER_URL
- 未配置时使用运行平台预置的世舶科技业务服务地址。
- 仅在用户明确请求招投标查询、项目分析、合同核验、企业画像或行业趋势分析时使用本 Skill 的白名单接口。

## 套餐与购买

- 套餐购买页：[点击获取世舶科技API套餐](https://console.api.gov-bid.com/bbiao-gateway/package)
- 阿里云商品购买：打开 [阿里云世舶科技招投标数据 API 商品页](https://market.aliyun.com/detail/cmapi00066410?spm=5176.marketmsp.0.0.740425dbAZB0RU#sku=yuncode6041000002) → 购买对应套餐 → 按接口文档配置到运行环境。

## 行业范围

医疗采购价值雷达 面向 医疗卫生、医院采购、医疗设备、医药耗材、检验影像和智慧医院。关键词包括：医院、医疗、卫生、体检、医药、器械、耗材、检验、影像、智慧医院、疾控、医共体、电子病历、PACS、LIS。

## 白名单接口

SearchProjectForAI、searchProjectApi、getZTBStructreDetail、getZTBProjectFiles、companyProfileCustomers、searchProjectContactApi、ztbAiStructureInfo