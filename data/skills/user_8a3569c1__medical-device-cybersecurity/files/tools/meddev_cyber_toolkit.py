#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meddev_cyber_toolkit.py — 医疗器械网络安全合规速查工具（零依赖、零网络、纯本地）

命令：
  reg --region <us|eu|cn>      区域网络安全注册要求速查
  checklist --phase <phase>    分阶段网络安全检查清单（design/development/submission/postmarket）
  sbom                         输出 SBOM JSON 字段模板（NTIA 最低要素 + FDA 补充）
  vuln --desc <描述>           CVSS 风格漏洞分级参考
  standard                     标准速查表
  --help                       全部命令说明

用法示例：
  python meddev_cyber_toolkit.py reg --region us
  python meddev_cyber_toolkit.py checklist --phase submission
  python meddev_cyber_toolkit.py sbom
  python meddev_cyber_toolkit.py vuln --desc "远程可被利用执行任意代码"
  python meddev_cyber_toolkit.py standard

注意：本工具仅输出规则速查与模板，不发起扫描、不采集数据、不联网。
核对基准日：2026-08-27
"""

import argparse
import json
import sys

BASELINE_DATE = "2026-08-27"

# ---------------------------------------------------------------- 区域要求
REGIONS = {
    "us": {
        "name": "美国 FDA（Cyber Device）",
        "baseline": "2026-02-03 最终指南 + FD&C Act §524B + QMSR（2026-02-02 生效）",
        "requirements": [
            "网络安全纳入 QMS（QMSR/ISO 13485:2016），SPDF 证据",
            "威胁建模（STRIDE/攻击树等，方法+结果+残余风险）",
            "安全架构视图（全局系统/多患者伤害/可更新可修补）",
            "安全风险评估（按可利用性评估，核查 CISA KEV）",
            "SBOM（机器可读，NTIA 最低要素，§524B 法定强制）",
            "安全测试报告（渗透/模糊/静态/漏洞扫描，独立团队，对应提交版本）",
            "CVD 协调漏洞披露流程",
            "上市后监控计划 + 补丁/更新机制",
            "网络安全标签（配置/更新/退役）",
            "风险-控制-测试可追溯矩阵",
            "缺 SBOM/渗透测试等关键项 = RTA 拒绝受理（2023-10-01 起有权）",
        ],
        "hint": "cyber device = 含软件 + 具备联网能力（Wi-Fi/蓝牙/USB/串口/NFC 等）+ 易受攻击技术特征；违反 §524B(b) 属 §301(q) 禁止行为",
    },
    "eu": {
        "name": "欧盟（MDR + NIS2 + CRA）",
        "baseline": "MDR Annex I 17.2 现行强制；CRA (EU) 2024/2847：2026-09-11 报告义务、2027-12-11 全面适用",
        "requirements": [
            "MDR Annex I 17.2：与风险相称的 IT 安全措施（参照 81001-5-1）",
            "CRA：产品分级（Default/Important I/Important II/Critical）确定符合性路径",
            "CRA 报告义务（2026-09-11 起）：24h 预警 / 72h 完整 / 14 天最终（ENISA + CSIRT）",
            "CRA：机器可读 SBOM（至少顶层依赖，随时可提供）",
            "CRA：安全默认配置、最小攻击面、无已知可利用漏洞、安全更新支持",
            "CRA 全面适用（2027-12-11 起）：符合性评定 + CE 标志 + 技术文档",
            "NIS2：医疗机构/重要实体网络安全管理与事件报告",
            "医械本体豁免 CRA，但供应链组件/非医械软件/远程处理在范围内",
            "罚款上限：1500 万欧或全球营业额 2.5%",
        ],
        "hint": "注意区分：医械产品走 MDR（豁免 CRA），配套软件/组件走 CRA；报告义务覆盖已上市产品",
    },
    "cn": {
        "name": "中国 NMPA",
        "baseline": "《医疗器械网络安全注册审查指导原则（2025 年修订版）》（网络安全能力 22 项）",
        "requirements": [
            "网络安全描述文档（单独提交，覆盖数据架构/能力/补丁/安全软件/风险管理/验证确认/可追溯/维护/漏洞评估）",
            "产品技术要求：明确数据接口、用户访问控制",
            "说明书：明确网络安全相关内容",
            "网络安全能力 22 项（2025 修订版，较 2022 版 19 项扩充）",
            "网络安全更新：编写网络安全更新研究报告（重大/轻微功能更新或补丁合并）",
            "网络安全事件应急响应 + 全生命周期质控（2025 修订版新增）",
            "医疗数据出境评估（2025 修订版新增，衔接数据出境规定与人遗条例）",
            "遗留设备（legacy device）判定与管理（2025 修订版新增）",
            "上位法：网络安全法（2026-01-01 修订版施行）、数据安全法、个保法",
        ],
        "hint": "适用：具有网络连接功能（电子数据交换/远程控制）或采用存储媒介交换数据的第二、三类器械，覆盖注册/变更/延续",
    },
}


def cmd_reg(args):
    region = REGIONS.get(args.region)
    if not region:
        print("未知区域，可选：us / eu / cn")
        return 1
    print(f"=== {region['name']} ===")
    print(f"核对基准日：{region['baseline']}\n")
    for i, r in enumerate(region["requirements"], 1):
        print(f"{i}. {r}")
    print(f"\n提示：{region['hint']}")
    return 0


# ---------------------------------------------------------------- 检查清单
PHASES = {
    "design": [
        "威胁建模（识别攻击面/信任边界/风险路径）",
        "安全架构设计（数据流图/架构视图）",
        "安全需求纳入需求规范（可追溯 ID）",
        "组件选型评估（供应链安全，OTS 组件安全能力确认）",
        "网络安全风险评估（ISO 14971 联动，按可利用性）",
        "安全默认配置原则（最小权限/最小功能）",
    ],
    "development": [
        "安全编码规范与静态分析（SAST）",
        "SBOM 生成（构建期自动化，版本绑定）",
        "组件漏洞匹配（NVD/KEV/厂商公告）",
        "安全测试（模糊/渗透/漏洞扫描，独立团队）",
        "数据加密与传输安全实现",
        "更新/补丁机制实现与验证（patchability）",
    ],
    "submission": [
        "网络安全描述文档（NMPA）/ 网络安全管理计划（FDA）",
        "威胁建模分析报告",
        "安全架构视图（全局/多患者伤害/可更新可修补）",
        "安全风险评估报告",
        "SBOM（机器可读，对应提交版本）+ 漏洞分析",
        "安全测试报告（版本一致，独立团队执行）",
        "CVD 流程文档",
        "上市后监控计划",
        "网络安全标签内容",
        "风险-控制-测试可追溯矩阵",
        "文档×代码/文档×版本一致性自查",
    ],
    "postmarket": [
        "漏洞监控机制（SBOM 匹配持续化）",
        "CVD 接收渠道（security 联系点/VDP）",
        "漏洞分级与修复时限执行",
        "补丁发布与用户通知流程",
        "网络安全事件应急响应（预案+演练）",
        "欧盟 CRA 报告义务（24h/72h/14 天，2026-09-11 起）",
        "上市后监控记录归档（FDA/NMPA 审查证据）",
    ],
}


def cmd_checklist(args):
    phases = [args.phase] if args.phase else list(PHASES.keys())
    for p in phases:
        if p not in PHASES:
            print(f"未知阶段：{p}，可选：design / development / submission / postmarket")
            return 1
        print(f"=== {p} 阶段检查清单 ===")
        for i, item in enumerate(PHASES[p], 1):
            print(f"  [ ] {item}")
        print()
    return 0


# ---------------------------------------------------------------- SBOM 模板
SBOM_TEMPLATE = {
    "format": "cyclonedx",
    "spec_version": "1.5",
    "metadata": {
        "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
        "tools": [{"name": "sbom-tool", "version": "x.y.z"}],
        "component": {
            "type": "application",
            "name": "设备软件名称",
            "version": "发布版本号",
            "supplier": {"name": "供应商名称"},
        },
    },
    "components": [
        {
            "type": "library",
            "name": "组件名称",
            "version": "组件版本",
            "purl": "pkg:type/namespace/name@version",
            "hashes": [{"alg": "SHA-256", "content": "组件哈希"}],
            "supplier": {"name": "组件供应商"},
            "properties": [
                {"name": "support-status", "value": "supported / end-of-life"},
                {"name": "end-of-support-date", "value": "YYYY-MM-DD"},
                {"name": "license", "value": "MIT / Apache-2.0 / ..."},
            ],
        }
    ],
    "dependencies": [
        {"ref": "设备软件", "dependsOn": ["组件A", "组件B"]}
    ],
    "vulnerabilities": [
        {
            "id": "CVE-2026-0000",
            "source": {"name": "NVD / CISA KEV / 厂商公告"},
            "ratings": [{"score": 9.8, "severity": "critical", "method": "CVSSv4"}],
            "analysis": {"state": "affected / not_affected / resolved / under_investigation"},
            "affects": [{"ref": "组件A"}],
        }
    ],
}


def cmd_sbom(args):
    print(json.dumps(SBOM_TEMPLATE, ensure_ascii=False, indent=2))
    print("\n# NTIA 最低要素：供应商名称/组件名称/组件版本/组件哈希/依赖关系/作者/时间戳")
    print("# FDA 补充建议：支持状态、停止支持日期、已知漏洞核查（CISA KEV）")
    return 0


# ---------------------------------------------------------------- 漏洞分级
def cmd_vuln(args):
    desc = args.desc or ""
    score_hint = "6.0（中危参考）"
    level = "中危"
    if any(k in desc for k in ["远程", "任意代码", "未授权", "全部", "数据泄露", "root", "RCE"]):
        score_hint = "9.0-10.0"
        level = "严重"
    elif any(k in desc for k in ["越权", "注入", "绕过", "提权", "敏感", "大量"]):
        score_hint = "7.0-8.9"
        level = "高危"
    elif any(k in desc for k in ["本地", "低权限", "信息", "枚举", "泄露少量"]):
        score_hint = "4.0-6.9"
        level = "中危"
    print(f"描述：{desc or '（未提供，示例输出）'}")
    print(f"CVSS 分级参考：{level}（{score_hint}）")
    print("注意：最终分级须结合本器械使用场景与患者安全影响（ISO 14971 视角），")
    print("      并核查 CISA KEV 目录确认是否已被积极利用。")
    return 0


# ---------------------------------------------------------------- 标准速查
STANDARDS = [
    ("ISO/IEC 81001-5-1:2021", "健康软件/健康 IT 全生命周期网络安全（主干标准）"),
    ("ISO 13485:2016", "医疗器械 QMS（FDA QMSR 并入引用）"),
    ("IEC 62304", "医疗器械软件生命周期"),
    ("ISO 14971:2019", "医疗器械风险管理（网络安全风险纳入）"),
    ("ISO/IEC 27001", "组织信息安全管理（非产品网络安全替代）"),
    ("IEC 62443", "工业自动化与控制系统安全"),
    ("ISO/IEC 15408 (CC)", "通用评估准则（深度安全评估参考）"),
    ("NTIA SBOM 最低要素", "SBOM 字段基线（FDA 认可）"),
    ("SPDX / CycloneDX", "SBOM 机器可读格式（FDA 均接受）"),
    ("CVSS v4.0", "漏洞评分体系（2023-11 发布）"),
]


def cmd_standard(args):
    print("=== 标准速查表 ===")
    for name, desc in STANDARDS:
        print(f"  {name:<28s} {desc}")
    print("\n关联法规：FD&C §524B（美）、MDR Annex I 17.2 + NIS2 + CRA（欧）、")
    print("          NMPA 网络安全注册审查指导原则（中）")
    return 0


# ---------------------------------------------------------------- 主入口
def main():
    p = argparse.ArgumentParser(
        prog="meddev_cyber_toolkit",
        description="医疗器械网络安全合规速查（零依赖、零网络、纯本地）",
    )
    sub = p.add_subparsers(dest="cmd")

    p_reg = sub.add_parser("reg", help="区域要求速查")
    p_reg.add_argument("--region", required=True, choices=["us", "eu", "cn"])

    p_chk = sub.add_parser("checklist", help="分阶段检查清单")
    p_chk.add_argument("--phase", choices=list(PHASES.keys()), default=None)

    sub.add_parser("sbom", help="SBOM JSON 字段模板")

    p_vuln = sub.add_parser("vuln", help="漏洞分级参考")
    p_vuln.add_argument("--desc", default="")

    sub.add_parser("standard", help="标准速查表")

    args = p.parse_args()
    if args.cmd == "reg":
        return cmd_reg(args)
    if args.cmd == "checklist":
        return cmd_checklist(args)
    if args.cmd == "sbom":
        return cmd_sbom(args)
    if args.cmd == "vuln":
        return cmd_vuln(args)
    if args.cmd == "standard":
        return cmd_standard(args)
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
