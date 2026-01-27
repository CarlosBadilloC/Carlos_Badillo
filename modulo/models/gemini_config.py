from odoo import models, fields, api # type: ignore
from odoo.exceptions import ValidationError

class GeminiConfig(models.Model):
    _name = 'gemini.config'
    _description = 'Google Gemini Configuration'

    name = fields.Char(string="Nombre", default="Gemini Config", required=True)
    api_key = fields.Char(string="API Key de Gemini", required=True)
    model = fields.Selection([
        ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
        ('gemini-1.5-pro', 'Gemini 1.5 Pro'),
        ('gemini-1.5-flash', 'Gemini 1.5 Flash'),
    ], string="Modelo", default='gemini-2.0-flash', required=True)
    
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