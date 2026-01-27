{
    'name': "modulo",
    'summary': "Agente IA personalizado con lectura de documentos e integración Google Gemini",
    'description': """
Extiende el modelo ai.agent para agregar capacidades de lectura y procesamiento de documentos con Google Gemini
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Artificial Intelligence',
    'version': '0.2',

    'depends': [
        'base',
        'ai_app',
    ],

    'data': [
        'views/ai_agent_views.xml',
        'views/ai_agent_menu.xml',
        'views/gemini_config_views.xml',
    ],
    
    'demo': [
        'demo/demo.xml',
    ],
    
    'external_dependencies': {
        'python': ['google-generativeai', 'PyPDF2'],
    },
    
    'installable': True,
    'license': 'LGPL-3',
}