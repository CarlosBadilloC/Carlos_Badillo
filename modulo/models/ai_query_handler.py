from odoo import models, api
from odoo.exceptions import UserError

class AIQueryHandler(models.AbstractModel):
    """
    Modelo abstracto que proporciona métodos para AI Agents.
    Los métodos aquí son reutilizables y agnósticos a la UI.
    """
    _name = 'ai.query.handler'
    _description = 'AI Query Handler - Consultas para IA'

    # ========== MÉTODOS DE INVENTARIO ==========

    @api.model
    def get_inventory_summary(self):
        """
        Retorna un resumen completo del inventario actual.
        
        Returns:
            dict: {
                'total_products': int,
                'total_stock_quantity': float,
                'low_stock_products': list,
                'status': str
            }
        """
        try:
            # Contar productos totales (solo productos almacenables)
            total_products = self.env['product.product'].search_count([
                ('type', '=', 'product')
            ])
            
            # Stock total disponible
            stock_quants = self.env['stock.quant'].search([
                ('location_id.usage', '=', 'internal')
            ])
            total_quantity = sum(quant.quantity for quant in stock_quants)
            
            # Productos con bajo stock (cantidad <= 5)
            low_stock = self.env['product.product'].search([
                ('type', '=', 'product'),
                ('qty_available', '<=', 5),
                ('qty_available', '>', 0)
            ], limit=10)
            
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

    @api.model
    def get_product_count(self):
        """
        Método simple para contar productos almacenables.
        
        Returns:
            dict: {'total_products': int, 'status': str}
        """
        try:
            count = self.env['product.product'].search_count([
                ('type', '=', 'product')
            ])
            return {
                'total_products': count,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    # ========== MÉTODOS DE CRM ==========

    @api.model
    def get_crm_summary(self):
        """
        Retorna un resumen completo de CRM (oportunidades por estado).
        
        Returns:
            dict: {
                'total_opportunities': int,
                'open_opportunities': int,
                'won_opportunities': int,
                'lost_opportunities': int,
                'total_expected_revenue': float,
                'status': str
            }
        """
        try:
            Lead = self.env['crm.lead']
            
            # Total de oportunidades
            total = Lead.search_count([('type', '=', 'opportunity')])
            
            # Oportunidades abiertas (no ganadas ni perdidas)
            open_opps = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', 'not in', [0, 100])
            ])
            
            # Oportunidades ganadas
            won_opps = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('probability', '=', 100)
            ])
            
            # Oportunidades perdidas
            lost_opps = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('probability', '=', 0),
                ('active', '=', False)
            ])
            
            # Ingresos esperados (oportunidades abiertas)
            open_leads = Lead.search([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', 'not in', [0, 100])
            ])
            total_expected_revenue = sum(lead.expected_revenue for lead in open_leads)
            
            return {
                'total_opportunities': total,
                'open_opportunities': open_opps,
                'won_opportunities': won_opps,
                'lost_opportunities': lost_opps,
                'total_expected_revenue': total_expected_revenue,
                'currency': self.env.company.currency_id.name,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @api.model
    def get_opportunities_by_stage(self):
        """
        Retorna el conteo de oportunidades por etapa del pipeline.
        
        Returns:
            dict: {
                'stages': [
                    {'name': str, 'count': int, 'expected_revenue': float},
                    ...
                ],
                'status': str
            }
        """
        try:
            Stage = self.env['crm.stage']
            Lead = self.env['crm.lead']
            
            stages = Stage.search([])
            stage_data = []
            
            for stage in stages:
                opportunities = Lead.search([
                    ('type', '=', 'opportunity'),
                    ('stage_id', '=', stage.id),
                    ('active', '=', True)
                ])
                
                stage_data.append({
                    'stage_id': stage.id,
                    'stage_name': stage.name,
                    'count': len(opportunities),
                    'expected_revenue': sum(opp.expected_revenue for opp in opportunities),
                    'sequence': stage.sequence
                })
            
            # Ordenar por secuencia
            stage_data.sort(key=lambda x: x['sequence'])
            
            return {
                'stages': stage_data,
                'total_stages': len(stage_data),
                'currency': self.env.company.currency_id.name,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @api.model
    def get_open_opportunities_count(self):
        """
        Método simple: conteo de oportunidades abiertas.
        
        Returns:
            dict: {'open_opportunities': int, 'status': str}
        """
        try:
            count = self.env['crm.lead'].search_count([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', 'not in', [0, 100])
            ])
            return {
                'open_opportunities': count,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
            
# Probar inventario
result = env['ai.query.handler'].get_product_count()
print(result)

# Probar CRM
result = env['ai.query.handler'].get_crm_summary()
print(result)

# Probar pipeline
result = env['ai.query.handler'].get_opportunities_by_stage()
print(result)