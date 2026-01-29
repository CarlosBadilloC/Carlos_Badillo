# from odoo import http


# class Modulo(http.Controller):
#     @http.route('/modulo/modulo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/modulo/modulo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('modulo.listing', {
#             'root': '/modulo/modulo',
#             'objects': http.request.env['modulo.modulo'].search([]),
#         })

#     @http.route('/modulo/modulo/objects/<model("modulo.modulo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('modulo.object', {
#             'object': obj
#         })
from odoo import http
from odoo.http import request

class AIAgentChatController(http.Controller):

    @http.route('/ai_agent/livechat', type='json', auth='public', csrf=False)
    def livechat_message(self, message, agent_id=None, **kwargs):
        agent = request.env['ai.agent'].browse(agent_id) if agent_id else request.env['ai.agent'].search([], limit=1)
        if not agent:
            return {"error": "No se encontró agente"}
        response = agent.action_ask_gemini(message)
        return {"response": response}

