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
    def _process_livechat_message(self, mail_channel, message_body, author):
        """Procesa mensajes de livechat y envía respuesta del agente IA"""
        try:
            integration = self.search([('active', '=', True)], limit=1)
            if not integration or not integration.ai_agent_id:
                return

            result = self._call_ai_agent(integration.ai_agent_id, message_body)

            if result:
                try:
                    mail_channel.message_post(
                        body=result,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment',
                        author_id=self.env.ref('base.partner_root').id
                    )
                except Exception as e:
                    _logger.error(f"Error al enviar mensaje a livechat: {e}")
        except Exception as e:
            _logger.error(f"Error procesando mensaje de livechat: {e}")

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
            else:
                return "¿En qué puedo ayudarte? Puedo consultar inventario, gestionar leads u oportunidades."
        except Exception as e:
            _logger.error(f"Error llamando agente IA: {e}")
            return f"Disculpa, ocurrió un error procesando tu solicitud."


class MailChannelMixin(models.AbstractModel):
    """Mixin para extender mail.channel sin heredar directamente"""
    _name = "mail.channel.ai.mixin"
    _description = "Mixin para integración IA con Livechat"

    @api.model
    def init(self):
        """Hook que se ejecuta después de que mail.channel está registrado"""
        super().init()
        self._patch_mail_channel()

    @api.model
    def _patch_mail_channel(self):
        """Parchea mail.channel para procesar mensajes con IA"""
        MailChannel = self.env.get('mail.channel')
        if not MailChannel:
            return

        original_message_post = MailChannel.message_post

        def message_post_with_ai(self, **kwargs):
            result = original_message_post(self, **kwargs)
            
            try:
                if hasattr(self, 'livechat_channel_id') and self.livechat_channel_id:
                    message_body = kwargs.get('body', '')
                    author_id = kwargs.get('author_id')
                    
                    if author_id and author_id != self.env.ref('base.partner_root').id:
                        integration = self.env['livechat.ai.integration'].search(
                            [('active', '=', True)],
                            limit=1
                        )
                        if integration:
                            integration._process_livechat_message(self, message_body, author_id)
            except Exception as e:
                _logger.warning(f"Error en integración livechat: {e}")
            
            return result

        MailChannel.message_post = message_post_with_ai