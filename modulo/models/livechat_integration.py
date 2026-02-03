from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class LivechatIntegration(models.Model):
    _name = "livechat.ai.integration"
    _description = "Integración IA con Livechat"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", required=True, default="AI Agent Integration")
    active = fields.Boolean(default=True)
    ai_agent_id = fields.Many2one('ai.agent', string="Agente IA", required=True)
    livechat_channel_id = fields.Many2one(
        'im_livechat.channel',
        string="Canal Livechat",
        required=False
    )

    @api.model
    def _call_ai_agent(self, ai_agent, prompt):
        """Llama al agente IA y obtiene respuesta"""
        try:
            if 'stock' in prompt.lower() or 'producto' in prompt.lower():
                return self.env['ai.inventory.actions'].search_products_detailed(prompt)
            elif 'lead' in prompt.lower() or 'oportunidad' in prompt.lower():
                return self.env['ai.crm.actions'].get_lead_info(prompt)
            elif 'cotizacion' in prompt.lower() or 'presupuesto' in prompt.lower():
                return self.env['ai.crm.actions'].search_quotations_with_stock(prompt)
            elif 'pipeline' in prompt.lower() or 'resumen' in prompt.lower():
                return self.env['ai.crm.actions'].get_pipeline_summary()
            elif 'inventario' in prompt.lower() or 'resumen' in prompt.lower():
                return self.env['ai.inventory.actions'].get_inventory_summary()
            else:
                return "¿En qué puedo ayudarte? Puedo consultar inventario, gestionar leads u oportunidades."
        except Exception as e:
            _logger.error(f"Error llamando agente IA: {e}")
            return f"Disculpa, ocurrió un error procesando tu solicitud."