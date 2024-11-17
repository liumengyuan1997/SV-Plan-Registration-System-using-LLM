
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

**Endpoint**: `/publish-event/`  
**Method**: `POST`  
**Permissions**: Admin only (requires `IsAdminRole` permission)  

#### Request Example:
```json
{
    "title": "Hackathon 2024",
    "description": "A global hackathon event for developers.",
    "date": "2024-12-01T10:00:00Z",
    "location": "San Francisco, CA"
}
```

#### Response:
- **Success (201 Created)**:
  ```json
  {
      "success": true,
      "message": "Event published successfully!",
      "data": {
          "id": 1,
          "title": "Hackathon 2024",
          "description": "A global hackathon event for developers.",
          "date": "2024-12-01T10:00:00Z",
          "location": "San Francisco, CA",
          "event_published_by": 2
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

---

# Serializers Documentation

## File: `serializers.py`

This file contains serializer classes for the `User` and `Event` models, providing validation and transformation for API data.

---

## 1. **SignupSerializer**

The `SignupSerializer` is used to handle user registration, including validation and creation of new `User` instances.

### **Fields**
| Field         | Type       | Description                              | Validation                       |
|---------------|------------|------------------------------------------|-----------------------------------|
| `email`       | `CharField`| User's email address.                    | Must be unique.                  |
| `password`    | `CharField`| User's password. Write-only.             | Required.                        |
| `role`        | `CharField`| User's role (e.g., Admin, User, etc.).   | Required.                        |
| `first_name`  | `CharField`| User's first name.                       | Optional.                        |
| `last_name`   | `CharField`| User's last name.                        | Optional.                        |

---

## 2. **EventSerializer**

The `EventSerializer` is used to handle the creation and validation of `Event` objects.

### **Fields**
| Field               | Type       | Description                | Validation |
|---------------------|------------|----------------------------|------------|
| `event_name`        | `CharField`| Name of the event.          | Required.  |
| `event_description` | `CharField`| Detailed description.       | Optional.  |
| `event_location`    | `CharField`| Location of the event.      | Required.  |
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

### **User Model**
| Field         | Type              | Description                                         | Notes                       |
|---------------|-------------------|-----------------------------------------------------|-----------------------------|
| `first_name`  | `CharField`       | User's first name.                                  | Optional (nullable).        |
| `last_name`   | `CharField`       | User's last name.                                   | Optional (nullable).        |
| `email`       | `EmailField`      | User's unique email address (primary key).          | Required.                   |
| `password`    | `CharField`       | User's password (stored in plain text).             | **Security Note:** Not secure. |
| `role`        | `CharField`       | User's role, either `Student` or `Admin`.           | Default: `Student`.         |

### **Event Model**
| Field                 | Type              | Description                                         | Notes                       |
|-----------------------|-------------------|-----------------------------------------------------|-----------------------------|
| `event_name`          | `CharField`       | Name of the event.                                  | Required.                   |
| `event_description`   | `TextField`       | Detailed description of the event.                 | Optional.                   |
| `event_location`      | `CharField`       | Location where the event will take place.           | Required.                   |
| `event_time`          | `DateTimeField`   | Date and time of the event.                        | Required.                   |
| `event_published_by`  | `ForeignKey`      | Reference to the `User` who published the event.    | Nullable; `SET_NULL` on deletion. |

---

# Authentication Requirements for Frontend

## 1. Authentication Method

The backend uses **Basic Authentication** for user verification. The frontend must include the user's credentials (`email:password`) encoded in **Base64** within the `Authorization` request header.

------

## 2. Header Format

The `Authorization` header should follow this format:

```
Authorization: Basic <Base64-encoded email:password>
```
