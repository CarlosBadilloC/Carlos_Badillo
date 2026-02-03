from odoo import models, api, fields
import logging
import re

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
            
            # Detectar intención específica con patrones más precisos
            
            # 1. COTIZACIONES - Máxima prioridad
            if re.search(r'cotizacion|cotización|presupuesto|quote', prompt_lower):
                product_name = self._extract_product_from_prompt(prompt)
                _logger.info(f"🔍 Detectado: Búsqueda de cotizaciones para '{product_name}'")
                return self.env['ai.crm.actions'].search_quotations_with_stock(product_name)
            
            # 2. STOCK BAJO
            elif re.search(r'stock\s+bajo|poco\s+stock|bajo\s+inventario|inventory\s+low', prompt_lower):
                _logger.info(f"🔍 Detectado: Stock bajo")
                return self.env['ai.inventory.actions'].check_low_stock(threshold=10)
            
            # 3. RESUMEN DE INVENTARIO
            elif re.search(r'resumen\s+inventario|inventario\s+completo|estado\s+inventario|inventory\s+summary', prompt_lower):
                _logger.info(f"🔍 Detectado: Resumen de inventario")
                return self.env['ai.inventory.actions'].get_inventory_summary()
            
            # 4. BÚSQUEDA POR CATEGORÍA
            elif re.search(r'categoría|categoria|categor|by\s+category', prompt_lower):
                category_name = self._extract_category_from_prompt(prompt)
                _logger.info(f"🔍 Detectado: Productos por categoría '{category_name}'")
                return self.env['ai.inventory.actions'].search_product_by_category(category_name or 'All')
            
            # 5. CREAR OPORTUNIDAD
            elif re.search(r'crear.*oportunidad|nueva.*oportunidad|create.*opportunity|new.*opportunity', prompt_lower):
                opportunity_data = self._extract_opportunity_data(prompt)
                _logger.info(f"🔍 Detectado: Crear oportunidad '{opportunity_data['name']}'")
                return self.env['ai.crm.actions'].create_opportunity(
                    name=opportunity_data['name'],
                    customer_name=opportunity_data['customer_name'],
                    email=opportunity_data['email'],
                    phone=opportunity_data['phone'],
                    stage_name=opportunity_data['stage_name'],
                    expected_revenue=opportunity_data['expected_revenue']
                )
            
            # 6. BÚSQUEDA POR ETAPA (CRM)
            elif re.search(r'etapa\s+(qualified|proposition|won|new)|leads?\s+en\s+(qualified|proposition|won|new)', prompt_lower):
                stage_name = self._extract_stage_from_prompt(prompt)
                _logger.info(f"🔍 Detectado: Búsqueda por etapa '{stage_name}'")
                return self.env['ai.crm.actions'].search_leads_by_stage(stage_name)
            
            # 7. RESUMEN DEL PIPELINE
            elif re.search(r'pipeline|resumen\s+ventas|sales\s+summary|pipeline\s+summary', prompt_lower):
                _logger.info(f"🔍 Detectado: Resumen del pipeline")
                return self.env['ai.crm.actions'].get_pipeline_summary()
            
            # 8. LISTAR OPORTUNIDADES
            elif re.search(r'oportunidad|opportunity|lead', prompt_lower) and re.search(r'list|listar|mostrar|show|todas|abiertas|abierto', prompt_lower):
                _logger.info(f"🔍 Detectado: Listar oportunidades abiertas")
                return self.env['ai.crm.actions'].list_open_opportunities(limit=10)
            
            # 9. INFORMACIÓN DE LEAD/OPORTUNIDAD ESPECÍFICA
            elif re.search(r'información|info|detalles|details|dame|tell\s+me', prompt_lower) and re.search(r'lead|oportunidad|opportunity', prompt_lower):
                lead_name = self._extract_lead_name_from_prompt(prompt)
                _logger.info(f"🔍 Detectado: Información de lead/oportunidad '{lead_name}'")
                return self.env['ai.crm.actions'].get_lead_info(lead_name)
            
            # 10. BÚSQUEDA DE PRODUCTOS (Por defecto para "busco", "productos", "stock")
            elif re.search(r'busco|search|productos|products|stock|inventario', prompt_lower):
                _logger.info(f"🔍 Detectado: Búsqueda general de productos")
                return self.env['ai.inventory.actions'].search_products_detailed(prompt)
            
            else:
                # Respuesta por defecto si no se identifica la acción
                _logger.info(f"🔍 No se detectó intención clara, mostrando menú de ayuda")
                return (
                    "👋 Hola, soy tu asistente de IA. Puedo ayudarte con:\n\n"
                    "📦 **Inventario:**\n"
                    "  • Consultar stock de productos (ej: 'stock de desks')\n"
                    "  • Ver productos por categoría (ej: 'productos de la categoría muebles')\n"
                    "  • Resumen del inventario (ej: 'resumen de inventario')\n"
                    "  • Detectar stock bajo (ej: '¿hay productos con stock bajo?')\n\n"
                    "💼 **CRM:**\n"
                    "  • Listar oportunidades abiertas (ej: 'muéstrame las oportunidades')\n"
                    "  • Buscar leads por etapa (ej: 'leads en qualified')\n"
                    "  • Ver resumen del pipeline (ej: 'resumen del pipeline')\n"
                    "  • Crear nuevas oportunidades (ej: 'crear oportunidad para cliente X')\n"
                    "  • Consultar cotizaciones (ej: 'cotizaciones de desks')\n\n"
                    "¿En qué puedo ayudarte?"
                )
                
        except Exception as e:
            _logger.error(f"❌ Error llamando agente IA: {e}", exc_info=True)
            return f"❌ Disculpa, ocurrió un error: {str(e)}"

    @api.model
    def _extract_product_from_prompt(self, prompt):
        """Extrae nombre de producto del prompt"""
        stopwords = ['para', 'de', 'del', 'la', 'el', 'productos', 'y', 'muéstrame', 'dame', 'verifica', 'disponible', 'stock', 'cotización', 'cotizaciones', 'presupuesto', 'quote', 'en', 'el', 'la']
        words = [w for w in prompt.split() if w.lower() not in stopwords and len(w) > 2]
        result = ' '.join(words[:4]) if words else 'producto'
        _logger.info(f"Producto extraído: '{result}'")
        return result

    @api.model
    def _extract_category_from_prompt(self, prompt):
        """Extrae nombre de categoría del prompt"""
        match = re.search(r'categoría\s+([a-záéíóú\w]+)|categoria\s+([a-záéíóú\w]+)', prompt, re.IGNORECASE)
        if match:
            category = match.group(1) or match.group(2)
            _logger.info(f"Categoría extraída: '{category}'")
            return category
        return 'All'

    @api.model
    def _extract_stage_from_prompt(self, prompt):
        """Extrae nombre de etapa del prompt"""
        stages = {
            'qualified': 'Qualified',
            'proposition': 'Proposition',
            'won': 'Won',
            'new': 'New'
        }
        for stage_key, stage_value in stages.items():
            if stage_key in prompt.lower():
                _logger.info(f"Etapa extraída: '{stage_value}'")
                return stage_value
        return 'New'

    @api.model
    def _extract_lead_name_from_prompt(self, prompt):
        """Extrae nombre del lead/oportunidad del prompt"""
        # Eliminar palabras clave y quedarse con el resto
        cleaned = re.sub(r'(información|info|detalles|details|dame|tell\s+me|lead|oportunidad|opportunity|del?|de|la)', '', prompt, flags=re.IGNORECASE).strip()
        _logger.info(f"Lead/Oportunidad extraída: '{cleaned}'")
        return cleaned or 'lead'

    @api.model
    def _extract_opportunity_data(self, prompt):
        """Extrae datos para crear oportunidad del prompt"""
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
        
        # Buscar cliente
        client_match = re.search(r'(?:cliente|customer|para)\s+"?([^"\n,]+)"?', prompt, re.IGNORECASE)
        if client_match:
            data['customer_name'] = client_match.group(1).strip()
        
        # Asignar nombre si no existe
        if not data['name'] and data['customer_name']:
            data['name'] = f"Oportunidad para {data['customer_name']}"
        elif not data['name']:
            data['name'] = "Nueva Oportunidad"
        
        _logger.info(f"Datos de oportunidad extraídos: {data}")
        return data