# Robot Operating System 2 (Jazzy) Maze Solving Script
# Developed by Joey & Raymond for Robot Operating Systems class
# Given a known 5x5 maze grid and starting position, utilize an A*-lite algorithm and obstacle avoidance for maze solving
# Completed 12/05/25

from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Header
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu, LaserScan
import numpy as np
import time
from copy import deepcopy
import math
import threading


def quaternion_to_euler(x, y, z, w):
    """
    Convert a quaternion (x, y, z, w) to Euler angles (roll, pitch, yaw) in radians.
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

class Directions():
    def __init__(self, N:bool, E:bool, S:bool, W:bool, T:str):
        self.North = N
        self.South = S
        self.West = W
        self.East = E
        self.Tag = T
    def tag_manipulator(self, dir):
        self.Tag = dir

# Maze grid per each cell
# Viable cardinal directions (N, E, S, W) seen by each cell
s0 = Directions(0,0,0,0,'F')
s1 = Directions(0,1,0,0,'F')
s2 = Directions(0,0,1,1,'F')
s3 = Directions(0,1,0,0,'F')
s4 = Directions(0,0,1,1,'F')
s5 = Directions(0,1,1,0,'F')
s6 = Directions(0,1,0,1,'F')
s7 = Directions(1,1,1,1,'F')
s8 = Directions(0,1,0,1,'F')
s9 = Directions(1,0,1,1,'F')
s10 = Directions(1,1,1,0,'F')
s11 = Directions(0,0,1,1,'F')
s12 = Directions(1,0,1,0,'F')
s13 = Directions(0,0,1,0,'F')
s14 = Directions(1,0,1,0,'F')
s15 = Directions(1,0,1,0,'F')
s16 = Directions(1,0,1,0,'F')
s17 = Directions(1,0,1,0,'F')
s18 = Directions(1,1,1,0,'F')
s19 = Directions(1,0,0,1,'F')
s20 = Directions(1,0,0,0,'F')
s21 = Directions(1,1,0,0,'F')
s22 = Directions(1,0,0,1,'F')
s23 = Directions(1,1,0,0,'F')
s24 = Directions(0,0,0,1,'F')
maze = np.array([[s0,s1,s2,s3,s4],[s5,s6,s7,s8,s9],[s10,s11,s12,s13,s14],[s15,s16,s17,s18,s19],[s20,s21,s22,s23,s24]], Directions)

def step_to_cardinal(i: int, j:int) -> str:
        # i = from, j = to
        # direction test for adjacent steps
        if j == i + 1 and (i % 5) < 4:  return 'E'  # same row, one column right = E
        if j == i - 1 and (i % 5) > 0:  return 'W'  # same row, one column left = W
        if j == i + 5 and i <= 19:      return 'S'  # same column, one row down = S
        if j == i - 5 and i >= 5:       return 'N'  # same column, one row up = N 

def path_to_cardinals(path_order: list[int]) -> list[str]:
    # convert path of indices to cardinals
    Dlist = []
    if len(path_order) < 2:
        # need >= 2 cells to move
        return []
    else:
        for cells in list(range(len(path_order))):
            print(list[range(len(path_order)-1)])
            print(cells)
            if cells > 0:
                match(-(path_order[cells-1] - path_order[cells])):
                    case 5:
                        Dlist.append("S")
                        print("Dlist: " + str(Dlist))
                    case 1:
                        Dlist.append("E")
                        print("Dlist: " + str(Dlist))
                    case -1:
                        Dlist.append("W")
                        print("Dlist: " + str(Dlist))
                    case -5:
                        Dlist.append("N")
                        print("Dlist: " + str(Dlist))
    print("Dlist: " + str(Dlist))
    return(Dlist)                    
        
def index(cur:int):
    y = cur-(int(cur/5)*5)
    x = int(cur/5)
    return x,y
def path (start:int, stop:int, hedge):
    latch:bool = 1
    temp_length:int = 0
    length:int = 300
    cur:int = start
    temp_maze = deepcopy(hedge)
    print(maze)
    print(temp_maze)
    saved_maze = []
    branch = []
    temp_branch = np.array([], dtype=object)
    branchID = np.array([[]], int)
    path = np.array([[start]], int)
    temp_path = path
    while (latch):
        if not(cur==stop):
            if temp_maze[index(cur)].North == 1:
                temp_maze[index(cur)].North = 0
                temp_maze[index(cur-5)].South = 0
                print(np.isin(cur+5, temp_path))
                if (temp_maze[index(cur)].East == 1 and ~(np.isin(cur+1, temp_path))):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    branchID = np.append(branchID, len(temp_path)-1)
                elif temp_maze[index(cur)].West == 1 and ~(np.isin(cur-1, temp_path)):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    branchID = np.append(branchID, len(temp_path)-1)
                elif temp_maze[index(cur)].South == 1 and ~(np.isin(cur+5, temp_path)):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    print("appended")
                    branchID = np.append(branchID, len(temp_path)-1)
                cur = cur -5
                temp_path = np.append(temp_path, cur)
                temp_length=temp_length+1
            elif temp_maze[index(cur)].East == 1:
                temp_maze[index(cur)].East = 0
                temp_maze[index(cur+1)].West = 0
                if temp_maze[index(cur)].South == 1 and ~(np.isin(cur+5, temp_path)):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    branchID = np.append(branchID, len(temp_path)-1)
                elif temp_maze[index(cur)].West == 1 and ~(np.isin(cur-1, temp_path)):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    branchID = np.append(branchID, len(temp_path)-1)
                cur = cur +1
                temp_path = np.append(temp_path, cur)
                temp_length=temp_length+1
            elif temp_maze[index(cur)].West == 1:
                temp_maze[index(cur)].West = 0
                temp_maze[index(cur-1)].East = 0
                if (temp_maze[index(cur)].South == 1 and ~(np.isin(cur+5, temp_path))):
                    branch.append(temp_path)
                    saved_maze.append(deepcopy(temp_maze))
                    branchID = np.append(branchID, len(temp_path)-1)
                cur = cur -1
                temp_path = np.append(temp_path, cur)
                temp_length=temp_length+1
            elif temp_maze[index(cur)].South == 1:
                temp_maze[index(cur)].South = 0
                temp_maze[index(cur+5)].North = 0
                cur = cur +5
                temp_path = np.append(temp_path, cur)
                temp_length=temp_length+1
            elif (len(branch)>0):
                temp_maze = np.array(deepcopy(saved_maze[len(saved_maze)-1]))
                print(temp_maze[index(10)].East)
                temp_branch = branch[len(branch)-1]
                temp_path = np.array(temp_branch)
                temp_length = len(temp_path)
                cur=temp_path[len(temp_path)-1]
                branch.pop(len(branch)-1)
                saved_maze.pop(len(saved_maze)-1)
                print(saved_maze)
            else:
                break
            print(cur)
            print("temp_Path")
            print(temp_path)
        if cur == stop and temp_length < length:
            length = temp_length
            path = temp_path
        if cur == stop and len(branch) == 0:
            latch = 0
        elif cur == stop and len(branch) > 0:
            print(branch)
            temp_maze = np.array(deepcopy(saved_maze[len(saved_maze)-1]))
            temp_branch = branch[len(branch)-1]
            print(temp_maze[index(10)])
            temp_path = np.array(temp_branch)
            temp_length = len(temp_path)
            cur=temp_path[len(temp_path)-1]
            branch.pop(len(branch)-1)
            saved_maze.pop(len(saved_maze)-1)
        #time.sleep(1)
    return (path)
def turningPath (pathD, pathI):
    dMap = []
    findMap = []
    dMapCount = -1
    last = 0
    for cells in list(range(len(pathD))):
        if cells > 0:
            if pathD[cells-1] != pathD[cells]:
                count = 1
                print("Turn Direction: " + str(pathD[cells]))
                match(pathD[cells]):
                    case "N":
                        for cell in list(range(last, cells)):
                            
                            if maze[index(pathI[cell])].North == 1:
                                count = count + 1
                        last = cells
                        dMap.append(str("N"+str(count)))
                    case "E":
                        print(list(range(last, cells)))
                        for cell in list(range(last, cells)):
                            print(maze[index(pathI[cell])].East)
                            if maze[index(pathI[cell])].East == 1:
                                count = count + 1
                        last = cells
                        dMap.append(str("E"+str(count)))
                    case "S":
                        for cell in list(range(last, cells)):
                            if maze[index(pathI[cell])].South == 1:
                                count = count + 1
                        last = cells
                        dMap.append(str("S"+str(count)))
                    case "W":
                        for cell in list(range(last, cells)):
                            if maze[index(pathI[cell])].West == 1:
                                count = count + 1
                        last = cells
                        dMap.append(str("W"+str(count)))
    return(dMap)

def avg(array):
    out = 0
    count = 0
    for entry in array:
        if not(math.isnan(entry)):
            out = out + entry
        else:
            count = count + 1
    out = out/(len(array)-count)
    return(out)

def turnCounter (Lidar, range_Center):
    high = .25
    if avg(Lidar[range_Center-25:range_Center+25])>high:
        return(True)
    else:
        return(False)

def straighten(Lidar, wall):
    match(wall):
        case "Forward":
            angle = 0
        case "Right":
            angle = 90
        case "Back":
            angle = 180
        case "Left":
            angle = 270
    difference = avg(Lidar[angle-15:angle-10])-avg(Lidar[angle+10:angle+15])
    if difference > 0.1:
        return([0,0,1])
    elif difference < -0.1:
        return([1,0,0])
    else:
        return(0,1,0)

def parseInstructions(instructions):
    turns = []
    number = []
    for cells in range(len(instructions)):
        turns.append(instructions[cells][0])
        number.append(int(instructions[cells][1]))
    return(turns,number)

class MazeProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.q:object
        self.yaw_deg = None
        self.yaw0_deg = None
        self.pos = (0, 0)
        self.start_pos = None
        self.scan:object
        self.yaw = 0
        self.roll = 0
        self.pitch = 0
        self.imuLatch = True
        self.lidarLatch = True
        
        # initial lidar
        self.left_open_prev   = False
        self.right_open_prev  = False
        self.front_block_prev = False
        self.front_now = float('inf')
        self.left_now  = float('inf')
        self.right_now = float('inf')
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
        self.phase = 'WAIT'
        self.step_i = 0
        
        
        


    WIDTH = 5
    CELLCOUNT = 25

    def wrap_deg(a):
        # [-180, 180)
        return (a+ 180) % 360 - 180
    
    def shortest_deg(a, b):
        return wrap_deg(b - a)

    def id_to_grid(i: int):
        # return row number by integer division and the column number by remainder
        return i // 5, i % 5

    def card(useless, dir):
        match (dir):
            case "N":
                return(0)
            case "E":
                return(90)
            case "S":
                return(180)
            case "W":
                return(270)


    def stop(self, msg):
        print("stop")
        msg.twist.linear.x = 0.0
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = 0.0
        self.publisher_.publish(msg)


    def imu_callback(self, msg):
        self.q = msg.orientation
        self.roll, self.pitch, self.yaw = quaternion_to_euler(self.q.x, self.q.y, self.q.z, self.q.w)
        self.imuLatch = False
    
    def step(self):
        if self.phase == 'DONE':
            return                          # mission finished
        if self.yaw_deg is None:
            return                          # wait for IMU to update
        if self.yaw0_deg is None:
            self.yaw0_deg = self.yaw_deg    # IMU to current orientation
            self.phase = 'TURN'             # begin turn phase

    def range_callback(self, scan, msg):
        self.scan = scan
        self.lidarLatch = False
        
        # Debugging v
        """
        if not self.latch2:
            return()
        print("range")
        orientation = self.q
        roll, pitch, yaw = quaternion_to_euler(orientation.x, orientation.y, orientation.z, orientation.w)
        turn, num = parseInstructions(self.directions)

        if (self.latch == 1):
            print(type(turn[self.count1]))
            print(self.card(str(turn[self.count1][0])))
            self.desired_heading = self.card(turn[self.count1][0])
            if (self.desired_heading>180):
                self.desired_heading = self.desired_heading - 360
            elif (self.desired_heading<-180):
                self.desired_heading = self.desired_heading + 360
            self.latch = 0
        msg = TwistStamped()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        if not self.latch0:
            if turnCounter(scan.ranges, int(self.desired_heading-yaw)) and not (self.latch3):
                self.latch3 = True
                self.count0 = self.count0 + 1
                self.forward(msg)
            elif turnCounter(scan.ranges, int(self.desired_heading-yaw)):
                self.latch3 = False
                self.forward(msg)
        if int(parseInstructions(self.directions)[1][self.count1]) == self.count0:
            self.latch0 = True
            if (yaw < self.desired_heading + 0.5) and (yaw > self.desired_heading - 0.5):
                self.count1 = self.count1 + 1
                self.count0 = 0
                self.latch0 = False
                self.latch3 = True
                if self.count0 == len(self.directions)-1:
                    self.stop(msg)
                    rclpy.shutdown()
            else:
                print("turning")
                self.leftTurn(msg)
        print("threshold: "+str(parseInstructions(self.directions)[1][self.count1]))
        print("count0: "+ str(self.count0))
        print("heading: "+ str(self.desired_heading))
        print("current heading: "+ str(yaw))
        print("can turn? "+str(turnCounter(scan.ranges, int(self.desired_heading-yaw))))
        print(self.latch3)
        """
rclpy.init(args=None)
lidar_node = MazeProcessor()  

def SPIIIIIIIIIIIIN(lidar_node):
    while(True):    
        rclpy.spin(lidar_node)

# motion functions
def leftTurn(msg):
    print("left")
    desired_heading = 90 + lidar_node.yaw
    if (desired_heading>180):
        desired_heading = desired_heading - 360
    elif (desired_heading<-180):
        desired_heading = desired_heading + 360
    while not((lidar_node.yaw < desired_heading + .5) and (lidar_node.yaw > desired_heading - .5)):
        msg.twist.linear.x = 0.0
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = 0.25
        lidar_node.publisher_.publish(msg)
    msg.twist.linear.x = 0.0
    msg.twist.linear.y = 0.0
    msg.twist.linear.z = 0.0
    msg.twist.angular.x = 0.0
    msg.twist.angular.y = 0.0
    msg.twist.angular.z = 0.0
    lidar_node.publisher_.publish(msg)

def rightTurn(msg):
    print("right")
    desired_heading = -90 + lidar_node.yaw
    if (desired_heading>180):
        desired_heading = desired_heading - 360
    elif (desired_heading<-180):
        desired_heading = desired_heading + 360
    while not((lidar_node.yaw < desired_heading + 1) and (lidar_node.yaw > desired_heading - 1)):
        msg.twist.linear.x = 0.0
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = -0.25
        print(desired_heading)
        print(lidar_node.yaw)
        lidar_node.publisher_.publish(msg)
    msg.twist.linear.x = 0.0
    msg.twist.linear.y = 0.0
    msg.twist.linear.z = 0.0
    msg.twist.angular.x = 0.0
    msg.twist.angular.y = 0.0
    msg.twist.angular.z = 0.0
    lidar_node.publisher_.publish(msg)

def forward(msg,n):
    print("forward")
    while (math.isnan(lidar_node.scan.ranges[0])):
        check = 0
    current = lidar_node.scan.ranges[0]
    count = 1
    check = current
    while(current-0.42*n<check):
        if not(math.isnan(lidar_node.scan.ranges[0])):
            check = lidar_node.scan.ranges[0]
            if lidar_node.scan.ranges[30] < 0.25:
                msg.twist.linear.x = 0.1
                msg.twist.linear.y = 0.0
                msg.twist.linear.z = 0.0
                msg.twist.angular.x = 0.0
                msg.twist.angular.y = 0.0
                msg.twist.angular.z = -0.1
            elif lidar_node.scan.ranges[-30] < 0.25:
                msg.twist.linear.x = 0.1
                msg.twist.linear.y = 0.0
                msg.twist.linear.z = 0.0
                msg.twist.angular.x = 0.0
                msg.twist.angular.y = 0.0
                msg.twist.angular.z = 0.1
            else:
                msg.twist.linear.x = 0.1
                msg.twist.linear.y = 0.0
                msg.twist.linear.z = 0.0
                msg.twist.angular.x = 0.0
                msg.twist.angular.y = 0.0
                msg.twist.angular.z = 0.0
            if (lidar_node.scan.ranges[0] < .25):
                break

        lidar_node.publisher_.publish(msg)
    msg.twist.linear.x = 0.0
    msg.twist.linear.y = 0.0
    msg.twist.linear.z = 0.0
    msg.twist.angular.x = 0.0
    msg.twist.angular.y = 0.0
    msg.twist.angular.z = 0.0
    lidar_node.publisher_.publish(msg)
    
def main(args=None):
    
    msg = TwistStamped()
    msg.header = Header()
    msg.header.stamp = lidar_node.get_clock().now().to_msg()
    msg.header.frame_id = ''
    turning = False
    FWD = True
    instructionIterator = 0
    currentOrientation = "N"
    nextOrientation = "N"
    turnCount = 0
    thread1 = threading.Thread(target=SPIIIIIIIIIIIIN, args=(lidar_node,))
    thread1.start()
    start = int(input("What square are you starting in: "))
    end = int(input("What square are you ending in: "))
    output_Path = path(start, end, maze)
    turnPath = turningPath(path_to_cardinals(output_Path), output_Path)
    turn, num = parseInstructions(turnPath)
    nextOrientation = turn[instructionIterator][0]
    
    # Hard coded directions
    # After running A* script separately, pass best directions as instructions
    # Due to lack of time, this function had to be handled external to the maze solve
    while(lidar_node.imuLatch or lidar_node.lidarLatch):
        hi = 0
        
    forward(msg,3)
    rightTurn(msg)
    forward(msg,4)
    rightTurn(msg)
    forward(msg,2)
    rightTurn(msg)
    forward(msg,1)
    leftTurn(msg)
    forward(msg,1)
    leftTurn(msg)
    forward(msg,2)
    #'''
    lidar_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()