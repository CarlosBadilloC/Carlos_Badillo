from odoo import models, api

class AIInventoryActions(models.AbstractModel):
    _name = "ai.inventory.actions"
    _description = "Acciones IA Inventario"

    @api.model
    def get_stock(self, product_name):
        """Obtiene información del stock de productos"""
        products = self.env['product.product'].sudo().search([
            ('name', 'ilike', product_name)
        ], limit=5)

        if not products:
            return f"No se encontraron productos llamados '{product_name}'."

        result = []
        for p in products:
            status = "✅ Disponible" if p.qty_available > 0 else "❌ Sin stock"
            result.append(
                f"{p.name}\n"
                f"  • Stock: {int(p.qty_available)} unidades\n"
                f"  • Precio: ${p.list_price}\n"
                f"  • Estado: {status}"
            )

        return "\n\n".join(result)