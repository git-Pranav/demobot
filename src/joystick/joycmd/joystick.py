#!/usr/bin/env python

"""
This is meant to work with the xbox 360 controller
"""

import rospy
import pygame
from std_msgs.msg    import Int8
from std_msgs.msg    import Int16MultiArray

class remote_control:
    def __init__(self):

        pygame.init()
        # Initialize the joystick
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.motor_msg = Int16MultiArray()
        self.motor_msg.data = [0,0,0]
        self.motor_pub = rospy.Publisher('joystick_msg', Int16MultiArray, queue_size = 5)

        self.led_msg = Int8()
        self.led_msg.data = 1
        self.light_pub = rospy.Publisher('toggle_led', Int8, queue_size = 2)

        self.light_toggle = 1 #This corresponds to the A button on xbox controller
        self.light_pattern = 2 #This corresponds to the A button on xbox controller

        self.trigger = False

        self.verticle = 0.0
        self.horizontal = 0.0

    def publish_pwm(self, FB_axis, LR_axis):
        leftPWM = int(255*(FB_axis+LR_axis))
        rightPWM = int(255*(FB_axis-LR_axis))

        if (leftPWM > 255):
            leftPWM = 255

        if (rightPWM > 255):
            rightPWM = 255

        if (leftPWM < -255):
            leftPWM = -255

        if (rightPWM < -255):
            rightPWM = -255

        #To revert add all these three statements back
        #self.motor_msg.data = [leftPWM, -rightPWM]
        #self.motor_pub.publish(self.motor_msg)
        #print str(leftPWM) + " " + str(rightPWM)

        #To revert delete from here to...
        temp_FB = 0
        temp_LR = 0
        if (FB_axis > 1):
            temp_FB = 1
        elif(FB_axis < -1):
            temp_FB = -1
        else:
            temp_FB = FB_axis
        

        if (LR_axis > 1):
            temp_LR = 1
        elif(LR_axis < -1):
            temp_LR = -1
        else:
            temp_LR = LR_axis
        

        self.motor_msg.data = [int(temp_FB*255), int(temp_LR*255), 0]
        self.motor_pub.publish(self.motor_msg)
        
        #print str(FB_axis) + " " + str(LR_axis)
        #Here

    def Main(self):
        rospy.init_node('remote_control')

        r = rospy.Rate(20)
        while not rospy.is_shutdown():
            for event in pygame.event.get():

                #Button events get priority over joystick axis
                if event.type == pygame.JOYBUTTONDOWN:
                    #button 0 corresponds to the A button on xbox controller
                    if(self.controller.get_button(0)): 
                        if (self.light_toggle == 1):
                            self.led_msg.data = 0
                            self.light_pub.publish(self.led_msg)
                            self.light_toggle = 0
                        else:
                            self.led_msg.data = 1
                            self.light_pub.publish(self.led_msg)
                            self.light_toggle = 1
                    #button 1 corresponds to the B button on xbox controller
                    if(self.controller.get_button(1)):
                        self.light_pattern = self.light_pattern + 1
                        if(self.light_pattern > 7):
                            self.light_pattern = 2
                        self.led_msg.data = self.light_pattern
                        self.light_pub.publish(self.led_msg)

                    #button 2 corresponds to the X button on xbox controller
                    if(self.controller.get_button(2)):
                        self.motor_msg.data = [0, 0, 0]
                        self.motor_pub.publish(self.motor_msg)

                    #button 3 corresponds to the Y button on xbox controller
                    if(self.controller.get_button(3)):
                        self.motor_msg.data = [0, 0, 1]
                        self.motor_pub.publish(self.motor_msg)
                    #Make sure to not pass through here if button pressed
                    continue

                # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                if event.type == pygame.JOYAXISMOTION:
                    if (self.controller.get_axis(2) > 0.88):
                        #print str(self.controller.get_axis(1)) + " " + str(self.controller.get_axis(3))
                        self.trigger = True
                        """
                        These statements are meant to eliminate the drift from the xbox controller.
                        Axis 1 drifts from 0.0-0.09: hence the 0.1 check
                        Axis 1 cannot reach a full 1.0 or -1.0 when axis pushed to max: hence 1.07 multiplier
                        Axis 1 is inverted. Up is -1, 1 is down. Used negative sign to invert it.
                        Axis 3 drifts from 0.0-0.15, also sticks if just flicked to 0.17: hence 0.18 check
                        """
                        if ((self.controller.get_axis(1) > 0.1) or (self.controller.get_axis(1) < -0.1)):

                            if ((self.controller.get_axis(3) > 0.18) or (self.controller.get_axis(3) < -0.18)):
                                #self.publish_pwm(-(self.controller.get_axis(1)*1.07), -self.controller.get_axis(3))
                                self.verticle = -(self.controller.get_axis(1)*1.07)
                                self.horizontal = -self.controller.get_axis(3)
                            else:
                                #self.publish_pwm(-(self.controller.get_axis(1)*1.07), 0.0)
                                self.verticle = -(self.controller.get_axis(1)*1.07)
                                self.horizontal = 0.0

                        elif((self.controller.get_axis(3) > 0.18) or (self.controller.get_axis(3) < -0.18)):
                            #self.publish_pwm(0.0, -self.controller.get_axis(3))
                            self.verticle = 0.0
                            self.horizontal = -self.controller.get_axis(3)

                        else:
                            #self.publish_pwm(0.0, 0.0)
                            self.verticle = 0.0
                            self.horizontal = 0.0
                    
                    #The trigger cant be relied on for catching events on pressing/depressing

                    #This else statement ensures that any axis event happens after trigger stops, we send motors we stop 
                    #sending on the next axis event. Which is sure to happen, because the joystick retracts to center
                    else:
                        if (self.trigger == True):
                            self.trigger = False
                            self.verticle = 0.0
                            self.horizontal = 0.0
                            self.motor_msg.data = [0, 0, 0]
                            self.motor_pub.publish(self.motor_msg)

            #Need an system which requires the controller to always keep publishing while  trigger is held down.
            if(self.trigger == True):
                self.publish_pwm(self.verticle, self.horizontal)
            r.sleep()

if __name__ == '__main__':
    joystick = remote_control()
    joystick.Main()

