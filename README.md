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