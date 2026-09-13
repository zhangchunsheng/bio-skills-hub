# 医药流通ERP 商品编码统一 — 数据模型参考

> 配套 `pharma-product-coding` SKILL.md 使用。以下 DDL 为建模示意（MySQL 风格），字段名与约束按设计意图给出；接真实 ERP 时按你们库类型调整方言即可。

## 1. SPU 主数据（自然属性层）

```sql
CREATE TABLE spu (
  spu_id        VARCHAR(32) PRIMARY KEY,
  generic_name  VARCHAR(128) NOT NULL,   -- 通用名
  trade_name    VARCHAR(128),            -- 商品名
  spec          VARCHAR(64),             -- 规格
  dosage_form   VARCHAR(64),             -- 剂型
  ingredient     VARCHAR(256),           -- 成分
  storage_cond  VARCHAR(64),             -- 贮藏条件
  base_barcode  VARCHAR(32),             -- 基础条码
  min_unit      VARCHAR(16) NOT NULL,    -- 最小单位（计量最小颗粒）
  status        TINYINT DEFAULT 1,
  created_at    DATETIME
);
-- 关键：厂家 NOT NULL 不在此表固化，厂家取数一律来自 batch_info（见第 4 节）。
-- SPU 只持有稳定的自然属性；自然属性未变则不新增 SPU 编码。
```

## 2. SKU 管理属性层

```sql
CREATE TABLE sku (
  sku_id         VARCHAR(32) PRIMARY KEY,
  spu_id         VARCHAR(32) NOT NULL,   -- 指向唯一 SPU（多 SKU 同挂一 SPU）
  org_id         VARCHAR(32) NOT NULL,   -- 总部 / 子公司
  sales_unit     VARCHAR(16) NOT NULL,   -- 最小销售单位
  base_price     DECIMAL(12,2),          -- 底价
  sale_price     DECIMAL(12,2),          -- 销价
  promo_price    DECIMAL(12,2),          -- 促销价
  channel        VARCHAR(32),            -- 渠道归属
  assess_owner   VARCHAR(32),            -- 考核归属
  alloc_strategy VARCHAR(32),            -- 分货策略
  qc_requirement VARCHAR(64),            -- 首营 / 质检要求
  FOREIGN KEY (spu_id) REFERENCES spu(spu_id)
);
-- 管理属性膨胀只扩 SKU，不裂 SPU；SKU 是"一品多码"的主要来源，靠批次账簿归因回 SPU。
```

## 3. 箱规换算层

```sql
CREATE TABLE case_spec (
  case_spec_id   VARCHAR(32) PRIMARY KEY,
  spu_id         VARCHAR(32),
  sku_id         VARCHAR(32),             -- 箱规可挂在 SPU 或 SKU
  unit_from      VARCHAR(16) NOT NULL,   -- 源单位
  unit_to        VARCHAR(16) NOT NULL,   -- 目标单位
  ratio          DECIMAL(12,4) NOT NULL, -- 转换比
  is_pricing_unit TINYINT DEFAULT 0,     -- 计量单位（定价单位）标记
  is_min_unit      TINYINT DEFAULT 0,     -- 最小单位标记
  is_report_unit   TINYINT DEFAULT 0      -- 报表单位标记
);
-- 约束：每个商品必须恰好有一个 is_pricing_unit=1、一个 is_min_unit=1、一个 is_report_unit=1。
-- 三者可不同（定价按盒、报表按件、库存按支），必须逐一标注，禁止默认等同。
-- 业务单据只引用 case_spec 的换算关系，禁止散落写死比例。
```

## 4. 批号信息（可变实例属性 + 厂家取数来源）

```sql
CREATE TABLE batch_info (
  batch_info_id VARCHAR(32) PRIMARY KEY,
  spu_id        VARCHAR(32) NOT NULL,
  sku_id        VARCHAR(32),
  batch_no      VARCHAR(64) NOT NULL,    -- 批号
  mf_name       VARCHAR(128),            -- 厂家名称（取数来源！不固化在 SPU）
  pkg_spec      VARCHAR(64),             -- 件包装（变化随批记录，不改 SPU）
  prod_date     DATE,                    -- 生产日期
  expiry_date   DATE,                    -- 效期
  clarity       VARCHAR(32),             -- 澄明度（注射 / 输液类关键指标）
  rebate        DECIMAL(12,2),           -- 返利（成本还原用）
  created_at    DATETIME,
  UNIQUE KEY uk_batch (spu_id, batch_no, prod_date)  -- 旧批号重启用复合键
);
-- 基础信息变化判定：
--   主体未变（件包装调整 / 厂家更名）→ 只更新本表字段，不改 SPU。
--   主体真变（实际厂家变更）→ 新 SPU + 本表 mf_name 写新厂家。
-- 厂家取数一律查本表，SPU 不存厂家。
```

## 5. 财务成本维度 + 批次账簿

```sql
CREATE TABLE cost_dimension (           -- 多维度成本归集
  dimension_id  VARCHAR(32) PRIMARY KEY,
  spu_id        VARCHAR(32) NOT NULL,   -- 归集根：品种（跨 SKU 归因）
  supplier_id   VARCHAR(32),            -- 供应商（上游渠道）
  contact_id    VARCHAR(32),            -- 联系人
  biz_format    VARCHAR(16),            -- 业态：商业 / 纯销 / 零售
  project_id    VARCHAR(32),            -- 项目
  cost_amount   DECIMAL(14,2)           -- 还原后成本
);

CREATE TABLE batch_ledger (             -- 批次账簿：打通 SPU + SKU + 交易
  ledger_id     VARCHAR(32) PRIMARY KEY,
  spu_id        VARCHAR(32) NOT NULL,
  sku_id        VARCHAR(32) NOT NULL,
  batch_info_id VARCHAR(32) NOT NULL,
  order_id      VARCHAR(32),
  actual_cost   DECIMAL(14,2),          -- = 销价 - 返利（成本还原）
  contribution  DECIMAL(14,2)           -- 品种贡献度
);
-- 批次账簿是破解一品多码的核心：把多 SKU 按批归因回同一 SPU，
-- 结合返利把销价还原为真实成本，体现品种贡献度。
```

## 6. 批号生成规则

```
batch_no = encode(mf_name, prod_date, expiry_date, clarity, pkg_spec)
```

- 重启用旧批号：因 `prod_date` 纳入，新生产日期使复合键 `(spu_id, batch_no, prod_date)` 全局唯一，不冲突。
- 厂家更名不影响 SPU（主体未变），只更新 `batch_info.mf_name`。
- 真换厂家（主体变）：新 SPU + 新 `batch_info.mf_name`。

## 7. 公司 / 部门视图扩展

```sql
CREATE TABLE org_view_attr (            -- 商品 × 公司 / 部门视图 业务属性
  id           VARCHAR(32) PRIMARY KEY,
  spu_id       VARCHAR(32),
  sku_id       VARCHAR(32),
  company_id   VARCHAR(32),             -- 公司视图
  dept_id      VARCHAR(32),             -- 部门视图
  biz_domain   VARCHAR(16),             -- 采购 / 销售 / 运营 / 财务 / 质量
  attr_json    JSON,                    -- 该视图下的业务属性
  FOREIGN KEY (spu_id) REFERENCES spu(spu_id)
);
-- 业务属性挂在"商品 × 视图"维度表，不污染 SPU 主数据；数据分析按视图切片。
```
