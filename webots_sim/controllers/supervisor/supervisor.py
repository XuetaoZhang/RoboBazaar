"""
RoboBazaar Supervisor - Message Router & Statistics
Webots Version: 2023a
"""
from controller import Supervisor
import json

class ScenarioSupervisor(Supervisor):
    def __init__(self):
        super().__init__()
        self.timestep = int(self.getBasicTimeStep())
        
        # Communication
        self.emitter = self.getDevice("emitter")  # Channel 2 (to robots/human)
        self.receiver = self.getDevice("receiver")  # Channel 1 (from robots)
        if self.receiver:
            self.receiver.enable(self.timestep)
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "auto_completed": 0,
            "human_assisted": 0,
            "total_paid": 0.0,
            "payments": []
        }
        
        # Active help requests
        self.help_requests = []
        
        print("[SUPERVISOR] Message router initialized")
        print("[SUPERVISOR] Listening on channel 1, broadcasting on channel 2")
    
    def run(self):
        step_count = 0
        while self.step(self.timestep) != -1:
            step_count += 1
            
            # Process incoming messages
            self._process_messages()
            
            # Print status every 10 seconds
            if step_count % 600 == 0:
                self._print_stats()
    
    def _process_messages(self):
        while self.receiver and self.receiver.getQueueLength() > 0:
            try:
                data = self.receiver.getString()
                self.receiver.nextPacket()
                msg = json.loads(data)
                
                msg_type = msg.get("type")
                robot_id = msg.get("robot_id", "unknown")
                
                if msg_type == "STATUS":
                    status = msg.get("status")
                    if status == "COMPLETE":
                        self.stats["total_tasks"] += 1
                    elif status == "AUTO_GRASP":
                        self.stats["auto_completed"] += 1
                
                elif msg_type == "HELP_REQUEST":
                    bounty = msg.get("bounty", 0)
                    position = msg.get("position", [0, 0, 0])
                    item = msg.get("item_shape", "unknown")
                    
                    self.help_requests.append({
                        "robot_id": robot_id,
                        "bounty": bounty,
                        "position": position,
                        "item": item
                    })
                    self.stats["human_assisted"] += 1
                    
                    print(f"[SUPERVISOR] 📢 {robot_id} requests help: {item}, bounty={bounty} USDC")
                    
                    # Forward to human controller
                    if self.emitter:
                        self.emitter.send(data)
                
                elif msg_type == "PAYMENT":
                    amount = msg.get("amount", 0)
                    self.stats["total_paid"] += amount
                    self.stats["payments"].append({
                        "robot": robot_id,
                        "amount": amount
                    })
                    
                    # Remove from help requests
                    self.help_requests = [r for r in self.help_requests if r["robot_id"] != robot_id]
                    
                    print(f"[SUPERVISOR] 💰 X402 Payment: {robot_id} paid {amount} USDC")
                    
            except Exception as e:
                print(f"[SUPERVISOR] Error: {e}")
    
    def _print_stats(self):
        print("\n" + "="*55)
        print("📊 ROBOBAZAAR STATISTICS")
        print("="*55)
        print(f"  Total Tasks Completed: {self.stats['total_tasks']}")
        print(f"  Auto Processed (80%):  {self.stats['auto_completed']}")
        print(f"  Human Assisted (20%):  {self.stats['human_assisted']}")
        print(f"  Total USDC Paid:       {self.stats['total_paid']:.2f}")
        print(f"  Pending Requests:      {len(self.help_requests)}")
        if self.stats['payments']:
            print("  Recent Payments:")
            for p in self.stats['payments'][-3:]:
                print(f"    - {p['robot']}: {p['amount']} USDC")
        print("="*55 + "\n")

if __name__ == "__main__":
    supervisor = ScenarioSupervisor()
    supervisor.run()
