{
    'name': "Agente AI",
    'summary': "Asistente IA para control de inventario y crm",
    'description': """
Módulo de integración de IA para control de inventario y CRM con soporte para livechat
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'mail',
        'product',
        'stock',
        'ai',
        'crm',
        'sale',
        'website',
        'im_livechat'
    ],
    'data': [
        'data/ai_actions.xml',
        'data/ai_crm_actions.xml',
        'data/ai_agent.xml',
        'data/ai_agent_source.xml',
        'data/livechat_ai_integration.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_common': [
            'modulo/static/css/dashboard.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}