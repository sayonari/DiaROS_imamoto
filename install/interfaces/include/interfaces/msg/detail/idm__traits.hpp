// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/Idm.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__IDM__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__IDM__TRAITS_HPP_

#include "interfaces/msg/detail/idm__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::Idm>()
{
  return "interfaces::msg::Idm";
}

template<>
inline const char * name<interfaces::msg::Idm>()
{
  return "interfaces/msg/Idm";
}

template<>
struct has_fixed_size<interfaces::msg::Idm>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interfaces::msg::Idm>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interfaces::msg::Idm>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__IDM__TRAITS_HPP_
