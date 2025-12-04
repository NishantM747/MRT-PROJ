#Still in progress...
#here we define basic tasks of a branch and its attribute
#the branch publish a request for getting respective coordinates and the map will givve the idea about those coord

import rclpy
from rclpy.node import Node
from messages.msg import BranchMsg

map={}
from .bot import bot
import random
from messages.msg import PathMsg
dict_branches={}  #this will have all the branch class objects with their id as key
branches=[] #this will have all the branch objects in the order in which they are created. Used for retracing so that the childd can go to whatever is alive.
class branch_node(Node):#The node branch will handle ros related works
    def __init__(self):
        super().__init__("branch_node")
        self.path_sub=self.create_subscription(PathMsg,"path_topic",self.update_path,10)   #this will get the path with id of branch and we will use the universal branch dict to get the branch class object from it and then update its attribute path
        #this pathmsg has id and the new coordinate it traversed as its attributes
        self.branch_pub=self.create_publisher(BranchMsg,"branch_topic",10)   #this will publish the branch info to exploration package

  
    def publish_branch_info(self,branch):
        msg=BranchMsg()
        msg.init_coord=branch.path[0] if branch.path else (0,0)
        msg.id=branch.id
        msg.leader_id=branch.leader.id
        msg.splitting=branch.spliting
        msg.member_ids=[i.id for i in branch.members]
        msg.next_id=branch.next.id if branch.next else -1
        self.branch_pub.publish(msg)


    def update_path(self,msg):
        branch=dict_branches[msg.id]
        branch.update_path(msg.coordinate)

node=None 
class branch:  #pure python class. This will handle the branch and its function. The node branch will handle ros related works
    min_size=2
    i=1
    def __init__(self,members,leader,id=i,spliting=True,retracing=False,path=None,prev=None):
        self.id=branch.i
        # super().__init__(f"branch_node{self.id}")
        self.leader=leader
        # self.node=node=branch_node()
        self.node=self.get_node()
        branch.i+=1
        self.members=members   #list of object form bot class
        # self.lidar_pub=self.create_publisher()
        self.leader.leader()
        for i in self.members:
            i.follower()
            i.follow_leader=self.leader
        self.path=[] if path is None else path  #list of coord tuples
        dict_branches[self.id]=self
        self.retracing=retracing
        self.prev=prev   #next branch object if split happens
        # self.pub()
        # self.path_sub=self.create_subscription(PathMsg,"path_topic",self.update_path,10)   #this will get the path with id of branch and we will use the universal branch dict to get the branch class object from it and then update its attribute path
        #this pathmsg has id and the new coordinate it traversed as its attributes
        self.spliting=spliting   #this shows if the branch is able to split further or not
        self.node.publish_branch_info(self)   #publish its info when created
        



    def get_node(self):  #single node for all branch class to use its publish function
        global node
        if node==None:
            node=branch_node()
        return node
    def check_surr(self):

        pass





    def split(self,surrounding):    #surrounding is not a list of tupple having viable paths start coordinates
        if len(self.members)==1:
            print(f"branch with id {self.id} is at its min")
            self.spliting=False
            x=random.choice(i for i in surrounding )
            new_branch=branch(members=self.members,leader=self.leader,spliting=False,path=[x],id=self.id)   #again the same branch is published with splitting False
            dict_branches[new_branch.id]=new_branch
            del dict_branches[self.id]
        else:
            frontier=surrounding.copy()  #list of viable paths
            new_branch_leader=self.check_leader(self.members)    #will return the bot object which will be the new leader of new branch
            n=len(self.members)//2   #number of members in the original
            self.members.remove(new_branch_leader)
            # new1=branch(members=self.members[:n],leader=self.leader)
            # new2=branch(members=self.members[n:],leader=new_branch_leader)
            
            if len(frontier)==3:
                
                x=random.choice(i for i in frontier)   #take a frontier, x is of form (a,b)
                # surrounding[x]=0  #means its not a frontier anymore
                # new1.pub(x)
                # new1.path.append(x)
                new1=branch(members=self.members[:n],leader=self.leader,path=[x],prev=self.id)    #this will publish the branch with init coord as x
                frontier.remove(x)
                # branch_node.publish_branch_info(new1)
                dict_branches[new1.id]=new1
                new2.split(surrounding)
                del dict_branches[self.id]
            else:
                x=random.choice(frontier) 
                # new1.pub(x)
                new1=branch(members=self.members[:n],leader=self.leader,path=[x],prev=self.id)
                branches.append(new1.id)
                # new1.path.append(x)
                # surrounding[x]=0  #means its not a frontier anymore
                frontier.remove(x)
                # new2.pub(frontier[0])
                # new2.path.append(frontier[0])
                new2=branch(members=self.members[n:],leader=new_branch_leader,path=[frontier[0]],id=self.id,prev=self.prev)
                frontier.remove(frontier[0])
                del dict_branches[self.id]
                dict_branches[new1.id]=new1
                dict_branches[new2.id]=new2
                # branch_node.publish_branch_info(new1)
                # branch_node.publish_branch_info(new2)

    def update_path(self,path):
        # branch_id=msg.id
        # branch=dict_branches[branch_id]
        self.path.append(path)

    def update_branch(self,members_added):
        self.members.extend(members_added)
        for i in members_added:
            i.follower()
            i.follow_leader=self.leader
    def change_leader(self,members):
        x=members[0].priority
        new_leader=members[0]
        for i in members:
            if i.priority<x:
                x=i.priority
                new_leader=i    
        return(new_leader)
            
            
    def returning(self):
        #Logic 1: make all the members retrace the path in reverse order to reach the previous leader
        self.retracing=True
        target_coord=self.path[0]
        self.leader.is_returning()
        for i in self.members:
            i.is_returning()
        new_path=self.path[::-1]   #reverse path
        #make them follow the path in reverse
        #call the path finding algo.

        idx=branches.index(self.prev)  #get the index of previous branch in branches list
        while idx>=0:
            if idx in dict_branches:
                prev=dict_branches[idx]   #getting the branch object of previous leader
                break
            idx-=1
        #now use this prev to find the previous father branch
        #now go and merge with this branch
        #----------------------------------------------------------------
        #after gettinng to this point, go to the previous leader and make it a part of that branch
        #so for this we will use the path of the previous leader. Since whenever a split is formed, then the path starts getting stored from that point only, so we just need to start from begining of previous leader path
        
        
        b2=dict_branches[self.prev]   #previous leader branch
        path_follow=b2.path
        #make them follow this path
        #once they get there, make them part of that branch
        b2.update_branch(self.members)
        #delete this branch from dict_branches
        
        #logic 2: Use path finding algorithm to reach the previous leader
        #this is better becz in previous logic, the returning group will keep on following the path but will not reach as that branch is also moving forward


        #logic 3: go to the nearest frontier and then independently keep the exploration going on from that point without making or destroying any branch
        
        del dict_branches[self.id]


    def merge(self,branch_to_merge_into):
        #merge self into branch_to_merge_into
        self.members.append(self.leader)
        branch_to_merge_into.update_branch(self.members)
        del dict_branches[self.id]
    def pub(self,init_coord):    #takes the start coord for the branch and publish data to exploration package
        pass
    




def main(args=None):
    rclpy.init(args=args)
    
    bot1=bot((0,0),1)
    bot2=bot((0,0),2)
    bot3=bot((0,0),3)
    bot4=bot((0,0),4)
    branch1=branch(leader=bot1,members=[bot2])
    branch2=branch(leader=bot3,members=[bot4])
    print(branch1.id,branch2.id)

    # rclpy.spin(node)   
    rclpy.shutdown()