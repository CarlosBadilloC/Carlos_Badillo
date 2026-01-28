{
    'name': "AI Query Handler",

    'summary': "Módulo para consultas de IA sobre CRM e Inventario",

    'description': """
        Proporciona métodos ORM reutilizables para que AI Agents consulten:
        - Información de inventario (productos, stock)
        - Métricas de CRM (oportunidades, leads, pipeline)
        
        Compatible con Odoo 19 AI Framework y JSON-RPC.
    """,

    'author': "Carlos Badillo",

    'category': 'Tools',
    'version': '1.0.0',

    # Dependencias necesarias
    'depends': [
        'base',
        'product',
        'stock',
        'crm',  # Nueva dependencia para CRM
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,

    # Datos cargados
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',  # Comentado: no usamos vistas por ahora
        # 'views/templates.xml',  # Comentado: no usamos templates por ahora
    ],
    
    'demo': [
        # 'demo/demo.xml',  # Comentado: no necesitamos datos demo
    ],
    
    'license': 'LGPL-3',
}