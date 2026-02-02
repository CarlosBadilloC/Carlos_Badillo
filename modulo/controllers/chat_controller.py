from odoo import http
from odoo.http import request


class ChatController(http.Controller):
    """
    Controller HTTP para Livechat + Agente IA
    Solo actúa como puente entre el frontend y el modelo ai.agent
    """

    @http.route(
        '/web/chat/send_message',
        type='json',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=False
    )
    def send_message(self, message, **kwargs):
        try:
            # Obtener el agente IA por defecto
            agent = request.env['ai.agent'].sudo().get_default_agent()

            if not agent:
                return {
                    'success': False,
                    'response': 'El asistente no está disponible en este momento.'
                }

            # Delegar TODO al agente
            response = agent.handle_chat(message)

            return {
                'success': True,
                'response': response
            }

        except Exception as e:
            # Log interno (no exponer errores crudos al usuario)
            request.env.cr.rollback()
            return {
                'success': False,
                'response': 'Ocurrió un problema al procesar tu mensaje. Intenta nuevamente.'
            }
