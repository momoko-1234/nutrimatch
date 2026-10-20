# DHC Product Catalog Schema

The seed catalog lives at `data/dhc_products.json`.

Each product uses this shape:

```json
{
  "id": "dhc-vitamin-c",
  "name": "DHC 維他命C",
  "category": "vitamin",
  "nutrients": ["Vitamin C"],
  "functions": ["immunity", "brightening_antioxidant"],
  "suitableFor": ["high_stress"],
  "avoidFor": ["kidney_disease"],
  "intakeTiming": "飯後補充較溫和，可分次補充",
  "dosage": "依產品標示每日建議量",
  "caution": "腎臟疾病或容易結石者請先諮詢專業人員。"
}
```

This JSON can later be migrated to a relational table or document database without changing the API response contract.
