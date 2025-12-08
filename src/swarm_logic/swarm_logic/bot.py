import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16
from messages.msg import PathMsg
from messages.srv import MoveMembers
from messages.srv import LeaderMove

# Global universal node instance
_bot_node_instance = None


def get_bot_node():
    """Get or create the universal BotNode instance"""
    global _bot_node_instance
    if _bot_node_instance is None:
        if not rclpy.ok():
            raise RuntimeError("rclpy not initialized. Call rclpy.init() first.")
        _bot_node_instance = BotNode()
    return _bot_node_instance


class Bot:
    """Pure Python class for Bot - handles attributes and logic only"""
    
    def __init__(self, id, priority, coord=(0, 0), color="white", returning=False, map=None):
        self.id = id
        self.coord = coord
        self.color = color
        self.priority = priority
        self.returning = returning
        self.path = []
        self.follow_leader = None  # initially following none
        self.LOS = 3  # line of sight
        self.map = map
        self.branch_id = None  # Will be set externally if this bot is a leader
        
        # Automatically register this bot with the universal node
        node = get_bot_node()
        node.add_bot(self)

    def update_coord(self, coord: tuple):
        """Update bot's coordinate - pure Python logic"""
        self.coord = coord

    def is_valid_move(self, coord: tuple) -> bool:
        """Check if the move is valid (adjacent cell)"""
        valid = [
            (self.coord[0] + 1, self.coord[1]),
            (self.coord[0] - 1, self.coord[1]),
            (self.coord[0], self.coord[1] + 1),
            (self.coord[0], self.coord[1] - 1),
        ]
        return coord in valid

    def move(self, coord: tuple):
        """Move method that delegates to the node"""
        node = get_bot_node()
        node.move_bot(self, coord)

    def set_leader(self):
        """Set this bot as a leader"""
        self.color = "blue"

    def set_follower(self):
        """Set this bot as a follower"""
        self.color = "green"

    def set_explorer(self):
        """Set this bot as an explorer"""
        self.color = "yellow"

    def set_is_returning(self):
        """Mark bot as returning"""
        self.returning = True
        self.color = "red"

    def follow(self, leader):
        """Set which leader this bot is following"""
        self.follow_leader = leader

    def is_leader(self) -> bool:
        """Check if this bot is a leader"""
        return self.color == "blue"

    def get_info(self) -> dict:
        """Get bot information as dictionary"""
        return {
            'id': self.id,
            'coord': self.coord,
            'color': self.color,
            'priority': self.priority,
            'returning': self.returning,
            'is_leader': self.is_leader()
        }


class BotNode(Node):
    """ROS2 Node class - handles all ROS2 operations for all bots"""
    
    def __init__(self):
        super().__init__('bot_node_ros')
        
        # Dictionary to store all bot objects with their ID as key
        self.bots = {}
        
        # ROS2 Services
        self.create_service(LeaderMove, 'leader_info', self.move_callback)
        
        # ROS2 Clients (shared across all bots)
        self.move_member_client = self.create_client(MoveMembers, 'move_members')
        
        # ROS2 Publishers (shared across all bots)
        self.send_coord_to_branch = self.create_publisher(PathMsg, 'path_topic', 10)
        
        self.get_logger().info("BotNode initialized")

    def add_bot(self, bot):
        """Add a bot object to the dictionary"""
        self.bots[bot.id] = bot
        self.get_logger().info(f"Bot {bot.id} added to node. Total bots: {len(self.bots)}")

    def remove_bot(self, bot_id: int):
        """Remove a bot from the dictionary"""
        if bot_id in self.bots:
            del self.bots[bot_id]
            self.get_logger().info(f"Bot {bot_id} removed from node")

    def get_bot(self, bot_id: int):
        """Get a bot object by ID"""
        self.get_logger().info("giving info about a bot")
        return self.bots.get(bot_id, None)

    def move_callback(self, request, response):
        """Service callback for leader movement"""
        self.get_logger().info(f"Received move request for Bot {request.id} to {request.coord}")
        
        coord = tuple(request.coord)
        bot_id = request.id
        
        # Get the bot object from dictionary
        bot_obj = self.bots.get(bot_id)
        
        if bot_obj is None:
            self.get_logger().error(f"Bot {bot_id} not found in bots dictionary")
            response.success = False
            return response
        
        # Call the move method
        self.move_bot(bot_obj, (coord[0], coord[1]))
        response.success = True
        
        return response

    def move_bot(self, bot, coord: tuple):
        """Move a bot to a new coordinate (handles ROS2 operations)"""
        # Check if move is valid using bot's logic
        # if not bot.is_valid_move(coord):
        #     self.get_logger().warn(f"Invalid move for Bot {bot.id} to {coord}")
        #     return  # invalid move, ignore

        # Update bot's coordinate (pure Python operation)
        bot.update_coord(coord)

        # If not leader → done
        if not bot.is_leader():
            self.get_logger().info(f"Bot {bot.id} moved to {coord} as follower.")
            self.publish_update_map(bot)
            return
        else:
            self.get_logger().info(f"Bot {bot.id} moved to {coord} as leader.")

        # ----- LEADER logic (ROS2 operations) -----
        # Leader must notify branch to move members
        if bot.branch_id is None:
            self.get_logger().warn(f"Leader Bot {bot.id} has no branch_id set")
            self.publish_update_map(bot)
            return

        while not self.move_member_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for move_members service...')

        req = MoveMembers.Request()
        req.branch_id = bot.branch_id
        req.x, req.y = coord

        future = self.move_member_client.call_async(req)

        # WAIT UNTIL MEMBERS FINISH MOVING
        rclpy.spin_until_future_complete(self, future)

        # Check result
        if future.result() and future.result().success:
            self.get_logger().info(f"Branch {bot.branch_id} followers moved to {coord}")
        
        self.publish_update_map(bot)

    def follow_path(self, bot_id: int, path: list):
        """Make a bot follow a path"""
        bot = self.get_bot(bot_id)
        if bot is None:
            self.get_logger().error(f"Bot {bot_id} not found")
            return
        
        for coord in path:
            self.move_bot(bot, coord)

    def set_bot_as_leader(self, bot_id: int):
        """Set a bot as leader and publish update"""
        bot = self.get_bot(bot_id)
        if bot:
            bot.set_leader()
            self.publish_update_map(bot)
            self.get_logger().info(f"Bot {bot_id} set as leader")

    def set_bot_as_follower(self, bot_id: int):
        """Set a bot as follower and publish update"""
        bot = self.get_bot(bot_id)
        if bot:
            bot.set_follower()
            self.publish_update_map(bot)
            self.get_logger().info(f"Bot {bot_id} set as follower")

    def set_bot_as_explorer(self, bot_id: int):
        """Set a bot as explorer and publish update"""
        bot = self.get_bot(bot_id)
        if bot:
            bot.set_explorer()
            self.publish_update_map(bot)
            self.get_logger().info(f"Bot {bot_id} set as explorer")

    def set_bot_returning(self, bot_id: int):
        """Mark bot as returning and publish update"""
        bot = self.get_bot(bot_id)
        if bot:
            bot.set_returning()
            self.publish_update_map(bot)
            self.get_logger().info(f"Bot {bot_id} set as returning")

    def publish_update_map(self, bot):
        """Publish map update when bot status changes"""
        # Implement publishing logic here
        msg = PathMsg()
        # Fill in the message fields based on your PathMsg definition
        # msg.bot_id = bot.id
        # msg.color = bot.color
        # self.send_coord_to_branch.publish(msg)
        pass

    def publish_path_to_branch(self, bot_id: int, path: list):
        """Publish path coordinates to branch"""
        bot = self.get_bot(bot_id)
        if bot is None:
            return
        
        msg = PathMsg()
        # Fill in the message based on your PathMsg definition
        self.send_coord_to_branch.publish(msg)


# Standalone main for testing bot_node separately (optional)
def main(args=None):
    rclpy.init(args=args)
    bot_node = get_bot_node()
    rclpy.spin(bot_node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()