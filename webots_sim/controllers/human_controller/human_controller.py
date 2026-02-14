"""
RoboBazaar Human Operator Controller
Webots Version: 2023a
Priority: Distance > Bounty > Random
"""
from controller import Robot, GPS, Receiver, Emitter
import math
import random
import json

class HumanController:
    def __init__(self):
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        
        # GPS
        self.gps = self.robot.getDevice("gps")
        if self.gps:
            self.gps.enable(self.timestep)
        
        # Communication - Human listens on channel 2 (from supervisor)
        self.receiver = self.robot.getDevice("receiver")
        if self.receiver:
            self.receiver.enable(self.timestep)
            print("[HUMAN] Receiver enabled")
        
        self.emitter = self.robot.getDevice("emitter")
        
        self.state = "IDLE"
        self.target_robot = None
        self.pending_requests = []
        self.step_count = 0
        self.action_counter = 0
        
        print("[HUMAN] Operator controller initialized")
    
    def run(self):
        while self.robot.step(self.timestep) != -1:
            self.step_count += 1
            
            # Check for help requests
            self._receive_messages()
            
            # State machine
            if self.state == "IDLE":
                if self.pending_requests:
                    self.target_robot = self._select_by_priority()
                    if self.target_robot:
                        print(f"[HUMAN] 🚶 Walking to {self.target_robot['robot_id']} (bounty: {self.target_robot['bounty']} USDC)")
                        self.state = "WALKING"
                        self.action_counter = 0
            
            elif self.state == "WALKING":
                self.action_counter += 1
                if self.action_counter > 150:
                    print(f"[HUMAN] Arrived at {self.target_robot['robot_id']}")
                    self._notify_arrived()
                    self.action_counter = 0
                    self.state = "PICKING"
            
            elif self.state == "PICKING":
                self.action_counter += 1
                if self.action_counter == 1:
                    print(f"[HUMAN] 📦 Picking {self.target_robot.get('item', 'item')} from shelf...")
                if self.action_counter > 100:
                    self.action_counter = 0
                    self.state = "PLACING"
            
            elif self.state == "PLACING":
                self.action_counter += 1
                if self.action_counter == 1:
                    print(f"[HUMAN] Placing item in robot's box...")
                if self.action_counter > 80:
                    print(f"[HUMAN] ✓ Item placed! Waiting for payment...")
                    self.target_robot = None
                    self.action_counter = 0
                    self.state = "IDLE"
    
    def _receive_messages(self):
        while self.receiver and self.receiver.getQueueLength() > 0:
            try:
                data = self.receiver.getString()
                self.receiver.nextPacket()
                msg = json.loads(data)
                
                if msg.get("type") == "HELP_REQUEST":
                    request = {
                        "robot_id": msg.get("robot_id"),
                        "bounty": msg.get("bounty", 0.5),
                        "position": msg.get("position", [0, 0, 0]),
                        "item": msg.get("item_shape", "irregular")
                    }
                    self.pending_requests.append(request)
                    print(f"[HUMAN] 📨 Help request received from {request['robot_id']}")
            except:
                pass
    
    def _select_by_priority(self):
        if not self.pending_requests:
            return None
        
        # Get my position
        my_pos = self.gps.getValues() if self.gps else [0, 0, 3]
        
        # Calculate distances
        for req in self.pending_requests:
            rpos = req.get("position", [0, 0, 0])
            req["distance"] = math.sqrt((my_pos[0]-rpos[0])**2 + (my_pos[2]-rpos[2])**2)
        
        # Sort by distance
        self.pending_requests.sort(key=lambda x: x["distance"])
        
        # Get closest
        min_dist = self.pending_requests[0]["distance"]
        closest = [r for r in self.pending_requests if abs(r["distance"] - min_dist) < 0.5]
        
        if len(closest) == 1:
            selected = closest[0]
        else:
            # Same distance: highest bounty
            closest.sort(key=lambda x: x.get("bounty", 0), reverse=True)
            max_bounty = closest[0].get("bounty", 0)
            highest = [r for r in closest if r.get("bounty", 0) == max_bounty]
            selected = random.choice(highest) if len(highest) > 1 else highest[0]
        
        # Remove from pending
        self.pending_requests = [r for r in self.pending_requests if r["robot_id"] != selected["robot_id"]]
        return selected
    
    def _notify_arrived(self):
        if self.emitter and self.target_robot:
            msg = {
                "type": "HUMAN_ARRIVED",
                "robot_id": self.target_robot["robot_id"]
            }
            self.emitter.send(json.dumps(msg).encode('utf-8'))

if __name__ == "__main__":
    HumanController().run()
