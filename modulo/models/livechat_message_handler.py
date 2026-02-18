from odoo import models, api
import logging
import re

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        """Intercepta creación de mensajes para procesar con IA si es livechat"""
        records = super().create(vals_list)
        
        for record in records:
            try:
                if record.model == 'discuss.channel' and record.res_id:
                    channel = self.env['discuss.channel'].browse(record.res_id)
                    
                    if hasattr(channel, 'livechat_channel_id') and channel.livechat_channel_id:
                        bot_partner = self.env.ref('base.partner_root', raise_if_not_found=False)
                        if record.author_id and (not bot_partner or record.author_id != bot_partner):
                            self._process_livechat_ai_response(channel, record)
            except Exception as e:
                _logger.warning(f"Error procesando mensaje livechat: {e}")
        
        return records

    @api.model
    def _process_livechat_ai_response(self, channel, message):
        """Procesa el mensaje con IA y envía respuesta automática"""
        try:
            integration = self.env['livechat.ai.integration'].search(
                [('active', '=', True)],
                limit=1
            )
            
            if not integration or not integration.ai_agent_id:
                _logger.info("No hay integración IA activa")
                return

            message_body = message.body or ''
            
            if '<' in message_body:
                message_body = re.sub('<[^<]+?>', '', message_body).strip()

            if not message_body:
                return

            _logger.info(f"Procesando mensaje de livechat: {message_body[:50]}...")

            # Obtener respuesta del agente IA
            response = integration._call_ai_agent(integration.ai_agent_id, message_body)

            if response:
                bot_partner = self.env.ref('base.partner_root', raise_if_not_found=False)
                
                # ✅ Enviar el HTML tal como viene de _format_a2ui_response
                channel.message_post(
                    body=response,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=bot_partner.id if bot_partner else False,
                    email_from=bot_partner.email if bot_partner else None
                )
                
                _logger.info(f"✅ Respuesta IA enviada al canal {channel.name}")
        except Exception as e:
            _logger.error(f"❌ Error procesando respuesta IA: {e}", exc_info=True)