"""
RoboBazaar E-puck Robot Controller
Simple wheeled robot for demo
"""
from controller import Robot
import random
import json

class EpuckController:
    def __init__(self):
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        self.name = self.robot.getName()
        
        # Motors
        self.left_motor = self.robot.getDevice("left wheel motor")
        self.right_motor = self.robot.getDevice("right wheel motor")
        if self.left_motor:
            self.left_motor.setPosition(float('inf'))
            self.left_motor.setVelocity(0)
        if self.right_motor:
            self.right_motor.setPosition(float('inf'))
            self.right_motor.setVelocity(0)
        
        # LEDs
        self.leds = []
        for i in range(8):
            led = self.robot.getDevice(f"led{i}")
            if led:
                self.leds.append(led)
        
        # Communication
        self.emitter = self.robot.getDevice("emitter")
        self.receiver = self.robot.getDevice("receiver")
        if self.receiver:
            self.receiver.enable(self.timestep)
        
        # State
        self.state = "IDLE"
        self.step_count = 0
        self.wait_counter = 0
        self.current_bounty = 0
        
        print(f"[{self.name}] E-puck controller initialized")
    
    def run(self):
        while self.robot.step(self.timestep) != -1:
            self.step_count += 1
            
            # State machine
            if self.state == "IDLE":
                self._set_leds(0, 255, 0)  # Green
                if self.step_count % 200 == 0 and random.random() < 0.3:
                    self.state = "ASSESS"
                    print(f"[{self.name}] New task detected")
            
            elif self.state == "ASSESS":
                if random.random() < 0.8:
                    print(f"[{self.name}] ✅ Regular package, auto processing")
                    self.state = "AUTO_PROCESS"
                else:
                    self.current_bounty = round(random.uniform(0.3, 1.5), 2)
                    print(f"[{self.name}] ⚠️ Irregular item, bounty={self.current_bounty} USDC")
                    self._send_help_request()
                    self.state = "WAIT_HUMAN"
            
            elif self.state == "AUTO_PROCESS":
                self._move_forward()
                self.wait_counter += 1
                if self.wait_counter > 80:
                    self._stop()
                    self.wait_counter = 0
                    self.state = "DELIVER"
            
            elif self.state == "WAIT_HUMAN":
                self._set_leds(255, 0, 0)  # Red
                self.wait_counter += 1
                if self.wait_counter > 200:
                    print(f"[{self.name}] Human helped!")
                    self._trigger_payment()
                    self.wait_counter = 0
                    self.state = "DELIVER"
            
            elif self.state == "DELIVER":
                self._set_leds(0, 0, 255)  # Blue
                self._move_forward()
                self.wait_counter += 1
                if self.wait_counter > 60:
                    self._stop()
                    self.wait_counter = 0
                    print(f"[{self.name}] ✓ Task complete")
                    self._send_complete()
                    self.state = "IDLE"
    
    def _move_forward(self):
        if self.left_motor and self.right_motor:
            self.left_motor.setVelocity(2)
            self.right_motor.setVelocity(2)
    
    def _stop(self):
        if self.left_motor and self.right_motor:
            self.left_motor.setVelocity(0)
            self.right_motor.setVelocity(0)
    
    def _set_leds(self, r, g, b):
        for led in self.leds:
            led.set(1 if r > 128 else 0)
    
    def _send_help_request(self):
        if self.emitter:
            msg = {
                "type": "HELP_REQUEST",
                "robot_id": self.name,
                "bounty": self.current_bounty
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))
        print(f"[{self.name}] 🔴 HELP REQUESTED - Bounty: {self.current_bounty} USDC")
    
    def _trigger_payment(self):
        if self.emitter:
            msg = {
                "type": "PAYMENT",
                "robot_id": self.name,
                "amount": self.current_bounty
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))
        print(f"[{self.name}] 💰 PAID {self.current_bounty} USDC")
    
    def _send_complete(self):
        if self.emitter:
            msg = {
                "type": "STATUS",
                "robot_id": self.name,
                "status": "COMPLETE"
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))

if __name__ == "__main__":
    EpuckController().run()
