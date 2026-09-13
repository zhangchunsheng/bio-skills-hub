# 参考图视觉 DNA 与同类原创

## 1. 先确定参考图角色

每张参考图只能承担明确角色：

- 环境形态；
- 店铺身份；
- 室内拓扑；
- 材料/色彩；
- 摄影机位；
- 人群节奏；
- 文字/Logo；
- 编辑目标。

禁止用同一张图同时推断看不见的地址、背面、室内、品牌授权和人群身份。

## 2. 可迁移的抽象 DNA

- 前景—中景—背景层级；
- 街道宽窄、连续店面和楼上用途的抽象关系；
- 自然遮挡、生活流动和经营节奏；
- 摄影机位、焦段、景深和光线；
- 材料粗糙度与维护程度；
- 店内功能区的相对组织（不复制独特布局）。

## 3. 不可复制

- 可识别建筑、门牌、道路几何；
- 真实店名、Logo、电话、二维码和广告；
- 真实人物、车牌、顾客或员工；
- 独特艺术作品、品牌包装和商业秘密；
- 参考图中的地域外观与目标地点冲突时的错误元素。

## 4. 固定提示词

```text
Image 1 is an environment and composition reference, not an edit target. Transfer only its abstract spatial layering, lived-in commercial rhythm, natural crowd behavior, material maintenance level and documentary camera language. Create an original location; do not copy identifiable buildings, signs, people, addresses, vehicles, exact street geometry or copyrighted brand assets. The target Chinese location, current evidence and business logic override the reference image's regional appearance.
```

## 5. 编辑目标例外

用户明确要求编辑某张图时，该图才是 edit target。必须写清：

- `Change only`
- `Keep unchanged`
- `Do not add`
- `Truth boundary`

若缺少可编辑目标，不假装已看到或已锁定图片。

## 6. V3 通用参考角色

除商业门店外，参考图还可承担：

- 人物身份与服装层次；
- 产品几何、材质与包装；
- 家庭/办公空间拓扑；
- 工业设备与工位关系；
- 自然地貌与季节；
- 活动流程与人群节奏；
- 小红书/自媒体的版式留白；
- 局部文字或品牌编辑目标。

每张参考图最多指定一个主角色和一个次角色。参考图中未被明确授权的真实人物、品牌、地址、作品、屏幕和个人信息不得进入结果。

## 7. 通用固定提示词

```text
Image 1 is a visual reference, not automatically an edit target. Transfer only the explicitly requested abstract attributes such as spatial layering, camera distance, lighting direction, material behavior, natural human rhythm or layout balance. Rebuild an original subject and environment. Do not copy identifiable people, faces, products, buildings, signs, addresses, copyrighted characters, exact composition or brand assets. Target evidence, locality, product geometry and truth boundary override the reference image.
```

## 8. 风格参考边界

风格迁移应拆成可执行摄影属性：色温、对比度、焦段、光源、粗糙度、留白和节奏。不要只写“像某摄影师/某品牌/某艺术家”，也不要复制在世创作者的可识别个人风格作为唯一目标。
