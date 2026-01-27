from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError

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

    @api.constrains('api_key')
    def _check_api_key_unique(self):
        """Verifica que la API Key sea única"""
        for record in self:
            existing = self.search([
                ('api_key', '=', record.api_key),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError('La API Key debe ser única')
    
    @api.constrains('temperature')
    def _check_temperature_range(self):
        """Verifica que temperature esté entre 0 y 1"""
        for record in self:
            if not (0 <= record.temperature <= 1):
                raise ValidationError('Temperature debe estar entre 0 y 1')