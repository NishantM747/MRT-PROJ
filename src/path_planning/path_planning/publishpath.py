import rclpy 
import sys
from rclpy.node import Node
from path_planning.path import pathplanning
from messages.msg import Roverpath
from messages.msg import Map
from messages.msg import Coord
from messages.msg import TaskInfoPath

class publishpath(Node):
    def __init__(self):
        self.map = {}
        super().__init__("publish_path_node")
        # Edit topic name later
        self.task_subscription_ = self.create_subscription(TaskInfoPath, "task_info_path", self.task_callback, 10)
        self.map_subscription_ = self.create_subscription(Map, "send_map", self.map_callback, 10)
        self.path_publisher_ = self.create_publisher(Roverpath, 'path_info', 10)


        self.start = None
        self.end = None
        self.id = None

    def task_callback(self, msg):

        self.current = (msg.bot_x, msg.bot_y) 
        self.pick = (msg.pick_x, msg.pick_y) 
        self.place = (msg.place_x, msg.place_y) 
        self.id = msg.bot_id

        self.taskid = msg.task_id
        self.publish_path()  # Directly call publish_path after receiving new coordinates

    def map_callback(self, msg):
        new_point = {(msg.x, msg.y): msg.status}
        self.map.update(new_point)
    
    def publish_path(self):
        msg = Roverpath()
        self.pathplanner = pathplanning(self.map)
        path1 = self.pathplanner.nav(self.current, self.pick)
        path2 = self.pathplanner.nav(self.pick, self.place)
        path = path1 + path2[1:]  # Combine paths, avoiding duplicate pick point
        self.get_logger().info(f"Publishing path for rover {self.id}: {path}")
        msg.roverid = self.id
        msg.task_id = self.taskid
        msg.path = [Coord(x=coord[0], y=coord[1]) for coord in path]  # Convert tuples to Coord objects
        self.path_publisher_.publish(msg)

def main():
    rclpy.init(args=None)
    node = publishpath()  
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


