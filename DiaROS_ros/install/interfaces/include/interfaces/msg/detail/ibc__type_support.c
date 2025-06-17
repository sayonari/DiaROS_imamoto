// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from interfaces:msg/Ibc.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "interfaces/msg/detail/ibc__rosidl_typesupport_introspection_c.h"
#include "interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "interfaces/msg/detail/ibc__functions.h"
#include "interfaces/msg/detail/ibc__struct.h"


#ifdef __cplusplus
extern "C"
{
#endif

void Ibc__rosidl_typesupport_introspection_c__Ibc_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  interfaces__msg__Ibc__init(message_memory);
}

void Ibc__rosidl_typesupport_introspection_c__Ibc_fini_function(void * message_memory)
{
  interfaces__msg__Ibc__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember Ibc__rosidl_typesupport_introspection_c__Ibc_message_member_array[2] = {
  {
    "result",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interfaces__msg__Ibc, result),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "confidence",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interfaces__msg__Ibc, confidence),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers Ibc__rosidl_typesupport_introspection_c__Ibc_message_members = {
  "interfaces__msg",  // message namespace
  "Ibc",  // message name
  2,  // number of fields
  sizeof(interfaces__msg__Ibc),
  Ibc__rosidl_typesupport_introspection_c__Ibc_message_member_array,  // message members
  Ibc__rosidl_typesupport_introspection_c__Ibc_init_function,  // function to initialize message memory (memory has to be allocated)
  Ibc__rosidl_typesupport_introspection_c__Ibc_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t Ibc__rosidl_typesupport_introspection_c__Ibc_message_type_support_handle = {
  0,
  &Ibc__rosidl_typesupport_introspection_c__Ibc_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, interfaces, msg, Ibc)() {
  if (!Ibc__rosidl_typesupport_introspection_c__Ibc_message_type_support_handle.typesupport_identifier) {
    Ibc__rosidl_typesupport_introspection_c__Ibc_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &Ibc__rosidl_typesupport_introspection_c__Ibc_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
