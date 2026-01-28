from odoo import http
from odoo.http import request

class AIInventoryController(http.Controller):
    """
    Controlador HTTP para exponer métodos del AI Query Handler.
    Endpoints consumibles por JSON-RPC (Postman, APIs externas).
    """

    @http.route('/ai/inventory/count', type='json', auth='user')
    def count_products(self):
        """
        Endpoint: GET /ai/inventory/count
        Retorna el conteo de productos usando el modelo AI Query Handler.
        """
        handler = request.env['ai.query.handler']
        return handler.get_product_count()

    @http.route('/ai/inventory/summary', type='json', auth='user')
    def inventory_summary(self):
        """
        Endpoint: GET /ai/inventory/summary
        Retorna resumen completo del inventario.
        """
        handler = request.env['ai.query.handler']
        return handler.get_inventory_summary()

    @http.route('/ai/crm/summary', type='json', auth='user')
    def crm_summary(self):
        """
        Endpoint: GET /ai/crm/summary
        Retorna resumen completo de CRM.
        """
        handler = request.env['ai.query.handler']
        return handler.get_crm_summary()

    @http.route('/ai/crm/opportunities/count', type='json', auth='user')
    def open_opportunities_count(self):
        """
        Endpoint: GET /ai/crm/opportunities/count
        Retorna conteo de oportunidades abiertas.
        """
        handler = request.env['ai.query.handler']
        return handler.get_open_opportunities_count()

    @http.route('/ai/crm/opportunities/stages', type='json', auth='user')
    def opportunities_by_stage(self):
        """
        Endpoint: GET /ai/crm/opportunities/stages
        Retorna oportunidades agrupadas por etapa.
        """
        handler = request.env['ai.query.handler']
        return handler.get_opportunities_by_stage()