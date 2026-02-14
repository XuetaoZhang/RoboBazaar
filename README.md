# RoboBazaar 🤖💰

> **A decentralized marketplace where robots autonomously hire and pay humans using X402 micropayments.**

---

## 🌟 Overview

In real-world logistics environments, robots handle ~80% of tasks autonomously. The remaining 20% — involving irregular, fragile, or oddly-shaped items — still require human dexterity. **RoboBazaar** bridges this gap by enabling robots to post bounties and pay human operators in USDC for on-demand assistance.

### How It Works

```
Robot encounters risky task
        ↓
AI Agent evaluates risk (risk_score > 0.7?)
        ↓
Robot posts bounty (0.5 USDC)
        ↓
Human operator accepts & helps
        ↓
X402 micropayment auto-executes
        ↓
Data flywheel: human actions → training data → smarter robots
```

---

## 📁 Project Structure

```
RoboBazaar/
├── victor_agent/          # AI Finance Agent (decision brain)
│   ├── finance_agent.py   # Core decision logic (rule engine + LLM)
│   ├── api_server.py      # FastAPI HTTP service
│   ├── prompts.py         # LLM prompt templates
│   ├── utils.py           # Utility functions
│   └── test_agent.py      # Unit tests
│
├── webots_sim/            # Webots simulation
│   ├── worlds/            # Simulation world files
│   └── controllers/       # Robot & human controllers
│
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── README.md              # This file
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/RoboBazaar.git
cd RoboBazaar
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run the Finance Agent API

```bash
cd victor_agent
python api_server.py
```

The API server starts at `http://localhost:8000`.

### 3. Test the Decision Engine

```bash
cd victor_agent
python test_agent.py
```

### 4. Run Webots Simulation

Open `webots_sim/worlds/warehouse.wbt` in Webots R2023a.

---

## 📡 API Reference

### `POST /api/agent/decide`

**Request:**
```json
{
    "robot_id": "robot_01",
    "risk_score": 0.85,
    "wallet_balance": 10.0,
    "task_description": "Pick up fragile glass"
}
```

**Response:**
```json
{
    "action": "PAY_HUMAN",
    "amount": 0.5,
    "currency": "USDC",
    "robot_id": "robot_01",
    "reason": "Risk score 0.85 exceeds threshold 0.7"
}
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Agent | Python + Crew.ai + LLM (Ollama / Azure OpenAI) |
| API Server | FastAPI + Uvicorn |
| Simulation | Webots R2023a |
| Payment | X402 Protocol (USDC on Base) |
| Frontend | React / Next.js + WebSocket + Wallet SDK |

---

## 👥 Team

| Member | Role |
|--------|------|
| **Victor** | AI Agent Developer + Pitch Lead |
| **MinQS** | Webots Simulation Engineer |
| **Yeahoung** | Bridge & Integration Developer |
| **Hersynne** | Frontend Operator Console |

---

## 📄 License

MIT License
