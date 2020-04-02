#! /usr/bin/env python

import rospy                               
from geometry_msgs.msg import Twist           
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

# Check if robot has escaped
def is_escaped(ranges):
    global escaped
    if ranges[0] > 30 and ranges[719] > 30 and ranges[360] > 30:
        escaped = True
    else:
        escaped = False

# Check if close to wall and determine to turn left or right
def scan_callback(laser):
    global turning
    global ref_yaw
    global turn_sign
    if not turning:
        is_escaped(laser.ranges)
        if laser.ranges[360] < 0.5:
            turning = True
            if laser.ranges[0] > 3:
                ref_yaw -= 1.5708
                turn_sign = -1
            else:
                ref_yaw += 1.5708
                turn_sign = 1

# Check if turn completed    
def odom_callback(odom):
    global turning
    if turning:
        eul = euler_from_quaternion([odom.pose.pose.orientation.x, odom.pose.pose.orientation.y, odom.pose.pose.orientation.z, odom.pose.pose.orientation.w])
        if abs(eul[2]-ref_yaw) < 1e-2:
            turning = False

# Initiate node, velocity publisher, laser subscriber and odometry subscriber
rospy.init_node('escape')        
pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
sub_laser = rospy.Subscriber('kobuki/laser/scan', LaserScan, scan_callback)    
sub_odom = rospy.Subscriber('/odom', Odometry, odom_callback)

# Initiate global variables
escaped = False
turning = False
turnsign = 0
ref_yaw = 0
rate = rospy.Rate(10)
vel = Twist()  

# Publish
while not rospy.is_shutdown():
    if escaped:
        vel.linear.x = 0
        vel.angular.z = 0
    elif turning:
        vel.linear.x = 0
        vel.angular.z = 0.2*turn_sign
    else:
        vel.linear.x = 0.5
        vel.angular.z = 0
    pub.publish(vel)
    rate.sleep()