# alx-backend-graphql_crm

A Django-based CRM system implementing GraphQL APIs using `graphene-django`. This project demonstrates building scalable and flexible APIs using GraphQL instead of traditional REST endpoints.

## Overview

GraphQL is a powerful query language and runtime for APIs that allows clients to request exactly the data they need. Unlike REST APIs with fixed data structures, GraphQL provides flexibility in response formats.

## Learning Objectives

By the end of this project, you will be able to:

- Explain GraphQL's advantages over REST
- Describe key GraphQL components (types, queries, mutations)
- Set up GraphQL in Django with `graphene-django`
- Build GraphQL queries and mutations
- Use GraphiQL/Insomnia for API testing
- Follow GraphQL API best practices

## Key Concepts

- **GraphQL vs REST**: Single endpoint vs multiple endpoints
- **Schema**: Defines data access (Types, Queries, Mutations)
- **Resolvers**: Functions fetching data for queries/mutations
- **Graphene-Django**: Seamless Django-GraphQL integration

## Quick Start

Prerequisites:
- Python 3.10+
- pip

Setup:
```powershell
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Optional: Seed example data
python seed_db.py

# Start development server
python manage.py runserver
```

Visit GraphiQL at: http://localhost:8000/graphql

## Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/  # Project settings
│   ├── schema.py            # Root GraphQL schema
│   └── urls.py             # URL configuration
├── crm/                    # Main app
│   ├── models.py          # Django models
│   ├── schema.py         # GraphQL types/mutations
│   └── filters.py       # Django-filter classes
└── graphql_crm/         # GraphQL integration
    └── schema.py       # Combined schema
```

## Tasks

### 0. Set Up GraphQL Endpoint

- [x] Create Django project and CRM app
- [x] Install graphene-django and django-filter
- [x] Define basic Query with hello field
- [x] Connect GraphQL endpoint

Test with:
```graphql
{
  hello
}
```

### 1. Build CRM Database with GraphQL Integration

Implement mutations for:

**Create Customer:**
```graphql
mutation {
  createCustomer(input: {
    name: "Alice"
    email: "alice@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
    }
    message
  }
}
```

**Bulk Create Customers:**
```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
    }
    errors
  }
}
```

**Create Product:**
```graphql
mutation {
  createProduct(input: {
    name: "Laptop"
    price: 999.99
    stock: 10
  }) {
    product {
      id
      name
      price
    }
  }
}
```

**Create Order:**
```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer { name }
      products { name price }
      totalAmount
    }
  }
}
```

### 2. Add Filtering Support

Implement filters for querying data:

**Filter Customers:**
```graphql
query {
  allCustomers(filter: { 
    nameIcontains: "Ali"
    createdAtGte: "2025-01-01" 
  }) {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```

**Filter Products:**
```graphql
query {
  allProducts(
    filter: { 
      priceGte: 100
      priceLte: 1000
    }
    orderBy: "-stock"
  ) {
    edges {
      node {
        name
        price
        stock
      }
    }
  }
}
```

## Best Practices

Area | Practice
--- | ---
Schema Design | Clean, modular, clear naming
Security | Auth in resolvers, avoid data exposure
Error Handling | Custom messages, graceful exceptions
Pagination | For large query sets
N+1 Problem | Use proper field selection
Testing | Unit test queries/mutations
Documentation | Use GraphiQL, document schema

## Development

Run tests:
```powershell
# All tests
python manage.py test -v2

# Specific test case
python manage.py test crm.tests.HelloQueryTests -v2
```

## Tools & Libraries

- `graphene-django`: GraphQL integration
- `django-filter`: Query filtering
- GraphiQL: Interactive API explorer
- Django ORM: Data access layer

## License

MIT License - see [LICENSE](LICENSE) file for details.