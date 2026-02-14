# RoboBazaar FinanceAgent

> 🧠 机器人决策大脑 - 判断何时需要付费雇佣人类帮助

---

## 📁 文件结构

```
victor_agent/
├── finance_agent.py    # 核心决策 Agent（规则引擎 + LLM 模式）
├── api_server.py       # FastAPI HTTP 服务（端口 8000）
├── prompts.py          # LLM 提示词模板
├── utils.py            # 工具函数（JSON 提取、日志等）
├── test_agent.py       # 单元测试脚本
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
└── README.md           # 本文档
```

---

## 🔄 运行逻辑

```
┌─────────────────────────────────────────────────────────────────┐
│                         API 请求入口                             │
│  POST /api/agent/decide                                          │
│  {robot_id, risk_score, wallet_balance, task_description}        │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     api_server.py                                 │
│  - 接收 HTTP 请求                                                │
│  - 参数验证 (Pydantic)                                           │
│  - 调用 FinanceAgent.decide()                                    │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   finance_agent.py                                │
│                                                                   │
│  FinanceAgent.decide()                                           │
│       │                                                          │
│       ├── use_llm=False ──► _decide_with_rules()                 │
│       │                     快速规则引擎：                        │
│       │                     IF risk > 0.7 AND balance >= bounty  │
│       │                     THEN PAY_HUMAN                       │
│       │                     ELSE CONTINUE_AUTONOMOUS             │
│       │                                                          │
│       └── use_llm=True ───► _decide_with_llm()                   │
│                             使用 Crew.ai + LLM：                  │
│                             1. 构建 Prompt (prompts.py)          │
│                             2. 调用 Ollama/Azure OpenAI          │
│                             3. 解析 JSON 输出 (utils.py)         │
│                             4. 失败则回退规则引擎                 │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                       决策结果                                    │
│  {                                                               │
│    "action": "PAY_HUMAN" | "CONTINUE_AUTONOMOUS",                │
│    "amount": 0.5,                                                │
│    "currency": "USDC",                                           │
│    "robot_id": "robot_01",                                       │
│    "reason": "Risk score 0.85 exceeds threshold 0.7"             │
│  }                                                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd victor_agent
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python test_agent.py
```

预期输出：
```
🎉 All tests passed!
```

### 3. 启动 API 服务

```bash
python api_server.py
```

服务将在 `http://localhost:8000` 启动。

### 4. 测试 API

```bash
curl -X POST http://localhost:8000/api/agent/decide \
  -H "Content-Type: application/json" \
  -d '{"robot_id":"robot_01","risk_score":0.85,"wallet_balance":10.0}'
```

---

## 📡 API 接口

### `POST /api/agent/decide`

**请求：**
```json
{
    "robot_id": "robot_01",
    "risk_score": 0.85,
    "wallet_balance": 10.0,
    "task_description": "Pick up fragile glass"
}
```

**响应：**
```json
{
    "action": "PAY_HUMAN",
    "amount": 0.5,
    "currency": "USDC",
    "robot_id": "robot_01",
    "reason": "Risk score 0.85 exceeds threshold 0.7"
}
```

### `GET /health`

健康检查接口。

---

## ⚙️ 配置说明

复制 `.env.example` 为 `.env` 并配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `RISK_THRESHOLD` | 风险阈值 | 0.7 |
| `DEFAULT_BOUNTY` | 默认赏金 | 0.5 USDC |
| `OLLAMA_BASE_URL` | Ollama 地址 | http://localhost:11434 |
| `AZURE_OPENAI_*` | Azure OpenAI 配置 | - |

---

## 🔗 与其他模块对接

| 对接模块 | 交互方式 | 说明 |
|----------|----------|------|
| **Webots 仿真** | HTTP POST | 机器人发送 risk_score，接收 action |
| **前端 Dashboard** | HTTP GET/POST | 显示决策结果和支付记录 |
| **X402 支付** | JSON 输出 | 返回 `PAY_HUMAN` 时触发链上支付 |

---

## 📖 核心决策逻辑

```python
if risk_score > 0.7 and wallet_balance >= 0.5:
    return "PAY_HUMAN"    # 付费雇佣人类
else:
    return "CONTINUE_AUTONOMOUS"  # 继续自主执行
```

**风险评分来源：**
- 物品形状检测（球形/不规则 → 高风险）
- 物品重量/危险程度
- 任务紧急性
