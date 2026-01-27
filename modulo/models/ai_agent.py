from odoo import models, fields # type: ignore

class AIAgent(models.Model):
    _inherit = 'ai.agent'

    custom_prompt = fields.Text(
        string="Prompt personalizado"
    )

    use_external_ai = fields.Boolean(
        string="Usar IA externa"
    )
