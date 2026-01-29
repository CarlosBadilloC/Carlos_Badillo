from odoo import models, api, fields
from odoo.addons.mail_bot.models.mail_bot import _WELCOME_MESSAGE

class AIInventoryAgent(models.Model):
    _name = 'ai.inventory.agent'
    _description = 'AI Inventory Agent'
    _inherit = 'mail.bot'
    
    name = fields.Char(default="Inventory Assistant")
    
    @api.model
    def _get_tools(self):
        """Retorna las tools disponibles para el agente"""
        return [
            {
                'name': 'get_inventory_summary',
                'description': 'Obtiene resumen del inventario',
                'action': self._tool_get_inventory_summary,
            },
            {
                'name': 'get_product_count',
                'description': 'Cuenta el total de productos',
                'action': self._tool_get_product_count,
            },
            {
                'name': 'get_crm_summary',
                'description': 'Obtiene resumen de CRM',
                'action': self._tool_get_crm_summary,
            }
        ]
    
    def _tool_get_inventory_summary(self):
        """Ejecuta la herramienta de resumen de inventario"""
        return self.env['ai.query.handler'].get_inventory_summary()
    
    def _tool_get_product_count(self):
        """Ejecuta la herramienta de conteo de productos"""
        return self.env['ai.query.handler'].get_product_count()
    
    def _tool_get_crm_summary(self):
        """Ejecuta la herramienta de resumen CRM"""
        return self.env['ai.query.handler'].get_crm_summary()
    
    @api.model
    def _get_system_prompt(self):
        """Prompt del sistema para guiar al agente"""
        return """You are an intelligent assistant specialized in inventory and CRM management for Odoo.

Your capabilities:
1. Answer questions about inventory (product count, stock levels, low stock items)
2. Provide CRM insights (opportunities, expected revenue, pipeline status)
3. Use the available tools to get accurate data

When a user asks about:
- "¿Cuánto stock queda?" → Use get_inventory_summary
- "¿Cuántos productos?" → Use get_product_count
- "¿Cuántas oportunidades?" → Use get_crm_summary

Always respond in the same language as the user (Spanish or English).
Be friendly, clear, and provide specific numbers.
Format: "We have {number} {unit}" or "Tenemos {número} {unidad}"

If you encounter an error, inform the user politely."""
    
    @api.model
    def _chat_post_message(self, message, author=None, **kwargs):
        """Procesa mensajes del chat"""
        # Aquí va la lógica para procesar el mensaje con IA
        pass