#Still in progress....
#To be used to get intimation from the exploration package about the dead end or split requirement


import rclpy
from rclpy.node import Node
from messages.msg import InfoMsg
from branch import branch,dict_branches
surrounding={}
class info_node(Node):
    def __init__(self):
        super().__init__("info_node")
        self.info_sub=self.create_subscription(InfoMsg,"infoNodeTopic",self.callback,10)   #this will get info form the exploration package and callback the function to call the split
        #msg has branch id and list of tuples having the first coordinate of possible paths.
        #the msg type will have data as wheater its "dead-end" or "split" 
        #the path is directly updated to the branch class using its subscription in branch class

    def callback(self,msg):
        
       
        
        if msg.data=="split":
            
            branch=dict_branches[msg.id]   #this is so that object of rbanch class can be called using the id as class objects can not be sent over msg
            branch.split(msg.surrounding)  

        elif msg.data=="dead-end":
            branch=dict_branches[msg.id]       #here we would make it retrace its path which is stored. After that we will contact the previous leader and make it a part of previous branch only
            #so msg will have the id adn the id of previous leader branch
            #branch will have to inform its members to return to leader and then disband
            branch.returning(msg.id_prev_leader)
         
