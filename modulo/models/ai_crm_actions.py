from odoo import models, api

class AICrmActions(models.AbstractModel):
    _name = "ai.crm.actions"
    _description = "Acciones IA CRM"

    @api.model
    def get_lead_info(self, lead_name):
        """Obtiene información de leads u oportunidades por nombre"""
        leads = self.env['crm.lead'].sudo().search([
            ('name', 'ilike', lead_name)
        ], limit=5)

        if not leads:
            return f"No se encontraron leads u oportunidades llamadas '{lead_name}'."

        result = []
        for l in leads:
            tipo = "Oportunidad" if l.type == "opportunity" else "Lead"
            stage = l.stage_id.name if l.stage_id else "Sin etapa"
            cliente = l.partner_id.display_name if l.partner_id else "Sin cliente"
            vendedor = l.user_id.name if l.user_id else "Sin vendedor"
            result.append(
                f"🧩 {l.name}\n"
                f"  • Tipo: {tipo}\n"
                f"  • Etapa: {stage}\n"
                f"  • Cliente: {cliente}\n"
                f"  • Vendedor: {vendedor}\n"
                f"  • Probabilidad: {l.probability}%\n"
                f"  • Ingreso esperado: ${l.expected_revenue:,.2f}"
            )

        return "\n\n".join(result)

    @api.model
    def list_open_opportunities(self, limit=10):
        """Lista oportunidades abiertas con dashboard A2UI"""
        opportunities = self.env['crm.lead'].sudo().search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '<', 100),
        ], limit=limit, order="probability desc, expected_revenue desc")

        if not opportunities:
            return "✅ No hay oportunidades abiertas."

        rows = []
        total_revenue = 0
        for o in opportunities:
            stage = o.stage_id.name if o.stage_id else "Sin etapa"
            customer = o.partner_id.display_name if o.partner_id else "Sin cliente"
            total_revenue += o.expected_revenue
            
            rows.append({
                'name': o.name,
                'customer': customer,
                'stage': stage,
                'probability': f"{o.probability}%",
                'revenue': f"${o.expected_revenue:,.2f}",
                'weighted': f"${o.expected_revenue * o.probability / 100:,.2f}"
            })

        response = {
            'text': f"📌 {len(opportunities)} Oportunidades Abiertas",
            'a2ui_dashboard': {
                'type': 'opportunities',
                'cards': [
                    {
                        'title': 'Total Oportunidades',
                        'value': len(opportunities),
                        'icon': '🎯',
                        'color': 'primary'
                    },
                    {
                        'title': 'Ingresos Totales',
                        'value': f"${total_revenue:,.2f}",
                        'icon': '💰',
                        'color': 'success'
                    }
                ],
                'columns': [
                    {'key': 'name', 'label': 'Oportunidad'},
                    {'key': 'customer', 'label': 'Cliente'},
                    {'key': 'stage', 'label': 'Etapa'},
                    {'key': 'probability', 'label': 'Probabilidad'},
                    {'key': 'revenue', 'label': 'Ingresos'},
                    {'key': 'weighted', 'label': 'Ponderado'}
                ],
                'rows': rows
            }
        }
        return response

    @api.model
    def create_opportunity(self, name, customer_name=None, email=None, phone=None, stage_name=None, expected_revenue=0.0):
        """Crea una oportunidad con los campos indicados"""
        if not name:
            return "❌ El nombre de la oportunidad es obligatorio."

        partner = False
        if customer_name or email or phone:
            domain = []
            if email:
                domain = ['|', ('email', '=', email), ('name', 'ilike', customer_name or '')]
            elif phone:
                domain = ['|', ('phone', '=', phone), ('name', 'ilike', customer_name or '')]
            else:
                domain = [('name', 'ilike', customer_name)]
            partner = self.env['res.partner'].sudo().search(domain, limit=1)
            if not partner and customer_name:
                partner = self.env['res.partner'].sudo().create({
                    'name': customer_name,
                    'email': email,
                    'phone': phone,
                })

        stage_id = False
        if stage_name:
            stage = self.env['crm.stage'].sudo().search([('name', 'ilike', stage_name)], limit=1)
            stage_id = stage.id if stage else False

        opportunity_vals = {
            'name': name,
            'partner_id': partner.id if partner else False,
            'email_from': email,
            'phone': phone,
            'expected_revenue': expected_revenue or 0.0,
            'type': 'opportunity',
        }
        if stage_id:
            opportunity_vals['stage_id'] = stage_id

        opportunity = self.env['crm.lead'].sudo().create(opportunity_vals)

        stage_label = opportunity.stage_id.name if opportunity.stage_id else "Sin etapa"
        return (
            f"✅ Oportunidad creada: {opportunity.name}\n"
            f"  • Cliente: {opportunity.partner_id.display_name or 'Sin cliente'}\n"
            f"  • Email: {opportunity.email_from or 'Sin email'}\n"
            f"  • Teléfono: {opportunity.phone or 'Sin teléfono'}\n"
            f"  • Etapa: {stage_label}\n"
            f"  • Ingreso esperado: ${opportunity.expected_revenue:,.2f}"
        )

    @api.model
    def get_pipeline_summary(self):
        """Resumen del pipeline por etapa con dashboard A2UI"""
        opportunities = self.env['crm.lead'].sudo().search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
        ])

        if not opportunities:
            return "✅ No hay datos en el pipeline."

        stage_data = {}
        for opp in opportunities:
            stage_name = opp.stage_id.name if opp.stage_id else "Sin etapa"
            if stage_name not in stage_data:
                stage_data[stage_name] = {'count': 0, 'revenue': 0.0, 'opportunities': []}
            stage_data[stage_name]['count'] += 1
            stage_data[stage_name]['revenue'] += opp.expected_revenue
            stage_data[stage_name]['opportunities'].append(opp)

        stage_rows = []
        total_revenue = 0
        for stage, data in stage_data.items():
            total_revenue += data['revenue']
            stage_rows.append({
                'stage': stage,
                'count': data['count'],
                'revenue': f"${data['revenue']:,.2f}",
                'avg_deal': f"${data['revenue']/data['count']:,.2f}" if data['count'] > 0 else "$0.00"
            })

        response = {
            'text': '📊 Resumen del Pipeline CRM',
            'a2ui_dashboard': {
                'type': 'pipeline',
                'cards': [
                    {
                        'title': 'Total Oportunidades',
                        'value': len(opportunities),
                        'icon': '🎯',
                        'color': 'primary'
                    },
                    {
                        'title': 'Ingresos Proyectados',
                        'value': f"${total_revenue:,.2f}",
                        'icon': '💰',
                        'color': 'success'
                    },
                    {
                        'title': 'Ingreso Promedio',
                        'value': f"${total_revenue/len(opportunities):,.2f}" if opportunities else "$0.00",
                        'icon': '📈',
                        'color': 'info'
                    }
                ],
                'stages': stage_rows,
                'columns': [
                    {'key': 'stage', 'label': 'Etapa'},
                    {'key': 'count', 'label': 'Cantidad'},
                    {'key': 'revenue', 'label': 'Ingresos'},
                    {'key': 'avg_deal', 'label': 'Promedio'}
                ]
            }
        }
        return response

    @api.model
    def search_leads_by_stage(self, stage_name):
        """Busca leads u oportunidades por etapa"""
        stages = self.env['crm.stage'].sudo().search([
            ('name', 'ilike', stage_name)
        ])

        if not stages:
            return f"No se encontraron etapas llamadas '{stage_name}'."

        leads = self.env['crm.lead'].sudo().search([
            ('stage_id', 'in', stages.ids)
        ], limit=10)

        if not leads:
            return f"No hay leads u oportunidades en la etapa '{stage_name}'."

        result = [f"Leads/Oportunidades en '{stage_name}':"]
        for l in leads:
            tipo = "Oportunidad" if l.type == "opportunity" else "Lead"
            result.append(f"  • {l.name} ({tipo})")

        return "\n".join(result)
    
    @api.model
    def create_lead(self, name, customer_name=None, email=None, phone=None, stage_name=None, expected_revenue=0.0):
        """Crea un lead con los campos indicados"""
        if not name:
            return "❌ El nombre del lead es obligatorio."

        partner = False
        if customer_name or email or phone:
            domain = []
            if email:
                domain = ['|', ('email', '=', email), ('name', 'ilike', customer_name or '')]
            elif phone:
                domain = ['|', ('phone', '=', phone), ('name', 'ilike', customer_name or '')]
            else:
                domain = [('name', 'ilike', customer_name)]
            partner = self.env['res.partner'].sudo().search(domain, limit=1)
            if not partner and customer_name:
                partner = self.env['res.partner'].sudo().create({
                    'name': customer_name,
                    'email': email,
                    'phone': phone,
                })

        stage_id = False
        if stage_name:
            stage = self.env['crm.stage'].sudo().search([('name', 'ilike', stage_name)], limit=1)
            stage_id = stage.id if stage else False

        lead_vals = {
            'name': name,
            'partner_id': partner.id if partner else False,
            'email_from': email,
            'phone': phone,
            'expected_revenue': expected_revenue or 0.0,
            'type': 'lead',
        }
        if stage_id:
            lead_vals['stage_id'] = stage_id

        lead = self.env['crm.lead'].sudo().create(lead_vals)

        stage_label = lead.stage_id.name if lead.stage_id else "Sin etapa"
        return (
            f"✅ Lead creado: {lead.name}\n"
            f"  • Cliente: {lead.partner_id.display_name or 'Sin cliente'}\n"
            f"  • Email: {lead.email_from or 'Sin email'}\n"
            f"  • Teléfono: {lead.phone or 'Sin teléfono'}\n"
            f"  • Etapa: {stage_label}\n"
            f"  • Ingreso esperado: ${lead.expected_revenue:,.2f}"
        )
    @api.model
    def search_quotations_with_stock(self, product_name):
        """Busca cotizaciones que contengan un producto y muestra stock disponible"""
        # Buscar productos relacionados
        products = self.env['product.product'].sudo().search([
            '|', '|',
            ('name', 'ilike', product_name),
            ('description', 'ilike', product_name),
            ('categ_id.name', 'ilike', product_name)
        ])

        if not products:
            return f"❌ No se encontraron productos relacionados con '{product_name}'."

        # Buscar cotizaciones (sale.order en estado draft o sent)
        quotations = self.env['sale.order'].sudo().search([
            ('state', 'in', ['draft', 'sent']),
            ('order_line.product_id', 'in', products.ids)
        ], limit=10)

        if not quotations:
            product_names = ', '.join(products.mapped('name')[:3])
            return f"📋 No se encontraron cotizaciones activas para productos relacionados con '{product_name}' ({product_names})."

        result = [f"📋 Encontré {len(quotations)} cotización(es) para productos relacionados con '{product_name}':\n"]

        for quote in quotations:
            customer = quote.partner_id.display_name if quote.partner_id else "Sin cliente"
            state_label = "Borrador" if quote.state == 'draft' else "Enviada"
            
            result.append(
                f"📄 **Cotización {quote.name}**\n"
                f"  • Cliente: {customer}\n"
                f"  • Estado: {state_label}\n"
                f"  • Fecha: {quote.date_order.strftime('%d/%m/%Y')}\n"
                f"  • Total: ${quote.amount_total:,.2f}\n"
                f"  • Productos:"
            )

            # Listar productos de la cotización que coincidan con la búsqueda
            for line in quote.order_line.filtered(lambda l: l.product_id in products):
                product = line.product_id
                qty_quoted = int(line.product_uom_qty)
                stock_available = int(product.qty_available)
                
                # Verificar si hay suficiente stock
                if stock_available >= qty_quoted:
                    stock_status = f"✅ Stock suficiente ({stock_available} disponibles)"
                elif stock_available > 0:
                    stock_status = f"⚠️ Stock parcial ({stock_available} disponibles de {qty_quoted} requeridos)"
                else:
                    stock_status = f"❌ Sin stock ({qty_quoted} requeridos)"

                result.append(
                    f"    - {product.name}\n"
                    f"      • Cantidad cotizada: {qty_quoted} unidades\n"
                    f"      • Precio unitario: ${line.price_unit:,.2f}\n"
                    f"      • Subtotal: ${line.price_subtotal:,.2f}\n"
                    f"      • {stock_status}"
                )

        return "\n\n".join(result)