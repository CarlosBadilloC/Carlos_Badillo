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
        """Busca productos de forma inteligente y devuelve información detallada con A2UI"""
        products = self.env['product.product'].sudo().search([
            '|', '|', 
            ('name', 'ilike', search_term),
            ('description', 'ilike', search_term),
            ('categ_id.name', 'ilike', search_term)
        ], limit=10)

        if not products:
            return f"❌ No se encontraron productos relacionados con '{search_term}'."

        # Crear estructura A2UI
        rows = []
        total_value = 0
        for p in products:
            stock_qty = int(p.qty_available)
            total_value += stock_qty * p.list_price
            category = p.categ_id.name if p.categ_id else "Sin categoría"
            status = "Disponible" if stock_qty > 0 else "Sin stock"
            
            rows.append({
                'name': p.name,
                'category': category,
                'stock': stock_qty,
                'unit_price': f"${p.list_price:,.2f}",
                'total_value': f"${stock_qty * p.list_price:,.2f}",
                'status': status
            })

        # Crear respuesta con A2UI dashboard
        response = {
            'text': f"🔍 Encontré {len(products)} producto(s) relacionado(s) con '{search_term}'",
            'a2ui_dashboard': {
                'type': 'table',
                'title': f"Productos: {search_term}",
                'columns': [
                    {'key': 'name', 'label': 'Producto'},
                    {'key': 'category', 'label': 'Categoría'},
                    {'key': 'stock', 'label': 'Stock'},
                    {'key': 'unit_price', 'label': 'Precio Unitario'},
                    {'key': 'total_value', 'label': 'Valor Total'},
                    {'key': 'status', 'label': 'Estado'}
                ],
                'rows': rows,
                'summary': {
                    'total_products': len(products),
                    'total_value': f"${total_value:,.2f}",
                    'in_stock': len([p for p in products if p.qty_available > 0])
                }
            }
        }
        return response
    
    @api.model
    def check_low_stock(self, threshold=10):
        """Verifica productos con stock bajo con dashboard A2UI"""
        products = self.env['product.product'].sudo().search([
            ('qty_available', '<', threshold),
            ('qty_available', '>', 0)
        ], limit=20)
        
        if not products:
            return "✅ Todos los productos tienen stock suficiente."
        
        rows = []
        total_restock_value = 0
        for p in products:
            stock_qty = int(p.qty_available)
            restock_suggestion = max(10 - stock_qty, 5)
            restock_value = restock_suggestion * p.list_price
            total_restock_value += restock_value
            
            rows.append({
                'name': p.name,
                'current_stock': stock_qty,
                'suggested_qty': restock_suggestion,
                'unit_price': f"${p.list_price:,.2f}",
                'restock_value': f"${restock_value:,.2f}",
                'category': p.categ_id.name if p.categ_id else "Sin categoría"
            })

        response = {
            'text': f"⚠️ {len(products)} producto(s) con stock bajo",
            'a2ui_dashboard': {
                'type': 'alert_table',
                'title': 'Productos con Stock Bajo',
                'summary': {
                    'total_products': len(products),
                    'restock_value': f"${total_restock_value:,.2f}"
                },
                'columns': [
                    {'key': 'name', 'label': 'Producto'},
                    {'key': 'category', 'label': 'Categoría'},
                    {'key': 'current_stock', 'label': 'Stock Actual'},
                    {'key': 'suggested_qty', 'label': 'Sugerido'},
                    {'key': 'unit_price', 'label': 'Precio'},
                    {'key': 'restock_value', 'label': 'Valor a Reabastecer'}
                ],
                'rows': rows,
                'action': {
                    'type': 'create_purchase_order',
                    'label': 'Crear Orden de Compra',
                    'products': [{'product_id': p.id, 'qty': max(10 - int(p.qty_available), 5)} for p in products]
                }
            }
        }
        return response

    @api.model
    def get_inventory_summary(self):
        """Obtiene resumen del inventario con dashboard A2UI"""
        products = self.env['product.product'].sudo().search([])
        
        total_products = len(products)
        products_in_stock = len(products.filtered(lambda p: p.qty_available > 0))
        total_value = sum(p.qty_available * p.list_price for p in products)
        low_stock_count = len(products.filtered(lambda p: 0 < p.qty_available < 5))
        
        # Datos por categoría
        category_data = {}
        for p in products:
            cat_name = p.categ_id.name if p.categ_id else "Sin categoría"
            if cat_name not in category_data:
                category_data[cat_name] = {'count': 0, 'value': 0.0}
            category_data[cat_name]['count'] += 1
            category_data[cat_name]['value'] += p.qty_available * p.list_price

        category_rows = [
            {
                'category': cat,
                'products': data['count'],
                'value': f"${data['value']:,.2f}"
            }
            for cat, data in category_data.items()
        ]

        response = {
            'text': '📊 Resumen del Inventario',
            'a2ui_dashboard': {
                'type': 'summary_cards',
                'cards': [
                    {
                        'title': 'Total de Productos',
                        'value': total_products,
                        'icon': '📦',
                        'color': 'primary'
                    },
                    {
                        'title': 'Productos Disponibles',
                        'value': products_in_stock,
                        'icon': '✅',
                        'color': 'success',
                        'subtitle': f"{(products_in_stock/total_products*100):.1f}% del total"
                    },
                    {
                        'title': 'Valor Total',
                        'value': f"${total_value:,.2f}",
                        'icon': '💰',
                        'color': 'info'
                    },
                    {
                        'title': 'Stock Bajo',
                        'value': low_stock_count,
                        'icon': '⚠️',
                        'color': 'warning'
                    }
                ],
                'table': {
                    'title': 'Productos por Categoría',
                    'columns': [
                        {'key': 'category', 'label': 'Categoría'},
                        {'key': 'products', 'label': 'Cantidad'},
                        {'key': 'value', 'label': 'Valor Total'}
                    ],
                    'rows': category_rows
                }
            }
        }
        return response


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