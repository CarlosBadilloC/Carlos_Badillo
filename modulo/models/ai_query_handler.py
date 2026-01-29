from odoo import models, api

class AIQueryHandler(models.AbstractModel):
    _name = 'ai.query.handler'
    _description = 'AI Query Handler - Inventory & CRM Queries'

    @api.model
    def get_product_count(self):
        """
        Retorna el total de productos almacenables en el sistema.
        """
        try:
            total_products = self.env['product.product'].search_count([
                ('type', '=', 'product'),
                ('active', '=', True)
            ])
            return {
                'total_products': total_products,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

@api.model
def get_inventory_summary(self):
    """
    Resumen de inventario alineado con Inventory > Reporting > Stock
    """
    try:
        Product = self.env['product.product']

        products = Product.search([
            ('type', '=', 'product'),
            ('active', '=', True)
        ])

        total_products = len(products)
        total_quantity = sum(products.mapped('qty_available'))

        low_stock_products = [
            {
                'id': p.id,
                'name': p.display_name,
                'qty_available': p.qty_available,
                'uom': p.uom_id.name
            }
            for p in products
            if 0 < p.qty_available <= 5
        ]

        return {
            'source': 'inventory_report_on_hand',
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
    def get_open_opportunities_count(self):
        """
        Retorna el total de oportunidades activas (no ganadas ni perdidas).
        """
        try:
            open_opportunities = self.env['crm.lead'].search_count([
                ('stage_id.is_won', '=', False),
                ('stage_id.is_lost', '=', False)
            ])
            return {
                'open_opportunities': open_opportunities,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @api.model
    def get_crm_summary(self):
        """
        Retorna resumen completo de CRM: total, abiertas, ganadas, perdidas, e ingresos esperados.
        """
        try:
            # Total de oportunidades
            total_opportunities = self.env['crm.lead'].search_count([])
            
            # Oportunidades abiertas
            open_opportunities = self.env['crm.lead'].search_count([
                ('stage_id.is_won', '=', False),
                ('stage_id.is_lost', '=', False)
            ])
            
            # Oportunidades ganadas
            won_opportunities = self.env['crm.lead'].search_count([
                ('stage_id.is_won', '=', True)
            ])
            
            # Oportunidades perdidas
            lost_opportunities = self.env['crm.lead'].search_count([
                ('stage_id.is_lost', '=', True)
            ])
            
            # Ingresos esperados
            opportunities = self.env['crm.lead'].search([
                ('stage_id.is_won', '=', False),
                ('stage_id.is_lost', '=', False)
            ])
            total_expected_revenue = sum(opp.expected_revenue or 0 for opp in opportunities)
            
            # Obtener moneda
            currency = self.env.company.currency_id.name if self.env.company.currency_id else 'USD'
            
            return {
                'total_opportunities': total_opportunities,
                'open_opportunities': open_opportunities,
                'won_opportunities': won_opportunities,
                'lost_opportunities': lost_opportunities,
                'total_expected_revenue': total_expected_revenue,
                'currency': currency,
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
        Retorna oportunidades agrupadas por etapa del pipeline.
        """
        try:
            stages = self.env['crm.stage'].search([], order='sequence')
            
            stages_data = []
            for stage in stages:
                opportunities = self.env['crm.lead'].search([
                    ('stage_id', '=', stage.id)
                ])
                count = len(opportunities)
                expected_revenue = sum(opp.expected_revenue or 0 for opp in opportunities)
                
                if count > 0:
                    stages_data.append({
                        'stage_id': stage.id,
                        'stage_name': stage.name,
                        'count': count,
                        'expected_revenue': expected_revenue,
                        'sequence': stage.sequence
                    })
            
            # Obtener moneda
            currency = self.env.company.currency_id.name if self.env.company.currency_id else 'USD'
            
            return {
                'stages': stages_data,
                'total_stages': len(stages_data),
                'currency': currency,
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }