import rclpy
from rclpy.node import Node
from messages.msg import Coord 
from messages.msg import rover_path
from messages.msg import rover_coord
from messages.srv import rover_list
class UpdateNode(Node):
    def __init__(self):
        super().__init__('Update_node')
        self.rover_paths = []
        self.pointers = {}
        self.subscription = self.create_subscription(
            rover_path,
            'path',
            self.listener_callback,
            10
        )
        self.srv = self.create_service(
            rover_list,
            'Update_position',
            self.update_position_callback
        )

    def listener_callback(self, msg):
        self.rover_paths.append(msg)
        self.pointers[msg.roverID] = 0
    def update_position_callback(self, request, response):
        for i in range(len(request.list)):
            if request.list[i].roverID not in self.pointers:
                response.list.append(request.list[i])
            else:
                rid = request.list[i].roverID
                if self.rover_paths[i].path[self.pointers[rid]] not in response.list:
                    up = rover_coord()
                    up.roverID = request.list[i].roverID
                    up.coord = self.rover_paths[i].path[self.pointers[rid]]
                    response.list.append(up) 
                    self.pointers[rid] += 1
                else :
                    response.list.append(request.list[i])
        return response
def main(args=None):
    rclpy.init(args=args)
    node = UpdateNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()