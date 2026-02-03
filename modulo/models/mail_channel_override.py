from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def create(self, vals):
        """Override para capturar nuevos canales"""
        record = super().create(vals)
        return record

    def message_post(self, **kwargs):
        """Override para procesar mensajes en canales livechat"""
        result = super().message_post(**kwargs)
        
        # Verificar si es un canal de livechat
        if self.livechat_channel_id:
            message_body = kwargs.get('body', '')
            author_id = kwargs.get('author_id')
            
            # Solo procesar mensajes que no sean del bot
            if author_id and author_id != self.env.ref('base.partner_root').id:
                try:
                    integration = self.env['livechat.ai.integration'].search(
                        [('active', '=', True)],
                        limit=1
                    )
                    if integration:
                        integration._process_livechat_message(self, message_body, author_id)
                except Exception as e:
                    _logger.error(f"Error en integración livechat: {e}")
        
        return result