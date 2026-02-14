"""
RoboBazaar Warehouse Robot Controller v4
Webots Version: 2023a
Features: GPS navigation, Emitter/Receiver communication, LED status, Dynamic bounty
"""
from controller import Robot, Camera, Motor, LED, GPS, Emitter, Receiver
import math
import random
import json

# ============ CONFIGURATION ============
BOX_AREA = (-6, 0, 4)      # Empty box pickup area
SHELF_AREA = (0, 0, -3)    # In front of shelves
DELIVERY_AREA = (6, 0, 4)  # Delivery zone
MOVE_SPEED = 0.5           # Movement speed multiplier

# ============ DYNAMIC BOUNTY CALCULATION ============
def calculate_bounty(weight: float, danger_level: float, urgency: float) -> float:
    base = 0.3
    weight_bonus = weight * 0.1
    danger_bonus = danger_level * 0.5
    urgency_bonus = urgency * 0.3
    total = base + weight_bonus + danger_bonus + urgency_bonus
    return round(min(total, 2.0), 2)

# ============ STATE ENUM ============
class State:
    IDLE = "IDLE"
    ASSESS = "ASSESS"
    GRASP = "GRASP"
    FETCH_BOX = "FETCH_BOX"
    APPROACH_SHELF = "APPROACH_SHELF"
    WAIT_HUMAN = "WAIT_HUMAN"
    RECEIVE_ITEM = "RECEIVE_ITEM"
    PAY_REWARD = "PAY_REWARD"
    DELIVER = "DELIVER"

# ============ MAIN CONTROLLER ============
class DeliveryRobotController:
    def __init__(self):
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.robot_name = self.robot.getName()
        self.state = State.IDLE
        self.target_item = None
        self.current_bounty = 0.0
        self.breathing_phase = 0.0
        self.has_empty_box = False
        self.step_count = 0
        self.wait_counter = 0
        self.target_position = None
        
        self._init_devices()
        self._init_motion()
        print(f"[{self.robot_name}] Controller v4 initialized")
    
    def _init_devices(self):
        """Initialize all robot devices."""
        # Camera
        self.camera = self.robot.getDevice("CameraTop")
        if self.camera:
            self.camera.enable(self.timestep * 4)
        
        # GPS for navigation
        self.gps = self.robot.getDevice("gps")
        if self.gps:
            self.gps.enable(self.timestep)
            print(f"[{self.robot_name}] GPS enabled")
        
        # Status LED (added in bodySlot)
        self.status_led = self.robot.getDevice("status_led")
        if self.status_led:
            print(f"[{self.robot_name}] Status LED found")
        
        # Nao's built-in LEDs
        self.chest_led = self.robot.getDevice("ChestBoard/Led")
        
        # Emitter for sending messages
        self.emitter = self.robot.getDevice("emitter")
        if self.emitter:
            print(f"[{self.robot_name}] Emitter enabled (channel 1)")
        
        # Receiver for incoming messages
        self.receiver = self.robot.getDevice("receiver")
        if self.receiver:
            self.receiver.enable(self.timestep)
            print(f"[{self.robot_name}] Receiver enabled (channel 2)")
        
        # Motors
        self.motors = {}
        motor_names = [
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
            "LHipYawPitch", "LHipRoll", "LHipPitch", "LKneePitch", "LAnklePitch", "LAnkleRoll",
            "RHipYawPitch", "RHipRoll", "RHipPitch", "RKneePitch", "RAnklePitch", "RAnkleRoll",
            "HeadYaw", "HeadPitch"
        ]
        for name in motor_names:
            motor = self.robot.getDevice(name)
            if motor:
                self.motors[name] = motor
    
    def _init_motion(self):
        """Initialize robot to stable standing pose."""
        # Use Nao's default standing position (all zeros = T-pose)
        # This is more stable than custom positions
        stable_positions = {
            "LShoulderPitch": 1.5, "RShoulderPitch": 1.5,  # Arms down
            "LShoulderRoll": 0.1, "RShoulderRoll": -0.1,
            "LElbowYaw": 0, "RElbowYaw": 0,
            "LElbowRoll": 0, "RElbowRoll": 0,
            "LHipYawPitch": 0, "RHipYawPitch": 0,
            "LHipRoll": 0, "RHipRoll": 0,
            "LHipPitch": 0, "RHipPitch": 0,  # Legs straight
            "LKneePitch": 0, "RKneePitch": 0,
            "LAnklePitch": 0, "RAnklePitch": 0,
            "LAnkleRoll": 0, "RAnkleRoll": 0,
            "HeadYaw": 0, "HeadPitch": 0,
        }
        for name, pos in stable_positions.items():
            if name in self.motors:
                self.motors[name].setPosition(pos)
    
    def run(self):
        """Main control loop."""
        while self.robot.step(self.timestep) != -1:
            self.step_count += 1
            
            # Check incoming messages
            self._check_messages()
            
            # Update LED based on state
            if self.state in [State.WAIT_HUMAN, State.APPROACH_SHELF]:
                self._update_breathing_light()
            elif self.state == State.IDLE:
                self._set_green_light()
            
            # State machine
            self._state_machine()
    
    def _state_machine(self):
        """Robot state machine."""
        if self.state == State.IDLE:
            # Check for new task every ~3 seconds
            if self.step_count % 200 == 0 and self._detect_task():
                self.state = State.ASSESS
                print(f"[{self.robot_name}] New task detected, assessing...")
        
        elif self.state == State.ASSESS:
            shape = self._detect_shape()
            if shape == "BOX":
                print(f"[{self.robot_name}] ✅ Regular package (BOX), auto processing")
                self._send_status("AUTO_GRASP")
                self.state = State.GRASP
            else:
                self._calculate_and_set_bounty(shape)
                print(f"[{self.robot_name}] ⚠️ Irregular item ({shape}), bounty={self.current_bounty} USDC")
                self._send_status("NEED_HELP")
                self.state = State.FETCH_BOX
        
        elif self.state == State.GRASP:
            self._animate_grasp()
            self.wait_counter += 1
            if self.wait_counter > 60:
                self.wait_counter = 0
                self.target_position = DELIVERY_AREA
                self.state = State.DELIVER
        
        elif self.state == State.FETCH_BOX:
            self.target_position = BOX_AREA
            if self._move_towards_target():
                self._animate_pickup_box()
                self.has_empty_box = True
                self.wait_counter = 0
                self.state = State.APPROACH_SHELF
        
        elif self.state == State.APPROACH_SHELF:
            self.target_position = SHELF_AREA
            if self._move_towards_target():
                self._trigger_help_request()
                self.wait_counter = 0
                self.state = State.WAIT_HUMAN
        
        elif self.state == State.WAIT_HUMAN:
            self.wait_counter += 1
            # Wait for human or timeout
            if self.wait_counter > 300:
                print(f"[{self.robot_name}] Human arrived (simulated)")
                self.wait_counter = 0
                self.state = State.RECEIVE_ITEM
        
        elif self.state == State.RECEIVE_ITEM:
            self.wait_counter += 1
            if self.wait_counter > 150:
                print(f"[{self.robot_name}] Item received in box!")
                self.wait_counter = 0
                self.state = State.PAY_REWARD
        
        elif self.state == State.PAY_REWARD:
            self._set_green_light()
            self._trigger_payment()
            self.has_empty_box = False
            self.target_position = DELIVERY_AREA
            self.state = State.DELIVER
        
        elif self.state == State.DELIVER:
            if self._move_towards_target():
                self._animate_drop()
                self.wait_counter = 0
                print(f"[{self.robot_name}] ✓ Task complete")
                self._send_status("COMPLETE")
                self.state = State.IDLE
    
    # ============ NAVIGATION ============
    def _get_position(self):
        """Get current GPS position."""
        if self.gps:
            pos = self.gps.getValues()
            return (pos[0], pos[1], pos[2])
        return (0, 0, 0)
    
    def _move_towards_target(self) -> bool:
        """
        Move robot towards target position.
        Returns True when reached.
        """
        if not self.target_position:
            return True
        
        current = self._get_position()
        target = self.target_position
        
        dx = target[0] - current[0]
        dz = target[2] - current[2]
        distance = math.sqrt(dx*dx + dz*dz)
        
        if distance < 0.5:
            # Reached target
            self._stop_walking()
            return True
        
        # Simple walking animation (in place for demo)
        self._animate_walk()
        return False
    
    def _animate_walk(self):
        """Simple walking animation."""
        phase = self.step_count * 0.1
        swing = math.sin(phase) * 0.2
        
        if "LHipPitch" in self.motors:
            self.motors["LHipPitch"].setPosition(-0.4 + swing)
        if "RHipPitch" in self.motors:
            self.motors["RHipPitch"].setPosition(-0.4 - swing)
        if "LShoulderPitch" in self.motors:
            self.motors["LShoulderPitch"].setPosition(1.4 - swing * 0.5)
        if "RShoulderPitch" in self.motors:
            self.motors["RShoulderPitch"].setPosition(1.4 + swing * 0.5)
    
    def _stop_walking(self):
        """Stop walking, return to standing."""
        self._init_motion()
    
    # ============ ANIMATIONS ============
    def _animate_grasp(self):
        """Grasp animation."""
        if self.wait_counter == 1:
            print(f"[{self.robot_name}] Grasping package...")
        if "LShoulderPitch" in self.motors:
            self.motors["LShoulderPitch"].setPosition(0.5)
        if "RShoulderPitch" in self.motors:
            self.motors["RShoulderPitch"].setPosition(0.5)
        if "LElbowRoll" in self.motors:
            self.motors["LElbowRoll"].setPosition(-1.0)
        if "RElbowRoll" in self.motors:
            self.motors["RElbowRoll"].setPosition(1.0)
    
    def _animate_pickup_box(self):
        """Pick up empty box animation."""
        print(f"[{self.robot_name}] Picking up empty box...")
        if "LShoulderPitch" in self.motors:
            self.motors["LShoulderPitch"].setPosition(0.3)
        if "RShoulderPitch" in self.motors:
            self.motors["RShoulderPitch"].setPosition(0.3)
    
    def _animate_drop(self):
        """Drop package animation."""
        print(f"[{self.robot_name}] Dropping package...")
        if "LShoulderPitch" in self.motors:
            self.motors["LShoulderPitch"].setPosition(1.5)
        if "RShoulderPitch" in self.motors:
            self.motors["RShoulderPitch"].setPosition(1.5)
    
    # ============ SHAPE DETECTION ============
    def _detect_shape(self) -> str:
        """80% BOX, 20% irregular."""
        if random.random() < 0.8:
            return "BOX"
        return random.choice(["SPHERE", "CONE", "IRREGULAR"])
    
    def _calculate_and_set_bounty(self, shape: str):
        shape_danger = {"SPHERE": 0.5, "CONE": 0.7, "IRREGULAR": 0.8}
        danger = shape_danger.get(shape, 0.5)
        weight = random.uniform(0.5, 2.0)
        urgency = random.uniform(0.2, 0.8)
        self.current_bounty = calculate_bounty(weight, danger, urgency)
        self.target_item = shape
    
    # ============ LED CONTROL ============
    def _set_green_light(self):
        """Green = normal operation."""
        if self.status_led:
            self.status_led.set(0x00FF00)
        if self.chest_led:
            self.chest_led.set(0x00FF00)
    
    def _update_breathing_light(self):
        """Red breathing = waiting for help."""
        self.breathing_phase += 0.06
        intensity = int(((math.sin(self.breathing_phase) + 1) / 2) * 255)
        color = (intensity << 16)  # Red
        
        if self.status_led:
            self.status_led.set(color)
        if self.chest_led:
            self.chest_led.set(color)
    
    # ============ COMMUNICATION ============
    def _send_status(self, status: str):
        """Send status to supervisor."""
        if self.emitter:
            msg = {
                "type": "STATUS",
                "robot_id": self.robot_name,
                "status": status,
                "bounty": self.current_bounty,
                "position": list(self._get_position())
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))
    
    def _trigger_help_request(self):
        """Send help request."""
        print(f"[{self.robot_name}] 🔴 HELP REQUESTED - Bounty: {self.current_bounty} USDC")
        print(f"[{self.robot_name}] 🔊 TTS: 'Need help! Bounty {self.current_bounty} USDC'")
        
        if self.emitter:
            msg = {
                "type": "HELP_REQUEST",
                "robot_id": self.robot_name,
                "bounty": self.current_bounty,
                "item_shape": self.target_item,
                "position": list(self._get_position())
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))
    
    def _trigger_payment(self):
        """Send X402 payment."""
        print(f"[{self.robot_name}] 💰 PAID {self.current_bounty} USDC - Thank you!")
        
        if self.emitter:
            msg = {
                "type": "PAYMENT",
                "robot_id": self.robot_name,
                "amount": self.current_bounty,
                "currency": "USDC",
                "recipient": "human_operator"
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))
    
    def _check_messages(self):
        """Check for incoming messages."""
        while self.receiver and self.receiver.getQueueLength() > 0:
            try:
                data = self.receiver.getString()
                self.receiver.nextPacket()
                msg = json.loads(data)
                
                if msg.get("type") == "HUMAN_ARRIVED" and msg.get("robot_id") == self.robot_name:
                    if self.state == State.WAIT_HUMAN:
                        print(f"[{self.robot_name}] Message: Human arrived!")
                        self.wait_counter = 999  # Trigger state transition
            except Exception as e:
                pass
    
    def _detect_task(self) -> bool:
        return random.random() < 0.25

# ============ ENTRY POINT ============
if __name__ == "__main__":
    controller = DeliveryRobotController()
    controller.run()
