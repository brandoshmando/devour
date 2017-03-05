from unittest import TestCase
from devour.schemas import Schema

class ExampleSchemaNoMeta(Schema):
    pass

class ExampleSchemaEmptyMeta(Schema):
    class Meta:
        pass

class ExampleSchemaNested(Schema):
    class Meta:
        attributes = ('nested_1',)

class ExampleSchema(Schema):
    key_1 = ExampleSchemaNested

    class Meta:
        attributes = ('key_1', 'key_2')

class ExampleSchemaNoNested(Schema):

    class Meta:
        attributes = ('key_1', 'key_2')


class TestSchema(TestCase):
    def setUp(self):
        self.data = {
            'key_1': 'val_1',
            'key_2': 'val_2',
            'key_3': 'val_3'
        }

        self.nested_data = {
            'key_1': {'nested_1': 'nested_val_1', 'nested_2': 'nested_val_2'},
            'key_2': 'val_2',
            'key_3': 'val_3'
        }

    def test_schema_returns_all_data(self):
        schema = ExampleSchemaEmptyMeta(data=self.data)
        ret = schema.data
        self.assertEqual(ret, self.data)

    def test_schema_returns_specified_data(self):
        schema = ExampleSchema(data=self.data)
        ret = schema.data
        del self.data['key_3']
        self.assertEqual(ret, self.data)

    def test_schema_returns_all_nested_data(self):
        schema = ExampleSchemaNoNested(data=self.nested_data)
        ret = schema.data
        del self.nested_data['key_3']
        self.assertEqual(ret, self.nested_data)

    def test_schema_returns_specified_nested_data(self):
        schema = ExampleSchemaEmptyMeta(data=self.nested_data)
        ret = schema.data
        del self.nested_data['key_1']['nested_2']
        self.assertEqual(ret, self.nested_data)

    def test_no_meta_causes_assertion_error(self):
        try:
            schema = ExampleSchemaNoMeta(data=self.nested_data)
            raise Exception('Schema initialized without Meta class')
        except AssertionError:
            pass
