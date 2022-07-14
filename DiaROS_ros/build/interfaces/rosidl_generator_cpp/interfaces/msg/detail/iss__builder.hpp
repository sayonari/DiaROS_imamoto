// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/Iss.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISS__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__ISS__BUILDER_HPP_

#include "interfaces/msg/detail/iss__struct.hpp"
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <utility>


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_Iss_is_speaking
{
public:
  Init_Iss_is_speaking()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::interfaces::msg::Iss is_speaking(::interfaces::msg::Iss::_is_speaking_type arg)
  {
    msg_.is_speaking = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::Iss msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::Iss>()
{
  return interfaces::msg::builder::Init_Iss_is_speaking();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__ISS__BUILDER_HPP_
