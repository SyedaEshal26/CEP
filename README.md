# 🤖 Multi-Robot Warehouse Pick-and-Place System

## 📌 Project Overview

The proposed system consists of two primary robotic units:

1. **Stationary Robotic Manipulator**
2. **Autonomous Mobile Rover**

The stationary manipulator is positioned at a known location and performs the object-picking operation. It then places the object onto the mobile rover. The rover autonomously navigates to a designated destination while carrying the object.

The overall system is implemented using **Robot Operating System (ROS)** and simulated in **Gazebo**, providing a controlled environment for testing robot coordination, navigation, sensing, and task execution.

The rover uses **odometry, IMU, wheel encoders, and ultrasonic sensing** for navigation and obstacle detection, while the manipulator uses servo-driven joints for object handling.

---

## 🎯 Objectives

The main objectives of this project are:

* Develop a multi-robot warehouse automation system.
* Perform continuous pick-and-place operations.
* Coordinate a stationary manipulator with an autonomous rover.
* Implement autonomous rover navigation.
* Use IMU feedback for accurate heading and turning.
* Use wheel encoders for odometry.
* Use ultrasonic sensing for obstacle detection.

---

## 🏗️ System Architecture

The system is divided into two major components:

```text
                  ┌─────────────────────────┐
                  │  Stationary Manipulator │
                  │                         │
                  │  Pick Object            │
                  │       ↓                 │
                  │  Place Object           │
                  └───────────┬─────────────┘
                              │
                              │ ROS Communication
                              ↓
                  ┌─────────────────────────┐
                  │     Autonomous Rover    │
                  │                         │
                  │  Receive Object         │
                  │       ↓                │
                  │  Navigate               │
                  │       ↓                │
                  │  Avoid Obstacles        │
                  │       ↓                │
                  │  Reach Destination      │
                  └─────────────────────────┘
```

The manipulator and rover communicate through ROS topics, allowing the system to synchronize object transfer and rover motion.

---

## 🔄 Operating Workflow

The complete operation follows these steps:

```text
Start
  │
  ▼
Manipulator reaches object
  │
  ▼
Object is picked
  │
  ▼
Manipulator places object on rover
  │
  ▼
/object_placed signal
  │
  ▼
Rover starts navigation
  │
  ▼
Read IMU + Odometry + Ultrasonic
  │
  ▼
Navigate toward destination
  │
  ├── Obstacle detected ──► Avoid obstacle
  │
  └── Clear path
          │
               ▼
   Reach destination
          │
               ▼
         Stop
```

This communication-based workflow enables the manipulator and rover to operate as a coordinated robotic team.

---

# 🛠️ Hardware

## Mobile Rover

The mobile rover uses a differential-drive configuration with:

* Four DC motors
* Motor drivers
* Wheel encoders
* IMU sensor
* Ultrasonic sensor
* Embedded controller

Wheel encoders provide feedback for odometry, while the IMU provides orientation information. The ultrasonic sensor is mounted at the front of the rover for obstacle detection.

---

## Robotic Manipulator

The stationary manipulator consists of multiple servo-driven joints.

Its primary functions are:

* Reach the object location
* Pick the object
* Move the object
* Place the object onto the rover

The manipulator can use predefined joint trajectories or inverse kinematics to reach the required positions.

---

# 💻 Software

The project uses the following software technologies:

* **ROS (Robot Operating System)**
* **Gazebo**
* **RViz**
* **Python**
* **Arduino**
* ROS Topics for inter-robot communication

Each functional component is implemented as an independent ROS node.

---

# 🧩 ROS Communication

The rover navigation node subscribes to sensor information and publishes velocity commands.

### Topics

| Topic               | Type/Purpose     | Function                             |
| ------------------- | ---------------- | ------------------------------------ |
| `/object_placed`    | Event/Status     | Indicates object transfer completion |
| `/rover/cmd_vel`    | Velocity command | Controls rover movement              |
| `/rover/odom`       | Odometry         | Provides rover position feedback     |
| `/rover/imu`        | IMU data         | Provides orientation information     |
| `/rover/ultrasonic` | Sensor data      | Provides obstacle information        |

These ROS topics provide communication between the manipulator, rover, and navigation system.

---

# 🧭 Rover Navigation

The rover navigation system uses:

* IMU
* Wheel odometry
* Ultrasonic sensing
* Waypoint navigation

The implemented movement strategy uses a **square trajectory with 4-meter sides**.

The IMU is used to estimate yaw and perform approximately **90° turns**, while wheel odometry is used to estimate the distance traveled along each straight segment.

### Navigation Concept

```text
             4 m
      ┌───────────────┐
      │               │
      │               │
   4m │               │ 4m
      │               │
      │               │
      └───────────────┘
             4 m
```

At each corner:

1. Rover reaches the waypoint.
2. IMU yaw is read.
3. Rover performs a 90° rotation.
4. Rover continues toward the next waypoint.

---

# 🚧 Obstacle Detection

The front-mounted ultrasonic sensor continuously monitors the environment.

```text
              Ultrasonic
                 Sensor
                    │
                    ▼
              ~~~~~~~~~~~
                 Rover
              ┌─────────┐
              │         │
              │  ROVER  │
              │         │
              └─────────┘
```

If an obstacle is detected within the monitored region, the navigation system can use the sensor information to prevent collision.

---

# 🖥️ Simulation

Gazebo is used to simulate:

* Warehouse environment
* Rover
* Robotic manipulator
* Obstacles
* Sensor behavior
* Robot motion
* Physical interactions

RViz is used to visualize:

* Robot pose
* Sensor information
* Navigation paths
* Rover/manipulator states

The simulation provides a safe environment for testing before physical implementation.

---

# 📊 Results

The simulation demonstrated:

* Successful coordination between the rover and manipulator.
* Consistent rover movement.
* Stable square-path navigation.
* IMU-based 90° turning.
* ROS-based task synchronization.
* Successful object-transfer coordination.
* Consistent operation across multiple cycles.

Minor positional drift was observed because of limitations associated with odometry.

---

# 🔧 Hardware Implementation

The proposed system can be implemented using:

```text
                 HOST COMPUTER
                      │
                 ROS CONTROL
                      │
          ┌───────────┴───────────┐
          │                       │
               ▼                                  ▼
    MOBILE ROVER             MANIPULATOR
          │                       │
     Arduino Uno             Servo Motors
          │                       │
     ┌────┴────┐              Object Pick
     │         │                  │
  Sensors   Motors                ▼
     │         │             Object Place
     │         │                  │
     └─────────┴──────────────────┘
```

The physical implementation requires consideration of sensor noise, mechanical constraints, communication reliability, and actuator limitations.
---

# 🚀 Getting Started

## Prerequisites

Install the required robotics software:

* ROS
* Gazebo
* RViz
* Python
* Arduino IDE

The project report specifies ROS as the main communication framework and Gazebo/RViz as the simulation and visualization environment.

## Clone the Repository

```bash
git clone https://github.com/SyedaEshal26/Multi-Robot-Warehouse-Pick-and-Place-System.git
cd Multi-Robot-Warehouse-Pick-and-Place-System
```

## Build the ROS Workspace

For a catkin-based ROS workspace:

```bash
catkin_make
```

Then source the workspace:

```bash
source devel/setup.bash
```

> Adjust these commands if your implementation uses a different ROS distribution or build system.

## Launch Simulation

After configuring the package and launch files:

```bash
roslaunch <Multi-Robot Warehouse Pick-and-Place System> rover1.launch
```

The launch file should start the Gazebo environment, robot models, required ROS nodes, and visualization components.

---

## 📜 License

This project was developed as an academic robotics project. 

---

## ⭐ Acknowledgement

This project was developed as part of the **Robotics (EL-422)** course under the supervision of **Dr. Riaz un Nabi**.

