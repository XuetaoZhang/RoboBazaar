**RoboBazaar Operator Console**  
  
**前端需求文档（PRD）**  
  
**1. 文档信息**  
	•	项目名称：RoboBazaar  
	•	模块名称：Operator Console（功能性前端）  
	•	文档类型：功能需求文档（PRD）  
	•	阶段：Hackathon MVP（7-Day Sprint）  
	•	前端技术建议：React / Next.js + WebSocket + Wallet SDK（MetaMask / RainbowKit）  
  
⸻  
  
**2. 产品定位（非常重要）**  

**2.0 产品说明**

RoboBazaar is a decentralized skill marketplace that enables robots to autonomously hire and pay human workers using the X402 payment protocol on the Base network. In real-world logistics and warehouse environments, robots handle approximately 80% of tasks autonomously. However, the remaining 20% — involving irregular, fragile, or oddly-shaped items — still require human dexterity and judgment. When a robot encounters such a task, it dynamically calculates a bounty based on item weight, danger level, and urgency. It then broadcasts a help request with a USDC reward. Nearby human operators receive the request on a dashboard, accept the task, and physically assist the robot. Upon task completion, the robot verifies the result using its onboard camera and triggers an automatic X402 micropayment to the human's wallet. Our system consists of four core components: (1) An AI FinanceAgent powered by LLMs that decides when to spend money on human help, (2) A Webots simulation demonstrating multi-robot coordination in a warehouse, (3) A bridge layer connecting simulation signals to the agent brain, and (4) A frontend dashboard for human operators to monitor bounties and accept tasks. Every human intervention generates labeled training data, creating a powerful data flywheel: more help → better data → smarter robots → fewer interventions needed. RoboBazaar doesn't build algorithms — it builds the commercial infrastructure to monetize them. We take a 5% platform fee on every transaction while enabling algorithm developers to earn passive income when their skills are purchased by robots in the field.
  
**2.1 定位说明**  
  
本前端不是营销型落地页（Landing Page），而是一个：  
  
**Human-in-the-Loop Robotics Operator Console**  
  
用于在**机器人发生异常时**：  
	•	实时展示状态  
	•	触发 X402 支付签名流程  
	•	在支付成功后接管/触发机器人恢复  
	•	展示个人与系统层面的贡献数据  
  
**2.2 目标用户**  
	•	远程协助人员（Human Operator）  
	•	黑客松评委（Demo 场景）  
	•	后续：运维人员 / 平台接单者  
  
⸻  
  
**3. 页面范围与结构**  
  
**3.1 页面数量**  
	•	**MVP 阶段仅 1 个页面**  
	•	/ Dashboard / Operator Console  
  
**3.2 页面整体结构（自上而下）**  
  
```
┌────────────────────────────┐
│ Top Status Bar              │
├────────────────────────────┤
│ Alert / Payment Modal       │
├────────────────────────────┤
│ Control Panel               │
├────────────────────────────┤
│ Metrics / Data Flywheel     │
└────────────────────────────┘

```
  
  
⸻  
  
**4. 功能模块需求**  
  
⸻  
  
**4.1 顶部状态栏（Robot Status Bar）**  
  
**功能说明**  
实时展示机器人当前运行状态，是**全站最高优先级信息**。  
  
**展示内容**  
	•	Robot ID（如：Robot #01）  
	•	当前状态：  
	•	🟢 Robot Active  
	•	🔴 WAITING FOR HELP  
	•	失败类型（可选）：  
	•	stuck / drop / grasp_failed  
	•	风险值（risk score，如 0.8）  
	•	最近更新时间（timestamp）  
  
**交互规则**  
	•	当状态为异常时：  
	•	状态栏整体变红  
	•	自动触发告警弹窗（见 4.2）  
  
⸻  
  
**4.2 告警 & 支付弹窗（Alert + X402 Flow）**  
  
**触发条件**  
	•	前端通过 WebSocket / 轮询接收到：  
  
```
{
  "robotId": "01",
  "status": "stuck",
  "risk": 0.8
}

```
  
**弹窗阶段划分（状态机）**  
**阶段 1：告警**  
	•	标题：Robot Needs Help  
	•	描述：Robot #01 is stuck (risk: 0.8)  
	•	主按钮：Help Robot  
  
⸻  
  
**阶段 2：X402 支付握手**  
	1.	用户点击 Help Robot  
	2.	前端向后端发起请求  
	3.	后端返回 **402 Payment Required**  
	4.	前端解析并展示：  
	•	Price：0.5 USDC  
	•	签名文案（Sign Message）：  
I agree to pay 0.5 USDC to help Robot #01  
  
⸻  
  
**阶段 3：钱包签名**  
	•	拉起钱包（MetaMask / RainbowKit）  
	•	类型：**Sign Message / EIP-712**  
	•	⚠️ 明确提示：  
“This is a signature request, not a token transfer.”  
  
⸻  
  
**阶段 4：支付确认**  
	•	前端携带 signature 重新请求后端  
	•	成功后显示：  
	•	✅ Payment Accepted  
  
⸻  
  
**4.3 控制面板（Control Panel）**  
  
**功能说明**  
**支付成功后解锁控制权**  
  
**初始状态**  
	•	按钮为灰色、不可点击：  
	•	Reset Robot  
	•	或 Confirm Human Assistance  
  
**解锁条件**  
	•	收到后端返回：  
  
{ "paymentAccepted": true }  
  
**操作行为**  
	•	用户点击按钮  
	•	前端调用后端接口  
	•	后端触发仿真 / 机器人恢复  
	•	状态回到 🟢 Robot Active  
  
⸻  
  
**4.4 数据飞轮 / 指标展示（Metrics）**  
  
**位置**  
	•	页面右下角 / 侧边栏（非核心但明显）  
  
**展示内容（MVP）**  
	•	My Contributions：  
	•	Tasks Solved: 1  
	•	Earned: 0.5 USDC  
	•	Platform Metrics（可 mock）：  
	•	Total Robots Rescued  
	•	Total Paid (USDC)  
  
**设计目的**  
	•	强化“机器-人零工经济”概念  
	•	帮助评委快速理解商业模型  
  
⸻  

**4.5 机器人展示（Metrics）**  

**说明**
现在给出了一个仿真机器人视频，需要展示到页面中，视频文件在assets\52aff143030c7066a01470f13fe12a54.mp4
占区域不应该太大，但必须显著；

⸻  
  
**5. 状态机（前端核心逻辑）**  
  
```
IDLE
 ↓
ROBOT_ACTIVE
 ↓ (status: stuck)
ALERT
 ↓ (user clicks Help)
PAYMENT_REQUIRED (402)
 ↓ (wallet sign)
PAYMENT_ACCEPTED
 ↓
CONTROL_UNLOCKED
 ↓
ROBOT_RECOVERED

```
  
  
⸻  
  
**6. 接口需求（最小集合）**  
  
**6.1 实时状态**  
	•	WebSocket：/ws  
	•	推送 robot status / risk  
  
（或）  
	•	HTTP Polling：GET /status?robotId=01  
  
⸻  
  
**6.2 X402 第一次请求**  
  
```
POST /help/request

```
→ 402 Payment Required  
  
Response Body（示例）：  
  
```
{
  "price": 0.5,
  "currency": "USDC",
  "signMessage": "I agree to pay 0.5 USDC to help Robot #01"
}

```
  
  
⸻  
  
**6.3 X402 第二次请求**  
  
```
POST /help/confirm
Headers:
  X-Payment-Signature: <signature>

```
  
  
⸻  
  
**6.4 控制接口**  
  
```
POST /assist/reset

```
  
  
⸻  
  
**7. 非功能性要求**  
	•	响应速度：状态更新 < 1s  
	•	UI 原则：  
	•	红 / 绿 强对比  
	•	避免复杂动画  
	•	Demo 友好：  
	•	所有关键状态必须“看得见”  
  
⸻  
  
**8. 明确不做的事情（MVP 排除项）**  
	•	用户系统 / 登录  
	•	真链上转账  
	•	复杂权限系统  
	•	多机器人管理  
  
⸻  
  
**9. 成功标准（Definition of Done）**  
	•	机器人异常 → 页面即时告警  
	•	可完成完整 X402 签名流程  
	•	支付成功 → 控制按钮解锁  
	•	点击控制 → 机器人恢复  
	•	Demo 全流程可在 2–3 分钟内跑完  
