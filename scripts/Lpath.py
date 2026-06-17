#!/usr/bin/env python3

import rospy
import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion


class LPathController:

    def __init__(self):

        rospy.init_node('l_path_controller')

        self.pub = rospy.Publisher('/rover/cmd_vel', Twist, queue_size=10)

        rospy.Subscriber('/rover/odom', Odometry, self.odom_callback)

        self.rate = rospy.Rate(60)

        self.current_yaw = 0.0

        rospy.sleep(2)

    # ==================================================
    # ODOM CALLBACK
    # ==================================================

    def odom_callback(self, msg):

        q = msg.pose.pose.orientation
        quat = [q.x, q.y, q.z, q.w]

        (_, _, yaw) = euler_from_quaternion(quat)

        self.current_yaw = yaw

    # ==================================================
    # STOP ROBOT
    # ==================================================

    def stop_robot(self):

        self.pub.publish(Twist())
        rospy.sleep(0.5)

    # ==================================================
    # NORMALIZE ANGLE
    # ==================================================

    def normalize_angle(self, angle):

        while angle > math.pi:
            angle -= 2 * math.pi

        while angle < -math.pi:
            angle += 2 * math.pi

        return angle

    # ==================================================
    # MOVE FORWARD
    # ==================================================

    def move_forward(self, speed, distance):

        vel = Twist()
        vel.linear.x = speed

        duration = distance / speed
        start = rospy.Time.now().to_sec()

        while (rospy.Time.now().to_sec() - start) < duration:

            self.pub.publish(vel)
            self.rate.sleep()

        self.stop_robot()

    # ==================================================
    # STABLE 90° TURN (FINAL ROBUST METHOD)
    # ==================================================

    def turn_left_90(self):

        vel = Twist()

        target = math.pi / 2
        initial_yaw = self.current_yaw

        rospy.loginfo("Executing Stable 90° Turn")

        while not rospy.is_shutdown():

            # how much we've actually turned
            current = abs(self.normalize_angle(self.current_yaw - initial_yaw))

            error = target - current

            # STOP CONDITION (tight accuracy)
            if error <= 0.01:
                break

            # proportional control
            speed = 3.5 * error

            # safety limits
            if speed > 1.5:
                speed = 1.5
            if speed < 0.25:
                speed = 0.25

            # slow down near target (critical for stability)
            if error < 0.25:
                speed = min(speed, 0.4)

            vel.angular.z = speed

            self.pub.publish(vel)
            self.rate.sleep()

        self.stop_robot()

    # ==================================================
    # MAIN EXECUTION
    # ==================================================

    def execute(self):

        rospy.loginfo("Starting L Path")

        # forward long distance
        self.move_forward(0.7, 5.0)

        # stable 90 degree turn
        self.turn_left_90()

        # forward second leg
        self.move_forward(0.7, 4.0)

        rospy.loginfo("L Path Completed Successfully")


if __name__ == '__main__':

    try:
        node = LPathController()
        node.execute()

    except rospy.ROSInterruptException:
        pass
