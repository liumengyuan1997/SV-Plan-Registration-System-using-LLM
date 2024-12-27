import openai
from PyPDF2 import PdfReader
from PIL import Image
from docx import Document
import pytesseract
from dateutil.parser import parse
from .models import Task, UploadedFile
from datetime import datetime
from django.shortcuts import get_object_or_404
from google.cloud import vision


openai.api_key = "openAI key"
def process_file_content(file, content_type):
    if file.name.endswith('.txt'):
        return file.read().decode('utf-8')
    elif file.name.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        return ''.join(page.extract_text() for page in pdf_reader.pages)
    elif file.name.endswith('.docx'):
        doc = Document(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    elif content_type.startswith('image/'):
        content = file.read()
        image = vision.Image(content=content)
        vision_client = vision.ImageAnnotatorClient()
        response = vision_client.text_detection(image=image)
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        texts = response.text_annotations
        return texts[0].description if texts else None
    else:
        return None

def generate_task_description_and_due_date(content):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that generates task descriptions and extracts due dates based on input content."},
            {"role": "user", "content": f"Analyze the following content and return a task name, task description, and a due date (if present):\n\n{content}"}
        ]
    )

    gpt_response = response["choices"][0]["message"]["content"]
    print(gpt_response)

    task_name = ""
    task_description = ""
    due_date = None

    lines = gpt_response.split('\n')
    for line in lines:
        if line.lower().startswith("task name:"):
            task_name = line.split(":", 1)[1].strip()
        elif line.lower().startswith("task description:"):
            task_description = line.split(":", 1)[1].strip()
        elif line.lower().startswith("due date:"):
            due_date_str = line.split(":", 1)[1].strip()
            try:
                due_date = parse(due_date_str).date()
            except:
                due_date = None

    return task_name, task_description, due_date

def task_detail_data(task_id):
    """Helper function to get task detail data."""
    task = get_object_or_404(Task, pk=task_id)
    uploaded_file = UploadedFile.objects.filter(taskId=task).first()

    return {
        'taskId': task.taskId,
        'taskName': task.taskName,
        'description': task.description,
        'entryDate': task.entryDate.strftime('%Y-%m-%d') if task.entryDate else None,
        'dueDate': task.dueDate.strftime('%Y-%m-%d') if task.dueDate else None,
        'taskStatus': task.taskStatus,
        'taskCategory': task.taskCategory,
        'file': None if not uploaded_file else {
            'fileId': uploaded_file.fileId,
            'filePath': uploaded_file.file.url
        }
    }

def validate_date(date_string):
    if not date_string:  # Check if the date_string is None or empty
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")