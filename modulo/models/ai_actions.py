from odoo import models, api

class AIInventoryActions(models.AbstractModel):
    _name = "ai.inventory.actions"
    _description = "Acciones IA Inventario"

    @api.model
    def get_stock(self, product_name):
        products = self.env['product.product'].sudo().search([
            ('name', 'ilike', product_name)
        ], limit=5)

        if not products:
            return f"No se encontraron productos llamados '{product_name}'."

        result = []
        for p in products:
            result.append(
                f"{p.name}: {p.qty_available} uds (Precio ${p.list_price})"
            )

        return "\n".join(result)
