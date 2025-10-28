from django.test import TestCase
from graphene.test import Client
from alx_backend_graphql_crm.schema import schema


class HelloQueryTests(TestCase):
    def setUp(self):
        self.client = Client(schema)

    def test_should_return_default_hello(self):
        # Query the hello field without variables
        query = """
        query { hello }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed, msg=f"Execution errors: {executed.get('errors')}")
        self.assertEqual(executed["data"]["hello"], "Hello, GraphQL!")

    def test_should_ignore_extra_fields_and_still_return_hello(self):
        # Graphene should ignore unknown fields and still resolve known ones
        query = """
        query { hello }
        """
        executed = self.client.execute(query, variable_values={"unused": "value"})
        self.assertNotIn("errors", executed)
        self.assertEqual(executed["data"]["hello"], "Hello, GraphQL!")

    def test_should_return_hello_when_query_named_operation(self):
        # Named operation shouldn't affect resolution
        query = """
        query HelloOp { hello }
        """
        executed = self.client.execute(query, operation_name="HelloOp")
        self.assertNotIn("errors", executed)
        self.assertEqual(executed["data"]["hello"], "Hello, GraphQL!")

    def test_should_return_hello_in_introspection_of_field_type(self):
        # Ensure the hello field is present in the schema with String type
        query = """
        {
          __type(name: "Query") {
            fields { name type { kind name ofType { name } } }
          }
        }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed)
        field_names = [f["name"] for f in executed["data"]["__type"]["fields"]]
        self.assertIn("hello", field_names)

    def test_should_not_error_when_requesting_only_hello(self):
        # Smoke test to ensure minimal query works reliably
        query = """
        { hello }
        """
        executed = self.client.execute(query)
        self.assertNotIn("errors", executed)
        self.assertEqual(executed["data"].get("hello"), "Hello, GraphQL!")