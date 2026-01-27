from odoo import models, fields # type: ignore

class AIAgent(models.Model):
    _inherit = 'ai.agent'

    x_custom_capability = fields.Char(
        string="Custom Capability"
    )

    x_can_read_documents = fields.Boolean(
        string="Can Read Documents",
        default=False
    )

    def action_run_custom_logic(self):
        for agent in self:
            # Aquí conectas TU API / LLM / RAG / etc
            pass
