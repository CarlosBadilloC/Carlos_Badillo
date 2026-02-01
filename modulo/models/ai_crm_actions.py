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
        """Lista oportunidades abiertas"""
        opportunities = self.env['crm.lead'].sudo().search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '<', 100),
        ], limit=limit, order="probability desc, expected_revenue desc")

        if not opportunities:
            return "✅ No hay oportunidades abiertas."

        result = ["📌 Oportunidades abiertas:"]
        for o in opportunities:
            stage = o.stage_id.name if o.stage_id else "Sin etapa"
            result.append(
                f"  • {o.name} ({stage}) - {o.probability}% - ${o.expected_revenue:,.2f}"
            )

        return "\n".join(result)

    @api.model
    def get_pipeline_summary(self):
        """Resumen del pipeline por etapa"""
        data = self.env['crm.lead'].sudo().read_group(
            [('type', '=', 'opportunity'), ('active', '=', True)],
            ['expected_revenue:sum'],
            ['stage_id'],
        )

        if not data:
            return "✅ No hay datos en el pipeline."

        result = ["📊 Resumen del pipeline por etapa:"]
        for row in data:
            stage = row['stage_id'][1] if row.get('stage_id') else "Sin etapa"
            count = row['__count']
            revenue = row['expected_revenue'] or 0.0
            result.append(f"  • {stage}: {count} oportunidades - ${revenue:,.2f}")

        return "\n".join(result)

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