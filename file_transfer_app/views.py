from django.shortcuts import render

# Create your views here.
# file_transfer_app/views.py

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import paho.mqtt.publish as publish
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import json

from .models import FileTransfer

@csrf_exempt
# @require_POST
# def upload_file(request):
#     file = request.FILES['file']
#     file_obj = FileTransfer.objects.create(file=file)
    
#     # Publish file information to MQTT topic
#     mqtt_message = json.dumps({
#         'file_path': file_obj.file.url,
#         'uploaded_at': str(file_obj.uploaded_at),
#     })
#     publish.single('thetr619@gmail.com/firmware', mqtt_message, hostname='maqiatto.com')

#     return HttpResponse('File uploaded successfully.')

def upload_file(request):
    if request.method == 'GET':
        # Handle GET requests (if needed)
        return render(request, 'upload_file.html')
    elif request.method == 'POST':
        if 'file' not in request.FILES:
            return HttpResponse('No file selected.', status=400)

        file = request.FILES['file']
        file_obj = FileTransfer.objects.create(file=file)

        # Get the file path
        file_path = file_obj.file.path

        # Read and publish each line as a separate message
        with open(file_path, 'r') as file_content:
            for line in file_content:
                # Remove leading and trailing whitespaces from the line
                cleaned_line = line.strip()
                encrypted_line = encrypt_aes(cleaned_line.encode())
                ascii_line = encrypted_line.decode('ascii', errors='ignore')
                mqtt_message = ascii_line
                publish.single('thetr619@gmail.com/firmware', mqtt_message, hostname='maqiatto.com', port=1883, auth={'username': 'thetr619@gmail.com', 'password': 'Room@Temp555'})

        return HttpResponse('File content uploaded successfully.')
        
    else:
        return HttpResponse('Method not allowed.', status=405)


def home(request):
    return HttpResponse("Welcome to the File Transfer App!")


def encrypt_aes(data):
    key = b'112ABCDEFGHI12312313310101010101'  # 32 bytes for AES-256
    nonce = b'122Y122X122Z122E'  # 16 bytes for AES-GCM

    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    # Append the authentication tag to the ciphertext
    encrypted_data = ciphertext + encryptor.tag
    return encrypted_data