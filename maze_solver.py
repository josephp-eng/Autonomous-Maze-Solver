# Robot Operating System 2 (Jazzy) Maze Solving Script
# Developed by Joey & Raymond for Robot Operating Systems class
# Given a known 5x5 maze grid and starting position, compute a route with our A*-inspired
# pathfinder (SampleLogic/A_Star.py) and drive a hardcoded path with obstacle avoidance
# Completed 12/05/25
# The original version of this file is kept in Archive/maze_solver_original.py.

#!/usr/bin/env python3

import math
import os
import sys
import threading

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu, LaserScan

# Pathfinding lives in A_Star.py so it can also be run on its own without ROS
try:
    # installed as part of the ROS 2 package (A_Star.py copied next to this file)
    from .A_Star import maze, path, path_to_cardinals, turningPath
except ImportError:
    # run directly from this repository, where A_Star.py lives in SampleLogic/
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SampleLogic'))
    from A_Star import maze, path, path_to_cardinals, turningPath


# Tuning values
TURN_SPEED = 0.25           # rad/s while turning in place
TURN_TOLERANCE_DEG = 1.0    # how close to the target heading counts as done
DRIVE_SPEED = 0.1           # m/s while driving forward
STEER_SPEED = 0.1           # rad/s correction when drifting toward a side wall
CELL_LENGTH = 0.42          # m travelled per maze cell
WALL_THRESHOLD = 0.25       # m; stop (front) or steer away (sides) when a wall is closer than this
SIDE_BEAM = 30              # LiDAR beam (degrees off center) used to watch the side walls


def quaternion_to_euler(x, y, z, w):
    """
    Convert a quaternion (x, y, z, w) to Euler angles (roll, pitch, yaw) in degrees.
    Assumes ZYX (yaw-pitch-roll) convention.
    """

    # Roll (x-axis rotation)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)

    # Pitch (y-axis rotation)
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    # Yaw (z-axis rotation)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)

    # radians to degrees
    roll = roll * 180 / math.pi
    pitch = pitch * 180 / math.pi
    yaw = yaw * 180 / math.pi

    return roll, pitch, yaw


class MazeProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.scan = None
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        # latches clear once the first IMU / LiDAR message arrives
        self.imuLatch = True
        self.lidarLatch = True

        # define new policy to use "best effort" quality for laser scans
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        # create subscriber with "best effort" setting to match turtlebot
        self.publisher_ = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.subscription_ = self.create_subscription(Imu, 'imu', self.imu_callback, 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.range_callback,
            qos_profile)

    # sensor callbacks

    def imu_callback(self, msg):
        q = msg.orientation
        self.roll, self.pitch, self.yaw = quaternion_to_euler(q.x, q.y, q.z, q.w)
        self.imuLatch = False

    def range_callback(self, scan, msg_info):
        # rclpy passes the message's MessageInfo as a second argument when the callback takes one (unused here)
        self.scan = scan
        self.lidarLatch = False

    # motion functions

    def publish_twist(self, linear=0.0, angular=0.0):
        # build and send a velocity command; the TurtleBot only uses linear.x and angular.z
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.twist.linear.x = float(linear)
        msg.twist.angular.z = float(angular)
        self.publisher_.publish(msg)

    def stop(self):
        # print("stop")
        self.publish_twist(0.0, 0.0)

    def turn(self, delta_deg):
        # rotate in place by delta_deg (positive = left / counterclockwise) using the IMU yaw
        desired_heading = self.yaw + delta_deg
        if (desired_heading>180):
            desired_heading = desired_heading - 360
        elif (desired_heading<-180):
            desired_heading = desired_heading + 360
        angular = TURN_SPEED if delta_deg > 0 else -TURN_SPEED
        while not((self.yaw < desired_heading + TURN_TOLERANCE_DEG) and (self.yaw > desired_heading - TURN_TOLERANCE_DEG)):
            # print(desired_heading)
            # print(self.yaw)
            self.publish_twist(0.0, angular)
        self.stop()

    def leftTurn(self):
        # print("left")
        self.turn(90)

    def rightTurn(self):
        # print("right")
        self.turn(-90)

    def forward(self, n):
        # drive forward n cells, measuring distance travelled with the LiDAR beam pointing at the wall ahead
        # print("forward")
        while (math.isnan(self.scan.ranges[0])):
            pass    # wait for a valid front reading
        current = self.scan.ranges[0]
        check = current
        while(current-CELL_LENGTH*n<check):
            ranges = self.scan.ranges
            if not(math.isnan(ranges[0])):
                check = ranges[0]
                # obstacle avoidance: steer away from a side wall that gets too close,
                # keeping the robot centered between the walls
                if ranges[SIDE_BEAM] < WALL_THRESHOLD:
                    angular = -STEER_SPEED      # too close on the left, steer right
                elif ranges[-SIDE_BEAM] < WALL_THRESHOLD:
                    angular = STEER_SPEED       # too close on the right, steer left
                else:
                    angular = 0.0
                if (ranges[0] < WALL_THRESHOLD):
                    break   # wall ahead is too close, stop early
                self.publish_twist(DRIVE_SPEED, angular)
        self.stop()


def spin_in_background(node):
    # keep processing sensor callbacks until rclpy is shut down
    try:
        rclpy.spin(node)
    except ExternalShutdownException:
        pass


def main(args=None):
    rclpy.init(args=args)
    lidar_node = MazeProcessor()

    # rclpy.spin() blocks forever, so run it in a background thread while the motion
    # functions below run here; daemon=True lets the program exit when main() finishes
    spin_thread = threading.Thread(target=spin_in_background, args=(lidar_node,), daemon=True)
    spin_thread.start()

    # compute a route with the pathfinder (printed for reference; not used to drive yet)
    start = int(input("What square are you starting in: "))
    end = int(input("What square are you ending in: "))
    output_Path = path(start, end, maze)
    turnPath = turningPath(path_to_cardinals(output_Path), output_Path)
    print("Computed path: " + str(output_Path))
    print("Turn instructions: " + str(turnPath))

    # wait for the first IMU and LiDAR messages
    while(lidar_node.imuLatch or lidar_node.lidarLatch):
        pass

    # Hard coded directions
    # After running A* script separately, pass best directions as instructions
    # Due to lack of time, this function had to be handled external to the maze solve
    lidar_node.forward(3)
    lidar_node.rightTurn()
    lidar_node.forward(4)
    lidar_node.rightTurn()
    lidar_node.forward(2)
    lidar_node.rightTurn()
    lidar_node.forward(1)
    lidar_node.leftTurn()
    lidar_node.forward(1)
    lidar_node.leftTurn()
    lidar_node.forward(2)

    rclpy.shutdown()
    spin_thread.join(timeout=1.0)
    lidar_node.destroy_node()

if __name__ == '__main__':
    main()
