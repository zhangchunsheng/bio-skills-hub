"""
Bionic Cognition - 仿生认知系统

整合前额叶意图解码、信息论策略优化、复杂度分类
"""

from .intent_decoder import IntentDecoder, get_intent_decoder, IntentType

__all__ = [
    'IntentDecoder', 'get_intent_decoder', 'IntentType'
]

__version__ = '1.0.0'
