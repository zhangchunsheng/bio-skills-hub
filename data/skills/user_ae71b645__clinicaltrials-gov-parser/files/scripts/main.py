#!/usr/bin/env python3
"""
ClinicalTrials.gov 解析器
监测并汇总竞争对手临床试验状态变化。

技术说明：ClinicalTrials.gov API v2 集成，试验监测，状态跟踪
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import requests
import time


@dataclass
class TrialStatus:
    """表示试验的状态信息。"""
    nct_id: str
    title: str
    status: str
    phase: Optional[str]
    sponsor: Optional[str]
    condition: Optional[str]
    last_update: Optional[str]
    enrollment_count: Optional[int]
    start_date: Optional[str]
    completion_date: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ClinicalTrialsMonitor:
    """
    从 ClinicalTrials.gov 监测并跟踪临床试验状态变化。

    API：ClinicalTrials.gov API v2
    速率限制：每秒 10 次请求
    """

    BASE_URL = "https://clinicaltrials.gov/api/v2"
    RATE_LIMIT_DELAY = 0.15  # 请求间隔秒数（最多每秒 10 次）

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "ClinicalTrials-Parser/1.0"
        })
        self._last_request_time = 0

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发起带速率限制的 API 请求。"""
        # 速率限制
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        self._last_request_time = time.time()

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise Exception("API rate limit exceeded. Please wait and try again.")
        else:
            raise Exception(f"API error {response.status_code}: {response.text}")

    def search_trials(
        self,
        sponsor: Optional[str] = None,
        condition: Optional[str] = None,
        status: Optional[str] = None,
        phase: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 100
    ) -> List[TrialStatus]:
        """
        搜索符合过滤条件的临床试验。

        Args:
            sponsor: 申办方/合作方名称
            condition: 适应症
            status: 试验状态（RECRUITING、ACTIVE_NOT_RECRUITING 等）
            phase: 试验阶段（EARLY_PHASE1、PHASE1、PHASE2 等）
            keyword: 搜索关键词
            limit: 最大结果数（1-1000）

        Returns:
            TrialStatus 对象列表
        """
        params = {"pageSize": min(limit, 1000)}

        # 构建 query.term 以进行组合搜索
        query_parts = []
        if sponsor:
            query_parts.append(f'"{sponsor}"')
        if condition:
            query_parts.append(condition)
        if keyword:
            query_parts.append(keyword)

        if query_parts:
            params["query.term"] = " ".join(query_parts)

        # 使用 filter.advanced 筛选状态和阶段
        filters = []
        if status:
            filters.append(f"area:STATUS status:{status}")
        if phase:
            filters.append(f"area:PHASE phase:{phase}")

        if filters:
            params["filter.advanced"] = " AND ".join(filters)

        data = self._make_request("studies", params)

        trials = []
        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})

            trial = TrialStatus(
                nct_id=identification.get("nctId", ""),
                title=identification.get("briefTitle", ""),
                status=status_module.get("overallStatus", "UNKNOWN"),
                phase=self._get_phase(protocol),
                sponsor=sponsor_module.get("leadSponsor", {}).get("name"),
                condition=self._get_first_condition(conditions_module),
                last_update=status_module.get("statusVerifiedDate"),
                enrollment_count=design_module.get("enrollmentInfo", {}).get("count"),
                start_date=status_module.get("startDateStruct", {}).get("date"),
                completion_date=status_module.get("completionDateStruct", {}).get("date")
            )
            trials.append(trial)

        return trials

    def get_trial(self, nct_id: str) -> Optional[TrialStatus]:
        """
        获取特定试验的详细信息。

        Args:
            nct_id: ClinicalTrials.gov 标识符（例如 NCT05108922）

        Returns:
            TrialStatus 对象，若未找到则返回 None
        """
        try:
            data = self._make_request(f"studies/{nct_id}")
            protocol = data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})

            return TrialStatus(
                nct_id=identification.get("nctId", nct_id),
                title=identification.get("briefTitle", ""),
                status=status_module.get("overallStatus", "UNKNOWN"),
                phase=self._get_phase(protocol),
                sponsor=sponsor_module.get("leadSponsor", {}).get("name"),
                condition=self._get_first_condition(conditions_module),
                last_update=status_module.get("statusVerifiedDate"),
                enrollment_count=design_module.get("enrollmentInfo", {}).get("count"),
                start_date=status_module.get("startDateStruct", ).get("date"),
                completion_date=status_module.get("completionDateStruct", {}).get("date")
            )
        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                return None
            raise

    def check_status_changes(
        self,
        trial_ids: List[str],
        since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        检查受监测试验的状态变化。

        Args:
            trial_ids: 需检查的 NCT ID 列表
            since: 检查自该日期起的变化（默认：30 天前）

        Returns:
            包含当前状态的试验列表
        """
        if since is None:
            since = datetime.now() - timedelta(days=30)

        changes = []
        for nct_id in trial_ids:
            trial = self.get_trial(nct_id)
            if trial:
                trial_dict = trial.to_dict()
                trial_dict["monitored_since"] = since.isoformat()
                changes.append(trial_dict)
            time.sleep(self.RATE_LIMIT_DELAY)

        return changes

    def get_recruitment_status(self, nct_id: str) -> Optional[Dict]:
        """
        获取详细的招募/入组状态。

        Args:
            nct_id: ClinicalTrials.gov 标识符

        Returns:
            包含招募详情的字典
        """
        trial = self.get_trial(nct_id)
        if not trial:
            return None

        return {
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "enrollment_count": trial.enrollment_count,
            "last_update": trial.last_update
        }

    def generate_summary(
        self,
        sponsor: Optional[str] = None,
        condition: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        生成试验活动摘要报告。

        Args:
            sponsor: 按申办方筛选
            condition: 按适应症筛选
            days: 回溯天数

        Returns:
            包含统计数据的摘要字典
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        trials = self.search_trials(
            sponsor=sponsor,
            condition=condition,
            limit=1000
        )

        status_counts = {}
        phase_counts = {}
        recent_updates = []

        for trial in trials:
            # 按状态计数
            status_counts[trial.status] = status_counts.get(trial.status, 0) + 1

            # 按阶段计数
            if trial.phase:
                phase_counts[trial.phase] = phase_counts.get(trial.phase, 0) + 1

            # 检查近期更新
            if trial.last_update and trial.last_update >= since_date:
                recent_updates.append(trial.to_dict())

        return {
            "report_date": datetime.now().isoformat(),
            "period_days": days,
            "filters": {"sponsor": sponsor, "condition": condition},
            "total_trials": len(trials),
            "status_breakdown": status_counts,
            "phase_breakdown": phase_counts,
            "recent_updates": recent_updates,
            "recent_update_count": len(recent_updates)
        }

    def _get_phase(self, protocol: Dict) -> Optional[str]:
        """从方案中提取阶段信息。"""
        design = protocol.get("designModule", {})
        phases = design.get("phases", [])
        return phases[0] if phases else None

    def _get_first_condition(self, conditions_module: Dict) -> Optional[str]:
        """从适应症模块获取第一个适应症。"""
        conditions = conditions_module.get("conditions", [])
        return conditions[0] if conditions else None


def main():
    """CLI 入口点。"""
    parser = argparse.ArgumentParser(
        description="ClinicalTrials.gov Parser - Monitor trial status changes"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for trials")
    search_parser.add_argument("--sponsor", help="Sponsor name")
    search_parser.add_argument("--condition", help="Medical condition")
    search_parser.add_argument("--status", help="Trial status")
    search_parser.add_argument("--phase", help="Trial phase")
    search_parser.add_argument("--keyword", help="Search keyword")
    search_parser.add_argument("--limit", type=int, default=100, help="Result limit")
    search_parser.add_argument("--output", choices=["json", "table"], default="table")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get trial details")
    get_parser.add_argument("nct_id", help="ClinicalTrials.gov ID")
    get_parser.add_argument("--output", choices=["json", "table"], default="table")

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor status changes")
    monitor_parser.add_argument(
        "--trials",
        required=True,
        help="Comma-separated NCT IDs"
    )
    monitor_parser.add_argument("--days", type=int, default=30, help="Days to look back")
    monitor_parser.add_argument("--output", choices=["json", "table"], default="table")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument("--sponsor", help="Filter by sponsor")
    report_parser.add_argument("--condition", help="Filter by condition")
    report_parser.add_argument("--days", type=int, default=30, help="Report period")
    report_parser.add_argument("--output", choices=["json", "text"], default="text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    monitor = ClinicalTrialsMonitor()

    try:
        if args.command == "search":
            trials = monitor.search_trials(
                sponsor=args.sponsor,
                condition=args.condition,
                status=args.status,
                phase=args.phase,
                keyword=args.keyword,
                limit=args.limit
            )
            if args.output == "json":
                print(json.dumps([t.to_dict() for t in trials], indent=2))
            else:
                print(f"\n{'NCT ID':<15} {'Status':<20} {'Phase':<12} {'Title'}")
                print("-" * 100)
                for trial in trials:
                    phase = trial.phase or "N/A"
                    print(f"{trial.nct_id:<15} {trial.status:<20} {phase:<12} {trial.title[:50]}...")
                print(f"\nTotal: {len(trials)} trials found")

        elif args.command == "get":
            trial = monitor.get_trial(args.nct_id)
            if trial:
                if args.output == "json":
                    print(json.dumps(trial.to_dict(), indent=2))
                else:
                    print(f"\n{'Field':<20} {'Value'}")
                    print("-" * 60)
                    for key, value in trial.to_dict().items():
                        print(f"{key:<20} {value or 'N/A'}")
            else:
                print(f"Trial {args.nct_id} not found")
                sys.exit(1)

        elif args.command == "monitor":
            trial_ids = [t.strip() for t in args.trials.split(",")]
            changes = monitor.check_status_changes(trial_ids)
            if args.output == "json":
                print(json.dumps(changes, indent=2))
            else:
                print(f"\n{'NCT ID':<15} {'Status':<20} {'Last Update':<15} {'Title'}")
                print("-" * 100)
                for change in changes:
                    print(f"{change['nct_id']:<15} {change['status']:<20} "
                          f"{change['last_update'] or 'N/A':<15} {change['title'][:40]}...")
                print(f"\nMonitored: {len(changes)} trials")

        elif args.command == "report":
            summary = monitor.generate_summary(
                sponsor=args.sponsor,
                condition=args.condition,
                days=args.days
            )
            if args.output == "json":
                print(json.dumps(summary, indent=2))
            else:
                print("\n" + "=" * 60)
                print("CLINICAL TRIALS SUMMARY REPORT")
                print("=" * 60)
                print(f"Report Date: {summary['report_date']}")
                print(f"Period: Last {summary['period_days']} days")
                if summary['filters']['sponsor']:
                    print(f"Sponsor: {summary['filters']['sponsor']}")
                if summary['filters']['condition']:
                    print(f"Condition: {summary['filters']['condition']}")
                print(f"\nTotal Trials: {summary['total_trials']}")
                print("\nStatus Breakdown:")
                for status, count in sorted(summary['status_breakdown'].items()):
                    print(f"  {status}: {count}")
                if summary['phase_breakdown']:
                    print("\nPhase Breakdown:")
                    for phase, count in sorted(summary['phase_breakdown'].items()):
                        print(f"  {phase}: {count}")
                print(f"\nRecent Updates ({summary['recent_update_count']} trials)")
                print("=" * 60)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
