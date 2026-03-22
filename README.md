# Autonomous-Maze-Solver
**Author:** Joseph Pokuta

**Course:** Robot Operating Systems | Michigan Technological University

Utilizing ROS2 (Jazzy) and Turtlebot 3 to solve a predetermined maze

## About
Our initial method of attack, inspired by the A* algorithm, had to be deprioritized as the time remaining on the project grew thin. 

Our initial idea was to turn the maze into a matrix that could be iterated over, analyzing branching paths and finding the shortest path between points A and B. The solution path was intended to be passed to our robot, which would interpret the instructions as they aligned with its lidar and IMU. This proved very difficult to troubleshoot due to the robot's technical limitations and the project's timeline. This caused us to pivot to hardcoding our forward movement and turning functions, which would then allow us to program a predetermined path.

## Control Logic
To visualize our navigation stack, we developed the following decision trees for our movement logic:
<div align="center">
  <img src="Images/decision tree 1.png" width="250" alt="Decision Tree for Forward Movement">
  <br>
  <sup><strong>Figure 1:</strong> Forward Movement Logic</sup>
</div>

<br>

<div align="center">
  <img src="Images/decision tree 2.png" width="450" alt="Decision Tree for Turning Logic">
  <br>
  <sup><strong>Figure 2:</strong> Turning Logic</sup>
</div>

## Project Structure
* `maze_solver.py`: The primary ROS2 node containing the multithreaded navigation logic, LiDAR data processing, and IMU-based turning functions.
* `SampleLogic/A_Star.py`: Sample A* path finding logic
* `Images/decision_tree_1.png` & `Images/decision_tree_2.png`: Logic flow diagrams for the movement algorithms

## How to Run
1. Create a new Python package:
   ```
   ros2 pkg create --build-type ament_python autonomous_maze_solver
   ```
3. Drop `maze_solver.py` into the `/scripts` or package folder.
4. Ensure `rclpy`, `sensor_msgs`, and `geometry_msgs` are included in your dependencies.
5. Ensure your Turtlebot 3 environment is sourced.
6. Run the solver node:
   ```
   ros2 run autonomous_maze_solver solver_node
   ```
   
### Note: Portability
This repository contains the core source code used during the project's development on an Ubuntu/ROS2 Jazzy environment. While the original workspace configuration (`package.xml`, `setup.py`) was hosted on a temporary boot drive, the `maze_solver.py` script contains the complete execution logic.


## Technical Challenges
The primary challenge of this project was managing the complexity of the Turtlebot 3 hardware alongside the ROS ecosystem.
* **Concurrency:** A significant hurdle was that `rclpy.spin()` creates an infinite loop. Since we needed the node to update continuously to process sensor data while simultaneously running navigation functions, we implemented multithreading. This allowed the node to "spin" in the background while the main logic executed.
* **System Architeecture:** Our entire program currently resides in a single Python script. Given Python’s runtime characteristics, a future improvement would involve a more distributed ROS architecture with separate nodes for sensing, planning, and acting.
* **Dead-Reckoning:** Our current solution relies heavily on odometry and the IMU. This led to inconsistent results. At times, the robot's success felt like a "coin toss" due to cumulative error in the sensors.

## Limitations & Future Work
While our "manual" navigation method provided a deep understanding of ROS implementation and multithreading, it highlighted the necessity of robust pathfinding.
### Key areas for future development:
* **Refining A-Star:** Re-implementing our matrix-based A* method now that we have a stable understanding of ROS communication.
* **Sensor Fusion:** Better integration of LiDAR and Odometry to reduce the reliance on dead-reckoning.
* **Modularization:** Breaking the project into a proper ROS package structure with launch files and separate configuration nodes.
