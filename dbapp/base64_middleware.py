import base64
import json
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from dbapp.models import User

class Base64Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Basic '):
            base64_message = auth_header.split(' ')[1]
            try:
                decoded_bytes = base64.b64decode(base64_message)
                decoded_str = decoded_bytes.decode('utf-8')
                email, password = decoded_str.split(':', 1)
                try:
                    validate_email(email)
                except ValidationError:
                    return JsonResponse({"error": "Invalid email format"}, status=400)
                request.auth_email = email
                request.auth_password = password
                
                try:
                    user = User.objects.get(email=email)
                    if user.password == password:  
                        request.user = user
                    else:
                        return JsonResponse({"error": "Invalid email or password"}, status=401)
                except User.DoesNotExist:
                    return JsonResponse({"error": "User does not exist"}, status=404)
            except (base64.binascii.Error, UnicodeDecodeError, ValueError):
                return JsonResponse({"error": "Invalid Basic Authentication header"}, status=400)

        if request.method == "POST" and request.content_type == "application/json":
            try:
                body = json.loads(request.body)
                if "base64_data" in body:
                    decoded_data = base64.b64decode(body["base64_data"]).decode('utf-8')
                    request.decoded_body_data = decoded_data
            except (json.JSONDecodeError, base64.binascii.Error, UnicodeDecodeError):
                pass
        response = self.get_response(request)
        return response