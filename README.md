# Autonomous-Maze-Solver
Utilizing ROS and Turtlebot 3 to solve a predetermined maze

## About
Our initial method of attack, inspired by the A* algorithm, had to be deprioritized as the time remaining on the project grew thin. 

Our initial idea was to turn the maze into a matrix that could be iterated over, analyzing branching paths and finding the shortest path between points A and B. The solution path was intended to be passed to our robot, which would interpret the instructions as they aligned with its lidar and IMU. This proved very difficult to troubleshoot due to the robot's technical limitations and the project's timeline. This caused us to pivot to hardcoding our forward movement and turning functions, which would then allow us to program a predetermined path.
**Forward Movement Logic**
<img width="202" height="512" alt="decision tree 1" src="https://github.com/user-attachments/assets/5720e58f-48c7-4550-87a1-b5499dfc6eec" /> 

**Turning Logic**
<img width="476" height="511" alt="decision tree 2" src="https://github.com/user-attachments/assets/751991c4-05b5-465f-ab7f-4e86dae05279" />

## Limitations
One issue we ran into was that rclpy.spin() creates an infinite loop; however, we needed to spin our node to update it. Our solution was to use multithreading to keep the node spinning while running other functions that relied on its updates. We did need some consistency features in our design. This was entirely in our forward movement, where we used the lidar to avoid clipping walls on the sides and front. Turning was wholly handled by relative motion using the IMU, guided by instructions from our programmed path. Overall, movement relies too heavily on dead-reckoning methods.

## Challenges
The biggest challenge by far of the project was the complexity and technological limitations of the turtlebots, ROS, and Python. Areas for improvement could include better distribution across the ROS system, where our entire program lived in a single Python script, and Python is not known for its speedy runtime. Attempting to model an A* algorithm was an exceptional challenge, and we would not change our approach. The method we settled on to solve the maze relied heavily on odometry, leading to inconsistent results and reducing our effectiveness; at times, it felt like whether our robot finished the maze was down to a coin toss. However, reverting to more manual navigation methods led us to a better understanding of multithreading and ROS implementation. Now that we know how to handle ROS better, we could revisit our A* method and approach it from a new perspective.


