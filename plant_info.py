import requests
from bs4 import BeautifulSoup

# OpenAI
import openai
import re

# Reemplaza la api_key con tu propia clave
openai.api_key = "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"

def obtener_descripcion(classification):
    prompt = f"Descripción de la planta {classification}(max 80 palabras): "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=170,
    )
    return response['choices'][0]['message']['content'].strip()

def obtener_nombre_comun(classification):
    prompt = f"Escribe solo el nombre común de {classification}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=100,
    )
    return response['choices'][0]['message']['content'].strip()

def obtener_cuidados(classification):
    prompt = f"Cuidados más importantes de la planta {classification} (ubicación, riego, suelo, fertilización, poda, protección de plagas y enfermedades). Separa la lista de cuidados por guiones '-' y trata que sean máximo 180 palabras"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=450,
    )
    return response['choices'][0]['message']['content'].strip()
