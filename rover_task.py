#!/usr/bin/env python3

import rospy
import math

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, Range
from std_msgs.msg import Bool, Int32


class RoverTask:

    def __init__(self):

        rospy.init_node("rover_task")

        # =================================================
        # PUBLISHERS
        # =================================================

        self.cmd_pub = rospy.Publisher(
            "/rover/cmd_vel",
            Twist,
            queue_size=10
        )

        self.done_pub = rospy.Publisher(
            "/object_done",
            Int32,
            queue_size=10
        )

        # =================================================
        # SUBSCRIBERS
        # =================================================

        rospy.Subscriber(
            "/rover/odom",
            Odometry,
            self.odom_cb
        )

        rospy.Subscriber(
            "/rover/imu",
            Imu,
            self.imu_cb
        )

        rospy.Subscriber(
            "/rover/ultrasonic",
            Range,
            self.ultra_cb
        )

        rospy.Subscriber(
            "/object_placed",
            Bool,
            self.obj_cb
        )

        # =================================================
        # ROBOT STATE
        # =================================================

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.obs = 999

        self.object_ready = False

        # =================================================
        # TASK STATE
        # =================================================

        self.state = "WAIT"

        self.square_count = 0

        self.point_index = 0

        self.waypoints = []

        # =================================================
        # LOOP RATE
        # =================================================

        self.rate = rospy.Rate(40)

        rospy.loginfo("FAST + STABLE ROVER TASK STARTED")

    # =====================================================
    # CALLBACKS
    # =====================================================

    def odom_cb(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def imu_cb(self, msg):

        q = msg.orientation

        siny = 2 * (q.w * q.z + q.x * q.y)
        cosy = 1 - 2 * (q.y * q.y + q.z * q.z)

        self.yaw = math.atan2(siny, cosy)

    def ultra_cb(self, msg):

        self.obs = msg.range

    def obj_cb(self, msg):

        self.object_ready = msg.data

    # =====================================================
    # HELPERS
    # =====================================================

    def norm(self, angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    def stop(self):

        self.cmd_pub.publish(Twist())

    # =====================================================
    # FAST + CONSISTENT MOTION
    # =====================================================

    def move_to_point(self, gx, gy):

        dx = gx - self.x
        dy = gy - self.y

        dist = math.sqrt(dx * dx + dy * dy)

        target_yaw = math.atan2(dy, dx)

        yaw_error = self.norm(target_yaw - self.yaw)

        cmd = Twist()

        # =================================================
        # LARGE TURN REGION
        # SAME TURN SPEED EVERY TIME
        # =================================================

        if abs(yaw_error) > 0.45:

            cmd.linear.x = 0.02

            if yaw_error > 0:
                cmd.angular.z = 2.2
            else:
                cmd.angular.z = -2.2

        # =================================================
        # MEDIUM CORRECTION REGION
        # =================================================

        elif abs(yaw_error) > 0.12:

            cmd.linear.x = 0.22

            cmd.angular.z = 2.0 * yaw_error

        # =================================================
        # STRAIGHT FAST REGION
        # =================================================

        else:

            # Faster when far
            if dist > 1.0:

                cmd.linear.x = 0.60

            # Medium distance
            elif dist > 0.4:

                cmd.linear.x = 0.38

            # Slow near target
            else:

                cmd.linear.x = 0.18

            # Tiny correction
            cmd.angular.z = 0.8 * yaw_error

        # =================================================
        # OBSTACLE STOP
        # =================================================

        if self.obs < 0.5:

            rospy.logwarn("OBSTACLE DETECTED")

            self.stop()

        else:

            self.cmd_pub.publish(cmd)

        # =================================================
        # TARGET REACHED
        # =================================================

        return dist < 0.08

    # =====================================================
    # MAIN LOOP
    # =====================================================

    def run(self):

        while not rospy.is_shutdown():

            # =================================================
            # WAIT FOR OBJECT
            # =================================================

            if self.state == "WAIT":

                self.stop()

                if self.object_ready and self.square_count < 5:

                    self.object_ready = False

                    x0 = self.x
                    y0 = self.y

                    # Square path
                    self.waypoints = [

                        (x0 + 4.0, y0),

                        (x0 + 4.0, y0 + 4.0),

                        (x0, y0 + 4.0),

                        (x0, y0)

                    ]

                    self.point_index = 0

                    rospy.loginfo(
                        f"STARTING SQUARE {self.square_count + 1}"
                    )

                    self.state = "MOVE"

            # =================================================
            # MOVE THROUGH WAYPOINTS
            # =================================================

            elif self.state == "MOVE":

                gx, gy = self.waypoints[self.point_index]

                reached = self.move_to_point(gx, gy)

                if reached:

                    self.stop()

                    rospy.sleep(0.15)

                    self.point_index += 1

                    # Square complete
                    if self.point_index >= 4:

                        self.square_count += 1

                        rospy.loginfo(
                            f"SQUARE {self.square_count} COMPLETE"
                        )

                        self.done_pub.publish(
                            self.square_count
                        )

                        self.state = "WAIT"

            self.rate.sleep()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    RoverTask().run()
