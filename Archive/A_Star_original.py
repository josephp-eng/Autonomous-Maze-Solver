# A*-lite algorithm developed by Joey & Raymond
# Utilized in the final maze_solver
# Given a known 5x5 maze grid, determines the shortest path from a starting position to the end

import numpy as np
import time
from copy import deepcopy
import math

class Directions():
    def __init__(self, N:bool, E:bool, S:bool, W:bool, T:str):
        self.North = N
        self.South = S
        self.West = W
        self.East = E
        self.Tag = T
    def tag_manipulator(self, dir):
        self.Tag = dir
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

# converts sequence of steps for maze navigation into instructions (N, E, S, W)
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

# keep track of direction
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
    out = sum(array)/len(array)
    return(out)

def turnCounter (target, Lidar, range_Center):
    latch:bool
    count = 0
    high = .1
    if avg(Lidar[range_Center-25:range_Center+25])>high and not latch:
        count = count + 1
        latch = True
    elif avg(Lidar[range_Center-25:range_Center+25])>high:
        high = avg(Lidar[range_Center-25:range_Center+25])
    elif avg(Lidar[range_Center-25:range_Center+25])<(high -.1):
        latch = False
        high = .1
    if target == count:
        return(False)
    else:
        return (True)

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
        


def main(args=None):
    test = 15
    print(maze[index(test)].North)
    print(maze[index(test)].South)
    print(maze[index(test)].East)
    print(maze[index(test)].West)
    print(index(test))
    start = int(input("What square are you starting in: "))
    #tag1 = input("What square is tag1 in: ")
    #tag2 = input("What square is tag2 in: ")
    #tag3 = input("What square is tag3 in: ")
    end = int(input("What square are you ending in: "))
    print(maze)
    output_Path = path(start, end, maze)
    print(output_Path)
    test = 15
    print(maze[index(test)].North)
    print(maze[index(test)].South)
    print(maze[index(test)].East)
    print(maze[index(test)].West)
    print(index(test))

    turnPath = turningPath(path_to_cardinals(output_Path), output_Path)
    print(turnPath)
    turn, num = parseInstructions(turnPath)
    print(turn)
    print(num)
    
if __name__ == '__main__':
    main()