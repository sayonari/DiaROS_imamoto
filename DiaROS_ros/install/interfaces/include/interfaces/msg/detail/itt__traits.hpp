// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from interfaces:msg/Itt.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ITT__TRAITS_HPP_
#define INTERFACES__MSG__DETAIL__ITT__TRAITS_HPP_

#include "interfaces/msg/detail/itt__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<interfaces::msg::Itt>()
{
  return "interfaces::msg::Itt";
}

template<>
inline const char * name<interfaces::msg::Itt>()
{
  return "interfaces/msg/Itt";
}

template<>
struct has_fixed_size<interfaces::msg::Itt>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<interfaces::msg::Itt>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<interfaces::msg::Itt>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // INTERFACES__MSG__DETAIL__ITT__TRAITS_HPP_
