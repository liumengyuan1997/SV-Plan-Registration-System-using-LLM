# SV-Plan-Registration-System-using-LLM
The SV Plan Registration System, managed by Khoury College, streamlines task management and event updates for the SV campus. Accessible via web and mobile, it allows users to track tasks with photos, file attachments, or voice memos. The system also informs users about essential campus events, keeping them engaged and up-to-date.

# API Documentation
---

### 1. Upload File - `FileUploadAPIView`

**Endpoint**: `/upload/<studentEmail>`  
**Method**: `POST`

#### Request Example:
```json
{
    "file": "<base64_encoded_file_content>",
}
```

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "message": "Task and file created successfully.",
    "task": {
        "taskId": 1,
        "taskName": "CS5200 Homework",
        "description": "Generated Task Description",
        "entryDate": "2024-11-19",
        "dueDate": "2024-12-31"
    },
    "file": {
        "fileId": 1,
        "filePath": "/media/uploads/example_file.txt"
    }
  }
  ```

- **Failure (400 Bad Request)**:
  ```json
    {
      "error": "Unsupported file type"
    }
  ```

### 2. Task Info - `TaskDetailAPIView`

**Endpoint**: `/task/<studentEmail>/<taskId>`  
**Method**: `GET`  
**Permissions**: Public (accessible to anyone)  

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "taskId": 1,
    "taskName": "CS5200 HW",
    "description": "This is a task description",
    "entryDate": "2024-11-19",
    "dueDate": "2024-12-01",
    "taskStatus": "In process",
    "taskCategory": "Daily Schedule",
    "file": {
        "fileId": 3,
        "filePath": "/media/uploads/example_file.txt"
    }
  }
  ```

- **Failure (404 Not Found)**:
  ```json
  {
    "detail": "Not found."
  }
  ```

---

### 3. Update Task Descriptioin - `UpdateTaskAPIView`

**Endpoint**: `task/update/<studentEmail>/<taskId>`  
**Method**: `POST`

#### Request Example:
```json
{
    "taskName": "CS5200 HW",
    "description": "CS5200 Phase5",
    "dueDate": "2024-12-15",
    "taskStatus": "Completed",
    "taskCategory": "Course"
}
```

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "taskId": 1,
    "taskName": "CS5200 HW",
    "description": "Updated task description",
    "dueDate": "2024-12-01",
    "studentId": null,
    "entryDate": "2024-11-19",
    "taskStatus": "Completed",
    "taskCategory": "Course"
  }
  ```

- **Failure (400 Bad Request)**:
  ```json
  {
    "error": "Invalid date format. Use YYYY-MM-DD."
  }
  ```

- **Failure (404 Not Found)**:
  ```json
  {
    "detail": "Not found."
  }
  ```

---

### 4. Get All Tasks - `AllTasksAPIView`

**Endpoint**: `/tasks/<studentEmail>`  
**Method**: `GET`

#### Response:
- **Success (200 Ok)**:
  ```json
  {
    "tasks": [
        {
            "taskId": 1,
            "taskName": "CS5200 HW",
            "description": "Complete the project report",
            "entryDate": "2024-11-01",
            "dueDate": "2024-12-01",
            "taskStatus": "Completed",
            "taskCategory": "Course",
            "file": {
                "fileId": 10,
                "filePath": "/media/uploads/project_report.pdf"
            }
        },
        {
            "taskId": 2,
            "taskName": "CS5200 HW2",
            "description": "Review design document",
            "entryDate": "2024-11-05",
            "dueDate": null,
            "taskStatus": "Completed",
            "taskCategory": "Course",
            "file": null
        }
    ]
  }
  ```

---

### 5. Sort Task By Due Date in Asc or Desc - `SortTasksByDueDateAPIView`

**Endpoint**: `tasks/sort-due-date/<studentEmail>`  
**Method**: `GET`

#### Query Parameters:

- `order` (required): asc/desc.

#### Response:
- **Success (200 Ok)**:
  ```json
  {
    "tasks": [
        {
            "taskId": 1,
            "description": "Complete the project report",
            "entryDate": "2024-11-01",
            "dueDate": "2024-12-01",
            "file": {
                "fileId": 10,
                "filePath": "/media/uploads/project_report.pdf"
            }
        },
        {
            "taskId": 2,
            "description": "Review design document",
            "entryDate": "2024-11-05",
            "dueDate": null,
            "file": null
        }
    ]
  }
  ```
---

### 6. Sort Task By Entry Date in Asc or Desc - `SortTasksByEntryDateAPIView`

**Endpoint**: `tasks/sort-entry-date/<studentEmail>`  
**Method**: `GET`

#### Query Parameters:

- `order` (required): asc/desc.

#### Response:
- **Success (200 Ok)**:
  ```json
  {
    "tasks": [
        {
            "taskId": 1,
            "description": "Complete the project report",
            "entryDate": "2024-11-01",
            "dueDate": "2024-12-01",
            "file": {
                "fileId": 10,
                "filePath": "/media/uploads/project_report.pdf"
            }
        },
        {
            "taskId": 2,
            "description": "Review design document",
            "entryDate": "2024-11-05",
            "dueDate": null,
            "file": null
        }
    ]
  }
  ```
---
### 5. Filter Tasks by Category (`FilterTaskByCategoryView`)

**URL:** `tasks/filter-tasks/<studentEmail>`  
**Method:** `GET`  
**Description:** Filters tasks by category.

#### Query Parameters:

- `taskName` (optional): The name of the task to filter by.
- `entryDate` (optional): The entry date of the task in the format YYYY-MM-DD.
- `dueDate` (optional): The due date of the task in the format YYYY-MM-DD.
- `taskStatus` (optional): The status of the task. Valid values depend on the application configuration. Examples: In process, Completed, Overdue.
- `taskStatus` (optional): A list of task categories to filter by. Examples: Course, DailySchedule, Research, Meeting.

#### Response:

- **Success (200 Ok)**:

```json
{
  "success": true,
  "count": 2,
  "tasks": [
    {
      "taskName": "Homework",
      "studentEmail": "duo@example.com",
      "entryDate": "2023-12-01",
      "dueDate": "2023-12-10",
      "taskStatus": "In process",
      "taskCategory": "Research"
    },
    {
      "taskName": "Project",
      "studentEmail": "duo@example.com",
      "entryDate": "2023-12-02",
      "dueDate": "2023-12-12",
      "taskStatus": "Completed",
      "taskCategory": "Meeting"
    }
  ]
}
```

- **Failure (400 Bad Request)**:
```json
{
  "success": false,
  "message": "Missing required parameter: category."
}
```

- **Failure (500 Internal Server Error)**:
```json
{
  "success": false,
  "message": "An error occurred while filtering tasks.",
  "error": "(1054, \"Unknown column 'taskCategory' in 'field list'\")"
}
```

- **Failure (404 Not Found)**:
```json
{
  "detail": "Not found."
}
```

---

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

## Endpoints

### 1. User Registration (`SignUpView`)

**URL:** `/signup/`  
**Method:** `POST`  
**Description:** Registers a new user.

#### Request Body:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "password": "securepassword123",
  "role": "Student",
  "department": "Khoury"
}
```

#### Response:

**Success:**

```json
{
  "message": "success!"
}
```

**Error:**

```json
{
  "errors": {
    "field_name": ["Error message here."]
  }
}
```

---

### 2. User Login (`SignInView`)

**URL:** `/signin/`  
**Method:** `POST`  
**Description:** Authenticates a user.

#### Request Body:

```json
{
  "email": "john.doe@example.com",
  "password": "securepassword123"
}
```

#### Response:

**Success:**

```json
{
  "role": "Student",
  "message": "Successful login"
}
```

**Error:**

```json
{
  "error": "Invalid email or password"
}
```

---

### 3. Publish Event (`PublishEventView`)

**URL:** `/publish-event/`  
**Method:** `POST`  
**Description:** Publishes a new event. Admin role required.

#### Request Body:

```json
{
  "event_name": "AI Workshop",
  "event_description": "A hands-on workshop on Artificial Intelligence.",
  "event_location": "Room 101",
  "event_time": "2024-11-30T14:00:00Z",
  "event_category": "Workshop"
}
```

#### Response:

**Success:**

```json
{
  "success": true,
  "message": "Event published successfully!"
}
```

**Error:**

```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "field_name": ["Error message here."]
  }
}
```

---

### 4. List All Events (`ListEventView`)

**URL:** `/list-events/`  
**Method:** `GET`  
**Description:** Lists all events with optional sorting.

#### Query Parameters:

- `sort` (optional): Sorting parameter (`event_time`, `-event_time`, `event_created_at`, `-event_created_at`).

#### Response:

**Success:**

```json
{
  "success": true,
  "events": [
    {
      "event_id": 1,
      "event_name": "AI Workshop",
      "event_description": "A hands-on workshop on AI.",
      "event_location": "Room 101",
      "event_time": "2024-11-30T14:00:00Z",
      "event_status": "In process",
      "event_category": "Workshop",
      "event_published_by": "admin@example.com",
      "event_created_at": "2024-11-20T14:00:00Z"
    }
  ]
}
```

**Error:**

```json
{
  "success": false,
  "message": "Invalid sort parameter."
}
```

---

### 5. Filter Events by Category (`FilterEventByCategoryView`)

**URL:** `/filter-events/`  
**Method:** `GET`  
**Description:** Filters events by category.

#### Query Parameters:

- `category` (required): The category of events to filter by.

#### Response:

**Success:**

```json
{
  "success": true,
  "count": 2,
  "events": [
    {
      "event_id": 1,
      "event_name": "AI Workshop",
      "event_description": "A hands-on workshop on AI.",
      "event_location": "Room 101",
      "event_time": "2024-11-30T14:00:00Z",
      "event_status": "In process",
      "event_category": "Workshop",
      "event_published_by": "admin@example.com",
      "event_created_at": "2024-11-20T14:00:00Z"
    }
  ]
}
```

**Error:**

```json
{
  "success": false,
  "message": "Missing required parameter: category."
}
```

---

# Serializers Documentation

## File: `serializers.py`

This file contains serializer classes for the `User` and `Event` models, providing validation and transformation for API data.

---

## 1. **SignupSerializer**

This serializer is used to validate and create a new user when a user signs up.

### Fields:

- **email** (required): The user's email address. It must be unique.
- **password** (required, write-only): The user's password. It will not be serialized in responses.
- **role** (required): The user's role. Possible values: `Student`, `Admin`.
- **first_name** (optional): The user's first name.
- **last_name** (optional): The user's last name.
- **department** (required): The user's department. Possible values: `Khoury`, `COE`.

### Validation Rules:

1. **Email Validation**:
   - Checks if the provided email already exists in the database.
   - Raises a `ValidationError` with the message `"Email already exists."` if the email is not unique.

### Methods:

1. **`validate_email(self, value)`**:

   - Validates the uniqueness of the email field.

2. **`create(self, validated_data)`**:
   - Creates a new `User` instance using the validated data.

---

## 2. **EventSerializer**

This serializer is used to validate and represent event data.

### Fields:

- **event_id** (read-only): The unique identifier of the event.
- **event_name** (required): The name of the event.
- **event_description** (required): A detailed description of the event.
- **event_location** (required): The location where the event will take place.
- **event_time** (required): The time when the event is scheduled. It must be in ISO 8601 format.
- **event_status** (read-only, default: `In process`): The current status of the event.
- **event_category** (required): The category of the event. Possible values:
  - `Workshop`
  - `Career Fair`
  - `Conference`
  - `Culture Festival`
  - `Volunteer`
  - `Opportunity`

### Validation Rules:

1. All required fields must be provided.
2. **DateTime Field**:
   - Ensures `event_time` is a valid datetime in ISO 8601 format.

---

##

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

## User Model

| Field Name | Field Type               | Additional Information                            |
| ---------- | ------------------------ | ------------------------------------------------- |
| first_name | CharField                | max_length=50                                     |
| last_name  | CharField                | max_length=50                                     |
| email      | EmailField (Primary Key) | Primary Key                                       |
| password   | CharField                | max_length=20                                     |
| role       | CharField (Choices)      | Choices: ['Student', 'Admin'], Default='Student'  |
| department | CharField (Choices)      | Choices: ['Khoury', 'COE'], Default='Khoury'      |
| created_at | DateTimeField            | Auto-generated timestamp when the user is created |

---

## Event Model

| Field Name         | Field Type                              | Additional Information                                                                                                   |
| ------------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| event_id           | AutoField (Primary Key)                 | Auto Increment                                                                                                           |
| event_name         | CharField                               | max_length=255                                                                                                           |
| event_description  | TextField                               | Detailed event description                                                                                               |
| event_location     | CharField                               | max_length=255                                                                                                           |
| event_time         | DateTimeField                           | ISO 8601 format                                                                                                          |
| event_published_by | ForeignKey to User (on_delete=SET_NULL) | If User deleted, set to NULL                                                                                             |
| event_status       | CharField (Choices)                     | Default='In process'                                                                                                     |
| event_category     | CharField (Choices)                     | Default='Conference', Choices: ['Workshop', 'Career Fair', 'Conference', 'Culture Festival', 'Volunteer', 'Opportunity'] |

---

## Relationships

- A `User` can publish multiple events (`One-to-Many` relationship via `ForeignKey` in `Event`).
- If the `User` is deleted, events they published will remain, but the `event_published_by` field will be set to `NULL`.

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