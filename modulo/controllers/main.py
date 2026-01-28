from odoo import http
from odoo.http import request

class AIInventoryController(http.Controller):

    @http.route('/ai/inventory/count', type='json', auth='user')
    def count_products(self):
        count = request.env['product.product'].search_count([])
        return {
            "total_products": count
        }
