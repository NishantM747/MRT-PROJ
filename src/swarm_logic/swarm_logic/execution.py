import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from messages.msg import BranchMsg
from messages.msg import InfoMsg
from messages.srv import MoveMembers
from messages.msg import PathMsg
from messages.srv import LeaderMove
import numpy as np
import threading
import time
from .bot import Bot, get_bot_node
from .branch import branch, get_branch_node
import random
from .task_allocation import Task,TaskAllocator,TaskInfo
class task_sim(Node):
    """ROS node to simulate and publish task requests"""
    
    def __init__(self, map_width=60, map_height=60, task_interval=5.0):
        super().__init__('task_sim_node')
        
        self.map_width = map_width
        self.map_height = map_height
        self.task_interval = task_interval
        self.task_id_counter = 1
        self.register_branches=register_branches()
        # Publisher for new tasks
        self.task_pub = self.create_publisher(TaskInfo, 'new_tasks', 10)
        
        # Timer to generate tasks periodically
        self.task_timer = self.create_timer(self.task_interval, self.generate_task)
        
        self.get_logger().info(f"Task simulator initialized. Publishing tasks every {task_interval} seconds")
        self.get_logger().info(f"Map bounds: width={map_width}, height={map_height}")
    
    def generate_task(self):
        """Generate a random task and publish it"""
        # Generate random coordinates within map bounds
        x = random.uniform(0, self.map_width)
        y = random.uniform(0, self.map_height)
        
        task_id = random.choice([1,2,3,4])   #4 predefined tasks
        
        # Create and publish task
        msg = TaskInfo()
        msg.id = task_id
        msg.x = float(x)
        msg.y = float(y)
        
        self.task_pub.publish(msg)
        
        self.get_logger().info(f"Published Task {task_id} at location ({x:.2f}, {y:.2f})")
    
    def publish_specific_task(self, id,x, y):
        """Manually publish a task at specific coordinates"""
        task_id = id
        
        msg = TaskInfo()
        msg.id = task_id
        msg.x = float(x)
        msg.y = float(y)
        
        self.task_pub.publish(msg)
        
        self.get_logger().info(f"Manually published Task {task_id} at location ({x:.2f}, {y:.2f})")
        
        return task_id
    
    def stop_task_generation(self):
        """Stop automatic task generation"""
        self.task_timer.cancel()
        self.get_logger().info("Task generation stopped")
    
    def start_task_generation(self):
        """Start automatic task generation"""
        self.task_timer = self.create_timer(self.task_interval, self.generate_task)
        self.get_logger().info("Task generation started")

    
class Map:
    """
    2D map represented by a numpy array.
    Values:
      1 -> traversable
      2 -> split required (2-way)
      3 -> split required (3-way)
    Coordinates are passed as (x, y) with 0 <= x < width and 0 <= y < height.
    """
    def __init__(self, width=60, height=60, prob_2=0.03, prob_3=0.01, seed=None):
        self.width = int(width)
        self.height = int(height)
        rng = np.random.default_rng(seed)
        # start all ones
        grid = np.ones((self.height, self.width), dtype=np.uint8)
        # random mask for 2s and 3s (ensure more 1s than others)
        r = rng.random((self.height, self.width))
        grid[r < prob_2] = 2
        grid[(r >= prob_2) & (r < prob_2 + prob_3)] = 3
        self.grid = grid

    def in_bounds(self, x, y):
        ix = int(x)
        iy = int(y)
        return 0 <= ix < self.width and 0 <= iy < self.height

    def get_value(self, x, y):
        """
        Return the value at coordinate (x, y).
        Raises IndexError if out of bounds.
        """
        if not self.in_bounds(x, y):
            raise IndexError(f"Coordinate out of bounds: ({x},{y})")
        # numpy array is indexed [row, col] => [y, x]
        return int(self.grid[int(y), int(x)])

    def set_value(self, x, y, val):
        """
        Set the value at (x, y) to 1, 2 or 3. Raises IndexError if out of bounds.
        """
        if val not in (1, 2, 3):
            raise ValueError("val must be 1, 2 or 3")
        if not self.in_bounds(x, y):
            raise IndexError(f"Coordinate out of bounds: ({x},{y})")
        self.grid[int(y), int(x)] = int(val)

    def sample_summary(self):
        """Return counts of each cell type for debugging."""
        unique, counts = np.unique(self.grid, return_counts=True)
        return dict(zip([int(u) for u in unique], [int(c) for c in counts]))


dict_active_branch = {}   # to keep track of which branch is active for movement


class leader_proxy:
    """Proxy class to hold leader information without inheriting from Bot"""
    def __init__(self, branch_id, leader_id, coord, splitting):
        self.branch_id = branch_id
        self.leader_id = leader_id
        self.coord = coord
        self.splitting = splitting
    
    def move(self, coord):
        """Move the actual bot through the bot_node"""
        print(f"move request for {self.leader_id}")
        bot_node = get_bot_node()
        bot = bot_node.get_bot(self.leader_id)
        print(bot)
        if bot:
            print(f"calling movement of {bot.id}")
            bot.move(coord)
            self.coord = coord  # Update proxy's coord


# Global flag for initialization
initialisation = False


def initials():
    """Initialize bots and branches"""
    global initialisation
    
    map_obj = Map()
    
    # Create bot objects - they automatically register with bot_node
    bot1 = Bot(id=1, priority=1, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot2 = Bot(id=2, priority=2, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot3 = Bot(id=3, priority=3, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot4 = Bot(id=4, priority=4, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot5 = Bot(id=5, priority=5, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot6 = Bot(id=6, priority=6, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot7 = Bot(id=7, priority=7, coord=(0, 0), color="white", returning=False, map=map_obj)
    bot8 = Bot(id=8, priority=8, coord=(0, 0), color="white", returning=False, map=map_obj)
    
    # Create branch - it automatically registers with branch_node
    branch1 = branch(members=[bot2, bot3, bot4, bot5, bot6,bot7,bot8], leader=bot1, path=[(0, 0)])
    
    initialisation = True
    
    return bot1, bot2, bot3, bot4, bot5, bot6, branch1


class movement(Node):
    def __init__(self, map=None):
        super().__init__('movement_node')
        self.get_logger().info("Movement node initialised.")
        
        self.split_pub = self.create_publisher(InfoMsg, "infoNodeTopic", 10)
        self.branch_sub = self.create_subscription(BranchMsg, "branch_topic", self.branch_callback, 10)
        
        self.get_logger().info(f"Subscribed to BranchMsg on topic: branch_topic")
        self.get_logger().info(f"Publishing InfoMsg on topic: infoNodeTopic")

        self.map = map if map else Map()
        
        # Initialize bots and branches
        self.get_initial()
        
    def get_initial(self):
        global initialisation
        if not initialisation:
            self.bots_and_branches = initials()
            self.get_logger().info("Bots and Branches initialised.")
            
            # Verify bots are in the bot_node's dictionary
            bot_node = get_bot_node()
            self.get_logger().info(f"Total bots registered: {len(bot_node.bots)}")
            for bot_id in bot_node.bots:
                self.get_logger().info(f"Bot {bot_id} is registered")
            
            # Verify branches are in the branch_node's dictionary
            branch_node_instance = get_branch_node()
            self.get_logger().info(f"Total branches registered: {len(branch_node_instance.dict_branches)}")
            for branch_id in branch_node_instance.dict_branches:
                self.get_logger().info(f"Branch {branch_id} is registered")
    
    def branch_callback(self, msg):
        branch_id = msg.id
        leader_id = msg.leader_id
        splitting = msg.splitting
        init_coord = tuple(msg.init_coord)
        
        self.get_logger().info(f"====== BRANCH_CALLBACK TRIGGERED ======")
        self.get_logger().info(f"Received branch info for Branch {msg.id}")
        self.get_logger().info(f"Leader ID: {leader_id}, Init Coord: {init_coord}, Splitting: {splitting}")
        
        dict_active_branch[branch_id] = True
        
        leader = leader_proxy(branch_id, leader_id, init_coord, splitting)
        
        # Run movement loop in a separate thread to not block the executor
        movement_thread = threading.Thread(target=self.movement_loop, args=(leader,), daemon=True)
        movement_thread.start()
        self.get_logger().info(f"Started movement thread for Branch {branch_id}")
        self.get_logger().info(f"====== BRANCH_CALLBACK COMPLETE ======")

    def move_leader(self, leader, branch_id, leader_id, coord):
        """Move leader using the bot object from bot_node"""
        self.get_logger().info(f"move called for leader {leader_id}")
        leader.move(tuple(coord))
    
    def movement_logic(self, leader, branch_id, leader_id, coord):
        """Movement logic based on map status"""
        self.get_logger().info(f"Movement logic for Leader {leader_id} at {coord}")
        
        try:
            status = self.map.get_value(coord[0], coord[1])
            self.get_logger().info(f"Map status at {coord}: {status}")
        except IndexError as e:
            self.get_logger().error(f"Coordinate {coord} out of bounds: {e}")
            dict_active_branch[branch_id] = False
            return
        
        if status == 1:
            # Move
            new_coord = (coord[0] + 1, coord[1] + 1)
            self.get_logger().info(f"Leader {leader_id} moving from {coord} to {new_coord}")
            self.move_leader(leader, branch_id, leader_id, new_coord)
            # Update leader proxy's coordinate after moving
            leader.coord = new_coord
            
        elif status == 2:
            # Split into 2 branches
            self.get_logger().info(f"Leader {leader_id} at {coord} requires 2-way split.")
            paths = [(coord[0] + 1, coord[1]), (coord[0], coord[1] + 1)]
            print(paths)
            
            self.send_split(paths, branch_id)
            dict_active_branch[branch_id] = False
            self.get_logger().info(f"Branch {branch_id} set to inactive after split request")
            
        elif status == 3:
            # Split into 3 branches
            self.get_logger().info(f"Leader {leader_id} at {coord} requires 3-way split.")
            paths = [(coord[0] + 1, coord[1]), (coord[0], coord[1] + 1), (coord[0] + 1, coord[1] + 1)]
            self.send_split(paths, branch_id)
            dict_active_branch[branch_id] = False
            self.get_logger().info(f"Branch {branch_id} set to inactive after split request")
    
    def movement_loop(self, leader):
        self.get_logger().info(f"Starting movement loop for Branch {leader.branch_id} from coordinate {leader.coord}.")
        
        loop_count = 0
        max_loops = 100  # Prevent infinite loops for debugging
        
        while dict_active_branch.get(leader.branch_id, False) and loop_count < max_loops:
            self.get_logger().info(f"Movement loop iteration {loop_count} for Branch {leader.branch_id}")
            self.movement_logic(leader, leader.branch_id, leader.leader_id, leader.coord)
            loop_count += 1
            time.sleep(0.5)  # Add delay to allow other callbacks to process
        
        if loop_count >= max_loops:
            self.get_logger().warn(f"Branch {leader.branch_id} reached max loop iterations")
        else:
            time.sleep(1.0)
            self.get_logger().info(f"Branch {leader.branch_id} movement loop ended after {loop_count} iterations")
    
    def send_split(self, coord, branch_id):
        msg = InfoMsg()
        # msg.surrounding = coord  # Use msg, not InfoMsg
        if len(coord) == 2:
            msg.c1 = coord[0]
            msg.c2 = coord[1]
        elif len(coord) == 3:
            msg.c1 = coord[0]
            msg.c2 = coord[1]
            msg.c3 = coord[2]
        msg.branch_id = branch_id  # Use msg, not InfoMsg
        msg.data = "split"  # Use msg, not InfoMsg
        
        self.get_logger().info(f"PUBLISHING split request for Branch {branch_id} with paths {coord}")
        self.get_logger().info(f"Publisher topic: {self.split_pub.topic_name}")
        self.get_logger().info(f"Number of subscribers: {self.split_pub.get_subscription_count()}")
        
        self.split_pub.publish(msg)
        
        # Give time for message to be received
        time.sleep(0.1)
        
        self.get_logger().info(f"Split message published for Branch {branch_id}")


def main(args=None):
    # Initialize ROS2
    rclpy.init(args=args)
    
    # Create both universal nodes first
    bot_node = get_bot_node()
    branch_node_instance = get_branch_node()
    
    # Create the movement node
    movement_node = movement()
    
    # Create the task simulator node
    task_sim_node = task_sim(map_width=60, map_height=60, task_interval=5.0)
    
    # Create a MultiThreadedExecutor to spin all four nodes
    executor = MultiThreadedExecutor()
    executor.add_node(bot_node)
    executor.add_node(branch_node_instance)
    executor.add_node(movement_node)
    executor.add_node(task_sim_node)
    
    try:
        # Spin all nodes together
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        executor.shutdown()
        bot_node.destroy_node()
        branch_node_instance.destroy_node()
        movement_node.destroy_node()
        task_sim_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()