from odoo import models, api

class AIQueryHandler(models.AbstractModel):
    _name = 'ai.query.handler'
    _description = 'AI Query Handler - Inventory & CRM (Corrected)'

    # ================= INVENTARIO =================

    @api.model
    def get_inventory_summary(self):
        """
        Resumen de inventario preparado para consumo por IA (sin ambigüedades).
        """
        try:
            Product = self.env['product.product']

            products = Product.search([
                ('type', '=', 'product'),
                ('active', '=', True)
            ])

            number_of_products = len(products)
            total_units_in_stock = sum(products.mapped('qty_available'))

            low_stock_products = [
                {
                    'id': p.id,
                    'name': p.display_name,
                    'qty_available': p.qty_available,
                    'uom': p.uom_id.name,
                }
                for p in products
                if 0 < p.qty_available <= 5
            ]

            return {
                # 🔑 claves claras para IA
                'number_of_products': number_of_products,
                'total_units_in_stock': total_units_in_stock,

                # datos auxiliares
                'low_stock_products': low_stock_products[:10],

                # texto ya interpretado (blindaje extra)
                'summary_text': (
                    f'Actualmente hay {total_units_in_stock} unidades disponibles '
                    f'en inventario, considerando {number_of_products} productos distintos.'
                ),

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
        Retorna el total de productos almacenables activos.
        """
        try:
            count = self.env['product.product'].search_count([
                ('type', '=', 'product'),
                ('active', '=', True)
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

    # ================= CRM =================

    @api.model
    def get_crm_summary(self):
        """
        Retorna resumen correcto de CRM.
        """
        try:
            Lead = self.env['crm.lead']

            total_opportunities = Lead.search_count([
                ('type', '=', 'opportunity')
            ])

            open_opportunities = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', 'not in', [0, 100])
            ])

            won_opportunities = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('probability', '=', 100)
            ])

            lost_opportunities = Lead.search_count([
                ('type', '=', 'opportunity'),
                ('probability', '=', 0),
                ('active', '=', False)
            ])

            open_leads = Lead.search([
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', 'not in', [0, 100])
            ])

            total_expected_revenue = sum(
                lead.expected_revenue or 0 for lead in open_leads
            )

            return {
                'total_opportunities': total_opportunities,
                'open_opportunities': open_opportunities,
                'won_opportunities': won_opportunities,
                'lost_opportunities': lost_opportunities,
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
    def get_open_opportunities_count(self):
        """
        Conteo simple de oportunidades abiertas.
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

    @api.model
    def get_opportunities_by_stage(self):
        """
        Oportunidades agrupadas por etapa.
        """
        try:
            Stage = self.env['crm.stage']
            Lead = self.env['crm.lead']

            stages_data = []

            for stage in Stage.search([], order='sequence'):
                opportunities = Lead.search([
                    ('type', '=', 'opportunity'),
                    ('stage_id', '=', stage.id),
                    ('active', '=', True)
                ])

                if opportunities:
                    stages_data.append({
                        'stage_id': stage.id,
                        'stage_name': stage.name,
                        'count': len(opportunities),
                        'expected_revenue': sum(
                            opp.expected_revenue or 0 for opp in opportunities
                        ),
                        'sequence': stage.sequence
                    })

            return {
                'stages': stages_data,
                'total_stages': len(stages_data),
                'currency': self.env.company.currency_id.name,
                'status': 'success'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
