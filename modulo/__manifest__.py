{
    'name': "modulo",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

   'description': """
    AI Agents for Odoo
    
    This module provides a framework for using AI agents in Odoo to automate tasks and provide assistance to users.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/ai.xml',
        'views/task.xml',
        'views/templates.xml',
        # Data
        'data/cronjobs.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": True,
}

