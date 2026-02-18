from odoo import models, api, fields
import logging
import re
import json

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
    def _get_help_menu(self):
        """Retorna un menú de ayuda cuando no se detecta una acción específica"""
        help_menu = {
            'text': '👋 ¿Cómo puedo ayudarte?',
            'a2ui_dashboard': {
                'type': 'help_menu',
                'options': [
                    {
                        'icon': '📦',
                        'title': 'Inventario',
                        'description': 'Buscar productos, verificar stock, estado de inventario',
                        'keywords': ['productos', 'stock', 'inventario', 'disponibilidad']
                    },
                    {
                        'icon': '🎯',
                        'title': 'CRM',
                        'description': 'Oportunidades, leads, pipeline de ventas',
                        'keywords': ['oportunidades', 'leads', 'pipeline', 'ventas']
                    },
                    {
                        'icon': '💰',
                        'title': 'Cotizaciones',
                        'description': 'Buscar presupuestos y cotizaciones de productos',
                        'keywords': ['cotización', 'presupuesto', 'quote', 'cotizaciones']
                    },
                    {
                        'icon': '⚠️',
                        'title': 'Stock Bajo',
                        'description': 'Ver productos con stock bajo para reabastecer',
                        'keywords': ['stock bajo', 'poco stock', 'reabastecer']
                    }
                ],
                'message': 'Prueba escribiendo frases como:\n• "Busco pelotas de futbol"\n• "¿Cuál es el resumen del pipeline?"\n• "¿Existe cotización para balones?"\n• "Muestra stock bajo"'
            }
        }
        return self._format_a2ui_response(help_menu)

    @api.model
    def _call_ai_agent(self, ai_agent, prompt):
        """Llama al agente IA y obtiene respuesta con soporte A2UI"""
        try:
            prompt_lower = prompt.lower()
            response = None
            
            # 1. COTIZACIONES
            if re.search(r'cotizacion|cotización|presupuesto|quote', prompt_lower):
                product_name = self._extract_product_from_prompt(prompt)
                _logger.info(f"🔍 Detectado: Búsqueda de cotizaciones para '{product_name}'")
                response = self.env['ai.crm.actions'].search_quotations_with_stock(product_name)
            
            # 2. STOCK BAJO
            elif re.search(r'stock\s+bajo|poco\s+stock|bajo\s+inventario', prompt_lower):
                _logger.info(f"🔍 Detectado: Stock bajo")
                response = self.env['ai.inventory.actions'].check_low_stock(threshold=10)
            
            # 3. RESUMEN DE INVENTARIO
            elif re.search(r'resumen\s+inventario|inventario\s+completo|estado\s+inventario', prompt_lower):
                _logger.info(f"🔍 Detectado: Resumen de inventario")
                response = self.env['ai.inventory.actions'].get_inventory_summary()
            
            # 4. RESUMEN DEL PIPELINE
            elif re.search(r'pipeline|resumen\s+ventas|sales\s+summary', prompt_lower):
                _logger.info(f"🔍 Detectado: Resumen del pipeline")
                response = self.env['ai.crm.actions'].get_pipeline_summary()
            
            # 5. LISTAR OPORTUNIDADES
            elif re.search(r'oportunidad|opportunity|lead', prompt_lower) and re.search(r'list|listar|mostrar|abiertas', prompt_lower):
                _logger.info(f"🔍 Detectado: Listar oportunidades abiertas")
                response = self.env['ai.crm.actions'].list_open_opportunities(limit=10)
            
            # 6. BÚSQUEDA DE PRODUCTOS
            elif re.search(r'busco|search|productos|products|stock', prompt_lower):
                _logger.info(f"🔍 Detectado: Búsqueda general de productos")
                response = self.env['ai.inventory.actions'].search_products_detailed(prompt)
            
            # Formatear respuesta A2UI si es un diccionario
            if isinstance(response, dict) and 'a2ui_dashboard' in response:
                return self._format_a2ui_response(response)
            
            return response or self._get_help_menu()
                
        except Exception as e:
            _logger.error(f"❌ Error llamando agente IA: {e}", exc_info=True)
            return f"❌ Disculpa, ocurrió un error: {str(e)}"
        
    @api.model
    def _format_a2ui_response(self, response_dict):
        """Formatea respuesta con protocolo A2UI para livechat"""
        text = response_dict.get('text', '')
        dashboard = response_dict.get('a2ui_dashboard', {})
        
        # Crear marcador A2UI especial que el cliente entenderá
        a2ui_json = {
            'type': 'dashboard',
            'data': dashboard
        }
        
        # Formato compatible con Odoo Livechat A2UI
        formatted = f"{text}\n\n<a2ui>{json.dumps(a2ui_json)}</a2ui>"
        return formatted

    @api.model
    def _extract_product_from_prompt(self, prompt):
        """Extrae nombre de producto del prompt usando regex con límites de palabra"""
        # ...existing code...
        stopwords_pattern = r'\b(existe|hay|alguna|algún|muéstrame|dame|verifica|para|con|en|el|la|los|las|de|del|cotización|cotizacion|cotizaciones|presupuesto|presupuestos|quote|quotes)\b'
        
        # Limpiar caracteres especiales primero
        cleaned = re.sub(r'[¿?¡!,;]', '', prompt.lower())
        
        # Eliminar stopwords usando regex (palabras completas)
        cleaned = re.sub(stopwords_pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Eliminar espacios múltiples y trim
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Tomar las primeras palabras significativas (mínimo 2 caracteres)
        words = [w for w in cleaned.split() if len(w) > 1]
        result = ' '.join(words[:5]) if words else 'producto'
        
        _logger.info(f"Producto extraído de '{prompt}': '{result}'")
        return result

    @api.model
    def _extract_category_from_prompt(self, prompt):
        """Extrae nombre de categoría del prompt"""
        # ...existing code...
        match = re.search(r'categoría\s+([a-záéíóú\w]+)|categoria\s+([a-záéíóú\w]+)', prompt, re.IGNORECASE)
        if match:
            category = match.group(1) or match.group(2)
            _logger.info(f"Categoría extraída: '{category}'")
            return category
        return 'All'

    @api.model
    def _extract_stage_from_prompt(self, prompt):
        """Extrae nombre de etapa del prompt"""
        # ...existing code...
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
        # ...existing code...
        cleaned = re.sub(r'(información|info|detalles|details|dame|tell\s+me|lead|oportunidad|opportunity|del?|de|la)', '', prompt, flags=re.IGNORECASE).strip()
        _logger.info(f"Lead/Oportunidad extraída: '{cleaned}'")
        return cleaned or 'lead'

    @api.model
    def _extract_opportunity_data(self, prompt):
        """Extrae datos para crear oportunidad del prompt"""
        # ...existing code...
        data = {
            'name': '',
            'customer_name': '',
            'email': '',
            'phone': '',
            'stage_name': '',
            'expected_revenue': 0.0
        }
        
        name_match = re.search(r'"([^"]+)"', prompt)
        if name_match:
            data['name'] = name_match.group(1)
        
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', prompt)
        if email_match:
            data['email'] = email_match.group(1)
        
        client_match = re.search(r'(?:cliente|customer|para)\s+"?([^"\n,]+)"?', prompt, re.IGNORECASE)
        if client_match:
            data['customer_name'] = client_match.group(1).strip()
        
        if not data['name'] and data['customer_name']:
            data['name'] = f"Oportunidad para {data['customer_name']}"
        elif not data['name']:
            data['name'] = "Nueva Oportunidad"
        
        _logger.info(f"Datos de oportunidad extraídos: {data}")
        return data