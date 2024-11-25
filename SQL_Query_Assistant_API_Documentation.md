
# SQL Query Assistant API Documentation

## Overview

This API provides two endpoints:
1. **GenerateSQLView**: Converts natural language into SQL queries using OpenAI.
2. **ExecuteSQLView**: Executes SQL queries and returns the result.

---

## Endpoints

### **1. Generate SQL**

#### **Endpoint**
`POST /api/generate-sql/`

#### **Description**
This endpoint takes a natural language input and generates a valid SQL query based on the database schema.

#### **Request**

- **Headers**
  ```http
  Content-Type: application/json
  ```

- **Body**
  ```json
  {
      "user_input": "<natural_language_query>"
  }
  ```

#### **Response**

- **Success**
  - **Status Code**: `200 OK`
  - **Body**:
    ```json
    {
        "sql_query": "<generated_sql_query>"
    }
    ```

- **Error**
  - **Status Code**: `400 Bad Request`
  - **Body**:
    ```json
    {
        "error": "'user_input' is required."
    }
    ```
  - **Status Code**: `500 Internal Server Error`
  - **Body**:
    ```json
    {
        "error": "<error_message>"
    }
    ```

#### **Example**

- **Request**:
  ```json
  {
      "user_input": "Show me all upcoming events."
  }
  ```

- **Response**:
  ```json
  {
      "sql_query": "SELECT * FROM events WHERE event_time > NOW();"
  }
  ```

---

### **2. Execute SQL**

#### **Endpoint**
`POST /api/execute-sql/`

#### **Description**
This endpoint takes a SQL query and executes it on the connected database.

#### **Request**

- **Headers**
  ```http
  Content-Type: application/json
  ```

- **Body**
  ```json
  {
      "sql_query": "<sql_query>"
  }
  ```

#### **Response**

- **Success**
  - **Status Code**: `200 OK`
  - **Body** (for SELECT queries):
    ```json
    {
        "result": [
            {"column1": "value1", "column2": "value2"},
            {"column1": "value3", "column2": "value4"}
        ]
    }
    ```
  - **Body** (for other queries like INSERT, UPDATE, DELETE):
    ```json
    {
        "result": {
            "message": "Query executed successfully."
        }
    }
    ```

- **Error**
  - **Status Code**: `400 Bad Request`
  - **Body**:
    ```json
    {
        "error": "'sql_query' is required."
    }
    ```
  - **Status Code**: `500 Internal Server Error`
  - **Body**:
    ```json
    {
        "error": "<error_message>"
    }
    ```

#### **Example**

- **Request**:
  ```json
  {
      "sql_query": "SELECT * FROM events WHERE event_time > NOW();"
  }
  ```

- **Response**:
  ```json
  {
      "result": [
          {"event_id": 1, "name": "Tech Conference", "event_time": "2024-12-01 10:00:00"},
          {"event_id": 2, "name": "Career Fair", "event_time": "2024-12-05 14:00:00"}
      ]
  }
  ```

---

## Internal Methods

### **`get_database_schema()`**
Fetches the schema of the connected database, including table names and their columns.

#### **Returns**
- A dictionary containing table names and their columns:
  ```python
  {
      "table_name": [
          {"Field": "column_name", "Type": "column_type"},
          ...
      ]
  }
  ```

---

### **`execute_sql(sql_query)`**
Executes the provided SQL query on the connected database.

#### **Parameters**
- **`sql_query`**: The SQL query to execute.

#### **Returns**
- For `SELECT` queries:
  ```python
  [
      {"column1": "value1", "column2": "value2"},
      ...
  ]
  ```
- For other queries:
  ```python
  {"message": "Query executed successfully."}
  ```

---

## Error Handling

1. **Invalid Inputs**:
   - Missing `user_input` or `sql_query` will result in a `400 Bad Request` response.

2. **Internal Errors**:
   - Any exceptions raised during schema fetching, SQL generation, or query execution will return a `500 Internal Server Error` with an error message.
