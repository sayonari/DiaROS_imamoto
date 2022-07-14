# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interfaces:msg/Isa.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Isa(type):
    """Metaclass of message 'Isa'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'interfaces.msg.Isa')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__isa
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__isa
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__isa
            cls._TYPE_SUPPORT = module.type_support_msg__msg__isa
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__isa

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Isa(metaclass=Metaclass_Isa):
    """Message class 'Isa'."""

    __slots__ = [
        '_prevgrad',
        '_frequency',
        '_grad',
        '_power',
        '_zerocross',
    ]

    _fields_and_field_types = {
        'prevgrad': 'float',
        'frequency': 'float',
        'grad': 'float',
        'power': 'float',
        'zerocross': 'int64',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('int64'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.prevgrad = kwargs.get('prevgrad', float())
        self.frequency = kwargs.get('frequency', float())
        self.grad = kwargs.get('grad', float())
        self.power = kwargs.get('power', float())
        self.zerocross = kwargs.get('zerocross', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.prevgrad != other.prevgrad:
            return False
        if self.frequency != other.frequency:
            return False
        if self.grad != other.grad:
            return False
        if self.power != other.power:
            return False
        if self.zerocross != other.zerocross:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @property
    def prevgrad(self):
        """Message field 'prevgrad'."""
        return self._prevgrad

    @prevgrad.setter
    def prevgrad(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'prevgrad' field must be of type 'float'"
        self._prevgrad = value

    @property
    def frequency(self):
        """Message field 'frequency'."""
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'frequency' field must be of type 'float'"
        self._frequency = value

    @property
    def grad(self):
        """Message field 'grad'."""
        return self._grad

    @grad.setter
    def grad(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'grad' field must be of type 'float'"
        self._grad = value

    @property
    def power(self):
        """Message field 'power'."""
        return self._power

    @power.setter
    def power(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'power' field must be of type 'float'"
        self._power = value

    @property
    def zerocross(self):
        """Message field 'zerocross'."""
        return self._zerocross

    @zerocross.setter
    def zerocross(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'zerocross' field must be of type 'int'"
            assert value >= -9223372036854775808 and value < 9223372036854775808, \
                "The 'zerocross' field must be an integer in [-9223372036854775808, 9223372036854775807]"
        self._zerocross = value
