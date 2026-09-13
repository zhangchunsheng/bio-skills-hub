# Pet-medical activity mode

Use this reference when the merchant is a pet hospital, animal hospital, or veterinary service. The activity object is intentionally replaceable between campaigns.

## Input contract

```json
{
  "activity_object": {
    "service_scene": "疫苗 | 体检 | 驱虫 | 绝育评估 | 老年宠 | 自定义",
    "target_segment": "犬/猫、年龄或生命周期、附近区域",
    "goal": "咨询 | 预约 | 到店 | 核销 | 真实评价 | 复诊",
    "offer": "待门店确认的服务/权益",
    "price": "待门店确认",
    "capacity": "待门店确认",
    "time_window": "待门店确认"
  }
}
```

When `activity_object` changes, regenerate the copy, platform plan, CTA, and review fields. Never carry over the old price, slot, service promise, or audience by accident.

## Channel handoff

`抖音本地推（触达） → 美团/高德（搜索、POI、到店） → 朋友圈（信任） → 私域（咨询、预约、提醒） → 门店服务/核销 → 真实评价 → 复诊`

Each handoff records the next owner and the next action. Do not treat exposure as inquiry, inquiry as appointment, appointment as arrival, or arrival as completed service.

## Required review gates

- Medical wording describes process, scope, preparation, and observable service details only.
- Case photos, records, names, phone numbers, order IDs, and chat screenshots are authorized and de-identified.
- Price, stock, time window, cancellation terms, and service promises are checked by the merchant.
- A vet or designated responsible person reviews clinical wording before publication.

## Prohibited output

No fake reviews, fake queues or slots, fabricated cases or metrics, efficacy/cure promises, online diagnosis, prescriptions, dosage instructions, coercive upsells, or platform-rule evasion.
