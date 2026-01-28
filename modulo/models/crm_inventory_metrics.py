from odoo import models, fields, api

class CrmInventoryMetrics(models.AbstractModel):
    _name = 'crm.inventory.metrics'
    _description = 'CRM and Inventory Metrics'

    @api.model
    def get_inventory_summary(self):
        """Obtiene un resumen del inventario disponible."""
        products = self.env['product.product'].search([])
        total_stock = sum(product.qty_available for product in products)
        return {
            'total_products': len(products),
            'total_stock': total_stock,
        }

    @api.model
    def get_crm_metrics(self):
        """Obtiene métricas del CRM, como oportunidades abiertas."""
        opportunities = self.env['crm.lead'].search([('stage_id.is_won', '=', False)])
        return {
            'open_opportunities': len(opportunities),
        }