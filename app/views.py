from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
from django.http import HttpResponse, HttpResponseBadRequest
import re
import os

from plant_info import obtener_nombre_comun, obtener_descripcion, obtener_cuidados

from django.conf import settings

# Login y logout
from django.contrib.auth import login, authenticate
from .forms import LoginForm, UserProfileForm, SignUpForm, BitacoraForm
from django.contrib import messages
from django.contrib.auth import logout

from .models import Bitacora, Planta

from social_django.utils import psa
from social_django.views import auth as social_auth

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404




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

def analisis(request):
    api_key = settings.OPENAI_API_KEY
    if request.method == 'GET':
        return render(request, 'analisis.html')
    elif request.method == 'POST':
        if 'imagefile' not in request.FILES:
            return HttpResponseBadRequest("Por favor, sube una imagen.")

        # Handle file upload
        imagefile = request.FILES['imagefile']
        imagefile_extension = imagefile.name.split('.')[-1].lower()

        if imagefile_extension not in ['jpg', 'jpeg']:
            return HttpResponseBadRequest("Por favor, sube una imagen con extensión JPG.")

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
        
        probabilities = F.softmax(output, dim=1) # esto significa que la suma de las probabilidades de todas las clases es 1

        _, predicted_class = probabilities.max(1) # devuelve la clase con la probabilidad más alta

        # Probabilidad de que sea la planta correcta:
        # Probabilidad asociada con la clase
        predicted_probability = torch.gather(probabilities, 1, predicted_class.view(-1, 1))
        #Probabilidad a porcentaje
        predicted_percentage = predicted_probability.item() * 100
        # Imprimimos la probabilidad en consola
        print("Probabilidad de que sea la planta correcta: ", predicted_percentage, "%")
        # Umbral de probabilidad (70% en este caso)
        probability_threshold = 70
        
        with open('order_DataSet.json', 'r') as json_file:
            data = json.load(json_file)
        

        # Dentro de la condición, si es true, entonces la planta está en el dataset y se puede mostrar la información
        #if str(predicted_class.item()) in data:
        if predicted_percentage >= probability_threshold and str(predicted_class.item()) in data:
            # Si no está autenticado, solo retorna prediction y image_path
            if not request.user.is_authenticated:
                return render(request, 'analisis.html', {
                    'prediction': data[str(predicted_class.item())]['plant_name'],
                    'image_path': image_recov,
                })
            classification = data[str(predicted_class.item())]['plant_name']

            # Obtén el nombre común, la descripción y los cuidados de la planta a partir de su nombre científico
            common_name = obtener_nombre_comun(classification)
            description = obtener_descripcion(classification)
            care = obtener_cuidados(classification)

            # Dividir la cadena de cuidados en una lista
            # care_list = care.split('-') if care else []
            care_list = [item.strip() for item in care.split('-') if item.strip()]

            # Eliminar el primer elemento vacío si existe
            if care_list and not care_list[0]:
                care_list.pop(0)
            

            # Renderiza la página con la información de la planta, es decir, que se muestre la imagen, el nombre común, la descripción y los cuidados
            return render(request, 'analisis.html', {
                'prediction': classification,
                'image_path': image_recov,
                'common_name': common_name,
                'description': description,
                'care': care,
                'care_list': care_list,
            })
            
        else:
            print("No se encontró la planta, prueba otra vez.")
            return render(request, 'analisis.html', {'error_message': 'La probabilidad es baja. Por favor, intenta de nuevo con otra foto.'})
        

def add_plant(request):
    if request.method == 'POST':
        # Asegúrate de que el usuario esté autenticado
        if request.user.is_authenticated:
            plant_name = request.POST['plant_name']
            common_name = request.POST['common_name']
            image_path = request.POST['image_path']
            description = request.POST['description']
            care = request.POST['care']
            
            # Obtén el usuario autenticado
            user = request.user
            # Crea una nueva planta con la información obtenida
            new_plant = Planta(usuario=user, nombre_cientifico=plant_name, nombre_comun=common_name, imagen=image_path, descripcion=description, cuidados=care)
            new_plant.save()
            # Redirige a la página de inicio
            return redirect('mi_jardin')
        else:
            # Si el usuario no está autenticado, redirige a la página de inicio de sesión
            return redirect('login')
    else:
        return HttpResponse('Método no permitido.')
    
def mi_jardin(request):
    # Asegúrate de que el usuario esté autenticado
    if request.user.is_authenticated:
        # Obtén el usuario actual
        user = request.user

        # Obtén las plantas asociadas al usuario actual
        plantas = Planta.objects.filter(usuario=user)

        # Impresión de depuración en la consola
        print("Usuario:", user)
        print("Plantas:", plantas)

        # Envía las plantas al contexto del template
        return render(request, 'mi_jardin.html', {'plantas': plantas})
    else:
        # Si el usuario no está autenticado, redirige a la página de inicio de sesión
        return redirect('login')
    
def detalle_planta(request, id_planta):
    # Asegúrate de que el usuario esté autenticado
    if request.user.is_authenticated:
        # Obtén el usuario actual
        user = request.user

        # Obtén la planta con el id dado
        planta = Planta.objects.get(id=id_planta)

        # Impresión de depuración en la consola
        # print("Usuario:", user)
        # print("Planta:", planta)

        # Campo para almacenar la lista de cuidados
        # cuidados = ArrayField(models.CharField(max_length=200, blank=True), blank=True)

        # Dividir la cadena de cuidados en una lista ;
        cuidados = planta.cuidados.split('-') if planta.cuidados else []
        # Eliminar el primer elemento vacío si existe
        cuidados.pop(0)

        # Envía la planta al contexto del template
        return render(request, 'detalle_planta.html', {'planta': planta, 'cuidados': cuidados})
    else:
        # Si el usuario no está autenticado, redirige a la página de inicio de sesión
        return redirect('login')
    



@login_required
def bitacora_planta(request, planta_id):
    planta = get_object_or_404(Planta, id=planta_id)
    bitacoras_planta = Bitacora.objects.filter(planta=planta)

    if request.method == 'POST':
        form = BitacoraForm(request.POST, request.FILES)
        if form.is_valid():
            bitacora = form.save(commit=False)
            bitacora.planta = planta
            bitacora.save()
            return redirect('bitacora_planta', planta_id=planta_id)
    else:
        form = BitacoraForm()

    return render(request, 'bitacora_planta.html', {'planta': planta, 'bitacoras_planta': bitacoras_planta, 'form': form})

def eliminar_bitacora(request, id_bitacora):
    # Obtén la bitácora con el id dado
    bitacora = Bitacora.objects.get(id=id_bitacora)

    # Obtén el ID de la planta asociada a la bitácora
    planta_id = bitacora.planta.id

    # Elimina la bitacora
    bitacora.delete()

    # Redirige a la página de bitacora_planta con el parámetro planta_id
    return redirect(reverse('bitacora_planta', kwargs={'planta_id': planta_id}))    
        
def eliminar_planta(request, id_planta):
    # Asegúrate de que el usuario esté autenticado
    if request.user.is_authenticated:
        # Obtén el usuario actual
        user = request.user

        # Obtén la planta con el id dado
        planta = Planta.objects.get(id=id_planta)

        # Elimina la planta
        planta.delete()

        # Redirige a la página de mi_jardin
        return redirect('mi_jardin')
    else:
        # Si el usuario no está autenticado, redirige a la página de inicio de sesión
        return redirect('login')


def user_logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('index')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('index')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
                form.add_error('username', 'Introduce un nombre de usuario válido.')
                form.add_error('password', 'Introduce una contraseña válida.')
                
        else:
            messages.error(request, 'Verifica los campos del formulario.')
    else:
        form = LoginForm()

    return render(request, 'login2.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)
            user.save()

            # Autentica al usuario utilizando el backend predeterminado
            authenticated_user = authenticate(request, username=user.username, password=user_form.cleaned_data['password1'])
            login(request, authenticated_user)

            messages.success(request, 'Registro exitoso.')
            return redirect('index')
    else:
        user_form = SignUpForm()
        profile_form = UserProfileForm()

    return render(request, 'register2.html', {'user_form': user_form, 'profile_form': profile_form})


def login_with_google(request):
    """Initiate the Google OAuth login."""
    # If the user is already authenticated, redirect to the desired page
    if request.user.is_authenticated:
        return redirect('index')  # Replace 'index' with the URL you want to redirect to

    # Redirect the user to the Google OAuth login page
    return social_auth(request, backend='google-oauth2')

@psa('social:complete')
def complete_google_auth(request, backend):
    
    if request.user.is_authenticated:
        # Si el usuario ya está autenticado, redirige a la página deseada
        return redirect('index')  # Reemplaza 'index' con la URL a la que deseas redirigir después de la autenticación

    email = request.backend.do_auth(request.user).email
    user = authenticate(request, username=email, password=None)

    if user is not None:
        login(request, user)
        return redirect('index')  # Reemplaza 'index' con la URL a la que deseas redirigir después de la autenticación
    return redirect('login')
