# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interfaces:msg/List.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_List(type):
    """Metaclass of message 'List'."""

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
                'interfaces.msg.List')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__list
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__list
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__list
            cls._TYPE_SUPPORT = module.type_support_msg__msg__list
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__list

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class List(metaclass=Metaclass_List):
    """Message class 'List'."""

    __slots__ = [
        '_n',
        '_you',
        '_bot',
        '_frequency',
    ]

    _fields_and_field_types = {
        'n': 'int64',
        'you': 'string',
        'bot': 'string',
        'frequency': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int64'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.n = kwargs.get('n', int())
        self.you = kwargs.get('you', str())
        self.bot = kwargs.get('bot', str())
        self.frequency = kwargs.get('frequency', float())

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
        if self.n != other.n:
            return False
        if self.you != other.you:
            return False
        if self.bot != other.bot:
            return False
        if self.frequency != other.frequency:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @property
    def n(self):
        """Message field 'n'."""
        return self._n

    @n.setter
    def n(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'n' field must be of type 'int'"
            assert value >= -9223372036854775808 and value < 9223372036854775808, \
                "The 'n' field must be an integer in [-9223372036854775808, 9223372036854775807]"
        self._n = value

    @property
    def you(self):
        """Message field 'you'."""
        return self._you

    @you.setter
    def you(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'you' field must be of type 'str'"
        self._you = value

    @property
    def bot(self):
        """Message field 'bot'."""
        return self._bot

    @bot.setter
    def bot(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'bot' field must be of type 'str'"
        self._bot = value

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
