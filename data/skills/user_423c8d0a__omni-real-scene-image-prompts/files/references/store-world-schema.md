# 店铺世界卡结构（内部使用）

## 1. Reality

- `reality_mode`: A / B / C
- `target_date`
- `target_scope`
- `truth_boundary`
- `evidence_manifest_id`
- `known_unknowns`

## 2. Geography

- `province_city_district`
- `street_or_town_scope`
- `terrain`
- `climate_season`
- `urban_morphology`
- `land_use`
- `micro_context`
- `property_type`
- `building_period`
- `road_system`
- `sidewalk_edge`
- `parking_delivery`
- `adjacent_uses`

## 3. Store identity

- `store_id`
- `store_category`
- `store_subtype`
- `price_band`
- `floor_area_m2`
- `bay_count`
- `frontage_m`
- `depth_m`
- `clear_height_m`
- `entrance_position`
- `door_opening`
- `window_positions`
- `columns_steps_ramps`
- `facade_structure`
- `primary_secondary_colors`
- `fixed_materials`
- `storefront_text_verbatim`
- `logo_authorization`
- `identity_signature`

## 4. Interior topology

- `customer_path`
- `employee_path`
- `goods_path`
- `delivery_path`
- `vehicle_path`
- `checkout`
- `display`
- `service_or_production`
- `waiting`
- `storage`
- `back_of_house`
- `sanitation_waste`
- `ventilation_exhaust_drainage_power`

所有空间必须能同时容纳设备、库存、人物和通道。不要只写风格词。

## 5. Business

- `core_equipment`
- `representative_inventory`
- `primary_operation`
- `secondary_operations`
- `payment`
- `handoff`
- `digital_commerce_evidence`
- `peak_pattern`
- `maintenance_level`

## 6. People and mobility

- `roles`
- `trip_purposes`
- `transport_modes`
- `entry_exit_directions`
- `dwell_times`
- `carried_objects`
- `actions`
- `weather_clothing`
- `privacy_constraints`

## 7. Camera

- `asset_type`
- `aspect_ratio`
- `camera_landing_point`
- `height_m`
- `distance_m`
- `angle`
- `equivalent_focal_length`
- `depth_of_field`
- `subject_coverage`
- `occlusions`
- `lighting`
- `material_response`

## 8. Locks and changes

- `must_keep`
- `may_change`
- `must_not_add`
- `reference_image_roles`

同店必须把结构化字段逐项锁定，不能只写一条自由文本签名。

## 9. 可见性过滤

最终提示词只写当前图位能看见或能影响画面的内容：

- 门头图不罗列看不见的后场小物；
- 室内图不虚构街区远处细节；
- 卫星视角不写人物和门头；
- 交易特写不承担完整建筑说明。

世界卡可以完整，最终提示词必须最少充分。
