// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from interfaces:msg/Irc.idl
// generated code does not contain a copyright notice

#ifndef INTERFACES__MSG__DETAIL__IRC__STRUCT_HPP_
#define INTERFACES__MSG__DETAIL__IRC__STRUCT_HPP_

#include <rosidl_runtime_cpp/bounded_vector.hpp>
#include <rosidl_runtime_cpp/message_initialization.hpp>
#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>


#ifndef _WIN32
# define DEPRECATED__interfaces__msg__Irc __attribute__((deprecated))
#else
# define DEPRECATED__interfaces__msg__Irc __declspec(deprecated)
#endif

namespace interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Irc_
{
  using Type = Irc_<ContainerAllocator>;

  explicit Irc_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->word = "";
    }
  }

  explicit Irc_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : word(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->word = "";
    }
  }

  // field types and members
  using _word_type =
    std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other>;
  _word_type word;

  // setters for named parameter idiom
  Type & set__word(
    const std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other> & _arg)
  {
    this->word = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    interfaces::msg::Irc_<ContainerAllocator> *;
  using ConstRawPtr =
    const interfaces::msg::Irc_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<interfaces::msg::Irc_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<interfaces::msg::Irc_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::Irc_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::Irc_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      interfaces::msg::Irc_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<interfaces::msg::Irc_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<interfaces::msg::Irc_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<interfaces::msg::Irc_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__interfaces__msg__Irc
    std::shared_ptr<interfaces::msg::Irc_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__interfaces__msg__Irc
    std::shared_ptr<interfaces::msg::Irc_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Irc_ & other) const
  {
    if (this->word != other.word) {
      return false;
    }
    return true;
  }
  bool operator!=(const Irc_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Irc_

// alias to use template instance with default allocator
using Irc =
  interfaces::msg::Irc_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace interfaces

#endif  // INTERFACES__MSG__DETAIL__IRC__STRUCT_HPP_
