# Carlos_Badillo

# Agente IA para Odoo 19


<img src="https://img.shields.io/badge/Odoo-19.0-blue.svg" alt="Odoo Version">

<img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">

<img src="https://img.shields.io/badge/License-LGPL--3-purple.svg" alt="License">


## Módulo de integración de Inteligencia Artificial para Odoo 19 que proporciona un asistente virtual especializado en gestión de inventario y CRM con soporte para LiveChat.

### 📋 Tabla de Contenidos


- Características
- Requisitos
- Instalación
- Configuración
- Uso
- Funcionalidades
- Arquitectura



### 🚀 Características


- Gestión de Inventario
	- ✅ Consulta de stock en tiempo real
	- ✅ Búsqueda inteligente de productos por nombre, descripción o categoría
	- ✅ Detección automática de productos con stock bajo
	- ✅ Resúmenes completos del inventario
	- ✅ Búsqueda por categorías
	- ✅ Cálculo de valor total del inventario
- Gestión de CRM
	- ✅ Creación de leads y oportunidades
	- ✅ Consulta de información de leads/oportunidades
	- ✅ Listado de oportunidades abiertas
	- ✅ Resumen del pipeline por etapas
	- ✅ Búsqueda de leads por etapa
	- ✅ Consulta de cotizaciones con verificación de stock
- Integración con LiveChat
	- ✅ Respuestas automáticas en tiempo real
	- ✅ Procesamiento de lenguaje natural
	- ✅ Detección inteligente de intenciones



### 📦 Requisitos



- **🧠Dependencias de Odoo**


	- 'base'
	- 'mail'
	- 'product'
	- 'stock'
	- 'ai'
	- 'crm'
	- 'sale'
	- 'website'
	- 'im_livechat'


- **🧠Dependencias de Python**

	
	- google-generativeai>=0.3.0
	- protobuf>=3.20.0
	- google-api-core>=2.11.0
	- google-auth>=2.16.0
	- grpcio>=1.48.0
	- requests>=2.28.0


- **🧠Versiones**


	- Odoo: 19.0+
	- Python: 3.10+
	- PostgreSQL: 12+



### 🔧 Instalación


- Clonar el Repositorio


  - git clone https://github.com/yourusername/modulo.git


- Instalar Dependencias Python


  - pip install -r requirements.txt


- Actualizar Lista de Aplicaciones


  - Accede a Odoo:

    1. Ve a Aplicaciones
    2. Haz clic en Actualizar lista de aplicaciones
    3. Busca "Agente AI"
    4. Haz clic en Instalar



### ⚙️ Configuración
- Configurar API Key
  - Navega a:
      Configuración → Configuración General → AI Configuration


  - AI API Key: [Tu clave de API de Google Gemini/OpenAI]
    
- Activar Integración con LiveChat
  - *Se debe configurar en la página web a utilizar*



- Configurar Agente IA
  - El agente "AI Asistente Integral" se crea automáticamente con:

    1. Nombre: AI Asistente Integral
    2. Estado: Activo
    3. Estilo de respuesta: Balanced
    4. System Prompt: Configurado para inventario y CRM
   

### 📖 Uso


- Integración con LiveChat
  - *El asistente responde automáticamente en LiveChat cuando detecta mensajes de usuarios.*

  - 💡 Ejemplos de consultas:
    1. 🔍 Cotizaciones:
    	Usuario: "¿Hay cotizaciones para pelotas?"
      	Bot: Muestra cotizaciones con verificación de stock
    2. ⚠️ Stock bajo:
    	Usuario: "productos con stock bajo"
      	Bot: Reporta productos bajo el umbral configurado
    3. 📦 Consultar stock:
    	Usuario: "busco sillas de oficina"
      	Bot: Lista todos los productos relacionados con stock y precios

### 🎯 Funcionalidades


- **Acciones de Inventario**


	 | Función| Descripción | Modelo |
	 |----------|-----------|-----------|
	 | get_stock()   | Obtiene stock de productos    | ai.inventory.actions   |
	 |search_products_detailed()   | Búsqueda avanzada con detalles   | ai.inventory.actions   |
	 | check_low_stock()   | Detecta productos con poco stock| ai.inventory.actions    |
	 | get_inventory_summary()   | Resumen completo del inventario   | 	ai.inventory.actions   |
	 | search_product_by_category()  | Búsqueda por categoría    |ai.inventory.actions    |

		
		
- **Acciones de CRM**


	 | Función| Descripción | Modelo |
	 |----------|-----------|-----------|
	 | create_opportunity()   |Crea nueva oportunidad   |ai.crm.actions   |
	 |create_lead()   | Crea nuevo lead   | 	ai.crm.actions   |
	 | get_lead_info()  | Obtiene información de lead| ai.crm.actions    |
	 |list_open_opportunities()   | Lista oportunidades abiertas   | 		ai.crm.actions  |
	 | get_pipeline_summary()  | 	Resumen del pipeline    |ai.crm.actions    |
	 |search_quotations_with_stock()  | 	Busca cotizaciones con stock    | ai.crm.actions   |



### 🏗️ Arquitectura


- **modulo/**
  - `__init__.py`
  - `__manifest__.py`

- **controllers/**
  - `controllers.py` → Controladores HTTP

- **data/**
  - `ai_actions.xml` → Acciones del agente IA
  - `ai_agent.xml` → Configuración del agente
  - `ai_crm_actions.xml` → Acciones CRM
  - `livechat_ai_integration.xml` → Integración LiveChat

- **models/**
  - `ai_actions.py` → Lógica de inventario
  - `ai_crm_actions.py` → Lógica CRM
  - `livechat_integration.py`
  - `livechat_message_handler.py`
  - `res_config_settings.py`

- **security/**
  - `ir.model.access.csv`

- **views/**
  - `res_config_settings_views.xml`
  - `templates.xml`
  - `views.xml`


### 👥 Autores


**Carlos Badillo** - *Desarrollo inicial*



### 🙏 Agradecimientos

- Sellside spa
- Comunidad de Odoo
- Google Generative AI



```mermaid
graph TD
    %% Capa de Usuario
    subgraph UI [INTERFAZ DE USUARIO - A2UI]
        A[Usuario Concesionaria] -- "Consulta: 'Stock de SUVs 2026'" --> B[Interfaz Odoo / Chatbot]
        B -- "Respuesta Dinámica" --> A
        B -- "Actualiza Vista UI (Kanban/Graph)" --> A
    end

    %% Capa de Inteligencia
    subgraph AI [CAPA DE ORQUESTACIÓN IA]
        C{Agent Controller}
        D[Clasificador de Intenciones]
        E[Memoria de Contexto]
        F[Tool Selector]

        B --> C
        C --> D
        D --> E
        E --> F
    end

    %% Capa de Datos y Herramientas
    subgraph DATA [BACKEND ODOO & DATOS]
        G[(PostgreSQL Odoo 19)]
        H[RAG: Manuales y Fichas Técnicas]
        I[Módulo Inventario: stock.quant]
        J[Módulo CRM: crm.lead]
        K[Módulo Ventas: sale.order]
    end

    %% Conexiones de Herramientas
    F -- "Text-to-SQL / ORM" --> G
    F -- "Búsqueda Semántica" --> H
    G --> I
    G --> J
    G --> K

    %% Protocolo A2UI (Agent to User Interface)
    K -- "Acción de Interfaz" --> B
    I -- "Push de Datos" --> B

    style UI fill:#f9f9f9,stroke:#333,stroke-width:2px
    style AI fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style DATA fill:#fff3e0,stroke:#e65100,stroke-width:2px


	
