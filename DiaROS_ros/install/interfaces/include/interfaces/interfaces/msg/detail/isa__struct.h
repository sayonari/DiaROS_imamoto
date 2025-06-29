// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/Isa.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISA__STRUCT_H_
#define INTERFACES__MSG__DETAIL__ISA__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/Isa in the package interfaces.
typedef struct interfaces__msg__Isa
{
  float prevgrad;
  float frequency;
  float grad;
  float power;
  int64_t zerocross;
} interfaces__msg__Isa;

// Struct for a sequence of interfaces__msg__Isa.
typedef struct interfaces__msg__Isa__Sequence
{
  interfaces__msg__Isa * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__Isa__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__ISA__STRUCT_H_
