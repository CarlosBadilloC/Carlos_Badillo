from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class LivechatIntegration(models.Model):
    _name = "livechat.ai.integration"
    _description = "Integración IA con Livechat"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre", required=True, default="AI Agent Integration")
    active = fields.Boolean(default=True)
    ai_agent_id = fields.Many2one('ai.agent', string="Agente IA", required=True)
    livechat_channel_id = fields.Many2one(
        'im_livechat.channel',
        string="Canal Livechat",
        required=False
    )

    @api.model
    def _call_ai_agent(self, ai_agent, prompt):
        """Llama al agente IA y obtiene respuesta"""
        try:
            prompt_lower = prompt.lower()
            
            # Palabras clave para cada sección
            inventory_keywords = ['stock', 'producto', 'disponible', 'inventario', 'catálogo', 'precio', 'cantidad', 'unidades']
            crm_keywords = ['lead', 'oportunidad', 'cliente', 'cotización', 'presupuesto', 'venta', 'pipeline', 'etapa']
            
            # Contar coincidencias de palabras clave
            inventory_matches = sum(1 for kw in inventory_keywords if kw in prompt_lower)
            crm_matches = sum(1 for kw in crm_keywords if kw in prompt_lower)
            
            # Priorizar según coincidencias
            if inventory_matches > crm_matches:
                return self.env['ai.inventory.actions'].search_products_detailed(prompt)
            elif crm_matches > inventory_matches:
                if 'cotización' in prompt_lower or 'presupuesto' in prompt_lower:
                    return self.env['ai.crm.actions'].search_quotations_with_stock(prompt)
                elif 'pipeline' in prompt_lower or 'resumen' in prompt_lower:
                    return self.env['ai.crm.actions'].get_pipeline_summary()
                else:
                    return self.env['ai.crm.actions'].get_lead_info(prompt)
            else:
                # Si no hay coincidencias claras, intentar búsqueda de inventario primero
                result = self.env['ai.inventory.actions'].search_products_detailed(prompt)
                if '❌ No se encontraron' in result:
                    # Si no hay productos, intentar con CRM
                    return self.env['ai.crm.actions'].list_open_opportunities()
                return result
                
        except Exception as e:
            _logger.error(f"Error llamando agente IA: {e}")
            return f"Disculpa, ocurrió un error procesando tu solicitud."