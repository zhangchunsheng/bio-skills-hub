"""
task_guard.py — 生产级 Cron 任务稳定性框架
10项能力：预检门控 · 文件锁 · 幂等 · 超时 · 心跳 · 熔断 · 退避重试 · 原子写入 · 结构化日志 · 告警

用法1（装饰器）:
    from biopharma_strategy.task_guard import TaskGuard
    guard = TaskGuard("daily_backup", timeout=900, required_dirs=["/path/to/backup"])
    @guard.run
    def main():
        ...  # 任意异常 → 自动记录+告警

用法2（上下文管理器）:
    with TaskGuard("daily_backup", timeout=900) as g:
        g.check_disk(min_free_gb=1)
        g.atomic_write("/path/to/output.json", json.dumps(data))
        g.mark_success()

用法3（退避重试）:
    from biopharma_strategy.task_guard import retry_with_backoff
    @retry_with_backoff(max_retries=3, base_delay=2)
    def fetch_data():
        return requests.get(url, timeout=get_timeout("http_quick"))
"""

import os, sys, json, time, logging, traceback, hashlib
import signal
try:
    import fcntl  # POSIX 专属文件锁；Windows 无此模块
except ImportError:
    fcntl = None
_HAS_SIGALRM = hasattr(signal, "SIGALRM")  # Windows 无 SIGALRM/alarm，超时功能降级
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Callable, List
from .pipeline_config import get_timeout  # noqa: E402

# ── 路径 ────────────────────────────────────────────
# 运行期目录按包命名空间隔离（避免与 biopharma-data-sources 同机并跑时互抢锁/状态）。
# 可用 BIOPHARMA_ROOT 覆盖到自定义根目录；无论是否覆盖，本包都在其下追加自己的子目录。
_BASE_ROOT = os.path.expanduser(os.environ.get("BIOPHARMA_ROOT", "~/.biopharma"))
APP_ROOT = os.path.join(_BASE_ROOT, "strategy")
LOCK_DIR = os.path.join(APP_ROOT, "locks")
LOG_DIR = os.path.join(APP_ROOT, "logs", "task_guard")
STATE_DIR = os.path.join(APP_ROOT, "state")
os.makedirs(LOCK_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

TG_TARGET = os.environ.get("TELEGRAM_CHAT_ID", "")


# ═══════════════════════════════════════════════════════════════
# 能力 10: 结构化日志
# ═══════════════════════════════════════════════════════════════

class JsonLogger:
    """JSON Lines 格式日志，每条一行，可解析。"""
    def __init__(self, task_name: str):
        self.task_name = task_name
        log_file = os.path.join(LOG_DIR, f"{task_name}.jsonl")
        self._handler = logging.FileHandler(log_file)
        self._handler.setFormatter(logging.Formatter('%(message)s'))
        self._logger = logging.getLogger(f"task_guard.{task_name}")
        self._logger.addHandler(self._handler)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

    def log(self, event: str, **kwargs):
        record = {"ts": datetime.now().isoformat(), "task": self.task_name, "event": event, **kwargs}
        self._logger.info(json.dumps(record, ensure_ascii=False, default=str))

    def close(self):
        self._handler.close()


# ═══════════════════════════════════════════════════════════════
# 能力 9: 告警推送
# ═══════════════════════════════════════════════════════════════

def send_alert(task_name: str, level: str, message: str):
    """通过 Telegram Bot API 推送告警（需 TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID）。未配置则静默跳过。"""
    try:
        emoji = {"critical": "🚨", "error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(level, "📢")
        msg = f"{emoji} 【{task_name}】{message}"
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token or not TG_TARGET:
            return
        import requests
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": TG_TARGET, "text": msg},
            timeout=10,
        )
    except Exception:
        pass  # 告警本身失败不能影响主任务


# ═══════════════════════════════════════════════════════════════
# 能力 2: 文件锁（防止并发）
# ═══════════════════════════════════════════════════════════════

@contextmanager
def file_lock(task_name: str, logger: JsonLogger):
    """获取排他文件锁，已有实例运行中则退出。Windows（无 fcntl）降级为无锁运行。"""
    lock_path = os.path.join(LOCK_DIR, f"{task_name}.lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    if fcntl is None:
        # Windows 无 fcntl：跳过并发锁（降级，不影响数据采集）
        logger.log("lock_skipped", reason="fcntl 不可用（Windows），跳过并发保护")
        try:
            yield
        finally:
            os.close(fd)
            logger.log("lock_released")
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.log("lock_acquired", pid=os.getpid())
        yield
    except BlockingIOError:
        logger.log("lock_conflict", reason="another instance is running")
        send_alert(task_name, "warning", "上一轮还未完成，跳过本轮")
        os.close(fd)
        sys.exit(0)
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        logger.log("lock_released")


# ═══════════════════════════════════════════════════════════════
# 能力 1: 预检门控
# ═══════════════════════════════════════════════════════════════

class PreFlight:
    """启动前检查：磁盘空间、必需目录、API连通性。"""

    @staticmethod
    def check_disk(min_free_gb: float, path: str = None) -> bool:
        import shutil
        target = path or os.path.expanduser("~")
        usage = shutil.disk_usage(target)  # 跨平台（Windows/macOS/Linux）
        free_gb = usage.free / (1024**3)
        if free_gb < min_free_gb:
            raise RuntimeError(f"磁盘空间不足: {free_gb:.1f}GB < {min_free_gb}GB")
        return True

    @staticmethod
    def check_dirs(directories: List[str]) -> bool:
        missing = [d for d in directories if not os.path.exists(d)]
        if missing:
            raise RuntimeError(f"目录不存在: {', '.join(missing)}")
        return True

    @staticmethod
    def check_writable(directories: List[str]) -> bool:
        for d in directories:
            test_file = os.path.join(d, ".rw_test")
            try:
                with open(test_file, 'w') as f:
                    f.write('x')
                os.remove(test_file)
            except Exception:
                raise RuntimeError(f"目录不可写: {d}")
        return True

    @staticmethod
    def check_api(url: str, timeout: int = 10) -> bool:
        import urllib.request
        try:
            urllib.request.urlopen(url, timeout=timeout)
            return True
        except Exception:
            raise RuntimeError(f"API不可达: {url}")


# ═══════════════════════════════════════════════════════════════
# 能力 7: 退避重试
# ═══════════════════════════════════════════════════════════════

def retry_with_backoff(max_retries: int = 3, base_delay: float = 2, backoff: float = 2,
                       exceptions: tuple = (Exception,),
                       no_retry_on: tuple = (ValueError, TypeError, ImportError,
                                             AttributeError, KeyError, IndexError,
                                             NotImplementedError, PermissionError)):
    """指数退避重试装饰器。

    Args:
        max_retries:  最大重试次数（含首次）
        base_delay:   首次重试等待秒数
        backoff:      每次重试延迟倍数
        exceptions:   触发重试的异常类型（默认所有 Exception）
        no_retry_on:  永不重试的异常类型（代码 bug，重试无意义）
                      默认排除：ValueError / TypeError / ImportError /
                                AttributeError / KeyError / IndexError /
                                NotImplementedError / PermissionError
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except no_retry_on as e:
                    # 代码 bug 类异常：直接抛出，不重试
                    raise
                except exceptions as e:
                    last_exc = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= backoff
            raise last_exc
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# 能力 6: 熔断器
# ═══════════════════════════════════════════════════════════════

class CircuitBreaker:
    """连续失败 N 次后熔断，冷却期后恢复。"""
    def __init__(self, name: str, failure_threshold: int = 3, cooldown_seconds: int = 600):
        self.name = name
        self.threshold = failure_threshold
        self.cooldown = cooldown_seconds
        self._state_file = os.path.join(STATE_DIR, f"cb_{name}.json")
        self._load()

    def _load(self):
        try:
            with open(self._state_file) as f:
                d = json.load(f)
            self._failures = d.get("failures", 0)
            self._last_failure = d.get("last_failure", "")
            self._open_since = d.get("open_since", "")
        except (FileNotFoundError, json.JSONDecodeError):
            self._failures = 0
            self._last_failure = ""
            self._open_since = ""

    def _save(self):
        with open(self._state_file, 'w') as f:
            json.dump({"failures": self._failures, "last_failure": self._last_failure,
                        "open_since": self._open_since}, f)

    @property
    def is_open(self) -> bool:
        if not self._open_since:
            return False
        elapsed = (datetime.now() - datetime.fromisoformat(self._open_since)).total_seconds()
        if elapsed > self.cooldown:
            self._open_since = ""
            self._failures = 0
            self._save()
            return False
        return True

    def record_success(self):
        self._failures = 0
        self._last_failure = ""
        self._open_since = ""
        self._save()

    def record_failure(self):
        self._failures += 1
        self._last_failure = datetime.now().isoformat()
        if self._failures >= self.threshold:
            self._open_since = datetime.now().isoformat()
        self._save()


# ═══════════════════════════════════════════════════════════════
# 能力 5: 心跳
# ═══════════════════════════════════════════════════════════════

class Heartbeat:
    """记录心跳时间戳，外部监控可检测失联。"""
    def __init__(self, task_name: str):
        self._file = os.path.join(STATE_DIR, f"heartbeat_{task_name}.json")

    def ping(self, status: str = "ok"):
        with open(self._file, 'w') as f:
            json.dump({"last_heartbeat": datetime.now().isoformat(), "status": status}, f)

    @staticmethod
    def get_stale_tasks(max_age_minutes: int = 120) -> List[str]:
        """扫描所有心跳文件，返回超时未更新的任务名列表。"""
        pattern = os.path.join(STATE_DIR, "heartbeat_*.json")
        import glob
        stale = []
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        for f in glob.glob(pattern):
            try:
                with open(f) as fh:
                    d = json.load(fh)
                last = datetime.fromisoformat(d["last_heartbeat"])
                if last < cutoff:
                    stale.append(os.path.basename(f).replace("heartbeat_", "").replace(".json", ""))
            except Exception:
                pass
        return stale


# ═══════════════════════════════════════════════════════════════
# 能力 3: 幂等性（重跑安全）
# ═══════════════════════════════════════════════════════════════

class IdempotentState:
    """基于内容哈希的幂等性保证：相同输入不重复处理。

    用法:
        idem = IdempotentState("daily_backup")
        if idem.already_processed(data_str, key="raw_feed"):
            print("跳过：本轮数据与上轮完全相同")
            return
        # ... 处理 ...
        idem.mark_processed(data_str, key="raw_feed")

        # 也可对输出文件做哈希比对
        if idem.check_output_hash("/path/to/report.json"):
            print("跳过：输出无变化")
            return
    """
    def __init__(self, task_name: str):
        self._file = os.path.join(STATE_DIR, f"idempotent_{task_name}.json")
        self._state = self._load()

    def _load(self) -> dict:
        try:
            with open(self._file) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"hashes": {}, "last_processed": ""}

    def _save(self):
        atomic_write(self._file, json.dumps(self._state, ensure_ascii=False))

    def already_processed(self, content: str, key: str = "default") -> bool:
        """检查相同内容是否已处理过。key 用于区分同一任务的不同数据类型。"""
        h = hashlib.sha256(content.encode()).hexdigest()
        stored = self._state.get("hashes", {}).get(key, "")
        return h == stored

    def mark_processed(self, content: str, key: str = "default"):
        """记录内容已处理，下次相同内容将跳过。"""
        h = hashlib.sha256(content.encode()).hexdigest()
        self._state.setdefault("hashes", {})[key] = h
        self._state["last_processed"] = datetime.now().isoformat()
        self._save()

    def check_output_hash(self, filepath: str) -> bool:
        """检查输出文件内容是否与上次运行完全相同（相同=可跳过）。"""
        try:
            with open(filepath) as f:
                content = f.read()
            return self.already_processed(content, key=f"output:{filepath}")
        except FileNotFoundError:
            return False

    def mark_output(self, filepath: str):
        """标记输出文件哈希，供下次 check_output_hash 比对。"""
        try:
            with open(filepath) as f:
                content = f.read()
            self.mark_processed(content, key=f"output:{filepath}")
        except FileNotFoundError:
            pass

    def clear(self):
        """重置所有幂等状态（用于强制重跑场景）。"""
        self._state = {"hashes": {}, "last_processed": ""}
        self._save()


# ═══════════════════════════════════════════════════════════════
# 能力 8: 原子写入
# ═══════════════════════════════════════════════════════════════

def atomic_write(filepath: str, content: str, mode: str = 'w'):
    """先写临时文件，成功后原子 rename。"""
    tmp = filepath + f".tmp.{os.getpid()}"
    with open(tmp, mode) as f:
        f.write(content)
    os.replace(tmp, filepath)  # atomic on POSIX


# ═══════════════════════════════════════════════════════════════
# 能力 4+主框架: 超时 + TaskGuard
# ═══════════════════════════════════════════════════════════════

class TaskGuard:
    """一站式任务稳定性框架。"""

    def __init__(self, name: str, timeout: int = 600,
                 required_dirs: List[str] = None,
                 required_writable: List[str] = None,
                 min_disk_gb: float = 0.5,
                 api_health_checks: List[str] = None):
        self.name = name
        self.timeout = timeout
        self.required_dirs = required_dirs or []
        self.required_writable = required_writable or []
        self.min_disk_gb = min_disk_gb
        self.api_checks = api_health_checks or []
        self.logger = JsonLogger(name)
        self.heartbeat = Heartbeat(name)
        self.breaker = CircuitBreaker(name)
        self.idempotent = IdempotentState(name)
        self._start_time = None
        self._success = False

    # ── 上下文管理器 ──
    def __enter__(self):
        self._start_time = time.time()
        self.logger.log("started")

        # 熔断检查
        if self.breaker.is_open:
            msg = f"熔断器开路（连续{self.breaker._failures}次失败），跳过本次执行"
            self.logger.log("circuit_open", failures=self.breaker._failures)
            send_alert(self.name, "critical", msg)
            sys.exit(0)

        # 预检
        try:
            PreFlight.check_disk(self.min_disk_gb)
            PreFlight.check_dirs(self.required_dirs)
            PreFlight.check_writable(self.required_writable)
            for url in self.api_checks:
                PreFlight.check_api(url)
            self.logger.log("preflight_pass")
        except Exception as e:
            self.logger.log("preflight_fail", error=str(e))
            send_alert(self.name, "error", f"预检失败: {e}")
            self.breaker.record_failure()
            sys.exit(1)

        # 心跳: 开始
        self.heartbeat.ping("running")

        # 超时: 设置 alarm（Windows 无 SIGALRM，跳过超时保护）
        if _HAS_SIGALRM:
            signal.signal(signal.SIGALRM, self._on_timeout)
            signal.alarm(self.timeout)
        else:
            self.logger.log("timeout_disabled", reason="SIGALRM 不可用（Windows）")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _HAS_SIGALRM:
            signal.alarm(0)  # 取消超时
        elapsed = time.time() - self._start_time

        if exc_type is None:
            self._success = True
            self.logger.log("completed", elapsed_sec=round(elapsed, 1))
            self.heartbeat.ping("ok")
            self.breaker.record_success()
        elif exc_type == SystemExit:
            self.logger.log("exited", elapsed_sec=round(elapsed, 1))
        else:
            err = f"{exc_type.__name__}: {exc_val}"
            self.logger.log("failed", error=err, elapsed_sec=round(elapsed, 1),
                            traceback=traceback.format_exc()[-500:])
            self.heartbeat.ping("error")
            self.breaker.record_failure()
            send_alert(self.name, "error",
                       f"执行失败（{round(elapsed,1)}s）: {str(exc_val)[:200]}")

        self.logger.close()
        return False  # 不抑制异常

    # ── 装饰器模式 ──
    def run(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
                self.mark_success()
                return result
        return wrapper

    # ── 辅助方法 ──
    def mark_success(self):
        self._success = True

    def atomic_write(self, path: str, content: str):
        """原子写入文件。"""
        atomic_write(path, content)
        self.logger.log("atomic_write", path=path, size=len(content))

    def is_duplicate_run(self, content: str, key: str = "default") -> bool:
        """幂等检查：本轮数据与上轮相同则跳过。"""
        return self.idempotent.already_processed(content, key)

    def mark_run_complete(self, content: str, key: str = "default"):
        """标记本轮数据已处理，防止重跑。"""
        self.idempotent.mark_processed(content, key)

    def _on_timeout(self, signum, frame):
        elapsed = time.time() - self._start_time
        self.logger.log("timeout", elapsed_sec=round(elapsed, 1))
        self.heartbeat.ping("timeout")
        self.breaker.record_failure()
        send_alert(self.name, "critical", f"执行超时（>{self.timeout}s），已强制终止")
        os._exit(1)


# ═══════════════════════════════════════════════════════════════
# 便捷工厂函数
# ═══════════════════════════════════════════════════════════════

def quick_guard(name: str, timeout: int = 600, **kwargs) -> TaskGuard:
    """快速创建 TaskGuard。"""
    return TaskGuard(name=name, timeout=timeout, **kwargs)
