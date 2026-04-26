"""
api/index.py — Entrypoint para Vercel Serverless Functions
===========================================================
A Vercel executa a partir da raiz do projeto, então precisamos
ajustar o sys.path para encontrar os módulos do backend.
"""
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Importar o app Flask do backend
from app import app

# Handler que a Vercel espera
handler = app
