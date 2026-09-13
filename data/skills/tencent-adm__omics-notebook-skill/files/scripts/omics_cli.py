#!/usr/bin/env python3
"""
Omics Platform CLI Command Builder & Executor（6 命令边界）

封装 omics-platform-cli 的命令拼接与执行，供 SKILL 调用。

⚠️ 能力边界（不可违反 · 最高优先级）⚠️
SKILL 只能调用以下 6 条 CLI 一级命令，禁止越界：

    login / whoami / config / notebook / cos / volume

禁止行为：
  1. 严禁编造其他命令（如 list / run / status / debug / app / project / import 等）
  2. 严禁直接调用 omics 后端 HTTP API、SQL、文件系统写入等任何旁路通道
  3. 严禁通过组合现有命令"模拟"出白名单外的语义

子命令结构（由 argparse 强约束）：
  - login                          OAuth 浏览器登录（仅作建议，SKILL 不主动调）
  - whoami                         当前登录用户
  - config show / clear            本地配置查看/清除（SKILL 不调 set，引导用户本机执行）
  - notebook create                在当前环境下创建 Notebook 实例
  - notebook list                  列当前 config 环境下的 Notebook 实例
  - notebook list-ipynb            列指定 COS 路径下的 .ipynb 文件
  - notebook start                 启动指定的 Notebook 实例
  - notebook stop                  停止指定的 Notebook 实例
  - cos list-mount                 列当前 config 环境下的 COS 挂载列表
  - volume list                    列当前 config 环境下的缓存卷列表

用法示例：
  python omics_cli.py whoami
  python omics_cli.py config show -o json
  python omics_cli.py config clear
  python omics_cli.py notebook create \
    --name my-notebook \
    --image ccr.ccs.tencentyun.com/omics-public/jupyter-base-notebook:2025-12-08 \
    --work-dir cos://my-bucket/notebooks \
    --notebook-file demo \
    --cos-mounts '[{"Bucket":"my-bucket","SubPath":"/notebooks","MountPath":"/mnt/data"}]' \
    --cpu 4 --memory 16 --boot-disk 20
  python omics_cli.py notebook list -o json
  python omics_cli.py cos list-mount -o json
  python omics_cli.py volume list -o json
"""

import argparse
import json
import os
import subprocess
import sys
import time

# 默认 CLI 可执行文件名，可通过环境变量 OMICS_CLI_PATH 覆盖
DEFAULT_CLI_NAME = "omics"


def find_cli() -> str:
    """查找 omics CLI 可执行文件的路径。优先级：环境变量 > PATH"""
    env_path = os.environ.get("OMICS_CLI_PATH")
    if env_path:
        if os.path.isfile(env_path) and os.access(env_path, os.X_OK):
            return env_path
        raise FileNotFoundError(
            f"OMICS_CLI_PATH 指定的路径不存在或不可执行: {env_path}\n"
            f"如尚未安装 omics-platform-cli，请前往下载页按页面提供的安装脚本和使用指南完成安装：\n"
            f"  https://cnb.cool/tencenthealthcareomics/omics-platform-cli"
        )

    cli_path = shutil_which(DEFAULT_CLI_NAME)
    if cli_path:
        return cli_path

    raise FileNotFoundError(
        f"未找到 '{DEFAULT_CLI_NAME}' 命令。\n"
        f"请前往下载页按页面提供的安装脚本和使用指南完成安装：\n"
        f"  https://cnb.cool/tencenthealthcareomics/omics-platform-cli"
    )


def shutil_which(name: str) -> str | None:
    """跨平台 which 实现"""
    for dir_name in os.environ.get("PATH", "").split(os.pathsep):
        full_path = os.path.join(dir_name, name)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            if sys.platform == "win32":
                exe_path = full_path + ".exe"
                if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                    return exe_path
            return full_path
    return None


# ──────────────────────────────────────────────
# 命令构建器（仅 3 个白名单一级命令）
# ──────────────────────────────────────────────

class OmicsCLI:
    """Omics Platform CLI 命令构建与执行封装（6 命令边界：login / whoami / config / notebook / cos / volume）"""

    def __init__(self, cli_path: str | None = None):
        self.cli_path = cli_path or find_cli()

    # --- 1. login（保留 builder 仅供 dry-run 演示，SKILL 不应自动 execute） ---
    def build_login(self) -> list[str]:
        return [self.cli_path, "login"]

    # --- 2. whoami ---
    def build_whoami(self) -> list[str]:
        return [self.cli_path, "whoami"]

    # --- 辅助：version（不属白名单一级命令，但属 CLI 自身工具命令，可调） ---
    def build_version(self) -> list[str]:
        return [self.cli_path, "version"]

    # --- 3. config show / clear（SKILL 不应调 set） ---
    def build_config_show(self, output: str = "table") -> list[str]:
        return [self.cli_path, "config", "show", "-o", output]

    def build_config_clear(self) -> list[str]:
        return [self.cli_path, "config", "clear"]

    # --- 4. notebook create（在当前环境下创建 Notebook 实例） ---
    # 可选镜像常量（与 CLI create_notebook.go 保持一致）
    IMAGE_JUPYTER_PYTHON = "ccr.ccs.tencentyun.com/omics-public/jupyter-base-notebook:2025-12-08"
    IMAGE_JUPYTER_R = "ccr.ccs.tencentyun.com/omics-public/jupyter-r-notebook:2026-03-03"

    def build_notebook_create(
        self,
        name: str,
        image: str,
        work_dir: str,
        notebook_file: str,
        cos_mounts: str | None = None,
        description: str | None = None,
        cpu: int | None = None,
        memory: int | None = None,
        gpu_type: str | None = None,
        gpu_count: int | None = None,
        boot_disk: int | None = None,
        auto_close: bool | None = None,
        auto_close_min: int | None = None,
        volume_mounts: str | None = None,
        output: str = "table",
    ) -> list[str]:
        """
        omics notebook create：在当前 config 环境下创建 Notebook 实例。

        必填参数:
          name           : Notebook 名称（≤20 字符，中英文/数字/_-/，不含连续斜杠）
          image          : 容器镜像，仅两个可选值：
                           - IMAGE_JUPYTER_PYTHON（Jupyterlab 4.0.0 + Python 3.10）
                           - IMAGE_JUPYTER_R（Jupyterlab 4.0.7 + R 4.5.2）
          work_dir       : 工作目录，格式 cos://{bucket}/{prefix}
          notebook_file  : Notebook 文件名（不含 .ipynb 扩展名）

        资源参数（CPU 模式 / GPU 模式二选一）:
          cpu            : CPU 核数（CLI 默认 1；可选 1/2/4/8/12/16/32/64）
          memory         : 内存 GiB（CLI 默认 1；必须匹配 CPU 核数对应的可选范围）
          gpu_type       : GPU 型号（T4 / V100），与 gpu_count 同时使用；GPU 模式下 CPU/内存由规格自动确定
          gpu_count      : GPU 卡数

        可选参数:
          description    : 描述（≤100 字符）
          cos_mounts     : 新增的 COS 存储桶挂载列表 JSON 数组字符串（可选，环境中已有的无需传），格式：
                           [{"Bucket":"my-bucket","SubPath":"/prefix","MountPath":"/mnt/data","ReadOnly":false}]
          boot_disk      : 存储 GiB（CLI 默认 20，最小 20）
          auto_close     : 是否启用自动关闭（CLI 默认 true）；显式传 False 会下发 --auto-close=false
          auto_close_min : 自动关闭分钟数（CLI 默认 2880，范围 60~43200）
          volume_mounts  : 缓存卷挂载列表 JSON 数组字符串（CLI 默认 []），格式：
                           [{"VolumeId":"vol-xxx","MountPath":"/vol-vol-xxx"}]
          output         : table / json

        注意：本 builder 只负责命令拼接，具体的 CPU/内存配对、GPU 规格、名称格式、
        COS/卷挂载字段等校验由 CLI 侧执行；SKILL 应把 CLI 报错原文转述给用户。
        """
        if not (name and name.strip()):
            raise ValueError("build_notebook_create: --name 不能为空")
        if not (image and image.strip()):
            raise ValueError("build_notebook_create: --image 不能为空")
        if not (work_dir and work_dir.strip()):
            raise ValueError("build_notebook_create: --work-dir 不能为空")
        if not (notebook_file and notebook_file.strip()):
            raise ValueError("build_notebook_create: --notebook-file 不能为空")

        # 注意：底层 omics CLI 的 notebook create 子命令不支持 -o/--output，
        # 这里不能追加 -o，否则 Go CLI 会报 unknown shorthand flag: 'o'
        cmd = [self.cli_path, "notebook", "create"]
        cmd.extend(["--name", name])
        cmd.extend(["--image", image])
        cmd.extend(["--work-dir", work_dir])
        cmd.extend(["--notebook-file", notebook_file])
        if cos_mounts and cos_mounts.strip():
            cmd.extend(["--cos-mounts", cos_mounts])
        if description:
            cmd.extend(["--description", description])
        if cpu is not None:
            cmd.extend(["--cpu", str(cpu)])
        if memory is not None:
            cmd.extend(["--memory", str(memory)])
        if gpu_type:
            cmd.extend(["--gpu-type", gpu_type])
        if gpu_count is not None:
            cmd.extend(["--gpu-count", str(gpu_count)])
        if boot_disk is not None:
            cmd.extend(["--boot-disk", str(boot_disk)])
        if auto_close is not None:
            # cobra BoolVar：显式传值用 --flag=true/false 形式，避免吞掉后续位置参数
            cmd.append(f"--auto-close={'true' if auto_close else 'false'}")
        if auto_close_min is not None:
            cmd.extend(["--auto-close-min", str(auto_close_min)])
        if volume_mounts:
            cmd.extend(["--volume-mounts", volume_mounts])
        return cmd

    # --- 5. notebook list（列当前 config 环境下的 Notebook 实例） ---
    def build_notebook_list(self, output: str = "table") -> list[str]:
        """omics notebook list：列当前 config 环境下的 Notebook 实例。"""
        return [self.cli_path, "notebook", "list", "-o", output]

    def build_notebook_list_ipynb(self, bucket: str, prefix: str | None = None, output: str = "table") -> list[str]:
        """
        omics notebook list-ipynb：列出指定 COS 路径下的 .ipynb 文件。

        参数:
          bucket : COS 存储桶名称（必填）
          prefix : COS 路径前缀（可选，不传则列桶根目录下的 .ipynb）
          output : table / json
        """
        if not (bucket and bucket.strip()):
            raise ValueError("build_notebook_list_ipynb: --bucket 不能为空")
        cmd = [self.cli_path, "notebook", "list-ipynb", "--bucket", bucket]
        if prefix and prefix.strip():
            cmd.extend(["--prefix", prefix])
        cmd.extend(["-o", output])
        return cmd

    # --- 6. notebook start（启动指定 Notebook 实例） ---
    def build_notebook_start(self, notebook_id: str) -> list[str]:
        """
        omics notebook start：启动当前 config 环境下指定 ID 的 Notebook 实例。

        参数:
          notebook_id : Notebook 实例 ID（必填，如 nb-xxxx）
        """
        if not (notebook_id and notebook_id.strip()):
            raise ValueError("build_notebook_start: --id 不能为空")
        return [self.cli_path, "notebook", "start", "--id", notebook_id]

    def start_and_wait(self, notebook_id: str, max_retries: int = 5, wait_seconds: int = 60) -> bool:
        """
        启动实例并轮询等待直到状态为 RUNNING。

        1. 执行 notebook start
        2. 等待 wait_seconds 秒后调 notebook list -o json 查状态
        3. 若 status != RUNNING 且未超最大重试次数，继续等待 → 重试
        4. 最多重试 max_retries 次

        返回: True=已 RUNNING, False=超时未启动
        """
        # 1. 执行 start
        start_args = self.build_notebook_start(notebook_id)
        print(f"\n▶ 执行命令: {' '.join(start_args)}\n")
        result = subprocess.run(start_args, capture_output=False, text=True)
        if result.returncode != 0:
            print(f"❌ 启动命令失败 (exit {result.returncode})", file=sys.stderr)
            return False

        # 2. 轮询
        list_args = self.build_notebook_list(output="json")
        for attempt in range(1, max_retries + 1):
            print(f"\n⏳ 等待 {wait_seconds}s 后检查状态 (第 {attempt}/{max_retries} 次)...")
            time.sleep(wait_seconds)

            print(f"▶ 执行命令: {' '.join(list_args)}")
            r = subprocess.run(list_args, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"⚠️ 查询列表失败 (exit {r.returncode})，重试中...", file=sys.stderr)
                continue

            try:
                items = json.loads(r.stdout)
            except json.JSONDecodeError:
                print(f"⚠️ 列表响应 JSON 解析失败，重试中...", file=sys.stderr)
                continue

            if not isinstance(items, list):
                print(f"⚠️ 列表响应格式异常，重试中...", file=sys.stderr)
                continue

            target = next((item for item in items if item.get("NotebookId") == notebook_id), None)
            if target is None:
                print(f"⚠️ 列表中未找到 {notebook_id}，可能仍在创建，重试中...", file=sys.stderr)
                continue

            status = target.get("InstanceStatus", "")
            print(f"   当前状态: {status}")
            if status.upper() == "RUNNING":
                print(f"✅ Notebook {notebook_id} 已就绪 (RUNNING)")
                return True

        print(f"\n❌ 已尝试 {max_retries} 次仍未达到 RUNNING 状态", file=sys.stderr)
        return False

    # --- 7. notebook stop（停止指定 Notebook 实例） ---
    def build_notebook_stop(self, notebook_id: str) -> list[str]:
        """
        omics notebook stop：停止当前 config 环境下指定 ID 的 Notebook 实例。

        参数:
          notebook_id : Notebook 实例 ID（必填，如 nb-xxxx）
        """
        if not (notebook_id and notebook_id.strip()):
            raise ValueError("build_notebook_stop: --id 不能为空")
        return [self.cli_path, "notebook", "stop", "--id", notebook_id]

    # --- 7. cos list-mount（列当前环境下的 COS 挂载列表） ---
    def build_cos_list_mount(self, output: str = "table") -> list[str]:
        """
        omics cos list-mount：列当前 config 环境下已有的 COS 挂载配置。

        输出字段：Bucket / SubPath / MountPath / ReadOnly，以及 TotalCount。
        主要用于创建 Notebook 前，帮用户确认当前环境有哪些可用的 COS 挂载，
        据此填写 notebook create 的 --cos-mounts。

        参数:
          output : table / json
        """
        return [self.cli_path, "cos", "list-mount", "-o", output]

    # --- 8. volume list（列当前环境下的缓存卷列表） ---
    def build_volume_list(self, output: str = "table") -> list[str]:
        """
        omics volume list：列当前 config 环境下的缓存卷列表。

        输出字段：VolumeId / Name / Status / Size(GiB) / MountPath，以及 TotalCount。
        主要用于创建 Notebook 前，帮用户确认当前环境有哪些可用的缓存卷，
        据此填写 notebook create 的 --volume-mounts。

        参数:
          output : table / json
        """
        return [self.cli_path, "volume", "list", "-o", output]

    # --- 执行 ---
    def execute(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        执行 CLI 命令。

        参数:
          args : 完整命令列表
          check: True 则在非零退出码时抛出 CalledProcessError

        退出码语义：
          0 → 成功
          1 → 业务错误
          2 → 鉴权失败（SKILL 应捕获并提示用户在本机跑 omics login，不要循环重试）
        """
        print(f"\n▶ 执行命令: {' '.join(args)}\n")
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, args, result.stdout, result.stderr
            )
        return result


# ──────────────────────────────────────────────
# CLI 入口（argparse 顶层只注册 6 个一级命令 + version 工具）
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Omics Platform CLI 命令构建与执行工具（6 命令边界：login / whoami / config / notebook / cos / volume）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--cli-path", default=None,
                        help="指定 omics 可执行文件的完整路径（默认自动查找 PATH）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印命令而不执行")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 1. login
    subparsers.add_parser("login", help="OAuth 浏览器登录（SKILL 不应自动调；引导用户本机执行）")

    # 2. whoami
    subparsers.add_parser("whoami", help="查看当前登录用户")

    # 工具：version
    subparsers.add_parser("version", help="CLI 版本号")

    # 3. config（show / clear；不暴露 set，避免 SKILL 误调）
    cfg = subparsers.add_parser("config", help="本地配置（show / clear；set 由用户在本机执行）")
    cfg_sub = cfg.add_subparsers(dest="config_action")
    cfg_show = cfg_sub.add_parser("show", help="显示当前配置")
    cfg_show.add_argument("-o", "--output", default="table", choices=["table", "json"])
    cfg_sub.add_parser("clear", help="清除本地配置")

    # 4. notebook（create / list / list-ipynb / start / stop）
    nb = subparsers.add_parser("notebook", help="Notebook 管理（create / list / list-ipynb / start / stop）")
    nb_sub = nb.add_subparsers(dest="notebook_action")

    nb_create = nb_sub.add_parser("create", help="在当前环境下创建 Notebook 实例")
    # 必填
    nb_create.add_argument("--name", required=True,
                           help="Notebook 名称（必填，≤20 字符，中英文/数字/_-/，不含连续斜杠）")
    nb_create.add_argument("--image", required=True,
                           help="容器镜像（必填）：jupyter-base-notebook:2025-12-08（Python）/ jupyter-r-notebook:2026-03-03（R）")
    nb_create.add_argument("--work-dir", dest="work_dir", required=True,
                           help="工作目录（必填，格式 cos://{bucket}/{prefix}）")
    nb_create.add_argument("--notebook-file", dest="notebook_file", required=True,
                           help="Notebook 文件名（必填，不含 .ipynb 扩展名）")
    nb_create.add_argument("--cos-mounts", dest="cos_mounts", default=None,
                           help='新增的 COS 存储桶挂载列表 JSON 数组（可选，环境中已有的无需传）')
    # 资源（CPU 模式 / GPU 模式）
    nb_create.add_argument("--cpu", type=int, default=None,
                           help="CPU 核数（CLI 默认 1；可选 1/2/4/8/12/16/32/64）")
    nb_create.add_argument("--memory", type=int, default=None,
                           help="内存 GiB（CLI 默认 1；须匹配 CPU 核数对应的可选范围）")
    nb_create.add_argument("--gpu-type", dest="gpu_type", default=None,
                           help="GPU 型号（T4 / V100），与 --gpu-count 同时使用")
    nb_create.add_argument("--gpu-count", dest="gpu_count", type=int, default=None,
                           help="GPU 卡数（选中后 CPU/内存由规格自动确定）")
    # 可选
    nb_create.add_argument("--description", default=None, help="描述（可选，≤100 字符）")
    nb_create.add_argument("--boot-disk", dest="boot_disk", type=int, default=None,
                           help="存储 GiB（CLI 默认 20，最小 20）")
    nb_create.add_argument("--auto-close", dest="auto_close", default=None,
                           action=argparse.BooleanOptionalAction,
                           help="启用自动关闭（CLI 默认 true）；用 --no-auto-close 关闭")
    nb_create.add_argument("--auto-close-min", dest="auto_close_min", type=int, default=None,
                           help="自动关闭分钟数（CLI 默认 2880，范围 60~43200）")
    nb_create.add_argument("--volume-mounts", dest="volume_mounts", default=None,
                           help='缓存卷挂载列表 JSON 数组（可选，默认 []）：[{"VolumeId":"vol-x","MountPath":"/vol-vol-x"}]')
    nb_create.add_argument("-o", "--output", default="table", choices=["table", "json"])

    nb_list = nb_sub.add_parser("list", help="列当前 config 环境下的 Notebook 实例")
    nb_list.add_argument("-o", "--output", default="table", choices=["table", "json"])

    nb_list_ipynb = nb_sub.add_parser("list-ipynb", help="列指定 COS 路径下的 .ipynb 文件")
    nb_list_ipynb.add_argument("--bucket", required=True, help="COS 存储桶名称（必填）")
    nb_list_ipynb.add_argument("--prefix", default=None, help="COS 路径前缀（可选，不传则列桶根目录下的 .ipynb）")
    nb_list_ipynb.add_argument("-o", "--output", default="table", choices=["table", "json"])

    nb_start = nb_sub.add_parser("start", help="启动指定的 Notebook 实例")
    nb_start.add_argument("--id", dest="notebook_id", required=True, help="Notebook 实例 ID（必填，如 nb-xxxx）")

    nb_stop = nb_sub.add_parser("stop", help="停止指定的 Notebook 实例")
    nb_stop.add_argument("--id", dest="notebook_id", required=True, help="Notebook 实例 ID（必填，如 nb-xxxx）")

    # 5. cos（list-mount）
    cos = subparsers.add_parser("cos", help="COS 管理（list-mount）")
    cos_sub = cos.add_subparsers(dest="cos_action")
    cos_list_mount = cos_sub.add_parser("list-mount", help="列当前 config 环境下的 COS 挂载列表")
    cos_list_mount.add_argument("-o", "--output", default="table", choices=["table", "json"])

    # 6. volume（list）
    vol = subparsers.add_parser("volume", help="缓存卷管理（list）")
    vol_sub = vol.add_subparsers(dest="volume_action")
    vol_list = vol_sub.add_parser("list", help="列当前 config 环境下的缓存卷列表")
    vol_list.add_argument("-o", "--output", default="table", choices=["table", "json"])

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        cli = OmicsCLI(cli_path=args.cli_path)

        if args.command == "login":
            cmd_args = cli.build_login()
        elif args.command == "whoami":
            cmd_args = cli.build_whoami()
        elif args.command == "version":
            cmd_args = cli.build_version()
        elif args.command == "config":
            if args.config_action == "show":
                cmd_args = cli.build_config_show(output=args.output)
            elif args.config_action == "clear":
                cmd_args = cli.build_config_clear()
            else:
                cfg.print_help(); sys.exit(1)
        elif args.command == "notebook":
            if args.notebook_action == "create":
                cmd_args = cli.build_notebook_create(
                    name=args.name,
                    image=args.image,
                    work_dir=args.work_dir,
                    notebook_file=args.notebook_file,
                    cos_mounts=args.cos_mounts,
                    description=args.description,
                    cpu=args.cpu,
                    memory=args.memory,
                    gpu_type=args.gpu_type,
                    gpu_count=args.gpu_count,
                    boot_disk=args.boot_disk,
                    auto_close=args.auto_close,
                    auto_close_min=args.auto_close_min,
                    volume_mounts=args.volume_mounts,
                    output=args.output,
                )
            elif args.notebook_action == "list":
                cmd_args = cli.build_notebook_list(output=args.output)
            elif args.notebook_action == "list-ipynb":
                cmd_args = cli.build_notebook_list_ipynb(
                    bucket=args.bucket, prefix=args.prefix, output=args.output
                )
            elif args.notebook_action == "start":
                if args.dry_run:
                    print("DRY RUN - 将执行以下命令:")
                    print(" ".join(cli.build_notebook_start(notebook_id=args.notebook_id)))
                    print("然后轮询等待 RUNNING（最多 5 次，每次 60s）")
                    sys.exit(0)
                ok = cli.start_and_wait(notebook_id=args.notebook_id)
                sys.exit(0 if ok else 1)
            elif args.notebook_action == "stop":
                cmd_args = cli.build_notebook_stop(notebook_id=args.notebook_id)
            else:
                nb.print_help(); sys.exit(1)
        elif args.command == "cos":
            if args.cos_action == "list-mount":
                cmd_args = cli.build_cos_list_mount(output=args.output)
            else:
                cos.print_help(); sys.exit(1)
        elif args.command == "volume":
            if args.volume_action == "list":
                cmd_args = cli.build_volume_list(output=args.output)
            else:
                vol.print_help(); sys.exit(1)
        else:
            parser.print_help(); sys.exit(1)

        if args.dry_run:
            print("DRY RUN - 将执行以下命令:")
            print(" ".join(cmd_args))
            sys.exit(0)

        result = cli.execute(cmd_args, check=False)
        sys.exit(result.returncode)

    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
