from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
     return LaunchDescription([
        Node(
            package='swarm_logic',
            executable='task_gui_node',
            name='task_gui'
        ),
        Node(
            package='swarm_logic',
            executable='task_allocation_node',
            name='task_allocation'
        ),
        Node(
            package='mapping',
            executable='generate',
            name='map_generation'
        ),
        Node(
            package='mapping',
            executable='explore',
            name='exploring'
        )
        
     ])

