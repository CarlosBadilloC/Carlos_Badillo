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
        """Formatea respuesta con protocolo A2UI para livechat - genera HTML directo"""
        text = response_dict.get('text', '')
        dashboard = response_dict.get('a2ui_dashboard', {})
        
        # Generar HTML para renderizar en el chat
        html = self._generate_dashboard_html(dashboard)
        
        # Retornar HTML con estilos inline
        return f"<div>{text}</div>{html}"
    
    @api.model
    def _generate_dashboard_html(self, dashboard):
        """Genera HTML directo para los dashboards con CSS inline"""
        dashboard_type = dashboard.get('type', '')
        
        if dashboard_type == 'table':
            return self._html_table_dashboard(dashboard)
        elif dashboard_type == 'summary_cards':
            return self._html_summary_cards(dashboard)
        elif dashboard_type == 'pipeline':
            return self._html_pipeline_dashboard(dashboard)
        elif dashboard_type == 'opportunities':
            return self._html_opportunities_dashboard(dashboard)
        elif dashboard_type == 'alert_table':
            return self._html_alert_table(dashboard)
        elif dashboard_type == 'help_menu':
            return self._html_help_menu(dashboard)
        
        return ""
    
    @api.model
    def _html_table_dashboard(self, dashboard):
        """Genera HTML para tabla de productos"""
        title = dashboard.get('title', 'Productos')
        columns = dashboard.get('columns', [])
        rows = dashboard.get('rows', [])
        
        html = f"""
        <div style="margin: 15px 0; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0;">
            <div style="padding: 15px; background: #f5f5f5; border-bottom: 1px solid #e0e0e0;">
                <h3 style="margin: 0; color: #333; font-size: 16px;">{title}</h3>
            </div>
            <div style="overflow-x: auto;">
                <table cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: #f9f9f9; border-bottom: 2px solid #e0e0e0;">
        """
        
        for col in columns:
            html += f"<th style='padding: 12px; text-align: left; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>{col['label']}</th>"
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for row in rows:
            html += "<tr style='border-bottom: 1px solid #f0f0f0;'>"
            for col in columns:
                value = row.get(col['key'], '')
                html += f"<td style='padding: 12px; color: #333; border-right: 1px solid #f0f0f0;'>{value}</td>"
            html += "</tr>"
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        return html
    
    @api.model
    def _html_summary_cards(self, dashboard):
        """Genera HTML para tarjetas resumen"""
        cards = dashboard.get('cards', [])
        table_data = dashboard.get('table', {})
        
        colors = {
            'primary': '#0066cc',
            'success': '#28a745',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
        
        html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 15px 0;'>"
        
        for card in cards:
            color = colors.get(card.get('color', 'primary'), '#0066cc')
            text_color = 'white' if card.get('color') != 'warning' else '#333'
            icon = card.get('icon', '📊')
            title = card.get('title', '')
            value = card.get('value', '')
            subtitle = card.get('subtitle', '')
            
            html += f"""
            <div style="background: {color}; color: {text_color}; padding: 15px; border-radius: 6px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>
                <div style="font-size: 12px; opacity: 0.85; margin-bottom: 6px;">{title}</div>
                <div style="font-size: 20px; font-weight: bold; margin: 6px 0;">{value}</div>
                {f'<div style="font-size: 11px; opacity: 0.75;">{subtitle}</div>' if subtitle else ''}
            </div>
            """
        
        html += "</div>"
        
        # Agregar tabla si existe
        if table_data:
            columns = table_data.get('columns', [])
            rows = table_data.get('rows', [])
            title = table_data.get('title', '')
            
            html += f"""
            <div style="margin: 15px 0; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0;">
                <div style="padding: 12px 15px; background: #f5f5f5; border-bottom: 1px solid #e0e0e0;">
                    <h4 style="margin: 0; color: #333; font-size: 14px;">{title}</h4>
                </div>
                <div style="overflow-x: auto;">
                    <table cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="background: #f9f9f9; border-bottom: 2px solid #e0e0e0;">
            """
            
            for col in columns:
                html += f"<th style='padding: 10px 12px; text-align: left; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>{col['label']}</th>"
            
            html += """
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for row in rows:
                html += "<tr style='border-bottom: 1px solid #f0f0f0;'>"
                for col in columns:
                    value = row.get(col['key'], '')
                    html += f"<td style='padding: 10px 12px; color: #333; border-right: 1px solid #f0f0f0;'>{value}</td>"
                html += "</tr>"
            
            html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
        
        return html
    
    @api.model
    def _html_alert_table(self, dashboard):
        """Genera HTML para tabla de alertas"""
        title = dashboard.get('title', 'Alertas')
        columns = dashboard.get('columns', [])
        rows = dashboard.get('rows', [])
        summary = dashboard.get('summary', {})
        
        html = f"""
        <div style="margin: 15px 0; background: #fff8e1; border-left: 4px solid #ffc107; padding: 15px; border-radius: 6px; border: 1px solid #ffe0b2;">
            <div style="color: #f57f17; font-weight: bold; margin-bottom: 12px; font-size: 14px;">⚠️ {title}</div>
            
            <div style="background: white; border-radius: 4px; overflow: hidden; margin-bottom: 12px; border: 1px solid #e0e0e0;">
                <div style="overflow-x: auto;">
                    <table cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="background: #f9f9f9; border-bottom: 2px solid #e0e0e0;">
        """
        
        for col in columns:
            html += f"<th style='padding: 10px 12px; text-align: left; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>{col['label']}</th>"
        
        html += """
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for row in rows:
            html += "<tr style='border-bottom: 1px solid #f0f0f0;'>"
            for col in columns:
                value = row.get(col['key'], '')
                html += f"<td style='padding: 10px 12px; color: #333; border-right: 1px solid #f0f0f0;'>{value}</td>"
            html += "</tr>"
        
        html += f"""
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;">
                <div style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #e0e0e0;">
                    <div style="color: #999; font-size: 11px; margin-bottom: 4px;">📦 Total Productos</div>
                    <div style="font-size: 16px; font-weight: bold; color: #333;">{summary.get('total_products', 0)}</div>
                </div>
                <div style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #e0e0e0;">
                    <div style="color: #999; font-size: 11px; margin-bottom: 4px;">💰 Reabastecer</div>
                    <div style="font-size: 16px; font-weight: bold; color: #d32f2f;">{summary.get('restock_value', '$0.00')}</div>
                </div>
            </div>
        </div>
        """
        return html
    
    @api.model
    def _html_opportunities_dashboard(self, dashboard):
        """Genera HTML para oportunidades"""
        cards = dashboard.get('cards', [])
        columns = dashboard.get('columns', [])
        rows = dashboard.get('rows', [])
        
        colors = {'primary': '#0066cc', 'success': '#28a745'}
        
        html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 15px 0;'>"
        
        for card in cards:
            color = colors.get(card.get('color', 'primary'), '#0066cc')
            html += f"""
            <div style="background: {color}; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 24px; margin-bottom: 6px;">{card.get('icon', '🎯')}</div>
                <div style="font-size: 11px; opacity: 0.85; margin-bottom: 4px;">{card.get('title', '')}</div>
                <div style="font-size: 18px; font-weight: bold;">{card.get('value', '')}</div>
            </div>
            """
        
        html += """
        </div>
        <div style="margin: 15px 0; background: white; border-radius: 6px; overflow: hidden; border: 1px solid #e0e0e0;">
            <div style="overflow-x: auto;">
                <table cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                    <thead>
                        <tr style="background: #f9f9f9; border-bottom: 2px solid #e0e0e0;">
        """
        
        for col in columns:
            html += f"<th style='padding: 10px 12px; text-align: left; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>{col['label']}</th>"
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for row in rows:
            html += "<tr style='border-bottom: 1px solid #f0f0f0;'>"
            for col in columns:
                value = row.get(col['key'], '')
                html += f"<td style='padding: 10px 12px; color: #333; border-right: 1px solid #f0f0f0;'>{value}</td>"
            html += "</tr>"
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        return html
    
    @api.model
    def _html_pipeline_dashboard(self, dashboard):
        """Genera HTML para pipeline"""
        cards = dashboard.get('cards', [])
        stages = dashboard.get('stages', [])
        
        colors = {'primary': '#0066cc', 'success': '#28a745', 'info': '#17a2b8'}
        
        html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin: 15px 0;'>"
        
        for card in cards:
            color = colors.get(card.get('color', 'primary'), '#0066cc')
            html += f"""
            <div style="background: {color}; color: white; padding: 12px; border-radius: 6px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 24px; margin-bottom: 6px;">{card.get('icon', '📊')}</div>
                <div style="font-size: 11px; opacity: 0.85; margin-bottom: 4px;">{card.get('title', '')}</div>
                <div style="font-size: 18px; font-weight: bold;">{card.get('value', '')}</div>
            </div>
            """
        
        html += """
        </div>
        <div style="margin: 15px 0;">
            <h4 style="color: #333; margin: 0 0 12px 0; font-size: 14px;">📊 Pipeline por Etapa</h4>
            <div style="background: white; border-radius: 6px; overflow: hidden; border: 1px solid #e0e0e0;">
                <div style="overflow-x: auto;">
                    <table cellpadding="0" cellspacing="0" style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="background: #f9f9f9; border-bottom: 2px solid #e0e0e0;">
                                <th style='padding: 10px 12px; text-align: left; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>Etapa</th>
                                <th style='padding: 10px 12px; text-align: center; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>Cantidad</th>
                                <th style='padding: 10px 12px; text-align: right; color: #666; font-weight: 600; border-right: 1px solid #f0f0f0;'>Ingresos</th>
                                <th style='padding: 10px 12px; text-align: right; color: #666; font-weight: 600;'>Promedio</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        for stage in stages:
            html += f"""
                            <tr style='border-bottom: 1px solid #f0f0f0;'>
                                <td style='padding: 10px 12px; color: #333; border-right: 1px solid #f0f0f0;'>{stage.get('stage', '')}</td>
                                <td style='padding: 10px 12px; color: #333; text-align: center; border-right: 1px solid #f0f0f0; font-weight: bold;'>{stage.get('count', 0)}</td>
                                <td style='padding: 10px 12px; color: #28a745; text-align: right; border-right: 1px solid #f0f0f0; font-weight: bold;'>{stage.get('revenue', '$0.00')}</td>
                                <td style='padding: 10px 12px; color: #333; text-align: right;'>{stage.get('avg_deal', '$0.00')}</td>
                            </tr>
            """
        
        html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        return html
    
    @api.model
    def _html_help_menu(self, dashboard):
        """Genera HTML para menú de ayuda"""
        options = dashboard.get('options', [])
        message = dashboard.get('message', '')
        
        html = """
        <div style="margin: 15px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 12px;">
        """
        
        for option in options:
            keywords = ', '.join(option.get('keywords', []))
            html += f"""
                <div style="background: rgba(255, 255, 255, 0.12); padding: 10px; border-radius: 4px; border: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="font-size: 20px; margin-bottom: 6px;">{option.get('icon', '📦')}</div>
                    <div style="font-weight: bold; font-size: 12px; margin-bottom: 3px;">{option.get('title', '')}</div>
                    <div style="font-size: 10px; margin-bottom: 4px; opacity: 0.9;">{option.get('description', '')}</div>
                    <div style="font-size: 9px; opacity: 0.8;">{keywords}</div>
                </div>
            """
        
        html += f"""
            </div>
            <div style="background: rgba(0, 0, 0, 0.15); padding: 10px; border-radius: 4px; font-size: 11px; line-height: 1.6; border-left: 3px solid rgba(255, 255, 255, 0.4);">
                {message.replace(chr(10), '<br/>')}
            </div>
        </div>
        """
        return html

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