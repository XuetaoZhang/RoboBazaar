"""
RoboBazaar FinanceAgent - 工具函数
"""
import re
import json
import logging
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("FinanceAgent")


def extract_json(text: str) -> Optional[dict]:
    """
    从 LLM 输出文本中提取 JSON 对象
    
    Args:
        text: LLM 原始输出
    
    Returns:
        解析后的 dict，失败返回 None
    """
    # 尝试直接解析
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # 使用正则提取 JSON 块
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # 尝试提取 markdown 代码块中的 JSON
    code_pattern = r'```(?:json)?\s*([\s\S]*?)```'
    code_matches = re.findall(code_pattern, text)
    
    for code in code_matches:
        try:
            return json.loads(code.strip())
        except json.JSONDecodeError:
            continue
    
    return None


def validate_decision(decision: dict) -> bool:
    """
    验证决策格式是否正确
    
    Args:
        decision: 决策 dict
    
    Returns:
        是否有效
    """
    required_keys = ["action", "amount", "currency", "reason"]
    valid_actions = ["PAY_HUMAN", "CONTINUE_AUTONOMOUS"]
    
    if not all(key in decision for key in required_keys):
        return False
    
    if decision["action"] not in valid_actions:
        return False
    
    if not isinstance(decision["amount"], (int, float)):
        return False
    
    return True


def format_decision_response(
    action: str,
    amount: float,
    robot_id: str = "",
    reason: str = ""
) -> dict:
    """
    格式化决策响应
    """
    return {
        "action": action,
        "amount": amount,
        "currency": "USDC",
        "robot_id": robot_id,
        "reason": reason
    }
