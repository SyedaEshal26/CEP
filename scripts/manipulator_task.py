#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Range
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import Bool


class ManipulatorTask:

    def __init__(self):

        rospy.init_node("manipulator_task")

        self.pub = rospy.Publisher(
            "/arm_controller/command",
            JointTrajectory,
            queue_size=10
        )

        self.place_pub = rospy.Publisher("/object_placed", Bool, queue_size=10)

        rospy.Subscriber("/manipulator/ultrasonic", Range, self.ultra_cb)

        self.distance = float("inf")
        self.buffer = []
        self.count = 0

        # LOG CONTROL VARIABLES
        self.last_log_time = rospy.Time.now()
        self.last_logged_distance = None

        rospy.loginfo("=" * 50)
        rospy.loginfo("MANIPULATOR READY - STABLE MODE WITH MORE BENDING")
        rospy.loginfo("=" * 50)

    # ---------------- SENSOR ----------------

    def ultra_cb(self, msg):
        self.distance = msg.range

        self.buffer.append(msg.range)
        if len(self.buffer) > 5:
            self.buffer.pop(0)

    def get_distance(self):
        if not self.buffer:
            return self.distance
        return sum(self.buffer) / len(self.buffer)

    # ---------------- ARM CONTROL ----------------

    def move(self, joints, duration=3.5):  # Slower movement for stability

        msg = JointTrajectory()
        msg.header.stamp = rospy.Time.now()

        msg.joint_names = [
            "shoulder_pitch_joint",
            "shoulder_roll_joint",
            "elbow_joint",
            "wrist_joint",
            "gripper_joint"
        ]

        point = JointTrajectoryPoint()
        point.positions = joints
        point.time_from_start = rospy.Duration(duration)  # Slower = more stable

        msg.points.append(point)

        self.pub.publish(msg)

    # ---------------- INCREASED BENDING POSES (More bend, stable) ----------------

    def forward_bend(self):
        # INCREASED BENDING: elbow 1.8 rad (103°), wrist 1.2 rad (69°)
        # [shoulder_pitch, shoulder_roll, elbow, wrist, gripper]
        return [0.15, 0.0, 1.8, 1.2, 0.5]  # More bending than before

    def release_pose(self):
        # Release with same increased bend
        return [0.15, 0.0, 1.8, 1.2, 0.8]

    def home_pose(self):
        # Home position - straight up
        return [0.0, 0.0, 0.0, 0.0, 0.5]

    # Alternative: Maximum safe bend
    def max_bend(self):
        return [0.18, 0.0, 2.0, 1.4, 0.5]

    def max_release(self):
        return [0.18, 0.0, 2.0, 1.4, 0.8]

    # Deeper bend for lower objects
    def deep_bend(self):
        return [0.2, 0.0, 2.2, 1.5, 0.5]

    def deep_release(self):
        return [0.2, 0.0, 2.2, 1.5, 0.8]

    # ---------------- PLACE ----------------

    def place(self):

        rospy.loginfo("=" * 40)
        rospy.loginfo("🤖 BENDING FORWARD (INCREASED BEND MODE)")
        rospy.loginfo("=" * 40)
        self.move(self.forward_bend(), 4.0)  # Slower movement
        rospy.sleep(4)

        rospy.loginfo("🤖 RELEASING OBJECT")
        self.move(self.release_pose(), 2.5)
        rospy.sleep(2.5)

        rospy.loginfo("🤖 RETURNING HOME")
        self.move(self.home_pose(), 2.8)
        rospy.sleep(2.8)

        self.place_pub.publish(True)

        rospy.loginfo("✅ OBJECT PLACED SIGNAL SENT")

    # ---------------- MAIN LOOP ----------------

    def run(self):

        rate = rospy.Rate(10)

        cooldown = False
        cooldown_start = rospy.Time.now()
        
        waiting = False
        wait_start = rospy.Time.now()

        while not rospy.is_shutdown() and self.count < 5:

            dist = self.get_distance()

            # LOG ONLY EVERY 2 SECONDS
            now = rospy.Time.now()
            if (now - self.last_log_time).to_sec() > 2.0:
                rospy.loginfo(f"📡 Distance: {dist:.2f}m")
                self.last_log_time = now

            if cooldown:
                if (rospy.Time.now() - cooldown_start).to_sec() < 50:
                    rate.sleep()
                    continue
                else:
                    cooldown = False
                    rospy.loginfo("✅ READY AGAIN")

            if dist < 0.85:
                if not waiting:
                    rospy.loginfo("🎯 OBJECT DETECTED! Waiting 5 seconds before placing...")
                    waiting = True
                    wait_start = rospy.Time.now()
                else:
                    elapsed = (rospy.Time.now() - wait_start).to_sec()
                    if elapsed >= 5.0:
                        rospy.loginfo("✅ 5 SECONDS COMPLETED - PLACING OBJECT")
                        self.place()
                        self.count += 1
                        rospy.loginfo(f"📊 COMPLETED: {self.count}/5")
                        cooldown = True
                        cooldown_start = rospy.Time.now()
                        waiting = False
                    else:
                        remaining = 5.0 - elapsed
                        if int(remaining) != int(remaining + 0.1):
                            rospy.loginfo(f"⏳ Waiting... {remaining:.1f} seconds remaining")
            else:
                if waiting:
                    rospy.loginfo("❌ OBJECT MOVED AWAY. Waiting reset.")
                    waiting = False

            rate.sleep()


if __name__ == "__main__":
    try:
        node = ManipulatorTask()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Manipulator node terminated.")
