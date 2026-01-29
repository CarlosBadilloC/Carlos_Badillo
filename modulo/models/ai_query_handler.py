@api.model
def get_inventory_summary(self):
    """
    Retorna un resumen completo del inventario actual.
    """
    try:
        # Contar productos totales (solo productos almacenables)
        total_products = self.env['product.product'].search_count([
            ('type', '=', 'product'),
            ('active', '=', True)  # ← Agregar esta línea
        ])
        
        # Stock total disponible
        stock_quants = self.env['stock.quant'].search([
            ('location_id.usage', '=', 'internal'),
            ('quantity', '>', 0)  # ← Solo contar con stock positivo
        ])
        total_quantity = sum(quant.quantity for quant in stock_quants)
        
        # Productos con bajo stock (cantidad <= 5)
        low_stock = self.env['product.product'].search([
            ('type', '=', 'product'),
            ('active', '=', True),
            ('qty_available', '<=', 5),
            ('qty_available', '>', 0)
        ], limit=20)  # ← Aumentar limit a 20
        
        low_stock_products = [
            {
                'id': product.id,
                'name': product.name,
                'qty_available': product.qty_available,
                'uom': product.uom_id.name
            }
            for product in low_stock
        ]
        
        return {
            'total_products': total_products,
            'total_stock_quantity': total_quantity,
            'low_stock_products': low_stock_products,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }