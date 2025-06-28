// NOLINT: This file starts with a BOM since it contain non-ASCII characters
// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from interfaces:msg/Iss.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISS__STRUCT_H_
#define INTERFACES__MSG__DETAIL__ISS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'timestamp'
// Member 'filename'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/Iss in the package interfaces.
typedef struct interfaces__msg__Iss
{
  bool is_speaking;
  rosidl_runtime_c__String timestamp;
  /// 追加: 合成音声ファイル名を送信
  rosidl_runtime_c__String filename;
} interfaces__msg__Iss;

// Struct for a sequence of interfaces__msg__Iss.
typedef struct interfaces__msg__Iss__Sequence
{
  interfaces__msg__Iss * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} interfaces__msg__Iss__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // INTERFACES__MSG__DETAIL__ISS__STRUCT_H_
