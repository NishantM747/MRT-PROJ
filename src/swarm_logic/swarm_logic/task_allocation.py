import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import math
import time
from messages.msg import TaskInfo
from messages.msg import Map
from messages.msg import TaskInfoPath   #this will be used to send the info about the path to the path planning team
from messages.msg import BotMove   # For publishing bot movements during region segregation
from .branch import branch, get_branch_node

from .bot import bot  


class Task:
    def __init__(self, id, x, y, drop_x, drop_y):
        self.id = id
        self.x = x
        self.y = y
        self.drop_x = drop_x
        self.drop_y = drop_y


class RobotProxy:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.task_queue = []
        self.max_capacity = 3

    def is_overloaded(self):
        return (len(self.task_queue) >= self.max_capacity)


class BotProxy:
    
    def __init__(self, id, priority, coord, color="white", returning=False):
        self.id = id
        self.priority = priority
        self.coord = coord
        self.color = color
        self.returning = returning
        self.branch_id = None
        self.follow_leader = None
    
    def set_leader(self):
        self.color = "blue"
    
    def set_follower(self):
        self.color = "green"
    
    def set_returning(self):
        self.returning = True
        self.color = "red"
    
    def move(self, coord: tuple):
        """Move bot to new coordinate. Updates coord attribute."""
        # NOTE: In actual implementation with real bot class, this would call bot.move()
        # which also triggers see() and updates the map. For now, just update coord.
        self.coord = coord



class TaskAllocator(Node):
    def __init__(self, map_width=60, map_height=60, region_size=20):
        super().__init__('task_allocation_node')
        self.map_width = map_width
        self.map_height = map_height
        self.region_size = region_size
        self.cols = math.ceil(map_width / region_size)

        self.region_leaders = {}
        self.all_leaders = []
        self.task_publishers = {}
        
        # Bot and item tracking (combined from items_and_bot_alloc)
        self.bot_dict = {}       # bot_id -> (x, y) initial coords
        self.items = {}          # item_id -> (drop_x, drop_y)
        self.bot_objects = {}    # bot_id -> BotProxy object
        self.active_branches = {}  # branch_id -> branch object
        
        # Map data for location validation (combined from MapProxy)
        self.map_dict = {}       # (x, y) -> status (0 = free, else blocked)
        
        # Subscriptions
        self.create_subscription(TaskInfo, 'new_tasks', self.task_callback, 10)
        self.create_subscription(Map, 'shelf_info', self.shelf_callback, 10)
        self.create_subscription(Map, 'bot_info', self.bot_callback, 10)
        self.create_subscription(Map, 'send_map', self.map_callback, 10)
        self.task_pub_to_path=self.create_publisher(TaskInfoPath, 'task_info_path', 10)
        
        # Publisher for bot movement during region segregation
        self.bot_move_pub = self.create_publisher(BotMove, 'bot_move', 10)
        
        self.get_logger().info("Task allocator initialised. Waiting for bot registration...")

   
    
    def shelf_callback(self, msg: Map):
        """Handle shelf info - creates item with drop-off location."""
        x = msg.x
        y = msg.y
        item_id = msg.status
        if item_id not in self.items:
            self.items[item_id] = (x, y)
            self.get_logger().info(f"Item {item_id} registered | Drop-off: ({x}, {y})")

    
    
    def bot_callback(self, msg: Map):
        """Handle bot registration. When (0,0,0) received, all bots are registered."""
        x = msg.x
        y = msg.y
        bot_id = msg.status  # Using status field for bot_id based on original code
        
        if msg.x == 0 and msg.y == 0 and msg.status == 0:
            # All bots have been sent - trigger branch creation
            self.get_logger().info("All bots have been registered!")
            self.get_logger().info(f"Total bots: {len(self.bot_dict)}")
            self.create_branches_from_bots()
        else:
            self.bot_dict[bot_id] = (x, y)
            self.get_logger().info(f"Bot {bot_id} registered at ({x}, {y})")

   
    
    def map_callback(self, msg: Map):
        """Handle map data - updates location validity."""
        x = msg.x
        y = msg.y
        status = msg.status
        self.map_dict[(x, y)] = status
        self.get_logger().debug(f"Map update: ({x}, {y}) = {status}")

    def is_location_free(self, x: int, y: int) -> bool:
        """Check if a location is free (status 0 = free)."""
        key = (int(x), int(y))
        if key in self.map_dict:
            return self.map_dict[key] == 0
        # If not in map, assume free (unexplored)
        return True

    def find_free_location_near(self, target_x: int, target_y: int) -> tuple:
        """Find a free location near the target. Returns target if free, else searches nearby."""
        if self.is_location_free(target_x, target_y):
            return (target_x, target_y)
        
        # Search in expanding squares around target
        for radius in range(1, 10):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = target_x + dx, target_y + dy
                    if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                        if self.is_location_free(nx, ny):
                            return (nx, ny)
        
        # Fallback to target even if blocked
        return (target_x, target_y)

    def _publish_bot_move(self, bot_id: int, init_pos: tuple, final_pos: tuple):
        """Publish bot movement message for visualization."""
        msg = BotMove()
        msg.bot_id = bot_id
        msg.init_x = int(init_pos[0])
        msg.init_y = int(init_pos[1])
        msg.final_x = int(final_pos[0])
        msg.final_y = int(final_pos[1])
        self.bot_move_pub.publish(msg)
        self.get_logger().info(f"Published movement for Bot {bot_id}: ({init_pos}) -> ({final_pos})")

    
    def create_branches_from_bots(self):
        """
        Create branches from registered bots.
        - Number of branches = half the number of bots
        - Each branch has 1 leader + remaining members divided equally
        - Bots are moved to their assigned regions
        """
        num_bots = len(self.bot_dict)
        if num_bots < 2:
            self.get_logger().warn("Not enough bots to create branches (need at least 2)")
            return
        
        num_branches = num_bots // 2
        self.get_logger().info(f"Creating {num_branches} branches from {num_bots} bots")
        
        # Create BotProxy objects for all bots
        bot_ids = sorted(self.bot_dict.keys())
        priority = 1
        for bot_id in bot_ids:
            coord = self.bot_dict[bot_id]
            self.bot_objects[bot_id] = BotProxy(
                id=bot_id,
                priority=priority,
                coord=coord
            )
            priority += 1
        
        # Calculate region centers based on number of branches
        region_centers = self._calculate_region_centers(num_branches)
        
        # Divide bots into branches
        bots_per_branch = num_bots // num_branches
        remaining_bots = num_bots % num_branches
        
        bot_list = [self.bot_objects[bid] for bid in bot_ids]
        bot_index = 0
        
        for branch_idx in range(num_branches):
            # Determine number of bots for this branch
            branch_size = bots_per_branch
            if branch_idx < remaining_bots:
                branch_size += 1
            
            # First bot becomes leader, rest are members
            leader = bot_list[bot_index]
            members = bot_list[bot_index + 1 : bot_index + branch_size]
            bot_index += branch_size
            
            # Get region center for this branch
            region_center = region_centers[branch_idx]
            
            # Find free location near region center for leader
            leader_coord = self.find_free_location_near(region_center[0], region_center[1])
            
            # Store initial position and move leader to region center
            leader_init = self.bot_dict[leader.id]
            leader.coord = leader_coord
            self.get_logger().info(f"Branch {branch_idx + 1}: Leader Bot {leader.id} moved to {leader_coord}")
            
            # Publish leader movement
            self._publish_bot_move(leader.id, leader_init, leader_coord)
            
            # Move members near leader (not too close)
            for i, member in enumerate(members):
                # Offset members - spread them out in the region (not close to leader)
                offset_x = ((i % 3) - 1) * 3  # -3, 0, 3
                offset_y = ((i // 3) - 1) * 3
                member_target = (leader_coord[0] + offset_x, leader_coord[1] + offset_y)
                member_coord = self.find_free_location_near(member_target[0], member_target[1])
                member_init = self.bot_dict[member.id]
                member.coord = member_coord
                self.get_logger().info(f"  Member Bot {member.id} moved to {member_coord}")
                
                # Publish member movement
                self._publish_bot_move(member.id, member_init, member_coord)
            
            # Create the branch using the branch class from branch.py
            try:
                new_branch = branch(
                    members=members,
                    leader=leader,
                    path=[leader_coord]
                )
                self.active_branches[new_branch.id] = new_branch
                self.get_logger().info(f"Branch {new_branch.id} created successfully")
            except Exception as e:
                self.get_logger().error(f"Failed to create branch: {e}")
                # Fallback: store branch info without using branch class
                self.active_branches[branch_idx + 1] = type('SimpleBranch', (), {
                    'id': branch_idx + 1,
                    'leader': leader,
                    'members': members,
                    'path': [leader_coord]
                })()
        
        self.get_logger().info(f"Created {len(self.active_branches)} branches")
        
        # Wait for bot movements to complete on the map
        self.get_logger().info("Waiting for bot movements to complete...")
        time.sleep(3.0)
        self.get_logger().info("Bot movements complete. Ready for task allocation.")
        
        # Register leaders with task allocation
        self.register_leaders_from_exploration(self.active_branches)

    def _calculate_region_centers(self, num_branches: int) -> list:
        """
        Calculate region centers based on number of branches.
        Divides the map into equal regions and returns center of each.
        """
        centers = []
        
        if num_branches == 1:
            centers.append((self.map_width // 2, self.map_height // 2))
        elif num_branches == 2:
            # Divide horizontally into 2 regions
            centers.append((self.map_width // 4, self.map_height // 2))
            centers.append((3 * self.map_width // 4, self.map_height // 2))
        elif num_branches <= 4:
            # Divide into 4 quadrants
            quadrant_centers = [
                (self.map_width // 4, self.map_height // 4),
                (3 * self.map_width // 4, self.map_height // 4),
                (self.map_width // 4, 3 * self.map_height // 4),
                (3 * self.map_width // 4, 3 * self.map_height // 4),
            ]
            centers = quadrant_centers[:num_branches]
        else:
            # Grid-based division for more branches
            cols = math.ceil(math.sqrt(num_branches))
            rows = math.ceil(num_branches / cols)
            cell_width = self.map_width // cols
            cell_height = self.map_height // rows
            
            for i in range(num_branches):
                col = i % cols
                row = i // cols
                cx = col * cell_width + cell_width // 2
                cy = row * cell_height + cell_height // 2
                centers.append((cx, cy))
        
        return centers
    
    def register_leaders_from_exploration(self, active_branches):
        """Register leaders from active branches for task allocation."""
        self.get_logger().info("Registering leaders from branches...")

        for branch_id, branch_obj in active_branches.items():
            leader_bot = branch_obj.leader

            proxy = RobotProxy(leader_bot.id, leader_bot.coord[0], leader_bot.coord[1])
            region_id = self.get_region_id(proxy.x, proxy.y)

            self.region_leaders[region_id] = proxy
            self.all_leaders.append(proxy)

            topic_name = f'/bot_{proxy.id}/assign_task'
            pub = self.create_publisher(TaskInfo, topic_name, 10)
            self.task_publishers[proxy.id] = pub

            self.get_logger().info(f"Leader {proxy.id} assigned to Region {region_id}")
        
        self.get_logger().info(f"Registration complete. {len(self.all_leaders)} leaders ready.")

    
    def get_region_id(self, x, y):
        col = int(x // self.region_size)
        row = int(y // self.region_size)
        return row * self.cols + col

    def assign_best_robot(self, task):
        region_id = self.get_region_id(task.x, task.y)
        local_leader = self.region_leaders.get(region_id)

        target_robot = None

        if local_leader and not local_leader.is_overloaded():
            target_robot = local_leader
            self.get_logger().info(f"Task {task.id}: Assigned locally to bot {target_robot.id}")

        else:
            self.get_logger().info(f"Task {task.id}: Local leader busy/missing. Searching neighbors")
            target_robot = self.find_nearest_available_neighbor(task.x, task.y)

        if target_robot:
            target_robot.task_queue.append(task)
            self.send_command_to_bot(target_robot.id, task)
            return True
        else:
            self.get_logger().warn(f"Task {task.id}: CRITICAL - All bots overloaded.")
            return False

    def find_nearest_available_neighbor(self, tx, ty):
        best_bot = None
        min_dist = float('inf')

        for bot in self.all_leaders:
            if not bot.is_overloaded():
                dist = math.sqrt((bot.x - tx)**2 + (bot.y - ty)**2)
                if dist < min_dist:
                    min_dist = dist
                    best_bot = bot
        return best_bot

    def send_command_to_bot(self, bot_id, task):
        # if bot_id in self.task_publishers:
        #     msg = TaskInfo()
        #     msg.id = task.id
        #     msg.x = float(task.x)
        #     msg.y = float(task.y)
        #     msg.x_drop = float(task.drop_x)
        #     msg.y_drop = float(task.drop_y)
        #     self.task_publishers[bot_id].publish(msg)
        msg=TaskInfoPath()
        msg.bot_id=bot_id
        msg.task_id=task.id
        msg.pick_x=task.x
        msg.pick_y=task.y
        msg.place_x=task.drop_x
        msg.place_y=task.drop_y
        msg.bot_x=self.bot_dict[bot_id][0]
        msg.bot_y=self.bot_dict[bot_id][1]
        self.task_pub_to_path.publish(msg)
    def task_callback(self, msg):
        self.get_logger().info(f"Received task {msg.id} | Current leaders: {len(self.all_leaders)} | Registered bots: {len(self.bot_dict)}")
        new_task = Task(msg.id, msg.x, msg.y, msg.x_drop, msg.y_drop)
        self.assign_best_robot(new_task)




def main(args=None):
    rclpy.init(args=args)
    node = TaskAllocator()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
