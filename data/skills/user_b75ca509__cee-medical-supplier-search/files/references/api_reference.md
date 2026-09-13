# 宁波中东欧医药交易(集采)平台 - 供应商搜索接口参考

## 接口信息

- **URL**: `GET https://globalmedsource.cn/mall/MallStores/storeList`
- **请求方式**: GET（开放接口，无需登录）
- **参数**:
  - `page`: 页码，默认 1
  - `limit`: 每页条数，默认 5
  - `keyword`: 企业名称关键词（需 URL 编码）
  - `search_type`: 固定为 `Supplier`
- **示例**: `https://globalmedsource.cn/mall/MallStores/storeList?page=1&limit=5&keyword=%E7%BE%8E%E7%94%9F&search_type=Supplier`

## 请求方式说明

该接口返回的是服务端渲染的 HTML 页面，供应商数据内嵌在页面中。技能通过 `scripts/search_suppliers.py` 脚本请求页面并解析 HTML 为结构化 JSON 数据。

## 脚本用法

```bash
python scripts/search_suppliers.py <企业关键词> [limit]
```

示例：
```bash
python scripts/search_suppliers.py 美生
python scripts/search_suppliers.py "medical" 10
```

## 脚本输出数据结构

### 匹配成功 (matched: true)

```json
{
  "code": 0,
  "data": {
    "matched": true,
    "keyword": "美生",
    "total": 1,
    "suppliers": [
      {
        "user_id": 3667,
        "company_name": "NINGBO MEDSUN MEDICAL CO., LTD.",
        "company_name_zh": null,
        "store_logo_url": "https://ceeimg.cbnb.cn/uploads/images/202604031608442772.png",
        "contact_number": "0574-86301708",
        "contact_email": "RICHARD@NB-MEDSUN.COM",
        "contact_address": "No. 298 Huangjipu Road, Jiangbei, 315031 Ningbo, P.R. China",
        "store_intro": "We, Ningbo MEDSUN Medical Co., Ltd. (MEDSUN), are a company specializing in...",
        "goods": [
          {
            "goods_id": 32975,
            "goods_name": "ADJUSTABLE PUSHBUTTON ACTIVATED SAFETY LANCET (MODEL XA)",
            "image_url": "https://ceeimg.cbnb.cn/uploads/images/202607291140029568.jpg!165",
            "goods_url": "/mall/MallGoods/goodDetail?goods_id=32975"
          }
        ]
      }
    ]
  }
}
```

### 未匹配 (matched: false)

```json
{
  "code": 0,
  "data": {
    "matched": false,
    "keyword": "不存在的公司",
    "total": 0,
    "suppliers": []
  }
}
```

### 参数错误

```json
{
  "code": 1,
  "msg": "请提供企业名称关键词，例如：python search_suppliers.py 美生",
  "success": false
}
```

## 字段说明

### suppliers[].supplier 字段

| 字段 | 说明 |
|------|------|
| user_id | 供应商ID |
| company_name | 公司英文名 |
| company_name_zh | 公司中文名（页面未提供时为 null） |
| store_logo_url | 店铺logo URL |
| contact_number | 联系电话 |
| contact_email | 联系邮箱 |
| contact_address | 联系地址 |
| store_intro | 店铺/企业简介 |
| goods | 核心商品列表 |

### goods[] 字段

| 字段 | 说明 |
|------|------|
| goods_id | 商品ID |
| goods_name | 商品名称 |
| image_url | 商品图片URL |
| goods_url | 商品详情页路径 |

## 注意事项

- 页面最多展示 `limit` 个供应商（默认 5 个）
- 每个供应商在页面中最多展示 3 个核心商品
- `total` 字段为平台返回的匹配总数
- 图片 URL 中的 `!165` 后缀为平台缩略图参数，可直接访问
