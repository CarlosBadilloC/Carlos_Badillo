from odoo import models, api

class AIInventoryActions(models.AbstractModel):
    _name = "ai.inventory.actions"
    _description = "Acciones IA Inventario"

    @api.model
    def get_stock(self, product_name):
        """Obtiene información detallada del stock de productos incluyendo marca"""
        products = self.env['product.product'].sudo().search([
            ('name', 'ilike', product_name)
        ], limit=10)

        if not products:
            return f"No se encontraron productos relacionados con '{product_name}'."

        result = []
        for p in products:
            status = "✅ Disponible" if p.qty_available > 0 else "❌ Sin stock"
            marca = p.product_tmpl_id.brand_id.name if hasattr(p.product_tmpl_id, 'brand_id') and p.product_tmpl_id.brand_id else "Sin marca"
            categoria = p.categ_id.name if p.categ_id else "Sin categoría"
            
            result.append(
                f"📦 {p.name}\n"
                f"  • Marca: {marca}\n"
                f"  • Categoría: {categoria}\n"
                f"  • Stock: {int(p.qty_available)} unidades\n"
                f"  • Precio: ${p.list_price:,.2f}\n"
                f"  • Estado: {status}"
            )
        
        return "\n\n".join(result)

    @api.model
    def search_products_by_keyword(self, keyword, limit=10):
        """Busca productos por palabra clave en nombre, descripción o categoría"""
        products = self.env['product.product'].sudo().search([
            '|', '|',
            ('name', 'ilike', keyword),
            ('description', 'ilike', keyword),
            ('categ_id.name', 'ilike', keyword)
        ], limit=limit)
        
        if not products:
            return f"No se encontraron productos relacionados con '{keyword}'."
        
        result = [f"🔍 Productos encontrados para '{keyword}':\n"]
        for p in products:
            stock_status = "✅" if p.qty_available > 0 else "❌"
            marca = p.product_tmpl_id.brand_id.name if hasattr(p.product_tmpl_id, 'brand_id') and p.product_tmpl_id.brand_id else "Sin marca"
            result.append(
                f"{stock_status} {p.name}\n"
                f"    Marca: {marca} | Stock: {int(p.qty_available)} unidades | Precio: ${p.list_price:,.2f}"
            )
        
        return "\n".join(result)

    @api.model
    def check_low_stock(self, threshold=10):
        """Verifica productos con stock bajo"""
        products = self.env['product.product'].sudo().search([
            ('qty_available', '<', threshold),
            ('qty_available', '>', 0)
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
  • Productos sin stock: {total_products - products_in_stock}
  • Valor total: ${total_value:,.2f}"""

    @api.model
    def search_product_by_category(self, category_name):
        """Busca productos por categoría con información detallada"""
        categories = self.env['product.category'].sudo().search([
            ('name', 'ilike', category_name)
        ])
        
        if not categories:
            return f"No se encontraron categorías llamadas '{category_name}'."
        
        products = self.env['product.product'].sudo().search([
            ('categ_id', 'in', categories.ids)
        ], limit=15)
        
        if not products:
            return f"No hay productos en la categoría '{category_name}'."
        
        result = [f"📁 Productos en '{category_name}':\n"]
        for p in products:
            stock_status = "✅" if p.qty_available > 0 else "❌"
            marca = p.product_tmpl_id.brand_id.name if hasattr(p.product_tmpl_id, 'brand_id') and p.product_tmpl_id.brand_id else "Sin marca"
            result.append(
                f"{stock_status} {p.name}\n"
                f"    Marca: {marca} | Stock: {int(p.qty_available)} unidades | Precio: ${p.list_price:,.2f}"
            )
        
        return "\n".join(result)