// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from interfaces:msg/Irc.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__IRC__BUILDER_HPP_
#define INTERFACES__MSG__DETAIL__IRC__BUILDER_HPP_

#include "interfaces/msg/detail/irc__struct.hpp"
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <utility>


namespace interfaces
{

namespace msg
{

namespace builder
{

class Init_Irc_word
{
public:
  Init_Irc_word()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::interfaces::msg::Irc word(::interfaces::msg::Irc::_word_type arg)
  {
    msg_.word = std::move(arg);
    return std::move(msg_);
  }

private:
  ::interfaces::msg::Irc msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::interfaces::msg::Irc>()
{
  return interfaces::msg::builder::Init_Irc_word();
}

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__IRC__BUILDER_HPP_
