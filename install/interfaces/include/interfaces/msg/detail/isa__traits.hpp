// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/Isa.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISA__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__ISA__TRAITS_HPP_

#include "interfaces/msg/detail/isa__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::Isa>()
{
  return "interfaces::msg::Isa";
}

template<>
inline const char * name<interfaces::msg::Isa>()
{
  return "interfaces/msg/Isa";
}

template<>
struct has_fixed_size<interfaces::msg::Isa>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<interfaces::msg::Isa>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<interfaces::msg::Isa>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__ISA__TRAITS_HPP_
