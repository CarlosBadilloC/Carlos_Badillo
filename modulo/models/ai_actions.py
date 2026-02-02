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
                f"📦 {p.name}\n"
                f"  • Stock: {int(p.qty_available)} unidades\n"
                f"  • Precio: ${p.list_price}\n"
                f"  • Estado: {status}"
            )
        
        return "\n\n".join(result)

    @api.model
    def search_products_detailed(self, search_term):
        """Busca productos de forma inteligente y devuelve información detallada"""
        # Buscar en nombre, descripción y categoría
        products = self.env['product.product'].sudo().search([
            '|', '|', 
            ('name', 'ilike', search_term),
            ('description', 'ilike', search_term),
            ('categ_id.name', 'ilike', search_term)
        ], limit=10)

        if not products:
            return f"❌ No se encontraron productos relacionados con '{search_term}'."

        result = [f"🔍 Encontré {len(products)} producto(s) relacionado(s) con '{search_term}':\n"]
        
        for p in products:
            stock_qty = int(p.qty_available)
            status = "✅ Disponible" if stock_qty > 0 else "❌ Sin stock"
            category = p.categ_id.name if p.categ_id else "Sin categoría"
            
            result.append(
                f"📦 **{p.name}**\n"
                f"  • Categoría: {category}\n"
                f"  • Stock disponible: {stock_qty} unidades\n"
                f"  • Precio unitario: ${p.list_price:,.2f}\n"
                f"  • Valor total en inventario: ${stock_qty * p.list_price:,.2f}\n"
                f"  • Estado: {status}"
            )
            
            # Agregar información adicional si hay poco stock
            if 0 < stock_qty < 5:
                result.append(f"  ⚠️ ¡Stock bajo! Considere reabastecer.")

        return "\n\n".join(result)

    @api.model
    def check_low_stock(self, threshold=10):
        """Verifica productos con stock bajo"""
        products = self.env['product.product'].sudo().search([
            ('qty_available', '<', threshold)
        ], limit=10)
        
        if not products:
            return "✅ Todos los productos tienen stock suficiente."
        
        result = ["⚠️ Productos con stock bajo:"]
        for p in products:
            result.append(f"  • {p.name}: {int(p.qty_available)} unidades")
        
        return "\n".join(result)

    @api.model
    def get_inventory_summary(self):
        """Obtiene un resumen del inventario"""
        products = self.env['product.product'].sudo().search([])
        
        total_products = len(products)
        products_in_stock = len(products.filtered(lambda p: p.qty_available > 0))
        total_value = sum(p.qty_available * p.list_price for p in products)
        
        return f"""📊 Resumen de Inventario:
  • Total de productos: {total_products}
  • Productos disponibles: {products_in_stock}
  • Valor total: ${total_value:,.2f}"""

    @api.model
    def search_product_by_category(self, category_name):
        """Busca productos por categoría"""
        categories = self.env['product.category'].sudo().search([
            ('name', 'ilike', category_name)
        ])
        
        if not categories:
            return f"No se encontraron categorías llamadas '{category_name}'."
        
        products = self.env['product.product'].sudo().search([
            ('categ_id', 'in', categories.ids)
        ], limit=10)
        
        if not products:
            return f"No hay productos en la categoría '{category_name}'."
        
        result = [f"Productos en '{category_name}':"]
        for p in products:
            result.append(f"  • {p.name}: {int(p.qty_available)} unidades")
        
        return "\n".join(result)