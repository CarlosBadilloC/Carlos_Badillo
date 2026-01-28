from odoo import models, fields

class AgentDocument(models.Model):
    _name = 'agent.document'
    _description = 'Agent Document'

    name = fields.Char(string="Nombre", required=True)
    agent_id = fields.Many2one(
        'ai.agent',
        string="Agente",
        ondelete='cascade',
        required=True
    )
    document_file = fields.Binary(
        string="Archivo",
        required=True
    )
    file_name = fields.Char(string="Nombre del Archivo")
    file_type = fields.Char(string="Tipo de Archivo")
    create_date = fields.Datetime(string="Fecha de Creación", readonly=True)