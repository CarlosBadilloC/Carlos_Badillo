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
        """Llama al agente IA y obtiene respuesta ejecutando acciones directamente"""
        try:
            prompt_lower = prompt.lower()
            
            # Palabras clave para cada sección
            inventory_keywords = ['stock', 'producto', 'disponible', 'inventario', 'catálogo', 'precio', 'cantidad', 'unidades', 'desk', 'escritorio', 'silla', 'mueble']
            crm_keywords = ['lead', 'oportunidad', 'cliente', 'cotización', 'presupuesto', 'venta', 'pipeline', 'etapa', 'qualified', 'proposition', 'won', 'new']
            
            # Contar coincidencias de palabras clave
            inventory_matches = sum(1 for kw in inventory_keywords if kw in prompt_lower)
            crm_matches = sum(1 for kw in crm_keywords if kw in prompt_lower)
            
            # INVENTARIO - Prioridad alta
            if inventory_matches >= crm_matches:
                # Detectar tipo específico de consulta de inventario
                if 'bajo' in prompt_lower or 'bajo' in prompt_lower:
                    return self.env['ai.inventory.actions'].check_low_stock(threshold=10)
                elif 'resumen' in prompt_lower or 'total' in prompt_lower:
                    return self.env['ai.inventory.actions'].get_inventory_summary()
                elif 'categoría' in prompt_lower or 'categoria' in prompt_lower:
                    # Extraer nombre de categoría
                    category_name = self._extract_category_from_prompt(prompt)
                    return self.env['ai.inventory.actions'].search_product_by_category(category_name or 'All')
                else:
                    # Búsqueda general de productos
                    return self.env['ai.inventory.actions'].search_products_detailed(prompt)
            
            # CRM - Prioridad media
            elif crm_matches > 0:
                # Crear oportunidad
                if 'crear' in prompt_lower and 'oportunidad' in prompt_lower:
                    opportunity_data = self._extract_opportunity_data(prompt)
                    return self.env['ai.crm.actions'].create_opportunity(
                        name=opportunity_data['name'],
                        customer_name=opportunity_data['customer_name'],
                        email=opportunity_data['email'],
                        phone=opportunity_data['phone'],
                        stage_name=opportunity_data['stage_name'],
                        expected_revenue=opportunity_data['expected_revenue']
                    )
                
                # Búsqueda por etapa
                elif 'etapa' in prompt_lower or 'qualified' in prompt_lower or 'proposition' in prompt_lower or 'won' in prompt_lower:
                    stage_name = self._extract_stage_from_prompt(prompt)
                    return self.env['ai.crm.actions'].search_leads_by_stage(stage_name)
                
                # Resumen del pipeline
                elif 'pipeline' in prompt_lower or 'resumen' in prompt_lower or 'etapa' in prompt_lower:
                    return self.env['ai.crm.actions'].get_pipeline_summary()
                
                # Cotizaciones
                elif 'cotización' in prompt_lower or 'cotizacion' in prompt_lower or 'presupuesto' in prompt_lower:
                    product_name = self._extract_product_from_prompt(prompt)
                    return self.env['ai.crm.actions'].search_quotations_with_stock(product_name)
                
                # Listar oportunidades
                elif 'oportunidad' in prompt_lower or 'lead' in prompt_lower:
                    return self.env['ai.crm.actions'].list_open_opportunities(limit=10)
                
                else:
                    return self.env['ai.crm.actions'].list_open_opportunities()
            
            else:
                # Respuesta por defecto
                return (
                    "👋 Hola, soy tu asistente de IA. Puedo ayudarte con:\n\n"
                    "📦 **Inventario:**\n"
                    "  • Consultar stock de productos\n"
                    "  • Ver productos por categoría\n"
                    "  • Resumen del inventario\n"
                    "  • Detectar stock bajo\n\n"
                    "💼 **CRM:**\n"
                    "  • Listar oportunidades abiertas\n"
                    "  • Buscar leads por etapa\n"
                    "  • Ver resumen del pipeline\n"
                    "  • Crear nuevas oportunidades\n"
                    "  • Consultar cotizaciones\n\n"
                    "¿En qué puedo ayudarte?"
                )
                
        except Exception as e:
            _logger.error(f"Error llamando agente IA: {e}", exc_info=True)
            return f"❌ Disculpa, ocurrió un error procesando tu solicitud: {str(e)}"

    @api.model
    def _extract_product_from_prompt(self, prompt):
        """Extrae nombre de producto del prompt"""
        # Palabras a ignorar
        stopwords = ['para', 'de', 'del', 'la', 'el', 'productos', 'y', 'muéstrame', 'dame', 'verifica', 'disponible', 'stock', 'cotización', 'cotizaciones']
        words = [w for w in prompt.split() if w.lower() not in stopwords and len(w) > 2]
        return ' '.join(words[:3]) if words else 'producto'

    @api.model
    def _extract_category_from_prompt(self, prompt):
        """Extrae nombre de categoría del prompt"""
        import re
        # Buscar patrones como "categoría [nombre]" o "de la categoría [nombre]"
        match = re.search(r'categoría\s+(\w+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1)
        return 'All'

    @api.model
    def _extract_stage_from_prompt(self, prompt):
        """Extrae nombre de etapa del prompt"""
        stages = ['Qualified', 'Proposition', 'Won', 'New']
        for stage in stages:
            if stage.lower() in prompt.lower():
                return stage
        return 'New'

    @api.model
    def _extract_opportunity_data(self, prompt):
        """Extrae datos para crear oportunidad del prompt"""
        import re
        
        data = {
            'name': '',
            'customer_name': '',
            'email': '',
            'phone': '',
            'stage_name': '',
            'expected_revenue': 0.0
        }
        
        # Buscar nombre entre comillas
        name_match = re.search(r'"([^"]+)"', prompt)
        if name_match:
            data['name'] = name_match.group(1)
        
        # Buscar email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', prompt)
        if email_match:
            data['email'] = email_match.group(1)
        
        # Buscar cliente (después de "cliente" o "para")
        client_match = re.search(r'(?:cliente|para)\s+"?([^"\n,]+)"?', prompt, re.IGNORECASE)
        if client_match:
            data['customer_name'] = client_match.group(1).strip()
        
        # Si no hay nombre, usar el del cliente
        if not data['name'] and data['customer_name']:
            data['name'] = f"Oportunidad para {data['customer_name']}"
        elif not data['name']:
            data['name'] = "Nueva Oportunidad"
        
        return data