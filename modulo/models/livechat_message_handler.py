from odoo import models, api, fields
from odoo.addons.bus.models.bus import json_dump
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        """Intercepta creación de mensajes para procesar con IA si es livechat"""
        records = super().create(vals_list)
        
        for record in records:
            try:
                # Verificar si es un mensaje de livechat
                if record.model == 'mail.channel' and record.res_id:
                    channel = self.env['mail.channel'].browse(record.res_id)
                    
                    # Verificar si el canal tiene livechat_channel_id
                    if hasattr(channel, 'livechat_channel_id') and channel.livechat_channel_id:
                        # Solo procesar mensajes de usuarios (no del bot)
                        if record.author_id and record.author_id != self.env.ref('base.partner_root'):
                            self._process_livechat_ai_response(channel, record)
            except Exception as e:
                _logger.warning(f"Error procesando mensaje livechat: {e}")
        
        return records

    @api.model
    def _process_livechat_ai_response(self, channel, message):
        """Procesa el mensaje con IA y envía respuesta automática"""
        try:
            # Obtener la integración IA
            integration = self.env['livechat.ai.integration'].search(
                [('active', '=', True)],
                limit=1
            )
            
            if not integration or not integration.ai_agent_id:
                return

            # Procesar el mensaje del usuario
            message_body = message.body
            # Limpiar HTML si es necesario
            if '<' in message_body:
                import re
                message_body = re.sub('<[^<]+?>', '', message_body)

            # Obtener respuesta del agente IA
            response = integration._call_ai_agent(integration.ai_agent_id, message_body)

            if response:
                # Enviar respuesta del bot automáticamente
                channel.message_post(
                    body=response,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=self.env.ref('base.partner_root').id
                )
                
                _logger.info(f"Respuesta IA enviada al canal {channel.name}")
        except Exception as e:
            _logger.error(f"Error procesando respuesta IA: {e}")