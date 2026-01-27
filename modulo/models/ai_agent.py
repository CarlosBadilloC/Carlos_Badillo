from odoo import models, fields # type: ignore


class AIAgentInherit(models.Model):
    _inherit = "ai.agent"

    x_custom_capability = fields.Char(
        string="Capacidad IA personalizada",
        help="Campo agregado por el módulo personalizado"
    )

    x_can_read_documents = fields.Boolean(
        string="Puede leer documentos",
        default=False
    )
