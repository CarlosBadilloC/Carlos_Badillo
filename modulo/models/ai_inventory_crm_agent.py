from odoo import models, api, fields

class AIInventoryCRMAgent(models.Model):
    _name = 'ai.inventory.crm.agent'
    _description = 'AI Agent for Inventory and CRM'

    name = fields.Char(default="Inventory & CRM Agent")
    description = fields.Text(default="AI Assistant for Inventory and CRM queries")

    @api.model
    def _get_tools(self):
        """Lista de herramientas disponibles para el agente"""
        return [
            {
                'name': 'get_inventory_summary',
                'description': 'Resumen de inventario: productos, cantidades y bajo stock',
                'action': self._tool_get_inventory_summary
            },
            {
                'name': 'get_product_count',
                'description': 'Total de productos en inventario',
                'action': self._tool_get_product_count
            },
            {
                'name': 'get_crm_summary',
                'description': 'Resumen de CRM: oportunidades, ganadas, perdidas, ingresos esperados',
                'action': self._tool_get_crm_summary
            },
            {
                'name': 'get_open_opportunities_count',
                'description': 'Conteo de oportunidades abiertas',
                'action': self._tool_get_open_opportunities_count
            },
            {
                'name': 'get_opportunities_by_stage',
                'description': 'Oportunidades agrupadas por etapa del pipeline',
                'action': self._tool_get_opportunities_by_stage
            }
        ]

    # --------------------- INVENTARIO ---------------------
    def _tool_get_inventory_summary(self):
        return self.env['ai.query.handler'].get_inventory_summary()

    def _tool_get_product_count(self):
        return self.env['ai.query.handler'].get_product_count()

    # --------------------- CRM ---------------------
    def _tool_get_crm_summary(self):
        return self.env['ai.query.handler'].get_crm_summary()

    def _tool_get_open_opportunities_count(self):
        return self.env['ai.query.handler'].get_open_opportunities_count()

    def _tool_get_opportunities_by_stage(self):
        return self.env['ai.query.handler'].get_opportunities_by_stage()

    # --------------------- PROMPT DEL SISTEMA ---------------------
    @api.model
    def _get_system_prompt(self):
        return """
You are an intelligent AI assistant for a company using Odoo 19.

Capabilities:
1. Inventory: get_product_count, get_inventory_summary
2. CRM: get_crm_summary, get_open_opportunities_count, get_opportunities_by_stage

Rules:
- Always respond using numbers from the database.
- Provide summaries and insights when possible.
- Answer in the same language as the user's question (Spanish or English).
- Handle errors gracefully if no data is found.

Example:
User: "¿Cuántos productos tenemos en stock?"
AI: "Actualmente tenemos {total_products} productos en inventario."
"""
