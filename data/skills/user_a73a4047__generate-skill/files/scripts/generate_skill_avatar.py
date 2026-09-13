#!/usr/bin/env python3
"""为 Agent Skill 生成升级版 SVG 头像（渐变背景 + 精致图标 + 自适应 RS 品牌章）。"""
import argparse
import colorsys
import hashlib
import html
import re
import subprocess
from pathlib import Path

import yaml

# 每组：(主色渐变起, 主色渐变止, 装饰色, 图标色)
PALETTES = (
    ("#0D9488", "#14B8A6", "#5EEAD4", "#F0FDFA"),  # 青绿
    ("#4F46E5", "#7C3AED", "#A78BFA", "#EEF2FF"),  # 靛紫
    ("#BE185D", "#EC4899", "#F9A8D4", "#FDF2F8"),  # 玫红
    ("#059669", "#10B981", "#6EE7B7", "#ECFDF5"),  # 翠绿
    ("#DC2626", "#F97316", "#FDBA74", "#FFF7ED"),  # 橙红
    ("#7C3AED", "#A855F7", "#D8B4FE", "#FAF5FF"),  # 紫罗兰
    ("#0284C7", "#0EA5E9", "#7DD3FC", "#F0F9FF"),  # 天蓝
    ("#B45309", "#D97706", "#FCD34D", "#FFFBEB"),  # 琥珀
    ("#4338CA", "#6366F1", "#A5B4FC", "#EEF2FF"),  # 蓝紫
    ("#0F766E", "#14B8A6", "#99F6E4", "#F0FDFA"),  # 深青
    ("#9333EA", "#C084FC", "#E9D5FF", "#FAF5FF"),  # 亮紫
    ("#0891B2", "#22D3EE", "#A5F3FC", "#ECFEFF"),  # 青蓝
)


def hex_to_hsl(hex_color):
    """将 #RRGGBB 转为 (h, s, l) 0-1 范围。"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    return colorsys.rgb_to_hls(r, g, b)


def hsl_to_hex(h, s, l):
    """将 (h, s, l) 0-1 范围转为 #RRGGBB。"""
    r, g, b = colorsys.hls_to_rgb(h, s, l)
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


def darken_color(hex_color, factor=0.3):
    """将颜色变暗，factor 越小越暗。"""
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h, min(s * 1.2, 1.0), l * factor)


def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    return yaml.safe_load(match.group(1)) if match else {}


def read_title(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else path.parent.name


def select_motif(name, title, description):
    """根据 Skill 名称、标题和描述选择最匹配的 motif。名称优先级最高。"""
    # 先按名称匹配（最精确）
    name_rules = (
        (("ad-placement", "广告植入"), "ad"),
        (("adaptation-rights", "改编权利"), "shield"),
        (("ai-fact", "事实核查"), "fact"),
        (("authorized-watermark", "水印去除"), "image"),
        (("bid-document", "投标"), "bid"),
        (("business-health", "经营健康"), "chart"),
        (("business-image", "商业图片"), "image"),
        (("character-asset", "角色资产"), "character"),
        (("contract-use", "合同用途"), "contract"),
        (("digital-invoice", "发票"), "invoice"),
        (("end-to-end", "端到端"), "compass"),
        (("fiction-deai", "小说去AI"), "book"),
        (("generate-skill", "生成技能"), "spark"),
        (("image-text", "图片文字"), "image"),
        (("interview-evaluation", "面试"), "resume"),
        (("knowledge-base", "知识库"), "knowledge"),
        (("livestream", "直播"), "mic"),
        (("local-password", "密码"), "lock"),
        (("marketing-plan", "营销"), "megaphone"),
        (("minor-content", "未成年人"), "shield"),
        (("official-doc", "公文"), "book"),
        (("operations-plan", "运营"), "operations"),
        (("product-plan", "产品"), "product"),
        (("project-material", "项目材料"), "folder"),
        (("resume-screening", "简历"), "resume"),
        (("seal-version", "用印"), "seal"),
        (("social-media", "自媒体"), "book"),
        (("short-drama-cost", "成本"), "calculator"),
        (("short-drama-delivery", "交付"), "delivery"),
        (("short-drama-rhythm", "节奏"), "film"),
        (("short-drama-storyboard", "分镜"), "film"),
        (("spoken-text", "口述"), "pen"),
        (("strategy-plan", "战略"), "compass"),
        (("style-distill", "风格"), "style"),
        (("task-breakdown", "任务拆解"), "task"),
        (("test-case", "测试"), "test"),
        (("thesis-deai", "论文"), "book"),
        (("three-way-match", "三单"), "match"),
    )
    text = f"{name} {title}"
    for terms, motif in name_rules:
        if any(term.lower() in text.lower() for term in terms):
            return motif

    # 名称匹配不到再用描述
    desc_rules = (
        (("分镜", "镜头表", "storyboard"), "film"),
        (("口述", "润色", "转写", "spoken"), "pen"),
        (("风格", "蒸馏", "写作风格"), "style"),
        (("小说", "论文", "去AI", "去ai", "AIGC", "检测"), "book"),
        (("图片", "图像", "水印", "文字提取", "OCR"), "image"),
        (("发票", "报销", "归档", "数电票"), "invoice"),
        (("三单", "匹配", "对账", "采购订单"), "match"),
        (("成本估算", "预算", "报价"), "calculator"),
        (("经营健康", "经营分析", "增长方案"), "chart"),
        (("营销", "品牌传播", "投放", "媒体"), "megaphone"),
        (("战略", "转型", "市场进入"), "compass"),
        (("投标", "招标", "标书"), "bid"),
        (("改编权利", "授权", "版权"), "shield"),
        (("用印", "版本检查", "seal"), "seal"),
        (("未成年人", "内容检查"), "shield"),
        (("密码", "钥匙串", "安全", "Keychain"), "lock"),
        (("广告植入", "商业表达", "带货"), "ad"),
        (("直播", "话术", "口播"), "mic"),
        (("合规", "核验", "核对", "漏项", "过期"), "seal"),
        (("角色资产", "人物设定"), "character"),
        (("简历", "面试", "招聘", "筛选"), "resume"),
        (("任务拆解", "待办", "执行计划"), "task"),
        (("运营方案", "用户运营", "活动", "留存"), "operations"),
        (("产品方案", "需求文档", "功能"), "product"),
        (("交付验收", "交付检查", "文件验收"), "delivery"),
        (("测试用例", "测试"), "test"),
        (("项目材料", "申报", "投标材料"), "folder"),
        (("知识库", "FAQ", "过期", "帮助中心"), "knowledge"),
        (("AI", "事实核查", "幻觉"), "fact"),
        (("技能", "Skill", "生成"), "spark"),
        (("合同", "条款"), "contract"),
        (("材料", "撰写", "报告", "总结"), "document"),
        (("短剧", "剧本"), "film"),
    )
    for terms, motif in desc_rules:
        if any(term.lower() in description.lower() for term in terms):
            return motif
    return "document"
    for terms, motif in rules:
        if any(term.lower() in text.lower() for term in terms):
            return motif
    return "document"


def motif_svg(motif, icon_color, accent_color):
    """返回 motif 图标的 SVG 内容。每个图标定义在 256×256 标准框内，用 transform 统一缩放居中到画布 50% 高度。"""
    s = icon_color
    a = accent_color
    sw = "14"  # 加粗描边
    common = f'stroke="{s}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    fill_a = f'fill="{a}"'

    # 所有图标定义在 0~256 的标准框内，居中放置
    # 画布 512×512，图标占 50% 高度 = 256px，居中 y=128~384
    # transform: translate(128, 128) 把 0,0 移到左上角，图标自然居中
    shapes = {
        # 短剧/分镜：胶片条 + 播放三角
        "film": (
            f'<rect x="20" y="32" width="216" height="192" rx="24" {common} opacity="0.9"/>'
            f'<path d="M20 80h216M20 176h216" stroke="{s}" stroke-width="2.5" opacity="0.4"/>'
            f'<path d="M64 32v192M108 32v192M152 32v192M196 32v192" stroke="{s}" stroke-width="2.5" opacity="0.3"/>'
            f'<path d="M96 100l64 40-64 40z" {fill_a} opacity="0.9"/>'
        ),
        # 笔/润色/去AI：羽毛笔 + 文字行
        "pen": (
            f'<path d="M60 40l-30 120 40-10 100-100z" {common} opacity="0.9"/>'
            f'<path d="M30 160l-10 40 40-10" {common} opacity="0.8"/>'
            f'<path d="M100 140l80-80" stroke="{s}" stroke-width="3" opacity="0.5"/>'
            f'<path d="M140 180h80M140 210h60" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.6"/>'
        ),
        # 风格蒸馏：调色板 + 画笔
        "style": (
            f'<circle cx="128" cy="128" r="80" {common} opacity="0.9"/>'
            f'<circle cx="92" cy="100" r="12" {fill_a} opacity="0.8"/>'
            f'<circle cx="140" cy="88" r="12" {fill_a} opacity="0.7"/>'
            f'<circle cx="168" cy="128" r="12" {fill_a} opacity="0.6"/>'
            f'<circle cx="128" cy="168" r="12" {fill_a} opacity="0.7"/>'
            f'<path d="M196 196l40 40-20 5-5 20z" {common} opacity="0.8"/>'
        ),
        # 书本/小说/论文：打开的书
        "book": (
            f'<path d="M40 60c40-20 80-20 88 0v136c-8-20-48-20-88 0z" {common} opacity="0.9"/>'
            f'<path d="M216 60c-40-20-80-20-88 0v136c8-20 48-20 88 0z" {common} opacity="0.9"/>'
            f'<path d="M64 100h50M64 130h50M64 160h40" stroke="{s}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
            f'<path d="M192 100h-50M192 130h-50M192 160h-40" stroke="{s}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
        ),
        # 图片/水印/文字提取：画框 + 山 + 太阳
        "image": (
            f'<rect x="20" y="36" width="216" height="184" rx="24" {common} opacity="0.9"/>'
            f'<circle cx="72" cy="96" r="24" {fill_a} opacity="0.7"/>'
            f'<path d="M44 192l60-60 44 40 40-52 48 72" {common} opacity="0.85"/>'
        ),
        # 发票/报销：票据 + 勾选
        "invoice": (
            f'<rect x="48" y="36" width="160" height="184" rx="20" {common} opacity="0.9"/>'
            f'<path d="M48 76h160M48 116h160M48 156h160M48 196h160" stroke="{s}" stroke-width="2.5" opacity="0.4"/>'
            f'<path d="M72 56l12 12 24-28" stroke="{a}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
            f'<path d="M72 136l12 12 24-28" stroke="{a}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
        ),
        # 三单匹配/对比：天平
        "match": (
            f'<path d="M128 40v176" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M56 80h144" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M56 80l-28 56h56z" {common} opacity="0.7"/>'
            f'<path d="M200 80l-28 56h56z" {common} opacity="0.7"/>'
            f'<circle cx="128" cy="40" r="14" {fill_a} opacity="0.8"/>'
        ),
        # 成本估算/计算器：计算器
        "calculator": (
            f'<rect x="56" y="36" width="144" height="184" rx="20" {common} opacity="0.9"/>'
            f'<rect x="72" y="52" width="112" height="36" rx="8" fill="{a}" opacity="0.3"/>'
            f'<circle cx="88" cy="116" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="128" cy="116" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="168" cy="116" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="88" cy="152" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="128" cy="152" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="168" cy="152" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="88" cy="188" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="128" cy="188" r="10" {fill_a} opacity="0.7"/>'
            f'<circle cx="168" cy="188" r="10" {fill_a} opacity="0.7"/>'
        ),
        # 经营健康/图表：增长曲线
        "chart": (
            f'<path d="M36 200V100" stroke="{s}" stroke-width="3" opacity="0.5"/>'
            f'<path d="M36 200h184" stroke="{s}" stroke-width="3" opacity="0.5"/>'
            f'<path d="M56 180l40-40 36 24 48-60 36 20" stroke="{a}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
            f'<circle cx="56" cy="180" r="8" {fill_a} opacity="0.8"/>'
            f'<circle cx="96" cy="140" r="8" {fill_a} opacity="0.8"/>'
            f'<circle cx="132" cy="164" r="8" {fill_a} opacity="0.8"/>'
            f'<circle cx="180" cy="104" r="8" {fill_a} opacity="0.8"/>'
            f'<circle cx="216" cy="124" r="8" {fill_a} opacity="0.8"/>'
        ),
        # 营销/喇叭：扩音器
        "megaphone": (
            f'<path d="M56 100l100-40v120l-100-40z" {common} opacity="0.9"/>'
            f'<path d="M156 60v120" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
            f'<path d="M156 80h40v80h-40" {common} opacity="0.7"/>'
            f'<path d="M56 120h-28" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.6"/>'
            f'<path d="M220 90c20 20 20 50 0 70" stroke="{a}" stroke-width="3.5" stroke-linecap="round" fill="none" opacity="0.8"/>'
        ),
        # 战略/指南针：指南针
        "compass": (
            f'<circle cx="128" cy="128" r="92" {common} opacity="0.9"/>'
            f'<circle cx="128" cy="128" r="12" {fill_a} opacity="0.8"/>'
            f'<path d="M128 64l16 48 48 16-48 16-16 48-16-48-48-16 48-16z" {fill_a} opacity="0.6"/>'
            f'<path d="M128 36v16M128 204v16M36 128h16M204 128h16" stroke="{s}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
        ),
        # 投标/文件夹：文件夹 + 星标
        "bid": (
            f'<path d="M36 80h80l20 20h84v136H36z" {common} opacity="0.9"/>'
            f'<path d="M128 120l12 28 28 8-20 20 6 28-26-14-26 14 6-28-20-20 28-8z" {fill_a} opacity="0.85"/>'
        ),
        # 改编权利/盾牌：盾牌 + 勾选
        "shield": (
            f'<path d="M128 32l108 44v80c0 72-42 120-108 144-66-24-108-72-108-144V76z" {common} opacity="0.9"/>'
            f'<path d="M80 140l32 32 64-72" stroke="{a}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
        ),
        # 合规/用印/版本：印章/认证
        "seal": (
            f'<circle cx="128" cy="128" r="80" {common} opacity="0.9"/>'
            f'<circle cx="128" cy="128" r="56" stroke="{s}" stroke-width="3" opacity="0.5"/>'
            f'<path d="M96 128l20 20 36-40" stroke="{a}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
            f'<path d="M128 208v28M108 218l20 20 20-20" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.6"/>'
        ),
        # 密码/安全：挂锁
        "lock": (
            f'<rect x="76" y="120" width="104" height="100" rx="18" {common} opacity="0.9"/>'
            f'<path d="M96 120v-28c0-28 16-48 32-48s32 20 32 48v28" {common} opacity="0.85"/>'
            f'<circle cx="128" cy="164" r="12" {fill_a} opacity="0.85"/>'
            f'<path d="M128 176v20" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
        ),
        # 广告植入：广告标签
        "ad": (
            f'<rect x="36" y="56" width="184" height="144" rx="20" {common} opacity="0.9"/>'
            f'<path d="M68 100h120M68 140h80" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.6"/>'
            f'<circle cx="180" cy="80" r="22" {fill_a} opacity="0.8"/>'
            f'<path d="M172 80l6 6 12-14" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
        ),
        # 直播/麦克风：麦克风
        "mic": (
            f'<rect x="100" y="40" width="56" height="96" rx="28" {common} opacity="0.9"/>'
            f'<path d="M80 120v20c0 26 22 48 48 48s48-22 48-48v-20" {common} opacity="0.8"/>'
            f'<path d="M128 188v28" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
            f'<path d="M108 216h40" stroke="{s}" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
        ),
        # 角色资产：人像 + 服装
        "character": (
            f'<circle cx="128" cy="80" r="44" {common} opacity="0.9"/>'
            f'<path d="M64 216c8-52 36-80 64-80s56 28 64 80" {common} opacity="0.85"/>'
            f'<path d="M108 96l20 20 20-20" stroke="{a}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.8"/>'
        ),
        # 简历/面试/招聘：简历文档 + 人像
        "resume": (
            f'<rect x="36" y="36" width="120" height="160" rx="18" {common} opacity="0.9"/>'
            f'<circle cx="96" cy="80" r="24" {common} opacity="0.8"/>'
            f'<path d="M60 140h60M60 164h60" stroke="{s}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
            f'<path d="M180 100l16 16 32-36" stroke="{a}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
        ),
        # 任务拆解：树状图
        "task": (
            f'<circle cx="128" cy="48" r="22" {common} opacity="0.9"/>'
            f'<path d="M128 70v30" stroke="{s}" stroke-width="3.5" opacity="0.7"/>'
            f'<path d="M128 100l-72 50" stroke="{s}" stroke-width="3.5" opacity="0.6"/>'
            f'<path d="M128 100v50" stroke="{s}" stroke-width="3.5" opacity="0.6"/>'
            f'<path d="M128 100l72 50" stroke="{s}" stroke-width="3.5" opacity="0.6"/>'
            f'<circle cx="56" cy="160" r="18" {common} opacity="0.8"/>'
            f'<circle cx="128" cy="160" r="18" {common} opacity="0.8"/>'
            f'<circle cx="200" cy="160" r="18" {common} opacity="0.8"/>'
            f'<path d="M56 178v20M56 178l-24 20" stroke="{s}" stroke-width="2.5" opacity="0.4"/>'
            f'<path d="M128 178v20" stroke="{s}" stroke-width="2.5" opacity="0.4"/>'
            f'<path d="M200 178v20M200 178l24 20" stroke="{s}" stroke-width="2.5" opacity="0.4"/>'
            f'<circle cx="32" cy="208" r="10" {fill_a} opacity="0.6"/>'
            f'<circle cx="56" cy="208" r="10" {fill_a} opacity="0.6"/>'
            f'<circle cx="128" cy="208" r="10" {fill_a} opacity="0.6"/>'
            f'<circle cx="200" cy="208" r="10" {fill_a} opacity="0.6"/>'
            f'<circle cx="224" cy="208" r="10" {fill_a} opacity="0.6"/>'
        ),
        # 运营方案：用户路径/漏斗
        "operations": (
            f'<path d="M56 60h144l-36 56v36l-36 36v36l-36 20" {common} opacity="0.9"/>'
            f'<circle cx="128" cy="60" r="12" {fill_a} opacity="0.8"/>'
            f'<circle cx="128" cy="116" r="12" {fill_a} opacity="0.7"/>'
            f'<circle cx="128" cy="172" r="12" {fill_a} opacity="0.6"/>'
            f'<circle cx="108" cy="216" r="12" {fill_a} opacity="0.5"/>'
        ),
        # 产品方案：产品/功能模块
        "product": (
            f'<rect x="36" y="56" width="80" height="80" rx="16" {common} opacity="0.8"/>'
            f'<rect x="140" y="56" width="80" height="80" rx="16" {common} opacity="0.8"/>'
            f'<rect x="36" y="156" width="80" height="80" rx="16" {common} opacity="0.8"/>'
            f'<rect x="140" y="156" width="80" height="80" rx="16" {common} opacity="0.8"/>'
            f'<circle cx="76" cy="96" r="14" {fill_a} opacity="0.7"/>'
            f'<circle cx="180" cy="96" r="14" {fill_a} opacity="0.6"/>'
        ),
        # 交付验收：包裹/交付
        "delivery": (
            f'<rect x="56" y="76" width="144" height="120" rx="18" {common} opacity="0.9"/>'
            f'<path d="M56 116h144" stroke="{s}" stroke-width="3" opacity="0.5"/>'
            f'<path d="M128 76v120" stroke="{s}" stroke-width="3" opacity="0.4"/>'
            f'<path d="M100 136l20 20 36-40" stroke="{a}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
        ),
        # 测试用例：测试/bug
        "test": (
            f'<rect x="36" y="40" width="184" height="176" rx="20" {common} opacity="0.9"/>'
            f'<path d="M72 100l20 20 36-40" stroke="{a}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none" opacity="0.9"/>'
            f'<path d="M72 160h100" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.5"/>'
            f'<path d="M72 190h70" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.5"/>'
        ),
        # 项目材料/文件夹：文件夹
        "folder": (
            f'<path d="M36 80h80l20 20h88v136H36z" {common} opacity="0.9"/>'
            f'<path d="M68 140h120M68 172h120M68 204h80" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.5"/>'
        ),
        # 知识库/FAQ：搜索/知识
        "knowledge": (
            f'<circle cx="112" cy="112" r="60" {common} opacity="0.9"/>'
            f'<path d="M156 156l50 50" stroke="{s}" stroke-width="5" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M92 112h40M112 92v40" stroke="{a}" stroke-width="3.5" stroke-linecap="round" opacity="0.7"/>'
        ),
        # AI 事实核查：放大镜 + 文档
        "fact": (
            f'<rect x="36" y="56" width="120" height="140" rx="16" {common} opacity="0.8"/>'
            f'<path d="M68 96h60M68 128h60M68 160h40" stroke="{s}" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
            f'<circle cx="180" cy="176" r="36" {common} opacity="0.9"/>'
            f'<path d="M206 202l24 24" stroke="{s}" stroke-width="5" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M164 176h32M180 160v32" stroke="{a}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>'
        ),
        # 技能生成：星星
        "spark": (
            f'<path d="M128 36l20 64 64 20-64 20-20 64-20-64-64-20 64-20z" {fill_a} opacity="0.85"/>'
            f'<path d="M200 180l12 36 36 12-36 12-12 36-12-36-36-12 36-12z" fill="{s}" opacity="0.5"/>'
            f'<path d="M60 196l10 28 28 10-28 10-10 28-10-28-28-10 28-10z" fill="{s}" opacity="0.35"/>'
        ),
        # 合同：合同文档
        "contract": (
            f'<path d="M56 36h104l56 56v148H56z" {common} opacity="0.9"/>'
            f'<path d="M160 36v60h56" {common} opacity="0.5"/>'
            f'<path d="M88 140h100M88 180h100M88 220h60" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.5"/>'
            f'<circle cx="196" cy="220" r="18" {fill_a} opacity="0.6"/>'
        ),
        # 文档/材料：文档
        "document": (
            f'<path d="M56 36h104l56 56v148H56z" {common} opacity="0.9"/>'
            f'<path d="M160 36v60h56" {common} opacity="0.5"/>'
            f'<path d="M88 140h100M88 180h100M88 220h60" stroke="{s}" stroke-width="3.5" stroke-linecap="round" opacity="0.5"/>'
            f'<circle cx="196" cy="220" r="18" {fill_a} opacity="0.6"/>'
        ),
    }
    # 用 transform 把 256×256 的图标缩放到 307×307（画布 60%），垂直居中
    icon_content = shapes.get(motif, shapes["document"])
    return f'<g transform="translate(102,102) scale(1.2)">{icon_content}</g>'


def render_svg(size, title, motif, palette):
    c1, c2, accent, icon_color = palette
    label = html.escape(title)
    icon = motif_svg(motif, icon_color, accent)
    # RS 章颜色：根据背景主色生成协调的深色版本，但保留色相
    h1, s1, l1 = hex_to_hsl(c1)
    h2, s2, l2 = hex_to_hsl(c2)
    # 使用背景色的色相，但降低明度、提高饱和度，形成深色但同色系的效果
    badge_c1 = hsl_to_hex(h1, min(s1 * 1.3, 1.0), l1 * 0.35)
    badge_c2 = hsl_to_hex(h2, min(s2 * 1.3, 1.0), l2 * 0.3)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 512 512" role="img" aria-label="{label}">
  <defs>
    <linearGradient id="bg-{label}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <radialGradient id="glow-{label}" cx="0.3" cy="0.25" r="0.7">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="badge-{label}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{badge_c1}"/>
      <stop offset="100%" stop-color="{badge_c2}"/>
    </linearGradient>
    <filter id="iconShadow-{label}" x="-20%" y="-20%" width="150%" height="150%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.2"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="104" fill="url(#bg-{label})"/>
  <rect width="512" height="512" rx="104" fill="url(#glow-{label})"/>
  <circle cx="400" cy="100" r="120" fill="#FFFFFF" opacity="0.06"/>
  <circle cx="80" cy="440" r="90" fill="#FFFFFF" opacity="0.05"/>
  <g filter="url(#iconShadow-{label})">{icon}</g>
  <g transform="translate(420,420)">
    <circle r="72" fill="url(#badge-{label})" stroke="#FFFFFF" stroke-width="4.5" stroke-opacity="0.5"/>
    <text y="14" text-anchor="middle" fill="#FFFFFF" font-family="&#39;SF Pro Display&#39;,&#39;Helvetica Neue&#39;,Arial,sans-serif" font-size="48" font-weight="700" letter-spacing="1">RS</text>
  </g>
</svg>
'''


def update_openai_yaml(skill_dir, display_name, description, name):
    path = skill_dir / "agents" / "openai.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    data = data or {}
    interface = data.setdefault("interface", {})
    interface.setdefault("display_name", display_name)
    interface.setdefault("short_description", description[:64])
    interface.setdefault("default_prompt", f"使用 ${name} 完成这项任务。")
    interface["icon_small"] = "./assets/avatar-small.svg"
    interface["icon_large"] = "./assets/avatar.svg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def render_skillhub_png(svg_path, png_path):
    result = subprocess.run(
        ["sips", "-s", "format", "png", str(svg_path), "--out", str(png_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not png_path.is_file():
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise RuntimeError(f"生成 Skill Hub PNG 头像失败: {detail}")


def generate(skill_dir):
    meta = read_frontmatter(skill_dir / "SKILL.md")
    name = str(meta.get("name") or skill_dir.name)
    description = str(meta.get("description") or "")
    title = read_title(skill_dir / "SKILL.md")
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    palette = PALETTES[digest[0] % len(PALETTES)]
    motif = select_motif(name, title, description)
    assets = skill_dir / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "avatar-small.svg").write_text(render_svg(128, title, motif, palette), encoding="utf-8")
    avatar_svg = assets / "avatar.svg"
    avatar_svg.write_text(render_svg(512, title, motif, palette), encoding="utf-8")
    render_skillhub_png(avatar_svg, assets / "avatar-skillhub.png")
    update_openai_yaml(skill_dir, title, description, name)
    return {"name": name, "title": title, "motif": motif}


def main():
    parser = argparse.ArgumentParser(description="为 Agent Skill 生成升级版 SVG 头像并更新 openai.yaml。")
    parser.add_argument("skill_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    for raw in args.skill_dirs:
        skill_dir = raw.resolve()
        if not (skill_dir / "SKILL.md").exists():
            raise SystemExit(f"缺少 SKILL.md: {skill_dir}")
        result = generate(skill_dir)
        print(f"generated {result['name']} motif={result['motif']}")


if __name__ == "__main__":
    main()
