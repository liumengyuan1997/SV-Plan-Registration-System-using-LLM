# SV-Plan-Registration-System-using-LLM
The SV Plan Registration System, managed by Khoury College, streamlines task management and event updates for the SV campus. Accessible via web and mobile, it allows users to track tasks with photos, file attachments, or voice memos. The system also informs users about essential campus events, keeping them engaged and up-to-date.

# API Documentation
---

### 1. Upload File - `UploadFileView`

**Endpoint**: `/upload/`  
**Method**: `POST`

#### Request Example:
```json
{
    "file": "file",
}
```

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "message": "Task and file created successfully.",
    "task": {
        "taskId": task.taskId,
        "description": task.description,
        "entryDate": task.entryDate,
        "dueDate": task.dueDate
    },
    "file": {
        "fileId": uploaded_file.fileId,
        "filePath": uploaded_file.file.url
    }
  }
  ```

- **Failure (400 Bad Request)**:
  ```json
  {
      "error": "Unsupported file type"
  }
  ```

### 2. Task Info - `TaskInfoView`

**Endpoint**: `/task/taskId`  
**Method**: `GET`  
**Permissions**: Public (accessible to anyone)  

#### Response:
- **Success (200 OK)**:
  ```json
  {
    "taskId": "task.taskId",
    "description": "task.description",
    "entryDate": "task.entryDate",
    "dueDate": "task.dueDate",
    "file": "None if not uploaded_file else {
        'fileId': uploaded_file.fileId,
        'filePath': uploaded_file.file.url
    }"
  }
  ```

- **Failure (404 Not Found)**:

---

### 3. Update Task Descriptioin - `UpdateTaskDescriptionView`

**Endpoint**: `/update/taskId`  
**Method**: `POST`

#### Request Example:
```json
{
    "description": "CS5200 Phase5",
    "dueDate": "2024-12-15"
}
```

#### Response:
- **Success (201 Created)**:
  ```json
  {
    "taskId": "task.taskId",
    "description": "task.description",
    "dueDate": "task.dueDate",
    "studentId": "task.studentId",
    "entryDate": "task.entryDate",
  }
  ```

- **Failure (404)**:
  ```json
  if task not exist
  ```

- **Failure (405)**:
  ```json
  if method is get
  ```

---

### 4. Get All Tasks - `AllTasksView`

**Endpoint**: `/alltasks`  
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

- **Failure (405)**:
  ```json
  if method is gost
  ```

---

### 5. Sort Task By Due Date in Asc or Desc - `SortTasksbyDDL`

**Endpoint**: `/task/sortbyduedate/`  
**Method**: `GET`
#### Request Example:
```json
{
    "order": "asc/desc",
}
```
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

- **Failure (405)**:
  ```json
  if method is gost
  ```
---

### 6. Sort Task By Entry Date in Asc or Desc - `SortTasksbyEntry`

**Endpoint**: `/task/sortbyentrydate/`  
**Method**: `GET`
#### Request Example:
```json
{
    "order": "asc/desc",
}
```
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

- **Failure (405)**:
  ```json
  if method is gost
  ```