import rclpy
from rclpy.node import Node
from messages.msg import Coord 
from messages.msg import RoverPath
from messages.msg import Rovercoord
from messages.srv import rover_list
from messages.msg import RoverAvail
from messages.srv import RoverAvailList
class UpdateNode(Node):
    def __init__(self):
        super().__init__('Update_node')
        self.rover_paths = {}
        self.pointers = {}
        self.subscription = self.create_subscription(
            RoverPath,
            'path_info',
            self.listener_callback,
            10
        )
        self.srv_update = self.create_service(
            rover_list,
            'Update_position',
            self.update_position_callback
        )
        self.srv_avail = self.create_service(
            RoverAvailList,
            'Available_Rovers',
            self.Available_position_callback
        )

    def listener_callback(self, msg):
        self.rover_paths[msg.roverID] = msg
        self.pointers[msg.roverID] = 0
    def update_position_callback(self, request, response):
        for i in range(len(request.list)):
            if request.request[i].roverID not in self.pointers:
                response.response.append(request.request[i])
            else:
                rid = request.request[i].roverID
                if self.rover_paths[rid].path[self.pointers[rid]] not in response.response:
                    up = Rovercoord()
                    up.roverID = request.request[i].roverID
                    up.coord = self.rover_paths[rid].path[self.pointers[rid]]
                    response.response.append(up) 
                    self.pointers[rid] += 1
                else :
                    response.response.append(request.request[i])
                if self.pointers[rid] >= len(self.rover_paths[rid].path):
                    del self.pointers[rid]
                    del self.rover_paths[rid]
        return response
    def Available_position_callback(self, request, response):
        for i in range(len(request.request)):
            up = RoverAvail()
            rid = request.request[i].roverid
            avail = request.request[i].avail
            tid = request.request[i].task_id
            if rid in self.pointers:
                avail = False
                tid = self.rover_paths[rid].task_id
            up.roverid = rid
            up.avail = avail
            up.task_id = tid
            response.response.append(up)
        return response
def main(args=None):
    rclpy.init(args=args)
    node = UpdateNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()