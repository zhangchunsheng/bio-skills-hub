# 批量视觉裂变与两两差异账本

## 1. 独立场景差异轴

1. domain；
2. audience；
3. content_objective；
4. platform；
5. geography；
6. space_type；
7. time_weather；
8. subject_identity；
9. key_objects；
10. primary_action；
11. emotional_evidence；
12. camera_view；
13. composition；
14. focal_length；
15. lighting；
16. materials_palette；
17. text_strategy；
18. asset_role。

任意两条独立场景默认至少 8 个轴不同。用户要求同主题批量时，可降低行业和主题差异，但必须增加人群、时刻、动作、空间、机位和内容角色差异。

## 2. 系列模式

系列不要求世界不同，而要求：

- identity_signature 相同；
- timeline 连续；
- camera_view 至少两种；
- asset_role 不重复；
- primary_action 有递进；
- 每张新增有效信息。

## 3. 多比例模式

锁定：subject/product/space/time/action identity。

变化：aspect_ratio、composition、text_safe_zone、subject_scale、foreground、crop_logic。

所有比例都必须完整可用，不能有“主图只是上一版裁切”的字段。

## 4. 批次覆盖率

对于100条以上批次建议最低覆盖：

- ≥8个行业/主题；
- ≥8类人群或关系；
- ≥6类空间；
- ≥6种主动作；
- ≥5种机位；
- ≥4种时间/天气；
- ≥4种内容角色；
- ≥3种比例（若任务允许）。

具体目标由用户任务调整。

## 5. 近似重复

即使文字不同，以下情况仍视为近似重复：

- 同一人物模板+同一桌面+同一自然窗光；
- 同一门店门头+只换行业招牌；
- 同一产品+只换背景颜色；
- 同一城市街景+只换行人服装；
- 同一构图+只换季节滤镜；
- 同一系列角色重复承担相同信息。

## 6. 审计

```bash
python scripts/audit_visual_plan.py plan.json --strict
```

脚本输出最弱两两差异、覆盖率、主导模板和锁定项漂移。
