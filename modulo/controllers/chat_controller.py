from odoo import http
from odoo.http import request

class ChatController(http.Controller):
    @http.route('/web/chat/send_message', type='json', auth='public', methods=['POST'], csrf=False)
    def send_message(self, message):
        # Aquí puedes procesar el mensaje y utilizar tu agente de IA
        response = request.env['ai.agent'].get_response(message)  # Asumiendo que tienes un método para obtener la respuesta
        return {'response': response}