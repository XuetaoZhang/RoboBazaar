"""
RoboBazaar FinanceAgent - FastAPI HTTP 服务
提供 REST API 接口供其他组件调用
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from finance_agent import FinanceAgent, DEFAULT_BOUNTY, RISK_THRESHOLD
from utils import logger

# ============ FastAPI App ============
app = FastAPI(
    title="RoboBazaar FinanceAgent API",
    description="机器人决策大脑 - 判断何时需要付费雇佣人类帮助",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Agent 实例
agent = FinanceAgent(use_llm=False)


# ============ 请求/响应模型 ============
class DecisionRequest(BaseModel):
    """决策请求"""
    robot_id: str = Field(..., description="机器人 ID")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="风险评分 (0.0-1.0)")
    wallet_balance: float = Field(..., ge=0.0, description="钱包余额 (USDC)")
    task_description: Optional[str] = Field(default="Pick up item", description="任务描述")


class DecisionResponse(BaseModel):
    """决策响应"""
    action: str = Field(..., description="动作: PAY_HUMAN | CONTINUE_AUTONOMOUS")
    amount: float = Field(..., description="支付金额")
    currency: str = Field(default="USDC", description="货币类型")
    robot_id: str = Field(..., description="机器人 ID")
    reason: str = Field(..., description="决策原因")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    risk_threshold: float
    default_bounty: float


# ============ API 路由 ============
@app.get("/", response_model=HealthResponse)
async def root():
    """根路径 - 健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        risk_threshold=RISK_THRESHOLD,
        default_bounty=DEFAULT_BOUNTY
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        risk_threshold=RISK_THRESHOLD,
        default_bounty=DEFAULT_BOUNTY
    )


@app.post("/api/agent/decide", response_model=DecisionResponse)
async def make_decision(request: DecisionRequest):
    """
    核心决策接口
    
    接收风险信号，返回支付决策
    """
    try:
        logger.info(f"API Request: {request.model_dump()}")
        
        result = agent.decide(
            robot_id=request.robot_id,
            risk_score=request.risk_score,
            wallet_balance=request.wallet_balance,
            task_description=request.task_description
        )
        
        return DecisionResponse(**result)
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/decide/llm", response_model=DecisionResponse)
async def make_decision_llm(request: DecisionRequest):
    """
    使用 LLM 的决策接口
    
    需要配置 Ollama 或 Azure OpenAI
    """
    try:
        llm_agent = FinanceAgent(use_llm=True)
        
        result = llm_agent.decide(
            robot_id=request.robot_id,
            risk_score=request.risk_score,
            wallet_balance=request.wallet_balance,
            task_description=request.task_description
        )
        
        return DecisionResponse(**result)
        
    except Exception as e:
        logger.error(f"LLM API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 启动服务 ============
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting FinanceAgent API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
