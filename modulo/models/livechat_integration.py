from odoo import models, api, fields
from odoo.addons.mail.models.mail_message import Message
import logging

_logger = logging.getLogger(__name__)

class LivechatIntegration(models.Model):
    _name = "livechat.ai.integration"
    _description = "Integración IA con Livechat"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", required=True, default="AI Agent Integration")
    active = fields.Boolean(default=True)
    ai_agent_id = fields.Many2one('ai.agent', string="Agente IA", required=True)
    livechat_channel_id = fields.Many2one('im_livechat.channel', string="Canal Livechat", required=True)
    
    @api.model
    def _process_livechat_message(self, mail_channel, message_body, author):
        """Procesa mensajes de livechat y envía respuesta del agente IA"""
        try:
            # Obtener la integración activa
            integration = self.search([('active', '=', True)], limit=1)
            if not integration:
                _logger.warning("No hay integración IA activa para livechat")
                return

            # Obtener el agente IA
            ai_agent = integration.ai_agent_id
            if not ai_agent:
                return

            # Llamar al agente IA con el mensaje del usuario
            result = self._call_ai_agent(ai_agent, message_body)

            # Enviar respuesta al canal de livechat
            if result:
                mail_channel.message_post(
                    body=result,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=self.env.ref('base.partner_root').id
                )
        except Exception as e:
            _logger.error(f"Error procesando mensaje de livechat: {e}")

    @api.model
    def _call_ai_agent(self, ai_agent, prompt):
        """Llama al agente IA y obtiene respuesta"""
        try:
            # Dependiendo del tipo de pregunta, llamar a las acciones correspondientes
            if 'stock' in prompt.lower() or 'producto' in prompt.lower():
                return self.env['ai.inventory.actions'].search_products_detailed(prompt)
            elif 'lead' in prompt.lower() or 'oportunidad' in prompt.lower():
                return self.env['ai.crm.actions'].get_lead_info(prompt)
            elif 'cotizacion' in prompt.lower() or 'presupuesto' in prompt.lower():
                return self.env['ai.crm.actions'].search_quotations_with_stock(prompt)
            else:
                # Respuesta genérica si no se identifica la acción
                return "¿En qué puedo ayudarte? Puedo consultar inventario, gestionar leads u oportunidades."
        except Exception as e:
            _logger.error(f"Error llamando agente IA: {e}")
            return f"Disculpa, ocurrió un error: {str(e)}"