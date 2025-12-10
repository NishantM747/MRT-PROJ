import rclpy
from rclpy.node import Node
from messages.msg import TaskInfo
from std_msgs.msg import String
import numpy as np
import matplotlib.pyplot as plt
import random

class DashboardNode(Node):
    def __init__(self):
        super().__init__('sim_dashboard')
      
        self.map_size = 100
        # 0 = Empty, 1 = Robot, 2 = Task
        self.grid = np.zeros((self.map_size, self.map_size))
        
        self.robot_positions = {} 
        self.active_tasks = []

        self.task_pub = self.create_publisher(TaskInfo, 'new_orders', 10)
       
        self.create_subscription(String, 'robot_login', self.update_robot_pos, 10)
       
        self.create_timer(5.0, self.generate_random_task)
        
        plt.ion()  # Interactive mode on (allows real-time updates)
        self.fig, self.ax = plt.subplots()
        self.get_logger().info("Dashboard Started. Generating random tasks...")

    def update_robot_pos(self, msg):
        try:
            data = msg.data.split(',')
            bot_id = int(data[0])
            x = float(data[1])
            y = float(data[2])
            self.robot_positions[bot_id] = (x, y)
            self.update_plot()
        except:
            pass

    def generate_random_task(self):
        # 1. Pick random Pickup & Drop locations
        px = random.randint(0, self.map_size - 1)
        py = random.randint(0, self.map_size - 1)
        
        dx = random.randint(0, self.map_size - 1)
        dy = random.randint(0, self.map_size - 1)
        
        task_id = random.randint(100, 999)
        
        # 2. Publish to ROS
        msg = TaskInfo()
        msg.id = task_id
        msg.pickup_x = float(px)
        msg.pickup_y = float(py)
        msg.drop_x = float(dx)
        msg.drop_y = float(dy)
        
        self.task_pub.publish(msg)
        
        # 3. Add to list for visualization
        self.active_tasks.append((px, py))
        self.get_logger().info(f"Generated Random Task {task_id} at ({px}, {py})")
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.set_xlim(0, self.map_size)
        self.ax.set_ylim(0, self.map_size)
        self.ax.set_title("Live Fleet Status")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        # Draw Tasks (Green X)
        if self.active_tasks:
            # Unzip list of tuples into two lists [x1, x2], [y1, y2]
            tx, ty = zip(*self.active_tasks) 
            self.ax.scatter(tx, ty, c='green', marker='x', s=100, label='Tasks')

        # Draw Robots (Red Circles)
        if self.robot_positions:
            rx = [pos[0] for pos in self.robot_positions.values()]
            ry = [pos[1] for pos in self.robot_positions.values()]
            self.ax.scatter(rx, ry, c='red', marker='o', s=120, label='Robots')
           
            for bot_id, (x, y) in self.robot_positions.items():
                self.ax.text(x, y+2, f"B{bot_id}", color='black', fontsize=9, ha='center')

        self.ax.legend(loc='upper right')
        plt.draw()
        plt.pause(0.01)

def main(args=None):
    rclpy.init(args=args)
    node = DashboardNode()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()