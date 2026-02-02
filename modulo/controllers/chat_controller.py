from odoo import http
from odoo.http import request
import json

class ChatController(http.Controller):
    
    @http.route('/web/chat/send_message', type='json', auth='public', methods=['POST'], csrf=False)
    def send_message(self, message, **kwargs):
        """Procesa mensajes del chat y usa el agente IA"""
        try:
            # Obtener el agente IA
            agent = request.env['ai.agent'].sudo().search([
                ('name', '=', 'AI Asistente Virtual')
            ], limit=1)
            
            if not agent:
                return {
                    'success': False,
                    'response': 'El agente IA no está configurado correctamente.'
                }
            
            # Procesar el mensaje con el agente
            response = agent.with_context(user_input=message).process_message(message)
            
            return {
                'success': True,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'response': f'Error procesando mensaje: {str(e)}'
            }
    
    @http.route('/web/chat/get_agent_info', type='json', auth='public', methods=['GET'])
    def get_agent_info(self, **kwargs):
        """Obtiene información del agente IA"""
        try:
            agent = request.env['ai.agent'].sudo().search([
                ('name', '=', 'AI Asistente Virtual'),
                ('active', '=', True)
            ], limit=1)
            
            if not agent:
                return {
                    'success': False,
                    'message': 'No hay agente IA disponible'
                }
            
            return {
                'success': True,
                'agent_name': agent.name,
                'agent_prompt': agent.system_prompt
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }