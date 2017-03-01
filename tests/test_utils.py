import mock
from unittest import TestCase
from devour.consumers import DevourConsumer


class DevourTestMixin(object):
    def generate_subclass(self, attrs, funcs={}, base=DevourConsumer):
        """
        :attrs: dictionary of attrs to be set on consumer. must be one of 'argnames'.
            :key: str attr name
            :val: str value
        :funcs: dictionary of functions

        """

        name = "TestDevourConsumer"
        attrs.update(funcs)
        subclass = type(name, (DevourConsumer,), attrs)
        return subclass

    def generate_mocked_consumer(self, messages):
        """
        :messages: list of messages to iterate through in test
        """

        consumer = mock.MagicMock()
        formatted_messages = []
        for i,m in enumerate(messages):
            mocked_message = mock.Mock()
            mocked_offset = mock.PropertyMock(return_value=i)
            mocked_value = mock.PropertyMock(return_value=m)
            type(mocked_message).offset = mocked_offset
            type(mocked_message).value = mocked_value
            formatted_messages.append(mocked_message)

        consumer.__iter__.return_value = formatted_messages

        return consumer
