{
    'name': "AI Query Handler",

    'summary': "Módulo para consultas de IA sobre CRM e Inventario",

    'description': """
        Proporciona métodos ORM reutilizables para que AI Agents consulten:
        - Información de inventario (productos, stock)
        - Métricas de CRM (oportunidades, leads, pipeline)
        
        Compatible con Odoo 19 AI Framework y JSON-RPC.
        
        Features:
        - 5 tools consumibles por AI Agents
        - Endpoints JSON-RPC para integración externa
        - Prompts del sistema para guiar comportamiento del agente
        - Respuestas estructuradas y fáciles de parsear
    """,

    'author': "Carlos Badillo",
    'models': [
        'models/crm_inventory_metrics.py',  # Añadir esta línea
    ],

    'category': 'Tools',
    'version': '1.0.0',

    # Dependencias necesarias
    'depends': [
        'base',
        'product',
        'stock',
        'crm',
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,

    # Datos cargados durante la instalación
    'data': [
        'security/ir.model.access.csv',
        'data/ai_prompts.xml',
        'views/test_views.xml',
    ],
    
    'demo': [],
    
    'license': 'LGPL-3',
}