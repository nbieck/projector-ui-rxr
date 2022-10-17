cmake_minimum_required(VERSION 3.5)
project(usb_cam)


# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED COMPONENTS core highgui videoio)
find_package(rclcpp_components REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_library(${PROJECT_NAME} SHARED
  src/usb_cam.cpp
  src/image_subscriber.cpp
)
ament_target_dependencies(${PROJECT_NAME} rclcpp OpenCV cv_bridge sensor_msgs rclcpp_components)
rclcpp_components_register_nodes(${PROJECT_NAME} "usb_cam_node::ImagePublisher")
rclcpp_components_register_nodes(${PROJECT_NAME} "usb_cam_node::ImageSubscriber")

install(TARGETS ${PROJECT_NAME} DESTINATION lib)
# Call ament build system
ament_package()