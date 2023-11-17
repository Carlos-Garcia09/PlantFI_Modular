from django.shortcuts import render
import torch
import torchvision
from app.utils import load_model
from django.core.files.storage import FileSystemStorage
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import json
from torchvision.models import resnet18
import torch.nn.functional as F
from django.http import HttpResponse
import re
import os

# Carga del modelo pre-entrenado
filename = 'results/xp1/xp1_weights_best_acc.tar'  # Ruta del modelo pre-entrenado
use_gpu = True  # Cargar pesos en la GPU si está disponible
model = resnet18(num_classes=1081)  # 1081 clases en Pl@ntNet-300K

# Funciones de utilidad
load_model(model, filename, False)
model.eval()

# Vistas de Django
def index(request):
    return render(request, 'index.html')

def about(request):
    if request.method == 'GET':
        return render(request, 'about.html')
    elif request.method == 'POST':
        # Handle file upload
        imagefile= request.FILES['imagefile']
        image_recov = "img/" + imagefile.name
        image_path = "static/img/" + imagefile.name
        image_data = imagefile.read()  # Get the image data from the InMemoryUploadedFile
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
            # Open and preprocess the image
        image = Image.open(image_path)
        preprocess = transforms.Compose([transforms.Resize(256),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

        input_tensor = preprocess(image)
        input_tensor = input_tensor.unsqueeze(0)  # Add a batch dimension

        # Pass the preprocessed image through your PyTorch model to obtain the model's output.
        with torch.no_grad():
            output = model(input_tensor)
        
        probabilities = F.softmax(output, dim=1)  # Apply softmax

        _, predicted_class = probabilities.max(1)
        
        with open('order_DataSet.json', 'r') as json_file:
            data = json.load(json_file)
        
        if str(predicted_class.item()) in data:
            classification = data[str(predicted_class.item())]['plant_name']
        
        else:
            print("Predicted class not found in the JSON data.")

        return render(request, 'about.html', {'prediction': classification, 'image_path': image_recov}) 
