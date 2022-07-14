// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/Iss.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__ISS__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__ISS__STRUCT_HPP_

#include <rosidl_runtime_cpp/bounded_vector.hpp>
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>


#ifndef _WIN32
# define DEPRECATED__interfaces__msg__Iss __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__Iss __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Iss_
{
  using Type = Iss_<ContainerAllocator>;

  explicit Iss_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_speaking = false;
    }
  }

  explicit Iss_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->is_speaking = false;
    }
  }

  // field types and members
  using _is_speaking_type =
    bool;
  _is_speaking_type is_speaking;

  // setters for named parameter idiom
  Type & set__is_speaking(
    const bool & _arg)
  {
    this->is_speaking = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::Iss_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::Iss_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::Iss_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::Iss_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::Iss_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::Iss_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::Iss_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::Iss_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::Iss_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::Iss_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__Iss
    std::shared_ptr<interfaces::msg::Iss_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__Iss
    std::shared_ptr<interfaces::msg::Iss_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Iss_ & other) const
  {
    if (this->is_speaking != other.is_speaking) {
      return false;
    }
    return true;
  }
  bool operator!=(const Iss_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Iss_

// alias to use template instance with default allocator
using Iss =
  interfaces::msg::Iss_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__ISS__STRUCT_HPP_
