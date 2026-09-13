#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""医疗器械 MDR 合规审计工具
依据欧盟 MDR 2017/745 法规检查技术文档的合规性

作者：AIPOCH
版本：1.1.0"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any


class ComplianceStatus(Enum):
    """合规状态"""
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class FindingCategory(Enum):
    """发现问题的分类"""
    CRITICAL = "CRITICAL"      # 严重缺陷 —— 可能导致不合规
    MAJOR = "MAJOR"            # 重大缺陷 —— 需要整改
    MINOR = "MINOR"            # 轻微缺陷 —— 建议改进
    INFO = "INFO"              # 信息提示


class CheckStatus(Enum):
    """检查状态"""
    PRESENT = "PRESENT"
    MISSING = "MISSING"
    INCOMPLETE = "INCOMPLETE"
    UNKNOWN = "UNKNOWN"


@dataclass
class Finding:
    """审计发现的问题"""
    category: FindingCategory
    regulation: str
    item: str
    status: CheckStatus
    description: str
    file_path: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class AuditSummary:
    """审计摘要"""
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0


@dataclass
class AuditReport:
    """审计报告"""
    audit_date: str = ""
    device_class: str = ""
    input_path: str = ""
    compliance_status: ComplianceStatus = ComplianceStatus.UNKNOWN
    findings: List[Finding] = field(default_factory=list)
    summary: AuditSummary = field(default_factory=AuditSummary)


class MDRChecker:
    """MDR 合规检查器"""

    # MDR 法规规定的关键文档要求
    REQUIRED_DOCUMENTS = {
        "I": [
            ("Clinical Evaluation", "clinical assessment", False),  # I 类可选
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance", "Post-market surveillance plan", True),
        ],
        "IIa": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
        ],
        "IIb": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
            ("SSCP", "Safety and clinical performance summary", True),
        ],
        "III": [
            ("Clinical Evaluation Report", "clinical evaluation report", True),
            ("Clinical Evaluation Plan", "clinical assessment plan", True),
            ("Risk Management", "risk management documents", True),
            ("Technical Documentation", "Technical documentation", True),
            ("Post-Market Surveillance Plan", "Post-market surveillance plan", True),
            ("PMCF Plan", "Post-marketing clinical follow-up plan", True),
            ("SSCP", "Safety and clinical performance summary", True),
            ("PMCF Evaluation Report", "PMCF Assessment Report", True),
        ],
    }

    # 文件关键词映射
    FILE_PATTERNS = {
        "Clinical Evaluation Report": [
            r"clinical[_\s]?evaluation[_\s]?report",
            r"cer[_\s]?",
            "clinical evaluation report",
            "clinical evaluation report",
        ],
        "Clinical Evaluation Plan": [
            r"clinical[_\s]?evaluation[_\s]?plan",
            r"cep[_\s]?",
            "clinical assessment plan",
            "clinical evaluation plan",
        ],
        "Risk Management": [
            r"risk[_\s]?management",
            "risk management",
            r"iso[_\s]?14971",
        ],
        "Post-Market Surveillance Plan": [
            r"post[_\s]?market[_\s]?surveillance",
            r"pms[_\s]?plan",
            "Post-market surveillance plan",
            "Post-market surveillance plan",
        ],
        "PMCF Plan": [
            r"pmcf[_\s]?plan",
            r"post[_\s]?market[_\s]?clinical[_\s]?follow[_\s]?up",
            "Post-marketing clinical follow-up",
            "pmcf[_\\s]?Evaluation",
        ],
        "SSCP": [
            r"sscp",
            r"summary[_\s]?of[_\s]?safety[_\s]?and[_\s]?clinical[_\s]?performance",
            "Safety and clinical performance summary",
        ],
        "PMCF Evaluation Report": [
            r"pmcf[_\s]?evaluation[_\s]?report",
            r"pmcf[_\s]?report",
            "pmcf assessment report",
        ],
    }

    def __init__(self, input_path: str, device_class: str, verbose: bool = False):
        self.input_path = Path(input_path)
        self.device_class = device_class.upper()
        self.verbose = verbose
        self.found_files: Dict[str, List[Path]] = {}
        self.report = AuditReport(
            audit_date=datetime.utcnow().isoformat() + "Z",
            device_class=self.device_class,
            input_path=str(self.input_path.absolute()),
        )

    def log(self, message: str):
        """输出日志"""
        if self.verbose:
            print(f"[MDR Auditor] {message}")

    def scan_files(self) -> Dict[str, List[Path]]:
        """扫描目录中的文件"""
        self.log(f"扫描目录: {self.input_path}")

        if not self.input_path.exists():
            raise FileNotFoundError(f"输入路径不存在: {self.input_path}")

        found = {}
        all_files = list(self.input_path.rglob("*"))

        for doc_type, patterns in self.FILE_PATTERNS.items():
            found[doc_type] = []
            for file_path in all_files:
                if file_path.is_file():
                    file_name = file_path.name.lower()
                    for pattern in patterns:
                        if re.search(pattern, file_name, re.IGNORECASE):
                            found[doc_type].append(file_path)
                            self.log(f"发现文件: {doc_type} -> {file_path}")
                            break

        self.found_files = found
        return found

    def check_document_completeness(self, doc_type: str, files: List[Path]) -> Finding:
        """检查文档完整性"""
        required_docs = self.REQUIRED_DOCUMENTS.get(self.device_class, [])
        is_required = any(d[0] == doc_type and d[2] for d in required_docs)

        if not files:
            if is_required:
                return Finding(
                    category=FindingCategory.CRITICAL,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.MISSING,
                    description=f"未找到{doc_type}相关文档",
                    recommendation=f"依据MDR要求，需提供{doc_type}"
                )
            else:
                return Finding(
                    category=FindingCategory.INFO,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.MISSING,
                    description=f"未找到{doc_type}（对Class {self.device_class}为可选项）",
                    recommendation="建议提供以提升合规水平"
                )

        # 检查文件内容完整性（简化检查）
        for file_path in files:
            if file_path.stat().st_size < 1000:  # 小于1KB可能是空文件或占位文件
                return Finding(
                    category=FindingCategory.MAJOR,
                    regulation=self._get_regulation_ref(doc_type),
                    item=doc_type,
                    status=CheckStatus.INCOMPLETE,
                    description=f"{doc_type}文件可能不完整（文件过小）: {file_path.name}",
                    file_path=str(file_path),
                    recommendation="请检查文件内容完整性"
                )

        return Finding(
            category=FindingCategory.INFO,
            regulation=self._get_regulation_ref(doc_type),
            item=doc_type,
            status=CheckStatus.PRESENT,
            description=f"发现{doc_type}文档: {len(files)}个",
            file_path=str(files[0]) if files else None
        )

    def _get_regulation_ref(self, doc_type: str) -> str:
        """获取法规引用条款"""
        regulation_map = {
            "Clinical Evaluation Report": "MDR Annex XIV Part A",
            "Clinical Evaluation Plan": "MDR Annex XIV Part A",
            "Risk Management": "MDR Annex I & EN ISO 14971",
            "Post-Market Surveillance Plan": "MDR Article 83 & Annex III",
            "PMCF Plan": "MDR Annex XIV Part B",
            "SSCP": "MDR Article 32",
            "PMCF Evaluation Report": "MDR Annex XIV Part B",
        }
        return regulation_map.get(doc_type, "MDR 2017/745")

    def check_cer_content(self, files: List[Path]) -> Optional[Finding]:
        """检查 CER 内容要求"""
        if not files:
            return None

        cer_file = files[0]
        try:
            content = self._read_file_content(cer_file)
            required_sections = [
                ("clinical assessment plan", FindingCategory.MAJOR),
                ("clinical data", FindingCategory.CRITICAL),
                ("risk return", FindingCategory.CRITICAL),
                ("Equivalent equipment", FindingCategory.MAJOR),
                ("SOTA", FindingCategory.MAJOR),
            ]

            missing_sections = []
            for section, severity in required_sections:
                if section not in content:
                    missing_sections.append((section, severity))

            if missing_sections:
                critical_missing = [s for s, c in missing_sections if c == FindingCategory.CRITICAL]
                major_missing = [s for s, c in missing_sections if c == FindingCategory.MAJOR]

                return Finding(
                    category=FindingCategory.CRITICAL if critical_missing else FindingCategory.MAJOR,
                    regulation="MDR Annex XIV Part A",
                    item="Clinical Evaluation Report - Content",
                    status=CheckStatus.INCOMPLETE,
                    description=f"CER内容不完整: 缺少关键部分 - {', '.join([s for s, c in missing_sections])}",
                    file_path=str(cer_file),
                    recommendation="请补充缺失的CER章节"
                )
        except Exception as e:
            return Finding(
                category=FindingCategory.MINOR,
                regulation="MDR Annex XIV Part A",
                item="Clinical Evaluation Report",
                status=CheckStatus.UNKNOWN,
                description=f"无法读取CER文档: {str(e)}",
                file_path=str(cer_file)
            )

        return None

    def check_pms_content(self, files: List[Path]) -> Optional[Finding]:
        """检查 PMS 计划内容要求"""
        if not files:
            return None

        pms_file = files[0]
        try:
            content = self._read_file_content(pms_file)
            required_elements = [
                "data collection",
                "trend report",
                "risk assessment",
                "alert system",
            ]

            missing = [e for e in required_elements if e not in content]

            if missing:
                return Finding(
                    category=FindingCategory.MAJOR,
                    regulation="MDR Article 83 & Annex III",
                    item="PMS Plan - Content",
                    status=CheckStatus.INCOMPLETE,
                    description=f"PMS计划内容不完整: 缺少 - {', '.join(missing)}",
                    file_path=str(pms_file),
                    recommendation="请依据MDR附录III的要求完善PMS计划"
                )
        except Exception as e:
            return Finding(
                category=FindingCategory.MINOR,
                regulation="MDR Article 83 & Annex III",
                item="PMS Plan",
                status=CheckStatus.UNKNOWN,
                description=f"无法读取PMS文档: {str(e)}",
                file_path=str(pms_file)
            )

        return None

    def _read_file_content(self, file_path: Path) -> str:
        """读取文件内容（支持多种格式）"""
        try:
            if file_path.suffix.lower() in ['.pdf']:
                return self._extract_pdf_text(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            self.log(f"读取文件失败 {file_path}: {e}")
            return ""

    def _extract_pdf_text(self, file_path: Path) -> str:
        """提取 PDF 文本（简化实现）"""
        # 实际实现需使用 PyPDF2 或 pdfplumber
        # 此处返回文件名作为简化检查
        return file_path.stem

    def _extract_docx_text(self, file_path: Path) -> str:
        """提取 Word 文本（简化实现）"""
        # 实际实现需使用 python-docx
        # 此处返回文件名作为简化检查
        return file_path.stem

    def run_audit(self) -> AuditReport:
        """执行审计"""
        self.log(f"开始审计 - 器械分类: Class {self.device_class}")

        # 扫描文件
        found_files = self.scan_files()

        # 检查所有必需文档
        all_findings = []
        checked_items = set()

        # 检查文档是否存在及基本完整性
        for doc_type, files in found_files.items():
            finding = self.check_document_completeness(doc_type, files)
            all_findings.append(finding)
            checked_items.add(doc_type)

        # 检查未找到的类型
        required_docs = self.REQUIRED_DOCUMENTS.get(self.device_class, [])
        for doc_type, name, is_required in required_docs:
            if doc_type not in checked_items:
                finding = self.check_document_completeness(doc_type, [])
                all_findings.append(finding)

        # 深入检查 CER 内容
        cer_files = found_files.get("Clinical Evaluation Report", [])
        if cer_files:
            cer_finding = self.check_cer_content(cer_files)
            if cer_finding:
                all_findings.append(cer_finding)

        # 深入检查 PMS 内容
        pms_files = found_files.get("Post-Market Surveillance Plan", [])
        if pms_files:
            pms_finding = self.check_pms_content(pms_files)
            if pms_finding:
                all_findings.append(pms_finding)

        # 汇总结果
        critical_count = sum(1 for f in all_findings if f.category == FindingCategory.CRITICAL and f.status != CheckStatus.PRESENT)
        major_count = sum(1 for f in all_findings if f.category == FindingCategory.MAJOR and f.status != CheckStatus.PRESENT)
        minor_count = sum(1 for f in all_findings if f.category == FindingCategory.MINOR and f.status != CheckStatus.PRESENT)

        self.report.findings = all_findings
        self.report.summary = AuditSummary(
            total_checks=len(all_findings),
            passed=sum(1 for f in all_findings if f.status == CheckStatus.PRESENT),
            warnings=minor_count,
            failed=critical_count + major_count
        )

        # 判定整体合规状态
        if critical_count > 0:
            self.report.compliance_status = ComplianceStatus.NON_COMPLIANT
        elif major_count > 0:
            self.report.compliance_status = ComplianceStatus.PARTIAL
        else:
            self.report.compliance_status = ComplianceStatus.COMPLIANT

        self.log(f"审计完成 - 状态: {self.report.compliance_status.value}")
        return self.report

    def to_json(self) -> str:
        """将报告转换为 JSON"""
        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, (AuditReport, AuditSummary, Finding)):
                return {k: serialize(v) for k, v in asdict(obj).items()}
            if isinstance(obj, list):
                return [serialize(item) for item in obj]
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj

        return json.dumps(serialize(self.report), ensure_ascii=False, indent=2)


def load_config(config_path: str) -> List[Dict[str, Any]]:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if isinstance(config, dict):
        return [config]
    return config


def main():
    parser = argparse.ArgumentParser(
        description='医疗器械 MDR 合规审计工具 - 欧盟 MDR 2017/745 合规检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  # 检查单个技术文档目录
  %(prog)s --input /path/to/technical/file --class IIa

  # 使用配置文件进行批量检查
  %(prog)s --config /path/to/config.json

  # 输出详细报告到文件
  %(prog)s --input /path/to/technical/file --class III --verbose --output report.json"""
    )

    parser.add_argument('--input', '-i', help='技术文档目录路径')
    parser.add_argument('--config', '-c', help='JSON 配置文件路径')
    parser.add_argument('--class', dest='device_class',
                       choices=['I', 'IIa', 'IIb', 'III'],
                       help='医疗器械分类 (I, IIa, IIb, III)')
    parser.add_argument('--output', '-o', help='输出报告路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='输出详细信息')

    args = parser.parse_args()

    # 校验参数
    if not args.config and (not args.input or not args.device_class):
        parser.error("必须提供 --config，或同时提供 --input 与 --class")

    results = []
    exit_code = 0

    try:
        if args.config:
            # 批量检查
            configs = load_config(args.config)
            for config in configs:
                checker = MDRChecker(
                    input_path=config['input'],
                    device_class=config.get('class', 'IIa'),
                    verbose=args.verbose
                )
                report = checker.run_audit()
                results.append(report)

                if report.compliance_status == ComplianceStatus.NON_COMPLIANT:
                    exit_code = 2
                elif exit_code == 0 and report.compliance_status == ComplianceStatus.PARTIAL:
                    exit_code = 1
        else:
            # 单次检查
            checker = MDRChecker(
                input_path=args.input,
                device_class=args.device_class,
                verbose=args.verbose
            )
            report = checker.run_audit()
            results.append(report)

            if report.compliance_status == ComplianceStatus.NON_COMPLIANT:
                exit_code = 2
            elif report.compliance_status == ComplianceStatus.PARTIAL:
                exit_code = 1

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if len(results) == 1:
                    f.write(checker.to_json())
                else:
                    f.write(json.dumps([checker.to_json() for _ in results], ensure_ascii=False, indent=2))
            print(f"报告已保存至: {args.output}")
        else:
            if len(results) == 1:
                print(checker.to_json())
            else:
                print(json.dumps([checker.to_json() for _ in results], ensure_ascii=False, indent=2))

        # 打印摘要
        print("\n" + "="*60)
        print("审计摘要")
        print("="*60)
        for i, report in enumerate(results, 1):
            if len(results) > 1:
                print(f"\n检查项 #{i}:")
            print(f"  路径: {report.input_path}")
            print(f"  分类: Class {report.device_class}")
            print(f"  状态: {report.compliance_status.value}")
            print(f"  合计: {report.summary.total_checks} | 通过: {report.summary.passed} | 警告: {report.summary.warnings} | 失败: {report.summary.failed}")

            critical = [f for f in report.findings if f.category == FindingCategory.CRITICAL and f.status != CheckStatus.PRESENT]
            if critical:
                print(f"\n  关键问题:")
                for f in critical:
                    print(f"    ⚠️  {f.item}: {f.description}")

        sys.exit(exit_code)

    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"执行错误: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()
