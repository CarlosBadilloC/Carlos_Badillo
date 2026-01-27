from odoo import models, fields, api # type: ignore

class OpenAIConfig(models.Model):
    _name = 'openai.config'
    _description = 'OpenAI Configuration'

    name = fields.Char(string="Nombre", default="OpenAI Config", required=True)
    api_key = fields.Char(string="API Key", required=True)
    model = fields.Selection([
        ('gpt-4o', 'GPT-4 Optimized'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ], string="Modelo", default='gpt-4o', required=True)
    
    max_tokens = fields.Integer(
        string="Max Tokens",
        default=2000,
        help="Máximo de tokens en la respuesta"
    )
    
    temperature = fields.Float(
        string="Temperature",
        default=0.7,
        help="Controla la creatividad (0-1)"
    )
    
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('api_key_unique', 'unique(api_key)', 'La API Key debe ser única'),
    ]