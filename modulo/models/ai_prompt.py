from odoo import models, fields

class AIPrompt(models.Model):
    _name = 'ai.prompt'
    _description = 'AI Prompt'

    name = fields.Char(required=True)
    category = fields.Char()
    content = fields.Text()
    tools_required = fields.Char()