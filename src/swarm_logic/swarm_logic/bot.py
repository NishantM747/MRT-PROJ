#here we will make the basic class of the bots from which their attributes will me controlled

import rclpy 
import sys
from rclpy.node import Node
from std_msgs.msg import Int16
from mapping.mapping_shi import GeneratedMap
from messages.srv import Mapinfo
from messages.msg import Map
from messages.msg import PathMsg
from messages.srv import MoveMembers
class bot(Node):
    def __init__(self,id,priority,coord=(0,0),color="white",returning=False):
        super().__init__("bot_node")
        self.id=id
        self.coord=coord
        self.color=color
        self.priority=priority
        self.returning=returning
        self.path=[]
        self.follow_leader=None    #initially following none
        self.LOS=3  #line of sight
        self.get_map = self.create_client(Mapinfo, 'map_info')
        self.map = GeneratedMap()
        self.send_map = self.create_publisher(Map,'send_map',10)
        self.send_coord_to_branch=self.create_publisher(PathMsg,'path_topic',10)    #cooord has x,y and branch id
    def get_map_info(self,x,y):
        while not self.get_map.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        request = Mapinfo.Request()
        request.x = x
        request.y = y
        future = self.get_map.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result().status 
    def sendmap(self,x,y,status):
        msg = Map()
        msg.x = x 
        msg.y = y
        msg.status = status
        self.send_map.publish(msg)
    def see(self):
        for x in range(1,self.LOS+1):
            v = get_map_info(self,self.coord[0]+x,self.coord[1])
            self.map.setValue(self.coord[0]+x,self.coord[1],v)
            self.sendmap(x,self.coord[1],v)
            if v == 1:
                break
        for x in range(1,self.LOS+1):
            v = get_map_info(self,self.coord[0]-x,self.coord[1])
            self.map.setValue(self.coord[0]-x,self.coord[1],v)
            self.sendmap(x,self.coord[1],v)
            if v == 1:
                break
        for y in range(1,self.LOS+1):
            v = get_map_info(self,self.coord[0],self.coord[1]+y)
            self.map.setValue(self.coord[0],self.coord[1]+y,v)
            self.sendmap(self.coord[0],y,v)
            if v == 1:
                break
        for y in range(1,self.LOS+1):
            v = get_map_info(self,self.coord[0],self.coord[1]-y)
            self.map.setValue(self.coord[0],self.coord[1]-y,v)
            self.sendmap(self.coord[0],y,v)
            if v == 1:
                break
    def move(self, coord: tuple):
        # Check adjacent move
        valid = [
            (self.coord[0] + 1, self.coord[1]),
            (self.coord[0] - 1, self.coord[1]),
            (self.coord[0], self.coord[1] + 1),
            (self.coord[0], self.coord[1] - 1),
        ]
        if coord not in valid:
            return  # invalid move, ignore

        # Move THIS bot
        self.coord = coord  

        # If not leader → done
        if not self.is_leader:
            return  

        # ----- LEADER logic -----
        # Leader must notify branch to move members
        
        client = self.create_client(MoveMembers, 'move_members')

        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for move_members service...')

        req = MoveMembers.Request()
        req.branch_id = self.branch_id
        req.x, req.y = coord

        future = client.call_async(req)

        # WAIT UNTIL MEMBERS FINISH MOVING
        rclpy.spin_until_future_complete(self, future)

        # Optionally check result
        if future.result().success:
            self.get_logger().info(f"Branch {self.branch_id} followers moved to {coord}")

        
    def follow_path(self,path):
        for i in range(len(path)):
            self.move(path[i])
            self.see
    def leader(self):
        self.color="blue"
        self.update_map()
    def follower(self):
        self.color="green"
        self.update_map()
    def explorer(self):
        self.color="yellow"
        self.update_map()
    def is_returning(self):
        self.returning=True
        self.color="red"
        self.update_map()
    def follow(self,leader):
        self.follow_leader=leader
    def is_leader(self):
        return self.color=="blue"
    def update_map(self): #called everytime a bot object is made or colour updated so that map can be updated
        #publish the id and colour of bot 
        pass


def main(args=None):
    rclpy.init(args=args)

    node=bot()
    rclpy.spin(node)   
    rclpy.shutdown()