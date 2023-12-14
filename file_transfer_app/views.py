# Create your views here.
# file_transfer_app/views.py


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from .models import FileTransfer

CipheredPassword = "QDwcg{dw`wiSbbX{d⌂isdwGbvsfwQQX\"FRQ"

@csrf_exempt
def upload_file(request):
    if request.method == 'GET':
        # Handle GET requests (if needed)
        return render(request, 'upload_file.html')
    
    elif request.method == 'POST':
        # if no file has uploaded and an upload request ran
        if 'file' not in request.FILES: 
            return HttpResponse('No file selected.', status=400)
        
        file = request.FILES['file']
        file_obj = FileTransfer.objects.create(file=file)

        # Get the file path
        file_path = file_obj.file.path

        # Send the ecrypted password (Hash)
        publish.single(
                    client_id='server',
                    topic='ntigraduationserver@gmail.com/FOTA',
                    keepalive=120,
                    payload=CipheredPassword, 
                    qos=2, 
                    retain=False, 
                    hostname='maqiatto.com',
                    port=1883, 
                    auth={'username': 'ntigraduationserver@gmail.com', 'password': 'Server'})

        # For debug purposes
        print("Password Sent")

        # Wait until receives the respond 
        Response = subscribe.simple(
                    client_id='server',
                    topics='ntigraduationserver@gmail.com/FOTA',
                    keepalive=120, 
                    qos=2, 
                    retained=False, 
                    hostname='maqiatto.com',
                    port=1883, 
                    auth={'username': 'ntigraduationserver@gmail.com', 'password': 'Server'})
        
        print("Response get: " + str(Response.payload.decode('ascii',errors='ignore')))

        # If the response is "P" then skip the next line, else retrun an HTTP response and exit the function.
        if Response != "P":
            return HttpResponse("Error: Security Access Denied.",status=406)
        
        # Defining a variable to count the number of records published
        i = 0
        
        # Read and publish each line as a separate message
        with open(file_path, 'r') as file_content:    # open file as read
            for line in file_content:                 # loop for each line
                # Increment the counter
                i += 1

                # Remove leading and trailing whitespaces from the line
                cleaned_line = line.strip()   
                
                # Assign the record to the payload variable
                mqtt_message = cleaned_line
                
                # Publish the record (payload) to the MQTT broker.
                publish.single(
                    client_id='server',
                    topic='ntigraduationserver@gmail.com/FOTA',
                    keepalive=120,
                    payload=mqtt_message, 
                    qos=2, 
                    retain=False, 
                    hostname='maqiatto.com',
                    port=1883, 
                    auth={'username': 'ntigraduationserver@gmail.com', 'password': 'Server'})
                
                # Print the published record line number
                print("+++ Record Sent +++")
                print("line: " + str(i))

        # Render the successful page
        return render(request, 'upload_file success.html')
        
    else:
        return HttpResponse('Method not allowed.', status=405)


def home(request):
    return render(request, 'LOGIN FORM.HTML')
