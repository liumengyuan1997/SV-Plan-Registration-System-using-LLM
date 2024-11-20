# API Documentation and Implementation Details

## Table of Contents

1. [API Documentation](#api-documentation)
2. [Serializers Documentation](#serializers-documentation)
3. [Permissions Documentation](#permissions-documentation)
4. [Models Documentation](#models-documentation)
5. [Authentication Requirements for Frontend](#authentication-requirements-for-frontend)

---

# API Documentation

## General Information

- **Base URL**: `/api/`
- **Content-Type**: `application/json`

---

### 1. User Registration - `SignUpView`

**Endpoint**: `/signup/`  
**Method**: `POST`  
**Permissions**: Public (accessible to anyone)

#### Request Example:

```json
{
  "email": "test@example.com",
  "password": "password123",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Response:

- **Success (201 Created)**:

  ```json
  {
    "message": "success!"
  }
  ```

- **Failure (400 Bad Request)**:
  ```json
  {
    "email": ["This field is required."],
    "password": ["This field must be at least 8 characters."]
  }
  ```

---

### 2. User Login - `SignInView`

**Endpoint**: `/signin/`  
**Method**: `POST`  
**Permissions**: Public (accessible to anyone)

#### Request Example:

```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

#### Response:

- **Success (200 OK)**:

  ```json
  {
    "message": "Successful login"
  }
  ```

- **Failure (400 Bad Request)**:

  ```json
  {
    "error": "Email and password are required"
  }
  ```

- **Failure (404 Not Found)**:

  ```json
  {
    "error": "User does not exist"
  }
  ```

- **Failure (401 Unauthorized)**:
  ```json
  {
    "error": "Invalid email or password"
  }
  ```

---

### 3. Publish Event - `PublishEventView`

**Endpoint**: `/publishevent/`  
**Method**: `POST`  
**Permissions**: Admin only (requires `IsAdminRole` permission)

#### Request Example:

```json
{
  "event_name": "Tech Conference 2024",
  "event_description": "A conference for tech enthusiasts to network and share knowledge.",
  "event_location": "San Francisco, CA",
  "event_time": "2024-12-15T10:00:00Z"
}
```

#### Response:

- **Success (201 Created)**:

  ```json
  {
    "success": true,
    "message": "Event published successfully!",
    "data": {
      "event_name": "Tech Conference 2024",
      "event_description": "A conference for tech enthusiasts to network and share knowledge.",
      "event_location": "San Francisco, CA",
      "event_time": "2024-12-15T10:00:00Z"
    }
  }
  ```

- **Failure (400 Bad Request)**:

  ```json
  {
    "success": false,
    "message": "Validation failed.",
    "errors": {
      "title": ["This field is required."]
    }
  }
  ```

- **Failure (500 Internal Server Error)**:
  ```json
  {
    "success": false,
    "message": "An unexpected error occurred.",
    "error": "Database error"
  }
  ```

### 4. List Events - `ListEventView`

**Endpoint**: `/events/`  
**Method**: `GET`  
**Permissions**: Public (accessible to anyone)

**Example Requests**

**_Fetch Events Sorted by `event_time` (Ascending)_**

GET /events/?sort=event_time

**_Fetch Events Sorted by `event_time` (Descending)_**

GET /events/?sort=-event_time

**_Fetch Events Sorted by `event_published_by` (Ascending)_**

GET /events/?sort=event_published_by

**_Fetch Events Sorted by `event_published_by` (Descending)_**

GET /events/?sort=-event_published_by

**_Fetch Events Sorted by `event_created_at` (Ascending)_**

GET /events/?sort=event_created_at

**_Fetch Events Sorted by `event_created_at` (Descending)_**

GET /events/?sort=-event_created_at

#### Response:

- **Success (200 OK)**:
  ```json
  {
    "success": true,
    "count": 8,
    "events": [
        {
            "event_id": 4,
            "event_name": "Sample Event123",
            "event_description": "This is a description of the event.",
            "event_location": "Conference Room A",
            "event_time": "2024-11-19T14:43:45-08:00",
            "event_status": "Overdue"
        },
        ...
      ]
  }
  ```

---

# Serializers Documentation

## File: `serializers.py`

This file contains serializer classes for the `User` and `Event` models, providing validation and transformation for API data.

---

## 1. **SignupSerializer**

The `SignupSerializer` is used to handle user registration, including validation and creation of new `User` instances.

### **Fields**

| Field        | Type        | Description                            | Validation      |
| ------------ | ----------- | -------------------------------------- | --------------- |
| `email`      | `CharField` | User's email address.                  | Must be unique. |
| `password`   | `CharField` | User's password. Write-only.           | Required.       |
| `role`       | `CharField` | User's role (e.g., Admin, User, etc.). | Required.       |
| `first_name` | `CharField` | User's first name.                     | Optional.       |
| `last_name`  | `CharField` | User's last name.                      | Optional.       |

---

## 2. **EventSerializer**

The `EventSerializer` is used to handle the creation and validation of `Event` objects.

### **Fields**

| Field               | Type            | Description                 | Validation |
| ------------------- | --------------- | --------------------------- | ---------- |
| `event_name`        | `CharField`     | Name of the event.          | Required.  |
| `event_description` | `CharField`     | Detailed description.       | Optional.  |
| `event_location`    | `CharField`     | Location of the event.      | Required.  |
| `event_time`        | `DateTimeField` | Date and time of the event. | Required.  |

---

# Permissions Documentation

## File: `permissions.py`

This file defines custom permission logic for the API, specifically focusing on user authentication and role-based access control.

---

## 1. **IsAdminRole**

The `IsAdminRole` class is a custom permission that ensures the user:

1. Provides valid authentication credentials (email and password).
2. Has an admin role.

---

# Models Documentation

## File: `models.py`

## **1. User Model**

### **Description**

The `User` model stores information about users, including their role and department.

### **Fields**

| Field Name   | Type            | Required | Default      | Description                                     |
| ------------ | --------------- | -------- | ------------ | ----------------------------------------------- |
| `first_name` | `CharField`     | Yes      | None         | The first name of the user.                     |
| `last_name`  | `CharField`     | Yes      | None         | The last name of the user.                      |
| `email`      | `EmailField`    | Yes      | Primary Key  | The unique email address of the user.           |
| `password`   | `CharField`     | Yes      | None         | The password for user authentication.           |
| `role`       | `CharField`     | Yes      | `Student`    | The role of the user (`Student` or `Admin`).    |
| `created_at` | `DateTimeField` | No       | Auto now add | The timestamp when the user was created.        |
| `department` | `CharField`     | Yes      | `Khoury`     | The department of the user (`Khoury` or `COE`). |

### **Role Choices**

- `Student`
- `Admin`

### **Department Choices**

- `Khoury`
- `COE`

### **Methods**

- `__str__()`: Returns the email of the user.

---

## **2. Event Model**

### **Description**

The `Event` model stores information about events, including details, location, and the publishing user.

### **Fields**

| Field Name           | Type            | Required | Default        | Description                                        |
| -------------------- | --------------- | -------- | -------------- | -------------------------------------------------- |
| `event_id`           | `AutoField`     | No       | Auto increment | The unique identifier for the event.               |
| `event_name`         | `CharField`     | Yes      | None           | The name of the event.                             |
| `event_description`  | `TextField`     | Yes      | None           | A detailed description of the event.               |
| `event_location`     | `CharField`     | Yes      | None           | The location where the event will be held.         |
| `event_time`         | `DateTimeField` | Yes      | None           | The time when the event will occur.                |
| `event_published_by` | `ForeignKey`    | No       | Null           | A reference to the `User` who published the event. |
| `event_created_at`   | `DateTimeField` | No       | Auto now add   | The timestamp when the event was created.          |
| `event_status`       | `CharField`     | Yes      | `In process`   | The current status of the event.                   |

### **Methods**

- `__str__()`: Returns the name of the event.

---

## **Relationships**

- `Event.event_published_by`: A foreign key relationship to the `User` model, indicating which user published the event.

---

## **Default Values**

- `User.role`: Defaults to `Student`.
- `User.department`: Defaults to `Khoury`.
- `Event.event_status`: Defaults to `In process`.

---

# Authentication Requirements for Frontend

## 1. Authentication Method

The backend uses **Basic Authentication** for user verification. The frontend must include the user's credentials (`email:password`) encoded in **Base64** within the `Authorization` request header.

---

## 2. Header Format

The `Authorization` header should follow this format:

```
Authorization: Basic <Base64-encoded email:password>
```
