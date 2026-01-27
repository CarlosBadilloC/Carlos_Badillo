{
    'name': "modulo",
    'summary': "Agente IA personalizado con lectura de documentos e integración OpenAI",
    'description': """
Extiende el modelo ai.agent para agregar capacidades de lectura y procesamiento de documentos con OpenAI
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Artificial Intelligence',
    'version': '0.1',

    'depends': [
        'base',
        'ai_app',
    ],

    'data': [
        'views/ai_agent_views.xml',
        'views/ai_agent_menu.xml',
        'views/openai_config_views.xml',
    ],
    
    'demo': [
        'demo/demo.xml',
    ],
    
    'external_dependencies': {
        'python': ['PyPDF2', 'openai'],
    },
    
    'installable': True,
    'license': 'LGPL-3',
}