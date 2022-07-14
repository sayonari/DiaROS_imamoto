// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/List.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__LIST__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__LIST__TRAITS_HPP_

#include "interfaces/msg/detail/list__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::List>()
{
  return "interfaces::msg::List";
}

template<>
inline const char * name<interfaces::msg::List>()
{
  return "interfaces/msg/List";
}

template<>
struct has_fixed_size<interfaces::msg::List>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interfaces::msg::List>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interfaces::msg::List>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__LIST__TRAITS_HPP_
