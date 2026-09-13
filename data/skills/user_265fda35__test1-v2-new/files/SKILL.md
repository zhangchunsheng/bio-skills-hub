---
name: xfyun-invoice
description: Recognize and extract structured data from invoices, receipts, and bills using iFlytek OCR API (科大讯飞票据识别). Supports VAT invoices, taxi receipts, train tickets, toll invoices, medical bills, bank receipts, and more.
---

# xfyun-invoice

OCR-based invoice and receipt recognition using the iFlytek (科大讯飞) API. Extracts structured fields from photos or scans of Chinese invoices and bills.

## When to Use

- User provides an invoice/receipt image and wants structured data extracted
- Need to digitize paper invoices (增值税发票、出租车票、火车票、医疗票据 etc.)
- Expense report automation — extract amounts, dates, vendor info from receipts

## Prerequisites

- **Python 3** (standard library only, no pip install needed)
- **Environment variables** (get from [讯飞控制台](https://console.xfyun.cn)):
  - `XFYUN_APP_ID` — Application ID
  - `XFYUN_API_KEY` — API Key
  - `XFYUN_API_SECRET` — API Secret

## Supported Image Formats

png, jpg/jpeg, bmp, gif, tif/tiff, pdf

## Usage

The script is at `scripts/invoice.py` relative to this skill directory.

### Basic Recognition

```bash
python3 scripts/invoice.py /path/to/invoice.png
```

### Options

| Flag | Description |
|------|-------------|
| `--raw` | Output raw API JSON response instead of formatted text |

### Examples

```bash
# Recognize a VAT invoice
python3 scripts/invoice.py ./vat_invoice.jpg

# Recognize a medical receipt with raw output
python3 scripts/invoice.py ./medical_bill.png --raw

# Recognize a taxi receipt
python3 scripts/invoice.py ./taxi_receipt.jpg
```

### Output Format (default)

Human-readable structured fields:

```
票据类型: 增值税普通发票

发票代码: 012345678901
发票号码: 12345678
开票日期: 2026年03月06日
金额: ¥1,234.56
...
```

### Output Format (--raw)

Full API JSON response including all metadata and encoded payload.

## Authentication

Uses HMAC-SHA256 signature-based auth (讯飞鉴权). The script handles all signing automatically — just set the three environment variables.

## API Details

- **Endpoint**: `POST https://api.xf-yun.com/v1/private/sc45f0684`
- **Auth**: HMAC-SHA256 signature in URL query parameters
- **Image limit**: Check your service tier on 讯飞控制台

## Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 10105 | Unauthorized app or invalid signature |
| 10110 | Missing required field |
| 10163 | Request body too large |
| 10200 | Image read failed |
| 11200 | Quota exceeded |

## Tips

- Ensure the image is clear and well-lit for best accuracy
- Crop to just the invoice area if possible (reduces noise)
- PDF support means you can pass scanned documents directly
