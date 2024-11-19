# SV-Plan-Registration-System-using-LLM
The SV Plan Registration System, managed by Khoury College, streamlines task management and event updates for the SV campus. Accessible via web and mobile, it allows users to track tasks with photos, file attachments, or voice memos. The system also informs users about essential campus events, keeping them engaged and up-to-date.

# API Documentation
---

### 1. Upload File - `FileUploadAPIView`

**Endpoint**: `/upload/`  
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

**Endpoint**: `/task/<taskId>`  
**Method**: `GET`  
**Permissions**: Public (accessible to anyone)  

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "taskId": 1,
    "description": "This is a task description",
    "entryDate": "2024-11-19",
    "dueDate": "2024-12-01",
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

**Endpoint**: `task/update/<taskId>`  
**Method**: `POST`

#### Request Example:
```json
{
    "description": "CS5200 Phase5",
    "dueDate": "2024-12-15"
}
```

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "taskId": 1,
    "description": "Updated task description",
    "dueDate": "2024-12-01",
    "studentId": null,
    "entryDate": "2024-11-19"
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

**Endpoint**: `/tasks`  
**Method**: `GET`

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

### 5. Sort Task By Due Date in Asc or Desc - `SortTasksByDueDateAPIView`

**Endpoint**: `tasks/sort-due-date/<order=asc/desc>`  
**Method**: `GET`

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

**Endpoint**: `tasks/sort-entry-date/<order=asc/desc>`  
**Method**: `GET`

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