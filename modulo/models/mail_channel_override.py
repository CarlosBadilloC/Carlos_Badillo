from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def message_post(self, **kwargs):
        """Override para procesar mensajes en canales livechat"""
        result = super().message_post(**kwargs)
        
        try:
            # Verificar si es un canal de livechat
            if hasattr(self, 'livechat_channel_id') and self.livechat_channel_id:
                message_body = kwargs.get('body', '')
                author_id = kwargs.get('author_id')
                
                # Solo procesar mensajes que no sean del bot
                bot_partner_id = self.env.ref('base.partner_root').id
                if author_id and author_id != bot_partner_id:
                    try:
                        integration = self.env['livechat.ai.integration'].search(
                            [('active', '=', True)],
                            limit=1
                        )
                        if integration:
                            integration._process_livechat_message(self, message_body, author_id)
                    except Exception as e:
                        _logger.error(f"Error en integración livechat: {e}")
        except Exception as e:
            _logger.warning(f"No se pudo procesar livechat (posiblemente no esté instalado): {e}")
        
        return result