// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/Ibc.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__IBC__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__IBC__TRAITS_HPP_

#include "interfaces/msg/detail/ibc__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::Ibc>()
{
  return "interfaces::msg::Ibc";
}

template<>
inline const char * name<interfaces::msg::Ibc>()
{
  return "interfaces/msg/Ibc";
}

template<>
struct has_fixed_size<interfaces::msg::Ibc>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<interfaces::msg::Ibc>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<interfaces::msg::Ibc>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__IBC__TRAITS_HPP_
