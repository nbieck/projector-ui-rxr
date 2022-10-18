#include <memory>
#include <chrono>
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class SampleClass : public rclcpp::Node
{
    public:
    SampleClass() : Node("sample_node")
    {
        timer_ = create_wall_timer(1s, std::bind(&SampleClass::timer_callback, this));
    }
    private:
    void timer_callback()
    {
        RCLCPP_INFO(this->get_logger(), "Hello World");
    }
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SampleClass>());
    rclcpp::shutdown();
    return 0;
}