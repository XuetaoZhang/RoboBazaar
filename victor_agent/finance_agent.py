"""
RoboBazaar FinanceAgent - 决策大脑
负责判断何时需要花钱雇佣人类帮助
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv

from utils import extract_json, validate_decision, format_decision_response, logger
from prompts import FINANCE_AGENT_SYSTEM_PROMPT, DECISION_TASK_TEMPLATE

# 加载环境变量
load_dotenv()

# ============ 配置 ============
RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", "0.7"))
DEFAULT_BOUNTY = float(os.getenv("DEFAULT_BOUNTY", "0.5"))


class FinanceAgent:
    """
    FinanceAgent - 机器人财务决策代理
    
    支持两种模式：
    1. 规则引擎模式（默认）：快速、确定性决策
    2. LLM 模式：使用 Crew.ai + LLM 进行智能决策
    """
    
    def __init__(self, use_llm: bool = False, llm_backend: str = "ollama"):
        """
        初始化 FinanceAgent
        
        Args:
            use_llm: 是否使用 LLM 进行决策
            llm_backend: LLM 后端 ("ollama" | "azure" | "gemini")
        """
        self.use_llm = use_llm
        self.llm_backend = llm_backend
        self.llm = None
        self.agent = None
        
        if use_llm:
            self._init_llm_agent()
        
        logger.info(f"FinanceAgent initialized (LLM: {use_llm}, Backend: {llm_backend})")
    
    def _init_llm_agent(self):
        """初始化 LLM Agent（需要安装 crewai）"""
        try:
            from crewai import Agent
            
            if self.llm_backend == "ollama":
                from langchain_community.llms import Ollama
                self.llm = Ollama(
                    model=os.getenv("OLLAMA_MODEL", "llama3"),
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                )
            elif self.llm_backend == "azure":
                from langchain_openai import AzureChatOpenAI
                self.llm = AzureChatOpenAI(
                    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
                )
            
            self.agent = Agent(
                role="Financial Decision Maker",
                goal="Decide whether the robot should pay for human assistance",
                backstory="You are the CFO of a robot. You manage its wallet and decide when to pay for help.",
                llm=self.llm,
                verbose=True
            )
            logger.info(f"LLM Agent initialized with {self.llm_backend}")
            
        except ImportError as e:
            logger.warning(f"Failed to initialize LLM: {e}. Falling back to rule engine.")
            self.use_llm = False
    
    def decide(
        self,
        robot_id: str,
        risk_score: float,
        wallet_balance: float,
        task_description: str = "Pick up item"
    ) -> dict:
        """
        核心决策函数
        
        Args:
            robot_id: 机器人 ID
            risk_score: 风险评分 (0.0-1.0)
            wallet_balance: 钱包余额 (USDC)
            task_description: 任务描述
        
        Returns:
            决策结果 dict
        """
        logger.info(f"[{robot_id}] Decision request: risk={risk_score}, balance={wallet_balance}")
        
        if self.use_llm and self.agent:
            return self._decide_with_llm(robot_id, risk_score, wallet_balance, task_description)
        else:
            return self._decide_with_rules(robot_id, risk_score, wallet_balance)
    
    def _decide_with_rules(
        self,
        robot_id: str,
        risk_score: float,
        wallet_balance: float
    ) -> dict:
        """
        规则引擎决策（快速、确定性）
        """
        if risk_score > RISK_THRESHOLD and wallet_balance >= DEFAULT_BOUNTY:
            decision = format_decision_response(
                action="PAY_HUMAN",
                amount=DEFAULT_BOUNTY,
                robot_id=robot_id,
                reason=f"Risk score {risk_score:.2f} exceeds threshold {RISK_THRESHOLD}"
            )
            logger.info(f"[{robot_id}] Decision: PAY_HUMAN ({DEFAULT_BOUNTY} USDC)")
        else:
            reason = "Risk acceptable" if risk_score <= RISK_THRESHOLD else "Insufficient balance"
            decision = format_decision_response(
                action="CONTINUE_AUTONOMOUS",
                amount=0,
                robot_id=robot_id,
                reason=reason
            )
            logger.info(f"[{robot_id}] Decision: CONTINUE_AUTONOMOUS")
        
        return decision
    
    def _decide_with_llm(
        self,
        robot_id: str,
        risk_score: float,
        wallet_balance: float,
        task_description: str
    ) -> dict:
        """
        使用 LLM Agent 决策
        """
        try:
            from crewai import Task, Crew
            
            task = Task(
                description=DECISION_TASK_TEMPLATE.format(
                    robot_id=robot_id,
                    risk_score=risk_score,
                    wallet_balance=wallet_balance,
                    bounty_required=DEFAULT_BOUNTY,
                    task_description=task_description
                ),
                agent=self.agent,
                expected_output="A JSON object with payment decision"
            )
            
            crew = Crew(agents=[self.agent], tasks=[task], verbose=True)
            result = crew.kickoff()
            
            # 解析 LLM 输出
            decision = extract_json(str(result))
            
            if decision and validate_decision(decision):
                decision["robot_id"] = robot_id
                logger.info(f"[{robot_id}] LLM Decision: {decision['action']}")
                return decision
            else:
                logger.warning(f"[{robot_id}] Invalid LLM output, falling back to rules")
                return self._decide_with_rules(robot_id, risk_score, wallet_balance)
                
        except Exception as e:
            logger.error(f"[{robot_id}] LLM error: {e}, falling back to rules")
            return self._decide_with_rules(robot_id, risk_score, wallet_balance)


# ============ 便捷函数 ============
def decide_payment(
    robot_id: str,
    risk_score: float,
    wallet_balance: float,
    use_llm: bool = False
) -> dict:
    """
    便捷决策函数
    
    Args:
        robot_id: 机器人 ID
        risk_score: 风险评分 (0.0-1.0)
        wallet_balance: 钱包余额 (USDC)
        use_llm: 是否使用 LLM
    
    Returns:
        决策结果 dict
    """
    agent = FinanceAgent(use_llm=use_llm)
    return agent.decide(robot_id, risk_score, wallet_balance)


# ============ 测试入口 ============
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        {"robot_id": "robot_01", "risk_score": 0.85, "wallet_balance": 10.0},  # 应付款
        {"robot_id": "robot_02", "risk_score": 0.45, "wallet_balance": 10.0},  # 不付款
        {"robot_id": "robot_03", "risk_score": 0.90, "wallet_balance": 0.1},   # 余额不足
    ]
    
    print("=" * 60)
    print("FinanceAgent Test Suite")
    print("=" * 60)
    
    agent = FinanceAgent(use_llm=False)
    
    for case in test_cases:
        result = agent.decide(**case)
        print(f"\nInput: {case}")
        print(f"Output: {json.dumps(result, indent=2)}")
