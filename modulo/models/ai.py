import json
import logging

import google.generativeai as genai

from odoo import models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AI(models.Model):
    _name = 'ai_agents.ai'
    _description = 'AI Connector'

    name = fields.Char()
    api_key = fields.Char()
    model_name = fields.Char(default='gemini-2.5-flash')
    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    base_context = fields.Text()

    # Campos heredados para compatibilidad (ya no se usan con Gemini)
    api_url = fields.Char()

    def create(self, vals):
        res = super(AI, self).create(vals)

        # Crear un partner para el AI
        partner = self.env['res.partner'].create({
            'name': res.name + " AI",
            'email': f'__ai__{res.name}__'
        })

        res.partner_id = partner.id

        return res

    def generate(self, message):
        """
        Enviar un mensaje a Google Gemini API
        """
        if not self.api_key:
            raise UserError("API Key de Gemini no configurada")

        try:
            # Configurar la API de Google
            genai.configure(api_key=self.api_key)
            
            # Crear el modelo
            model = genai.GenerativeModel(self.model_name)
            
            # Generar respuesta
            response = model.generate_content(message)
            
            return response.text
            
        except Exception as e:
            _logger.warning(f"Error en respuesta de Gemini: {str(e)}")
            raise UserError(f"Error en respuesta de Gemini: {str(e)}")

    def action_chat(self):
        """
        Iniciar o encontrar un canal de conversación con el AI.
        """
        channel_model = self.env['discuss.channel']
        members = [self.partner_id.id, self.env.user.partner_id.id]
        uuid = f'{members[0]}-{members[1]}'
        
        # Verificar si existe un canal con este AI
        channel = channel_model.search([('uuid', '=', uuid)], limit=1)

        # Si no existe, crear uno nuevo
        if not channel:
            channel = channel_model.create({
                'name': self.name,
                'channel_type': 'chat',
                'channel_partner_ids': [(4, partner_id) for partner_id in members],
                'uuid': uuid,
                'ai_id': self.id,
            })

        discuss_action = self.env.ref('mail.action_discuss').read()[0]
        
        # Abrir ventana de chat
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web#action={discuss_action['id']}&active_id=discuss.channel_{channel.id}",
            'target': 'self',
        }