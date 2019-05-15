#!/usr/bin/env python
"""
   twist_to_motors - converts a twist message to motor commands.  Needed for navigation stack
   
   
    Copyright (C) 2012 Jon Stephan. 
     
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import rospy
import roslib
from std_msgs.msg import UInt8
from geometry_msgs.msg import Twist
from beobot_diff.msg import Adc, Motor




def rf_map(value, frommin, frommax, tomin, tomax):
	if(value < frommin):
		value = frommin
	if(value > frommax):
		value = frommax
	return (((value-frommin)*(tomax-tomin))/(frommax-frommin)) + tomin
#############################################################
#############################################################
class TwistToMotors():
#############################################################
#############################################################

    #############################################################
    def __init__(self):
    #############################################################
        rospy.init_node("twist_to_motors")
        nodename = rospy.get_name()
        rospy.loginfo("%s started" % nodename)
    
        self.w = rospy.get_param("~base_width", 70)
    
        self.pub_motor = rospy.Publisher('cmd_motor', Motor, queue_size=10)
        rospy.Subscriber('rf', Adc, self.rfCallback)
    
    
        self.rate = rospy.get_param("~rate", 17)
        self.timeout_ticks = rospy.get_param("~timeout_ticks", 2)
        self.left = 0
        self.right = 0
        
    #############################################################
    def spin(self):
    #############################################################
    
        r = rospy.Rate(self.rate)
        idle = rospy.Rate(10)
        then = rospy.Time.now()
        self.ticks_since_target = self.timeout_ticks
    
        ###### main loop  ######
        while not rospy.is_shutdown():
        
            while not rospy.is_shutdown() and self.ticks_since_target < self.timeout_ticks:
                self.spinOnce()
                r.sleep()
            idle.sleep()
                
    #############################################################
    def spinOnce(self):
    #############################################################
    
        # dx = (l + r) / 2
        # dr = (r - l) / w
           
        self.right = 100 * self.dx + self.dr * self.w / 2 
        self.left = 100 * self.dx - self.dr * self.w / 2
	
	if (self.left < 0):
		self.left = 0
	if (self.right < 0):
		self.right = 0        
	# rospy.loginfo("publishing: (%d, %d)", left, right) 
        
	msg = Motor()
	msg.a = self.left
	msg.b = self.right       
        self.pub_motor.publish(msg)
        self.ticks_since_target += 1 

    #############################################################
    def rfCallback(self,msg):
    #############################################################
        # rospy.loginfo("-D- twistCallback: %s" % str(msg))
        self.ticks_since_target = 0
        #self.dx = msg.linear.x
        #self.dr = msg.angular.z
        #self.dy = msg.linear.y
        self.dx = rf_map(msg.adc0, 1000.0, 2000.0, 0.0, 1.0)
        self.dr = rf_map(msg.adc1, 1000.0, 2000.0, -1.0, 1.0)
        self.dy = 0    
#############################################################
#############################################################
if __name__ == '__main__':
    """ main """
    try:
        twistToMotors = TwistToMotors()
        twistToMotors.spin()
    except rospy.ROSInterruptException:
        pass
