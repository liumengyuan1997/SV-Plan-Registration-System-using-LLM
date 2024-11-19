import openai
from PyPDF2 import PdfReader
from PIL import Image
from docx import Document
import pytesseract
from dateutil.parser import parse

openai.api_key = "sk-F26KW4HCJiSlbCfhR1XnyyKf11QnvbUN7lD0ZBYSgbT3BlbkFJs9TZ5gsij14tIJNLk_G__1-aEnKWzF4qA7V81-zGoA"
def process_file_content(file):
    if file.name.endswith('.txt'):
        return file.read().decode('utf-8')
    elif file.name.endswith('.pdf'):
        pdf_reader = PdfReader(file)
        return ''.join(page.extract_text() for page in pdf_reader.pages)
    elif file.name.endswith('.docx'):
        doc = Document(file)
        return '\n'.join([p.text for p in doc.paragraphs])
    elif file.content_type.startswith('image/'):
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    else:
        return None

def generate_task_description_and_due_date(content):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that generates task descriptions and extracts due dates based on input content."},
            {"role": "user", "content": f"Analyze the following content and return a task description and a due date (if present):\n\n{content}"}
        ]
    )

    gpt_response = response["choices"][0]["message"]["content"]
    print(gpt_response)

    task_description = ""
    due_date = None

    lines = gpt_response.split('\n')
    for line in lines:
        if line.lower().startswith("task description:"):
            task_description = line.split(":", 1)[1].strip()
        elif line.lower().startswith("due date:"):
            due_date_str = line.split(":", 1)[1].strip()
            try:
                due_date = parse(due_date_str).date()  # 使用 dateutil 解析日期
            except:
                due_date = None

    return task_description, due_date