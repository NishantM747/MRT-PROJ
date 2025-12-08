# # # import rclpy
# # # from rclpy.node import Node
# # # from messages.msg import BranchMsg
# # # from messages.msg import InfoMsg
# # # from messages.srv import MoveMembers

# # # mapping={}
# # # from .bot import Bot
# # # import random
# # # from messages.msg import PathMsg
# # # dict_branches={}  #this will have all the branch class objects with their id as key
# # # branches=[] #this will have all the branch objects in the order in which they are created. Used for retracing so that the childd can go to whatever is alive.
# # # coordinates_explored={}  #this will have all the coordinates explored with their branch id as value
# # # class branch_node(Node):#The node branch will handle ros related works
# # #     def __init__(self):
# # #         super().__init__("branch_node")
# # #         self.path_sub=self.create_subscription(PathMsg,"path_topic",self.update_path_callback,10)   #this will get the path with id of branch and we will use the universal branch dict to get the branch class object from it and then update its attribute path
# # #         #this pathmsg has id and the new coordinate it traversed as its attributes
# # #         self.branch_pub=self.create_publisher(BranchMsg,"branch_topic",10)   #this will publish the branch info to exploration package
# # #         self.move_srv = self.create_service(MoveMembers, 'move_members', self.move_members_callback)
# # #         self.info_sub=self.create_subscription(InfoMsg,"infoNodeTopic",self.callback,10)


# # #     def callback(self,msg):
# # #         if msg.data=="split":
# # #             self.get_logger().info(f"Branch {msg.id} received split command")
# # #             branch=dict_branches[msg.id]   #this is so that object of rbanch class can be called using the id as class objects can not be sent over msg
# # #             branch.split(msg.surrounding)  

# # #         elif msg.data=="dead-end":
# # #             branch=dict_branches[msg.id]       #here we would make it retrace its path which is stored. After that we will contact the previous leader and make it a part of previous branch only
# # #             #so msg will have the id adn the id of previous leader branch
# # #             #branch will have to inform its members to return to leader and then disband
# # #             branch.returning(msg.id_prev_leader)
         

  
# # #     def publish_branch_info(self,branch):
# # #         msg=BranchMsg()
# # #         #for init coord
# # #         self.get_logger().info(f"Publishing info of Branch {branch.id}")
# # #         if len(branch.path)>0:
# # #             if len(branch.path)==1:
# # #                 init=branch.path[0]
                
# # #             else:
# # #                 init=branch.path[-1]    #this is the case when a branch is updated. so it should start from where it left
# # #         else: 
# # #             init=(0,0)
# # #         msg.init_coord=init
# # #         msg.id=branch.id
# # #         msg.leader_id=branch.leader.id
# # #         msg.splitting=branch.spliting
# # #         msg.member_ids=[i.id for i in branch.members]
# # #         msg.next_id=branch.prev.id if branch.prev else -1
# # #         self.branch_pub.publish(msg)

# # #     def move_members_callback(self, request, response):
# # #         branch_id = request.branch_id
# # #         target_coord = (request.x,request.y)
# # #         if branch_id in dict_branches:
# # #             branch = dict_branches[branch_id]
# # #             for member in branch.members:
# # #                 member.move(target_coord)
# # #             branch.update_path(target_coord)
# # #             response.success = True
# # #         else:
# # #             response.success = False
# # #         return response
# # #     def update_path_callback(self,msg):    #this will get the new coord , AND CHECK IF IT BELONGS TO ME OR NOT USING THE ID. If not, it will call the merge function of branch class
# # #         branch=dict_branches[msg.id]
# # #         coord=msg.coordinate
# # #         if coord in coordinates_explored:
# # #             #means someone else already taken this coordinate
# # #             other_branch_id=coordinates_explored[coord]
# # #             if other_branch_id!=branch.id:
# # #                 other_branch=dict_branches[other_branch_id]
# # #                 #call the function such that this old branch reaches the new branch to merge into
# # #                 # branch.merge(other_branch)
# # #                 self.get_logger().info(f"Branch {branch.id} stepped into Branch {other_branch.id} at coordinate {coord}")
# # #                 branch.update_path(coord)
# # #         else:
# # #             branch.update_path(msg.coordinate)
# # #             for i in branch.members:
# # #                 i.move(coord)
# # #             coordinates_explored[coord]=branch.current

# # # node=None 
# # # class branch:  #pure python class. This will handle the branch and its function. The node branch will handle ros related works
# # #     min_size=2
# # #     i=1
# # #     def __init__(self,members,leader,id=i,spliting=True,retracing=False,path=None,prev=None):
# # #         self.id=branch.i
# # #         self.leader=leader
# # #         self.leader.branch_id=self.id
# # #         self.node=self.get_node()
# # #         self.members=members   #list of object form bot class
# # #         self.leader.leader()
# # #         for i in self.members:
# # #             i.follower()
# # #             i.follow_leader=self.leader
# # #             i.branch_id=self.id
# # #         self.path=[] if path is None else path  #list of coord tuples
# # #         dict_branches[self.id]=self
# # #         self.retracing=retracing
# # #         self.prev=prev   #prev branch object if split happens
# # #         self.current=self.id   #this is to point to the branch which is currently active in case of splits
# # #         print(f"Branch created with id {self.id}, leader {self.leader.id}" )
        
# # #         self.spliting=spliting   #this shows if the branch is able to split further or not
# # #         self.node.publish_branch_info(self)   #publish its info when created
        
# # #         branch.i+=1


# # #     def get_node(self):  #single node for all branch class to use its publish function
# # #         global node
# # #         if node==None:
# # #             node=branch_node()
# # #         return node
  


# # #     def merge_path_based(self,branch_to_merge_into):
# # #         #what we think is that we attribute every coordinate if the map its branch id as the id of the branch which has traversed it. If a branch steps on a coor not its own/not new, then ut becomes the part of that branch 
# # #         #move the self to branch_to_merge_into
# # #         #then add the members and leader and delete self from dict_branches
# # #         self.members.append(self.leader)
# # #         branch_to_merge_into.update_branch(self.members)
# # #         self.current=branch_to_merge_into.current  
# # #         del dict_branches[self.id]


# # #     def split(self,surrounding):    #surrounding is now a list of tupple having viable paths start coordinates
# # #         print(f"Branch with id {self.id} is splitting")
# # #         if len(self.members)==1:
# # #             print(f"branch with id {self.id} is at its min")
# # #             self.spliting=False
# # #             x=random.choice(i for i in surrounding )
# # #             new_branch=branch(members=self.members,leader=self.leader,spliting=False,path=[x],id=self.id)   #again the same branch is published with splitting False
# # #             dict_branches[new_branch.id]=new_branch
# # #             del dict_branches[self.id]
# # #         else:
# # #             frontier=surrounding.copy()  #list of viable paths
# # #             new_branch_leader=self.check_leader(self.members)    #will return the bot object which will be the new leader of new branch
# # #             n=len(self.members)//2   #number of members in the original
# # #             self.members.remove(new_branch_leader)
            
            
# # #             if len(frontier)==3:
                
# # #                 x=random.choice(frontier)   #take a frontier, x is of form (a,b)
                
# # #                 new1=branch(members=self.members[:n],leader=self.leader,path=[x],prev=self.id)    #this will publish the branch with init coord as x
# # #                 frontier.remove(x)
# # #                 # branch_node.publish_branch_info(new1)
# # #                 dict_branches[new1.id]=new1
# # #                 new2.split(surrounding)
# # #                 del dict_branches[self.id]
# # #             else:
# # #                 x=random.choice(frontier)
                
# # #                 new1=branch(members=self.members[:n],leader=self.leader,path=[x],prev=self.id)
# # #                 branches.append(new1.id)
                
# # #                 frontier.remove(x)
               
# # #                 new2=branch(members=self.members[n:],leader=new_branch_leader,path=[frontier[0]],id=self.id,prev=self.prev)
# # #                 frontier.remove(frontier[0])
# # #                 del dict_branches[self.id]
# # #                 dict_branches[new1.id]=new1
# # #                 dict_branches[new2.id]=new2
# # #                 print(f"Branch with id {self.id} split into branches {new1.id} and {new2.id}")
                

# # #     def update_path(self,path):
        
# # #         self.path.append(path)

# # #     def update_branch(self,members_added):
# # #         self.members.extend(members_added)
# # #         for i in members_added:
# # #             i.follower()
# # #             i.follow_leader=self.leader
# # #         print(f"Branch {self.id} updated with new members {[i.id for i in members_added]}")
# # #         self.node.publish_branch_info(self)   #havee to publish it again
# # #     def change_leader(self,members):
# # #         x=members[0].priority
# # #         new_leader=members[0]
# # #         for i in members:
# # #             if i.priority<x:
# # #                 x=i.priority
# # #                 new_leader=i    
# # #         return(new_leader)
            
            
# # #     def returning(self):
# # #         #work in progress...
# # #         #Logic 1: make all the members retrace the path in reverse order to reach the previous leader
# # #         self.retracing=True
# # #         target_coord=self.path[0]
# # #         self.leader.is_returning()
# # #         for i in self.members:
# # #             i.is_returning()
# # #         new_path=self.path[::-1]   #reverse path
# # #         #make them follow the path in reverse
# # #         #call the path finding algo.
# # #         idx=branches.index(self.prev)  #get the index of previous branch in branches list
# # #         while idx>=0:
# # #             if branches[idx] in dict_branches:
# # #                 prev=dict_branches[branches[idx]]   #getting the branch object of previous leader
# # #                 break
# # #             idx-=1
# # #         #now use this prev to find the previous father branch
# # #         #now go and merge with this branch
# # #         #----------------------------------------------------------------
# # #         b2=dict_branches[self.prev]   #previous leader branch
# # #         path_follow=b2.path
# # #         #make them follow this path
# # #         #once they get there, make them part of that branch
# # #         b2.update_branch(self.members)
# # #         #delete this branch from dict_branches   
# # #         del dict_branches[self.id]


# # #     def merge(self,branch_to_merge_into):
# # #         #merge self into branch_to_merge_into
# # #         self.members.append(self.leader)
# # #         branch_to_merge_into.update_branch(self.members)
# # #         self.current=branch_to_merge_into.current   #this will make all the path transfer to the new branch id
# # #         del dict_branches[self.id]
  
    




# # # def main(args=None):
# # #     rclpy.init(args=args)
    
# # #     bot1=bot(coord=(0,0),id=1)
# # #     bot2=bot(coord=(0,0),id=2)
# # #     bot3=bot(coord=(0,0),id=3)
# # #     bot4=bot(coord=(0,0),id=4)
# # #     branch1=branch(leader=bot1,members=[bot2])
# # #     branch2=branch(leader=bot3,members=[bot4])
# # #     print(branch1.id,branch2.id)

# # #     # rclpy.spin(node)   
# # #     rclpy.shutdown()

# # # if __name__ == '__main__':
# # #     main()

# # # --------------------------------------------------------------------------------------------
# # import rclpy
# # from rclpy.node import Node
# # from messages.msg import BranchMsg
# # from messages.msg import InfoMsg
# # from messages.srv import MoveMembers
# # from .bot import Bot
# # import random
# # from messages.msg import PathMsg

# # mapping = {}
# # coordinates_explored = {}  # this will have all the coordinates explored with their branch id as value
# # branches = []  # this will have all the branch objects in the order in which they are created. Used for retracing so that the child can go to whatever is alive.

# # # Global universal branch_node instance
# # _branch_node_instance = None


# # def get_branch_node():
# #     """Get or create the universal BranchNode instance"""
# #     global _branch_node_instance
# #     if _branch_node_instance is None:
# #         if not rclpy.ok():
# #             raise RuntimeError("rclpy not initialized. Call rclpy.init() first.")
# #         _branch_node_instance = branch_node()
# #     return _branch_node_instance


# # class branch_node(Node):  # The node branch will handle ros related works
# #     def __init__(self):
# #         super().__init__("branch_node")
        
# #         # Dictionary to store all branch objects with their ID as key
# #         self.dict_branches = {}
        
# #         self.path_sub = self.create_subscription(PathMsg, "path_topic", self.update_path_callback, 10)
# #         self.branch_pub = self.create_publisher(BranchMsg, "branch_topic", 10)
# #         self.move_srv = self.create_service(MoveMembers, 'move_members', self.move_members_callback)
# #         self.info_sub = self.create_subscription(InfoMsg, "infoNodeTopic", self.callback, 10)
        
# #         self.get_logger().info("BranchNode initialized")

# #     def add_branch(self, branch_obj):
# #         """Add a branch object to the dictionary"""
# #         self.dict_branches[branch_obj.id] = branch_obj
# #         self.get_logger().info(f"Branch {branch_obj.id} added to node. Total branches: {len(self.dict_branches)}")

# #     def remove_branch(self, branch_id: int):
# #         """Remove a branch from the dictionary"""
# #         if branch_id in self.dict_branches:
# #             del self.dict_branches[branch_id]
# #             self.get_logger().info(f"Branch {branch_id} removed from node")

# #     def get_branch(self, branch_id: int):
# #         """Get a branch object by ID"""
# #         return self.dict_branches.get(branch_id, None)

# #     def callback(self, msg):
# #         if str(msg.data) == "split":
# #             self.get_logger().info(f"Branch {msg.branch_id} received split command")
# #             branch = self.dict_branches.get(msg.branch_id)
# #             if branch:
# #                 branch.split(list(msg.surrounding))

# #         elif msg.data == "dead-end":
# #             branch = self.dict_branches.get(msg.branch_id)
# #             if branch:
# #                 branch.returning()

# #     def publish_branch_info(self, branch):
# #         msg = BranchMsg()
# #         self.get_logger().info(f"Publishing info of Branch {branch.id}")
        
# #         if len(branch.path) > 0:
# #             if len(branch.path) == 1:
# #                 init = branch.path[0]
# #             else:
# #                 init = branch.path[-1]
# #         else:
# #             init = (0, 0)
        
# #         msg.init_coord = init
# #         msg.id = branch.id
# #         msg.leader_id = branch.leader.id
# #         msg.splitting = branch.spliting
# #         msg.member_ids = [i.id for i in branch.members]
# #         msg.next_id = branch.prev.id if branch.prev else -1
# #         self.branch_pub.publish(msg)

# #     def move_members_callback(self, request, response):
# #         branch_id = request.branch_id
# #         target_coord = (request.x, request.y)
        
# #         if branch_id in self.dict_branches:
# #             branch = self.dict_branches[branch_id]
# #             for member in branch.members:
# #                 member.move(target_coord)
# #             branch.update_path(target_coord)
# #             response.success = True
# #         else:
# #             response.success = False
# #         return response

# #     def update_path_callback(self, msg):
# #         branch = self.dict_branches.get(msg.id)
# #         if not branch:
# #             return
        
# #         coord = msg.coordinate
        
# #         if coord in coordinates_explored:
# #             other_branch_id = coordinates_explored[coord]
# #             if other_branch_id != branch.id:
# #                 other_branch = self.dict_branches.get(other_branch_id)
# #                 if other_branch:
# #                     self.get_logger().info(f"Branch {branch.id} stepped into Branch {other_branch.id} at coordinate {coord}")
# #                     branch.update_path(coord)
# #         else:
# #             branch.update_path(coord)
# #             for i in branch.members:
# #                 i.move(coord)
# #             coordinates_explored[coord] = branch.current


# # class branch:  # pure python class. This will handle the branch and its function.
# #     min_size = 2
# #     i = 1
    
# #     def __init__(self, members, leader, id=None, spliting=True, retracing=False, path=None, prev=None):
# #         if id is None:
# #             self.id = branch.i
# #             branch.i += 1
# #         else:
# #             self.id = id
            
# #         self.leader = leader
# #         self.leader.branch_id = self.id
# #         self.node = get_branch_node()
# #         self.members = members
# #         self.leader.set_leader()
        
# #         for i in self.members:
# #             i.set_follower()
# #             i.follow_leader = self.leader
# #             i.branch_id = self.id
        
# #         self.path = [] if path is None else path
# #         self.retracing = retracing
# #         self.prev = prev
# #         self.current = self.id
# #         self.spliting = spliting
        
# #         # Register this branch with the universal node
# #         self.node.add_branch(self)
        
# #         print(f"Branch created with id {self.id}, leader {self.leader.id}")
        
# #         # Publish its info when created
# #         self.node.publish_branch_info(self)

# #     def merge_path_based(self, branch_to_merge_into):
# #         self.members.append(self.leader)
# #         branch_to_merge_into.update_branch(self.members)
# #         self.current = branch_to_merge_into.current
# #         self.node.remove_branch(self.id)

# #     def split(self, surrounding):
# #         print(f"Branch with id {self.id} is splitting")
        
# #         if len(self.members) == 1:
# #             print(f"branch with id {self.id} is at its min")
# #             self.spliting = False
# #             x = random.choice(surrounding)
# #             new_branch = branch(members=self.members, leader=self.leader, spliting=False, path=[x], id=self.id)
# #             self.node.remove_branch(self.id)
# #         else:
# #             frontier = surrounding.copy()
# #             new_branch_leader = self.check_leader(self.members)
# #             n = len(self.members) // 2
# #             self.members.remove(new_branch_leader)
            
# #             if len(frontier) == 3:
# #                 x = random.choice(frontier)
# #                 new1 = branch(members=self.members[:n], leader=self.leader, path=[x], prev=self.id)
# #                 frontier.remove(x)
# #                 new2 = branch(members=self.members[n:], leader=new_branch_leader, path=[], prev=self.id)
# #                 new2.split(frontier)
# #                 self.node.remove_branch(self.id)
# #             else:
# #                 x = random.choice(frontier)
# #                 new1 = branch(members=self.members[:n], leader=self.leader, path=[x], prev=self.id)
# #                 branches.append(new1.id)
# #                 frontier.remove(x)
# #                 new2 = branch(members=self.members[n:], leader=new_branch_leader, path=[frontier[0]], id=self.id, prev=self.prev)
# #                 frontier.remove(frontier[0])
# #                 self.node.remove_branch(self.id)
# #                 print(f"Branch with id {self.id} split into branches {new1.id} and {new2.id}")

# #     def update_path(self, path):
# #         self.path.append(path)

# #     def update_branch(self, members_added):
# #         self.members.extend(members_added)
# #         for i in members_added:
# #             i.set_follower()
# #             i.follow_leader = self.leader
# #         print(f"Branch {self.id} updated with new members {[i.id for i in members_added]}")
# #         self.node.publish_branch_info(self)

# #     def check_leader(self, members):
# #         x = members[0].priority
# #         new_leader = members[0]
# #         for i in members:
# #             if i.priority < x:
# #                 x = i.priority
# #                 new_leader = i
# #         return new_leader

# #     def returning(self):
# #         self.retracing = True
# #         target_coord = self.path[0]
# #         self.leader.set_returning()
# #         for i in self.members:
# #             i.set_returning()
# #         new_path = self.path[::-1]
        
# #         idx = branches.index(self.prev)
# #         while idx >= 0:
# #             if branches[idx] in self.node.dict_branches:
# #                 prev = self.node.dict_branches[branches[idx]]
# #                 break
# #             idx -= 1
        
# #         b2 = self.node.dict_branches.get(self.prev)
# #         if b2:
# #             path_follow = b2.path
# #             b2.update_branch(self.members)
# #             self.node.remove_branch(self.id)

# #     def merge(self, branch_to_merge_into):
# #         self.members.append(self.leader)
# #         branch_to_merge_into.update_branch(self.members)
# #         self.current = branch_to_merge_into.current
# #         self.node.remove_branch(self.id)


# # def main(args=None):
# #     rclpy.init(args=args)
    
# #     # Get the universal branch_node instance
# #     branch_node_instance = get_branch_node()
    
# #     # Example usage
# #     # bot1 = Bot(coord=(0, 0), id=1, priority=1)
# #     # bot2 = Bot(coord=(0, 0), id=2, priority=2)
# #     # bot3 = Bot(coord=(0, 0), id=3, priority=3)
# #     # bot4 = Bot(coord=(0, 0), id=4, priority=4)
# #     # branch1 = branch(leader=bot1, members=[bot2])
# #     # branch2 = branch(leader=bot3, members=[bot4])
# #     # print(branch1.id, branch2.id)
    
# #     rclpy.spin(branch_node_instance)
# #     rclpy.shutdown()


# # if __name__ == '__main__':
# #     main()



# import rclpy
# from rclpy.node import Node
# from messages.msg import BranchMsg
# from messages.msg import InfoMsg
# from messages.srv import MoveMembers
# from .bot import Bot
# import random
# from messages.msg import PathMsg

# mapping = {}
# coordinates_explored = {}  # this will have all the coordinates explored with their branch id as value
# branches = []  # this will have all the branch objects in the order in which they are created. Used for retracing so that the child can go to whatever is alive.

# # Global universal branch_node instance
# _branch_node_instance = None


# def get_branch_node():
#     """Get or create the universal BranchNode instance"""
#     global _branch_node_instance
#     if _branch_node_instance is None:
#         if not rclpy.ok():
#             raise RuntimeError("rclpy not initialized. Call rclpy.init() first.")
#         _branch_node_instance = branch_node()
#     return _branch_node_instance


# class branch_node(Node):  # The node branch will handle ros related works
#     def __init__(self):
#         super().__init__("branch_node")
        
#         # Dictionary to store all branch objects with their ID as key
#         self.dict_branches = {}
        
#         self.path_sub = self.create_subscription(PathMsg, "path_topic", self.update_path_callback, 10)
#         self.branch_pub = self.create_publisher(BranchMsg, "branch_topic", 10)
#         self.move_srv = self.create_service(MoveMembers, 'move_members', self.move_members_callback)
#         self.info_sub = self.create_subscription(InfoMsg, "infoNodeTopic", self.callback, 10)
        
#         self.get_logger().info("BranchNode initialized")
#         self.get_logger().info(f"Subscribed to InfoMsg on topic: infoNodeTopic")
#         self.get_logger().info(f"Publishing BranchMsg on topic: branch_topic")

#     def add_branch(self, branch_obj):
#         """Add a branch object to the dictionary"""
#         self.dict_branches[branch_obj.id] = branch_obj
#         self.get_logger().info(f"Branch {branch_obj.id} added to node. Total branches: {len(self.dict_branches)}")

#     def remove_branch(self, branch_id: int):
#         """Remove a branch from the dictionary"""
#         if branch_id in self.dict_branches:
#             del self.dict_branches[branch_id]
#             self.get_logger().info(f"Branch {branch_id} removed from node")

#     def get_branch(self, branch_id: int):
#         """Get a branch object by ID"""
#         return self.dict_branches.get(branch_id, None)

#     def callback(self, msg):
#         self.get_logger().info(f"Received callback with data: {msg.data}")
#         print(msg.c1,msg.c2,msg.c3)
#         if tuple(msg.c3)==():
#             surr=[]
#             surr.append(tuple(msg.c1))
#             surr.append(tuple(msg.c2))
#             print(surr)
#         else:
            
#             surr=[]
#             surr.append(tuple(msg.c1))
#             surr.append(tuple(msg.c2))
#             surr.append(tuple(msg.c3))
#             print(surr)
#         if msg.data == "split":
#             self.get_logger().info(f"Branch {msg.branch_id} received split command")
#             print(self.dict_branches)
#             branch = self.dict_branches.get(msg.branch_id)
#             if branch:
#                 self.get_logger().info(f"Found branch {branch.id}, calling split with {surr}")
#                 branch.split(surr)
#             else:
#                 self.get_logger().error(f"Branch {msg.branch_id} not found in dict_branches!")

#         elif msg.data == "dead-end":
#             branch = self.dict_branches.get(msg.branch_id)
#             if branch:
#                 branch.returning()
#             else:
#                 self.get_logger().error(f"Branch {msg.branch_id} not found for dead-end!")

#     def publish_branch_info(self, branch):
#         msg = BranchMsg()
#         self.get_logger().info(f"Publishing info of Branch {branch.id}")
        
#         if len(branch.path) > 0:
#             if len(branch.path) == 1:
#                 init = branch.path[0]
#             else:
#                 init = branch.path[-1]
#         else:
#             init = (0, 0)
        
#         msg.init_coord = init
#         msg.id = branch.id
#         msg.leader_id = branch.leader.id
#         msg.splitting = branch.spliting
#         msg.member_ids = [i.id for i in branch.members]
#         msg.next_id = branch.prev.id if branch.prev else -1
#         self.branch_pub.publish(msg)

#     def move_members_callback(self, request, response):
#         branch_id = request.branch_id
#         target_coord = (request.x, request.y)
        
#         if branch_id in self.dict_branches:
#             branch = self.dict_branches[branch_id]
#             for member in branch.members:
#                 member.move(target_coord)
#             branch.update_path(target_coord)
#             response.success = True
#         else:
#             response.success = False
#         return response

#     def update_path_callback(self, msg):
#         branch = self.dict_branches.get(msg.id)
#         if not branch:
#             return
        
#         coord = msg.coordinate
        
#         if coord in coordinates_explored:
#             other_branch_id = coordinates_explored[coord]
#             if other_branch_id != branch.id:
#                 other_branch = self.dict_branches.get(other_branch_id)
#                 if other_branch:
#                     self.get_logger().info(f"Branch {branch.id} stepped into Branch {other_branch.id} at coordinate {coord}")
#                     branch.update_path(coord)
#         else:
#             branch.update_path(coord)
#             for i in branch.members:
#                 i.move(coord)
#             coordinates_explored[coord] = branch.current


# class branch:  # pure python class. This will handle the branch and its function.
#     min_size = 2
#     i = 1
    
#     def __init__(self, members, leader, id=None, spliting=True, retracing=False, path=None, prev=None):
#         if id is None:
#             self.id = branch.i
#             branch.i += 1
#         else:
#             self.id = id
            
#         self.leader = leader
#         self.leader.branch_id = self.id
#         self.node = get_branch_node()
#         self.members = members
#         self.leader.set_leader()
        
#         for i in self.members:
#             i.set_follower()
#             i.follow_leader = self.leader
#             i.branch_id = self.id
        
#         self.path = [] if path is None else path
#         self.retracing = retracing
#         self.prev = prev
#         self.current = self.id
#         self.spliting = spliting
        
#         # Register this branch with the universal node
#         self.node.add_branch(self)
        
#         print(f"Branch created with id {self.id}, leader {self.leader.id}")
        
#         # Publish its info when created
#         self.node.publish_branch_info(self)

#     def merge_path_based(self, branch_to_merge_into):
#         self.members.append(self.leader)
#         branch_to_merge_into.update_branch(self.members)
#         self.current = branch_to_merge_into.current
#         self.node.remove_branch(self.id)

#     def split(self, surrounding):
#         print(f"Branch with id {self.id} is splitting")
        
#         if len(self.members) == 1:
#             print(f"branch with id {self.id} is at its min")
#             self.spliting = False
#             x = random.choice(surrounding)
#             new_branch = branch(members=self.members, leader=self.leader, spliting=False, path=[x], id=self.id)
#             self.node.remove_branch(self.id)
#         else:
#             print("split started")
#             frontier = surrounding.copy()
#             print(frontier)
#             new_branch_leader = self.check_leader(self.members)
#             print(new_branch_leader.id)
#             n = len(self.members) // 2
#             # self.members.remove(new_branch_leader)
            
#             # if len(frontier) == 3:
#             #     x = random.choice(frontier)
#             #     new1 = branch(members=self.members[:n], leader=self.leader, path=[x], prev=self.id)
#             #     frontier.remove(x)
#             #     new2 = branch(members=self.members[n:], leader=new_branch_leader, path=[], prev=self.id)
#             #     new2.split(frontier)
#             #     self.node.remove_branch(self.id)
#             # ...existing code...
#             # ...existing code...
#             if len(frontier) == 3:
#                 print(frontier)
#                 if len(self.member)<5:
#                     frontier.pop()
#                     self.split(frontier)
#                 # choose two new leaders from current members (lowest priority wins)
#                 candidates = sorted(self.members, key=lambda b: b.priority)
#                 new_leader1 = candidates[0] if len(candidates) >= 1 else new_branch_leader
#                 new_leader2 = candidates[1] if len(candidates) >= 2 else (candidates[0] if candidates else new_branch_leader)

#                 # remove chosen leaders from the pool of members
#                 remaining = [m for m in self.members if m not in (new_leader1, new_leader2)]

#                 # evenly distribute remaining members among three groups
#                 groups = [[], [], []]
#                 for idx, m in enumerate(remaining):
#                     groups[idx % 3].append(m)

#                 # assign one frontier coordinate to each new branch
#                 random.shuffle(frontier)
#                 coord_a, coord_b, coord_c = frontier[0], frontier[1], frontier[2]

#                 # create three new branches
#                 b1 = branch(members=groups[0], leader=self.leader, path=[coord_a], prev=self.id)
#                 b2 = branch(members=groups[1], leader=new_leader1, path=[coord_b], prev=self.id)
#                 b3 = branch(members=groups[2], leader=new_leader2, path=[coord_c], prev=self.id)

#                 # remove the original branch from the node registry
#                 self.node.remove_branch(self.id)
# # ...existing code...

#             else:
#                 self.members.remove(new_branch_leader)
#                 x = random.choice(frontier)
#                 print(x)
#                 new1 = branch(id=self.id,members=self.members[:n], leader=self.leader, path=[x], prev=self.id)
#                 branches.append(new1.id)
#                 frontier.remove(x)
#                 new2 = branch(members=self.members[n:], leader=new_branch_leader, path=[frontier[0]], prev=self.prev)
#                 frontier.remove(frontier[0])
#                 self.node.remove_branch(self.id)
#                 print(f"Branch with id {self.id} split into branches {new1.id} and {new2.id}")

#     def update_path(self, path):
#         self.path.append(path)

#     def update_branch(self, members_added):
#         self.members.extend(members_added)
#         for i in members_added:
#             i.set_follower()
#             i.follow_leader = self.leader
#         print(f"Branch {self.id} updated with new members {[i.id for i in members_added]}")
#         self.node.publish_branch_info(self)

#     def check_leader(self, members):
#         x = members[0].priority
#         new_leader = members[0]
#         for i in members:
#             if i.priority < x:
#                 x = i.priority
#                 new_leader = i
#         return new_leader

#     def returning(self):
#         self.retracing = True
#         target_coord = self.path[0]
#         self.leader.set_returning()
#         for i in self.members:
#             i.set_returning()
#         new_path = self.path[::-1]
        
#         idx = branches.index(self.prev)
#         while idx >= 0:
#             if branches[idx] in self.node.dict_branches:
#                 prev = self.node.dict_branches[branches[idx]]
#                 break
#             idx -= 1
        
#         b2 = self.node.dict_branches.get(self.prev)
#         if b2:
#             path_follow = b2.path
#             b2.update_branch(self.members)
#             self.node.remove_branch(self.id)

#     def merge(self, branch_to_merge_into):
#         self.members.append(self.leader)
#         branch_to_merge_into.update_branch(self.members)
#         self.current = branch_to_merge_into.current
#         self.node.remove_branch(self.id)


# def main(args=None):
#     rclpy.init(args=args)
    
#     # Get the universal branch_node instance
#     branch_node_instance = get_branch_node()
    
#     # Example usage
#     # bot1 = Bot(coord=(0, 0), id=1, priority=1)
#     # bot2 = Bot(coord=(0, 0), id=2, priority=2)
#     # bot3 = Bot(coord=(0, 0), id=3, priority=3)
#     # bot4 = Bot(coord=(0, 0), id=4, priority=4)
#     # branch1 = branch(leader=bot1, members=[bot2])
#     # branch2 = branch(leader=bot3, members=[bot4])
#     # print(branch1.id, branch2.id)
    
#     rclpy.spin(branch_node_instance)
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()

import rclpy
from rclpy.node import Node
from messages.msg import BranchMsg
from messages.msg import InfoMsg
from messages.srv import MoveMembers
from .bot import Bot
import random
from messages.msg import PathMsg

mapping = {}
coordinates_explored = {}  # this will have all the coordinates explored with their branch id as value
branches = []  # this will have all the branch objects in the order in which they are created. Used for retracing so that the child can go to whatever is alive.

# Global universal branch_node instance
_branch_node_instance = None


def get_branch_node():
    """Get or create the universal BranchNode instance"""
    global _branch_node_instance
    if _branch_node_instance is None:
        if not rclpy.ok():
            raise RuntimeError("rclpy not initialized. Call rclpy.init() first.")
        _branch_node_instance = branch_node()
    return _branch_node_instance


class branch_node(Node):  # The node branch will handle ros related works
    def __init__(self):
        super().__init__("branch_node")
        
        # Dictionary to store all branch objects with their ID as key
        self.dict_branches = {}
        
        self.path_sub = self.create_subscription(PathMsg, "path_topic", self.update_path_callback, 10)
        self.branch_pub = self.create_publisher(BranchMsg, "branch_topic", 10)
        self.move_srv = self.create_service(MoveMembers, 'move_members', self.move_members_callback)
        self.info_sub = self.create_subscription(InfoMsg, "infoNodeTopic", self.callback, 10)
        
        self.get_logger().info("BranchNode initialized")
        self.get_logger().info(f"Subscribed to InfoMsg on topic: infoNodeTopic")
        self.get_logger().info(f"Publishing BranchMsg on topic: branch_topic")

    def add_branch(self, branch_obj):
        """Add a branch object to the dictionary"""
        self.dict_branches[branch_obj.id] = branch_obj
        self.get_logger().info(f"Branch {branch_obj.id} added to node. Total branches: {len(self.dict_branches)}")

    def remove_branch(self, branch_id: int):
        """Remove a branch from the dictionary"""
        if branch_id in self.dict_branches:
            del self.dict_branches[branch_id]
            self.get_logger().info(f"Branch {branch_id} removed from node")

    def get_branch(self, branch_id: int):
        """Get a branch object by ID"""
        return self.dict_branches.get(branch_id, None)

    def callback(self, msg):
        self.get_logger().info(f"Received callback with data: {msg.data}")
        print(msg.c1, msg.c2, msg.c3)
        if tuple(msg.c3) == ():
            surr = []
            surr.append(tuple(msg.c1))
            surr.append(tuple(msg.c2))
            print(surr)
        else:
            surr = []
            surr.append(tuple(msg.c1))
            surr.append(tuple(msg.c2))
            surr.append(tuple(msg.c3))
            print(surr)
        if msg.data == "split":
            self.get_logger().info(f"Branch {msg.branch_id} received split command")
            print(self.dict_branches)
            branch = self.dict_branches.get(msg.branch_id)
            if branch:
                self.get_logger().info(f"Found branch {branch.id}, calling split with {surr}")
                branch.split(surr)
            else:
                self.get_logger().error(f"Branch {msg.branch_id} not found in dict_branches!")

        elif msg.data == "dead-end":
            branch = self.dict_branches.get(msg.branch_id)
            if branch:
                branch.returning()
            else:
                self.get_logger().error(f"Branch {msg.branch_id} not found for dead-end!")

    def publish_branch_info(self, branch):
        msg = BranchMsg()
        self.get_logger().info(f"====== PUBLISHING BRANCH INFO ======")
        print(branch.path)
        self.get_logger().info(f"Publishing info of Branch {branch.id}")
        
        if len(branch.path) > 0:
            if len(branch.path) == 1:
                init = branch.path[0]
            else:
                init = branch.path[-1]
        else:
            init = (0, 0)
        
        msg.init_coord = init
        msg.id = branch.id
        msg.leader_id = branch.leader.id
        print(msg.leader_id)
        msg.splitting = branch.spliting
        msg.member_ids = [i.id for i in branch.members]
        print(msg.member_ids)
        # msg.next_id = branch.prev.id if branch.prev else -1
        # print(msg.next_id)
        self.get_logger().info(f"Branch {branch.id}: leader={branch.leader.id}, init_coord={init}, splitting={branch.spliting}")
        self.get_logger().info(f"Subscriber count on branch_topic: {self.branch_pub.get_subscription_count()}")
        
        self.branch_pub.publish(msg)
        
        self.get_logger().info(f"Branch {branch.id} info published successfully")
        self.get_logger().info(f"====== PUBLISH COMPLETE ======")

    def move_members_callback(self, request, response):
        branch_id = request.branch_id
        target_coord = (request.x, request.y)
        
        if branch_id in self.dict_branches:
            branch = self.dict_branches[branch_id]
            for member in branch.members:
                member.move(target_coord)
            branch.update_path(target_coord)
            response.success = True
        else:
            response.success = False
        return response

    def update_path_callback(self, msg):
        branch = self.dict_branches.get(msg.id)
        if not branch:
            return
        
        coord = msg.coordinate
        
        if coord in coordinates_explored:
            other_branch_id = coordinates_explored[coord]
            if other_branch_id != branch.id:
                other_branch = self.dict_branches.get(other_branch_id)
                if other_branch:
                    self.get_logger().info(f"Branch {branch.id} stepped into Branch {other_branch.id} at coordinate {coord}")
                    branch.update_path(coord)
        else:
            branch.update_path(coord)
            for i in branch.members:
                i.move(coord)
            coordinates_explored[coord] = branch.current


class branch:  # pure python class. This will handle the branch and its function.
    min_size = 2
    i = 1
    
    def __init__(self, members, leader, id=None, spliting=True, retracing=False, path=None, prev=None):
        if id is None:
            self.id = branch.i
            branch.i += 1
        else:
            self.id = id
            
        self.leader = leader
        self.leader.branch_id = self.id
        self.node = get_branch_node()
        self.members = members
        self.leader.set_leader()
        
        for i in self.members:
            i.set_follower()
            i.follow_leader = self.leader
            i.branch_id = self.id
        
        self.path = [] if path is None else path
        self.retracing = retracing
        self.prev = prev
        self.current = self.id
        self.spliting = spliting
        
        # Register this branch with the universal node
        self.node.add_branch(self)
        
        print(f"Branch created with id {self.id}, leader {self.leader.id}")
        
        # Publish its info when created
        self.node.publish_branch_info(self)

    def merge_path_based(self, branch_to_merge_into):
        self.members.append(self.leader)
        branch_to_merge_into.update_branch(self.members)
        self.current = branch_to_merge_into.current
        self.node.remove_branch(self.id)

    def split(self, surrounding):
        print(f"Branch with id {self.id} is splitting")
        
        if len(self.members) == 1:
            print(f"branch with id {self.id} is at its min")
            self.spliting = False
            x = random.choice(surrounding)
            new_branch = branch(members=self.members, leader=self.leader, spliting=False, path=[x], id=self.id)
            self.node.remove_branch(self.id)
        else:
            print("split started")
            frontier = surrounding.copy()
            print(frontier)
            new_branch_leader = self.check_leader(self.members)
            print(new_branch_leader.id)
            n = len(self.members) // 2
            
            if len(frontier) == 3:
                print(frontier)
                if len(self.members) < 5:
                    frontier.pop()
                    self.split(frontier)
                else:
                    # choose two new leaders from current members (lowest priority wins)
                    candidates = sorted(self.members, key=lambda b: b.priority)
                    new_leader1 = candidates[0] if len(candidates) >= 1 else new_branch_leader
                    new_leader2 = candidates[1] if len(candidates) >= 2 else (candidates[0] if candidates else new_branch_leader)

                    # remove chosen leaders from the pool of members
                    remaining = [m for m in self.members if m not in (new_leader1, new_leader2)]

                    # evenly distribute remaining members among three groups
                    groups = [[], [], []]
                    for idx, m in enumerate(remaining):
                        groups[idx % 3].append(m)

                    # assign one frontier coordinate to each new branch
                    random.shuffle(frontier)
                    coord_a, coord_b, coord_c = frontier[0], frontier[1], frontier[2]

                    # create three new branches
                    b1 = branch(members=groups[0], leader=self.leader, path=[coord_a], prev=self.id)
                    b2 = branch(members=groups[1], leader=new_leader1, path=[coord_b], prev=self.id)
                    b3 = branch(members=groups[2], leader=new_leader2, path=[coord_c], prev=self.id)

                    # remove the original branch from the node registry
                    self.node.remove_branch(self.id)
            else:
                self.members.remove(new_branch_leader)
                x = random.choice(frontier)
                print(x)
                new1 = branch(id=self.id, members=self.members[:n], leader=self.leader, path=[x], prev=self.id)
                branches.append(new1.id)
                frontier.remove(x)
                new2 = branch(members=self.members[n:], leader=new_branch_leader, path=[frontier[0]], prev=self.prev)
                frontier.remove(frontier[0])
                self.node.remove_branch(self.id)
                print(f"Branch with id {self.id} split into branches {new1.id} and {new2.id}")

    def update_path(self, path):
        self.path.append(path)

    def update_branch(self, members_added):
        self.members.extend(members_added)
        for i in members_added:
            i.set_follower()
            i.follow_leader = self.leader
        print(f"Branch {self.id} updated with new members {[i.id for i in members_added]}")
        self.node.publish_branch_info(self)

    def check_leader(self, members):
        x = members[0].priority
        new_leader = members[0]
        for i in members:
            if i.priority < x:
                x = i.priority
                new_leader = i
        return new_leader

    def returning(self):
        self.retracing = True
        target_coord = self.path[0]
        self.leader.set_returning()
        for i in self.members:
            i.set_returning()
        new_path = self.path[::-1]
        
        idx = branches.index(self.prev)
        while idx >= 0:
            if branches[idx] in self.node.dict_branches:
                prev = self.node.dict_branches[branches[idx]]
                break
            idx -= 1
        
        b2 = self.node.dict_branches.get(self.prev)
        if b2:
            path_follow = b2.path
            b2.update_branch(self.members)
            self.node.remove_branch(self.id)

    def merge(self, branch_to_merge_into):
        self.members.append(self.leader)
        branch_to_merge_into.update_branch(self.members)
        self.current = branch_to_merge_into.current
        self.node.remove_branch(self.id)


def main(args=None):
    rclpy.init(args=args)
    
    # Get the universal branch_node instance
    branch_node_instance = get_branch_node()
    
    rclpy.spin(branch_node_instance)
    rclpy.shutdown()


if __name__ == '__main__':
    main()