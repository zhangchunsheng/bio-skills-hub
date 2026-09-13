#!/bin/bash
# 自主学习效果量化评估脚本（医药版）
# 用于生成每日/周度/月度学习评估报告

LEARNING_DIR="$HOME/.workbuddy/learning_records_pharma"
mkdir -p "$LEARNING_DIR"

DATE=$(date +%Y-%m-%d)
WEEK=$(date +%Y-W%U)
MONTH=$(date +%Y-%m)

echo "=========================================="
echo "  医药财务总监·战略顾问 学习评估系统"
echo "  评估日期: $DATE"
echo "=========================================="

# 1. 每日学习记录收集
collect_daily_record() {
    local output_file="$LEARNING_DIR/daily_$DATE.json"

    cat > "$output_file" << 'TEMPLATE'
{
  "date": "'$DATE'",
  "learning_time_hours": 0,
  "new_policies_tracked": 0,
  "policies_list": [],
  "pipeline_analysis_cases": 0,
  "pipeline_analysis_list": [],
  "model_assumption_revisions": 0,
  "assumption_revisions_list": [],
  "learning_effectiveness_score": 0,
  "learning_ROI": 0,
  "core_ability_scores": {
    "task_planning": 0,
    "tool_usage": 0,
    "multi_turn_dialogue": 0,
    "code_generation": 0,
    "knowledge_accuracy": 0
  },
  "core_ability_total_score": 0,
  "summary": "待填写"
}
TEMPLATE

    echo "[每日记录] 已创建模板: $output_file"
    echo "  → 请编辑此文件填写今日学习记录"
}

# 2. 核心能力评估报告生成
generate_core_ability_report() {
    local output_file="$LEARNING_DIR/core_ability_$DATE.json"

    cat > "$output_file" << 'TEMPLATE'
{
  "assessment_date": "'$DATE'",
  "assessment_period": "每日",
  "task_planning": {
    "bd_deal_decomposition": {"score": 0, "description": "", "improvement": ""},
    "market_access_planning": {"score": 0, "description": "", "improvement": ""},
    "milestone_planning": {"score": 0, "description": "", "improvement": ""},
    "total": 0
  },
  "tool_usage": {
    "database_retrieval": {"score": 0, "description": "", "improvement": ""},
    "model_parameter_accuracy": {"score": 0, "description": "", "improvement": ""},
    "policy_interpretation": {"score": 0, "description": "", "improvement": ""},
    "total": 0
  },
  "multi_turn_dialogue": {
    "pipeline_context_memory": {"score": 0, "description": "", "improvement": ""},
    "cross_scenario_linking": {"score": 0, "description": "", "improvement": ""},
    "dialogue_coherence": {"score": 0, "description": "", "improvement": ""},
    "total": 0
  },
  "code_generation": {
    "pharma_model_code": {"score": 0, "description": "", "improvement": ""},
    "sensitivity_code": {"score": 0, "description": "", "improvement": ""},
    "coding_standard": {"score": 0, "description": "", "improvement": ""},
    "total": 0
  },
  "knowledge_accuracy": {
    "cde_policy_accuracy": {"score": 0, "description": "", "improvement": ""},
    "clinical_data_accuracy": {"score": 0, "description": "", "improvement": ""},
    "industry_knowledge_freshness": {"score": 0, "description": "", "improvement": ""},
    "total": 0
  },
  "core_ability_total_score": 0,
  "assessment": "待评估"
}
TEMPLATE

    echo "[核心能力报告] 已创建模板: $output_file"
    echo "  → 请编辑此文件完成核心能力自评"
}

# 3. 周度汇总
generate_weekly_summary() {
    local output_file="$LEARNING_DIR/weekly_$WEEK.json"

    echo "[周度汇总] 本周评估周: $WEEK"

    # 统计本周每日记录
    local weekly_policies=0
    local weekly_pipelines=0
    local weekly_revisions=0
    local weekly_hours=0

    for f in "$LEARNING_DIR"/daily_*.json; do
        if [ -f "$f" ]; then
            # 简单计数（实际使用中建议用jq解析）
            weekly_policies=$((weekly_policies + 1))
        fi
    done

    cat > "$output_file" << TEMPLATE
{
  "week": "$WEEK",
  "total_policies_tracked": $weekly_policies,
  "total_pipelines_analyzed": $weekly_pipelines,
  "total_model_revisions": $weekly_revisions,
  "total_learning_hours": $weekly_hours,
  "summary": "待汇总"
}
TEMPLATE

    echo "  已生成周度汇总: $output_file"
}

# 执行
collect_daily_record
generate_core_ability_report
generate_weekly_summary

echo ""
echo "=========================================="
echo "  评估模板生成完成！"
echo "  记录目录: $LEARNING_DIR"
echo "  请编辑生成的JSON文件填写实际数据"
echo "=========================================="
