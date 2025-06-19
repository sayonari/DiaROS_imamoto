// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/Iss.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISS__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__ISS__TRAITS_HPP_

#include "interfaces/msg/detail/iss__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::Iss>()
{
  return "interfaces::msg::Iss";
}

template<>
inline const char * name<interfaces::msg::Iss>()
{
  return "interfaces/msg/Iss";
}

template<>
struct has_fixed_size<interfaces::msg::Iss>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<interfaces::msg::Iss>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<interfaces::msg::Iss>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__ISS__TRAITS_HPP_
