"""
提示词管理模块 - 支持通用分析和述职规范分析两种模式
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# 提示词缓存
_prompt_cache: Dict[str, str] = {}
_config_cache: Optional[dict] = None


def _get_service_dir() -> Path:
    """获取 services 目录路径"""
    return Path(__file__).parent


def load_config() -> dict:
    """加载提示词配置"""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config_path = _get_service_dir() / "prompt_config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
            logger.info(f"提示词配置加载成功，当前模式: {_config_cache['active_mode']}")
            return _config_cache
    except Exception as e:
        logger.error(f"加载提示词配置失败: {e}，使用默认配置")
        # 返回默认配置
        return {
            "active_mode": "generic",
            "modes": {
                "generic": {
                    "prompts": {
                        "page_analysis": "prompts/generic_page_analysis_prompt.txt",
                        "chapter_analysis": "prompts/generic_chapter_analysis_prompt.txt",
                        "overall_analysis": "prompts/generic_overall_analysis_prompt.txt",
                        "transcript_analysis": "prompts/transcript_prompt.txt"
                    }
                }
            }
        }


def get_active_mode() -> str:
    """获取当前激活的模式"""
    config = load_config()
    return config.get("active_mode", "generic")


def get_mode_info(mode: Optional[str] = None) -> dict:
    """获取指定模式的信息"""
    config = load_config()
    mode = mode or config.get("active_mode", "generic")
    return config["modes"].get(mode, config["modes"]["generic"])


def load_prompt(prompt_type: str, mode: Optional[str] = None) -> str:
    """
    加载指定类型的提示词

    Args:
        prompt_type: 提示词类型 (page_analysis/chapter_analysis/overall_analysis/transcript_analysis)
        mode: 分析模式 (generic/review)，默认使用配置文件中的 active_mode

    Returns:
        提示词内容
    """
    mode = mode or get_active_mode()
    cache_key = f"{mode}:{prompt_type}"

    # 检查缓存
    if cache_key in _prompt_cache:
        return _prompt_cache[cache_key]

    # 获取提示词文件路径
    mode_info = get_mode_info(mode)
    prompt_file = mode_info["prompts"].get(prompt_type)

    if not prompt_file:
        logger.error(f"未找到 {mode} 模式下的 {prompt_type} 提示词配置")
        raise ValueError(f"未找到 {mode} 模式下的 {prompt_type} 提示词配置")

    # 加载提示词文件
    prompt_path = _get_service_dir() / prompt_file
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            _prompt_cache[cache_key] = content
            logger.info(f"提示词加载成功: {prompt_type} (模式: {mode})")
            return content
    except Exception as e:
        logger.error(f"加载提示词文件失败: {prompt_path}, 错误: {e}")
        raise


def reload_prompts():
    """重新加载所有提示词（清空缓存）"""
    global _prompt_cache, _config_cache
    _prompt_cache.clear()
    _config_cache = None
    logger.info("提示词缓存已清空")


def get_available_modes() -> dict:
    """获取所有可用的分析模式"""
    config = load_config()
    return {
        mode: {
            "name": info.get("name", mode),
            "description": info.get("description", ""),
            "features": info.get("features", {})
        }
        for mode, info in config["modes"].items()
    }


def switch_mode(mode: str) -> bool:
    """
    切换分析模式（修改配置文件）

    Args:
        mode: 目标模式 (generic/review)

    Returns:
        是否切换成功
    """
    config = load_config()

    if mode not in config["modes"]:
        logger.error(f"无效的模式: {mode}")
        return False

    config["active_mode"] = mode

    # 保存配置文件
    config_path = _get_service_dir() / "prompt_config.json"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        # 清空缓存
        reload_prompts()

        logger.info(f"分析模式已切换到: {mode}")
        return True
    except Exception as e:
        logger.error(f"切换模式失败: {e}")
        return False


# 便捷函数
def load_page_analysis_prompt(mode: Optional[str] = None) -> str:
    """加载页面分析提示词"""
    return load_prompt("page_analysis", mode)


def load_chapter_analysis_prompt(mode: Optional[str] = None) -> str:
    """加载章节分析提示词"""
    return load_prompt("chapter_analysis", mode)


def load_overall_analysis_prompt(mode: Optional[str] = None) -> str:
    """加载整体分析提示词"""
    return load_prompt("overall_analysis", mode)


def load_transcript_analysis_prompt(mode: Optional[str] = None) -> str:
    """加载转写分析提示词"""
    return load_prompt("transcript_analysis", mode)
