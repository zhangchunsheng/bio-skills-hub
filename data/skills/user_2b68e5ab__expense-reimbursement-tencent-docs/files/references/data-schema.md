# Reimbursement Builder Data Schema

Create a UTF-8 JSON file with this structure:

```json
{
  "company": "上海某某有限公司",
  "outputDir": "/absolute/path/to/outputs",
  "records": [
    {
      "time": "2026-07-01 10:00",
      "category": "高铁",
      "reason": "高铁：G123 上海虹桥-北京南",
      "amount": 123.45,
      "invoiceNo": "1234567890",
      "invoicePdf": "/absolute/path/to/invoice.pdf",
      "tripPdf": "/absolute/path/to/itinerary.pdf"
    }
  ]
}
```

Required fields:

- `company`: Buyer/company name used in workbook title and output filenames.
- `records[].time`: Date/time or date range used for reimbursement.
- `records[].category`: Chinese category label, for example `高铁`, `酒店`, `飞机`, `打车`.
- `records[].reason`: Short reimbursement reason.
- `records[].amount`: Numeric amount in RMB.
- `records[].invoiceNo`: Invoice number or stable document identifier.
- `records[].invoicePdf`: Absolute path to the original invoice PDF.

Optional fields:

- `outputDir`: Absolute output directory. Defaults to `./outputs` from the current working directory.
- `records[].tripPdf`: Absolute path to itinerary PDF, usually for ride-hailing or flight itinerary details.
- `records[].invoicePdfName` and `records[].tripPdfName`: Override generated names. Use only when the source file already has a finance-approved name.

The builder writes:

- `曾兴报销——<company>.xlsx`
- `曾兴报销——<company>_PDF/`
- `曾兴报销——<company>_原始PDF附件包.zip`
- `曾兴报销——<company>_preview.png`
