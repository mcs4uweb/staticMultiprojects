import json
import graphene

# Define a simple GraphQL type
class User(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    email = graphene.String()

# Define the Query object with a resolver
class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.ID(required=True))

    def resolve_user(self, info, id):
        # In a real-world scenario, you would fetch data from a database
        # For this example, we'll return a hardcoded user
        if id == "1":
            return User(id="1", name="Alice", email="alice@example.com")
        return None

# Create the schema
schema = graphene.Schema(query=Query)

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query')
        variables = body.get('variables', {})

        # Execute the query against the schema
        result = schema.execute(query, variables=variables)

        # Return the GraphQL result
        return {
            'statusCode': 200,
            'body': json.dumps(result.data)
        }
    except Exception as e:
        # Handle errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }