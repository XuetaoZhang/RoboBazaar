# RoboBazaar Webots Simulation

> Webots Version: **2023a**

## Quick Start

```bash
# Open the simulation
webots webots_sim/worlds/warehouse.wbt
```

## Directory Structure

```
webots_sim/
├── worlds/
│   └── warehouse.wbt           # Main scene (4 shelves, 3 robots, 1 human)
├── controllers/
│   ├── robot_controller/       # Nao robot controller
│   │   └── robot_controller.py
│   ├── human_controller/       # Human NPC controller
│   │   └── human_controller.py
│   └── supervisor/             # Scene manager
│       └── supervisor.py
└── sounds/                     # TTS audio files (optional)
```

## Features

| Feature | Implementation |
|---------|----------------|
| Shape Detection | BOX=auto, SPHERE/CONE/IRREGULAR=help |
| Dynamic Bounty | `bounty = f(weight, danger, urgency)` |
| Status LED | Green=normal, Red breathing=help |
| English TTS | Speaker device |
| Priority Selection | Distance → Bounty → Random |
| X402 Payment | Emitter/Receiver messaging |

## Business Logic

- **80%** Regular packages → Auto delivery
- **20%** Irregular items → Human help → X402 payment

## Scene Elements

- 4 shelf rows with various packages
- Empty box area (corner)
- Delivery zone
- 3 Nao robots
- 1 Human operator

## Workflow

1. Robot detects package shape
2. If irregular → Fetch empty box → Go to shelf
3. Red LED + TTS: "Need help! Bounty 0.75 USDC..."
4. Human walks to robot, picks item, places in box
5. Robot detects item → Triggers X402 payment
6. Green LED → Deliver to delivery zone
