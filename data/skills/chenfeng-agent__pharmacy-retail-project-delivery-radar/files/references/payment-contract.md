# 支付契约

这是按次收费的企业 PaySkill，无免费版本。唯一生产入口为 `POST https://pay.chenfengai.cn/api/pharmacy-retail-project-delivery-radar`。

## 付费前置检查

调用本 Skill 前，Agent 必须检查当前宿主是否已安装并启用 `weixinpay` 插件：已安装时才可继续；未安装时提示“当前 Agent 暂不支持微信支付付费能力”并终止流程，不得发起订单或降级为免费输出。

首次请求必须携带 `input` 和本包规定的 `mode`，服务端返回 HTTP 402、`WeixinPay-Required`、`X-Out-Trade-No` 和本次价格；付款前只返回支付说明，不交付完整结果。

Agent 必须保存 `WeixinPay-Required` 和 `X-Out-Trade-No`，将 `WeixinPay-Required` 的值作为 `paymentCode` 调用 `weixinpay_pay`，向用户申请微信支付授权。支付成功后必须保持首次请求体完全不变，并携带原 `WeixinPay-Required` 与原 `X-Out-Trade-No` 重新请求同一接口；不得省略重试或创建第二笔订单。

服务端在交付前核对订单、Skill slug、CNY 金额、支付状态、请求摘要和幂等键。模型超时、输入超限、验付失败、状态未知或结果保存失败时不交付，按原订单恢复或退款，不创建第二笔订单。