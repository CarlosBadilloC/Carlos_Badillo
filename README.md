# Carlos_Badillo

# Agente IA para Odoo 19


<img src="https://img.shields.io/badge/Odoo-19.0-blue.svg" alt="Odoo Version">

<img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">

<img src="https://img.shields.io/badge/License-LGPL--3-purple.svg" alt="License">


## Módulo de integración de Inteligencia Artificial para Odoo 19 que proporciona un asistente virtual especializado en gestión de inventario y CRM con soporte para LiveChat.

### 📋 Tabla de Contenidos


Características
Requisitos
Instalación
Configuración
Uso
Funcionalidades
Arquitectura
Ejemplos
Solución de Problemas
Contribuir
Licencia



### 🚀 Características


Gestión de Inventario
✅ Consulta de stock en tiempo real
✅ Búsqueda inteligente de productos por nombre, descripción o categoría
✅ Detección automática de productos con stock bajo
✅ Resúmenes completos del inventario
✅ Búsqueda por categorías
✅ Cálculo de valor total del inventario
Gestión de CRM
✅ Creación de leads y oportunidades
✅ Consulta de información de leads/oportunidades
✅ Listado de oportunidades abiertas
✅ Resumen del pipeline por etapas
✅ Búsqueda de leads por etapa
✅ Consulta de cotizaciones con verificación de stock
Integración con LiveChat
✅ Respuestas automáticas en tiempo real
✅ Procesamiento de lenguaje natural
✅ Detección inteligente de intenciones
✅ Soporte multicanal



### 📦 Requisitos



**🧠Dependencias de Odoo**


'base'
'mail'
'product'
'stock'
'ai'
'crm'
'sale'
'website'
'im_livechat'


**🧠Dependencias de Python**


google-generativeai>=0.3.0
protobuf>=3.20.0
google-api-core>=2.11.0
google-auth>=2.16.0
grpcio>=1.48.0
requests>=2.28.0


**🧠Versiones**


Odoo: 19.0+
Python: 3.10+
PostgreSQL: 12+



### 🔧 Instalación


-Clonar el Repositorio


git clone https://github.com/yourusername/modulo.git


-Instalar Dependencias Python


pip install -r requirements.txt


-Actualizar Lista de Aplicaciones


Accede a Odoo:

1. Ve a Aplicaciones
2. Haz clic en Actualizar lista de aplicaciones
3. Busca "Agente AI"
4. Haz clic en Instalar
