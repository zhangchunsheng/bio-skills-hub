# R12 通用真实世界卡

世界卡只在内部使用，不向用户输出。

## 1. 事实层

```yaml
truth_mode: A|B|C|D
claim_scope: exact_subject|evidence_based_original|general_concept|speculative_reconstruction
source_date:
permission:
truth_boundary:
```

## 2. 地理与本地化层

```yaml
country:
province_state:
city_county:
micro_location:
terrain:
climate:
urban_rural_morphology:
built_period:
land_use:
local_infrastructure:
```

非地点场景也必须说明其所处文化、行业和生活语境。

## 3. 时间层

```yaml
era:
season:
day_type: weekday|weekend|holiday|event_day
clock_time:
weather:
light_direction:
recent_conditions:
```

近期下雨会影响地面、鞋底、车辆和伞；冬季会影响衣着、植物、日照角度和室内外温差。

## 4. 空间层

```yaml
space_type:
dimensions:
openings:
levels:
obstacles:
functional_zones:
entry_exit:
human_flow:
goods_vehicle_flow:
safety_clearance:
```

## 5. 主体层

```yaml
subject_type:
identity_signature:
age_or_lifecycle:
body_or_geometry:
clothing_or_surface:
condition:
position:
orientation:
```

## 6. 物体与材料层

```yaml
key_objects:
tools_equipment:
materials:
wear_state:
cleanliness_state:
packaging_or_labels:
contact_relations:
```

## 7. 动作与流程层

```yaml
primary_action:
secondary_actions:
precondition:
tool_object_relation:
visible_result:
next_step:
process_flow:
```

## 8. 社会关系层

```yaml
roles:
relationships:
visit_or_work_purpose:
interaction_direction:
transport_mode:
crowd_density:
privacy_level:
```

## 9. 摄影光学层

```yaml
camera_location:
camera_height:
distance:
angle:
focal_length_equivalent:
aperture_behavior:
shutter_motion:
exposure_balance:
composition:
foreground_midground_background:
text_safe_zone:
```

## 10. 文字与品牌层

```yaml
brand_status: authorized|original|generic|none
p0_text:
p1_text:
background_text_policy:
layout_hierarchy:
ui_policy:
```

## 11. 连续性层

```yaml
series_id:
subject_lock:
product_lock:
space_lock:
time_lock:
allowed_variations:
forbidden_drift:
```

## 12. 合规层

```yaml
personal_data:
minor_policy:
medical_financial_legal_policy:
public_event_policy:
synthetic_label:
prohibited_claims:
```

## 13. 因果审计

至少检查：

- 地域是否支持建筑、植物、衣着和交通；
- 时间天气是否支持光线、地面和行为；
- 空间是否支持设备、动作和流线；
- 身份是否支持服装、工具和姿态；
- 动作是否产生可见结果；
- 相机是否能在该位置看到所写内容；
- 文字是否适合交给模型直接生成；
- 画面是否会被误认作现实证据。

## 14. 验证

```bash
python scripts/validate_scene_world.py tests/sample_scene_world.json --strict
```
