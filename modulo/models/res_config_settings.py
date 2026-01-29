from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_api_key = fields.Char(string="AI API Key", config_parameter='modulo.ai_api_key')
