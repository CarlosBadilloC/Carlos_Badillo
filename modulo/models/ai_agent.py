from odoo import models, fields, api
import logging
import requests
import traceback
import google.generativeai as genai

_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'
    
    @api.model
    def message_post(self, **kwargs):
        """Override message_post para interceptar mensajes y procesarlos con IA"""
        message = super(DiscussChannel, self).message_post(**kwargs)
        
        # Verificar si es el canal del AI Agent
        if self.name == 'AI AGENT' and kwargs.get('body'):
            try:
                response = self._process_ai_message(kwargs.get('body'))
                if response:
                    self.message_post(
                        body=response,
                        message_type='comment',
                        subtype_xmlid='mail.mt_comment'
                    )
            except Exception as e:
                _logger.error(f"Error procesando mensaje IA: {str(e)}\n{traceback.format_exc()}")
        
        return message
    
    def _process_ai_message(self, user_message):
        """Procesa el mensaje del usuario con el agente IA"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('modulo.ai_api_key')
        
        if not api_key:
            return "⚠️ No se ha configurado la API Key. Ve a Configuración > Técnico > Parámetros del sistema"
        
        # Configurar Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Definir herramientas disponibles
        tools = [
            {
                "name": "get_odoo_stock",
                "description": "Busca productos en el inventario de Odoo por nombre",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "Nombre del producto a buscar"
                        }
                    },
                    "required": ["product_name"]
                }
            }
        ]
        
        # Crear prompt con contexto
        prompt = f"""Eres un asistente de IA para un sistema Odoo. 
Puedes ayudar a consultar información de inventario.

Herramientas disponibles:
- get_odoo_stock: Busca productos en el inventario

Pregunta del usuario: {user_message}
"""
        
        # Generar respuesta
        response = model.generate_content(prompt)
        
        # Si la IA necesita buscar stock, ejecutar la función
        if 'stock' in user_message.lower() or 'inventario' in user_message.lower() or 'producto' in user_message.lower():
            # Extraer nombre del producto del mensaje
            stock_info = self._get_odoo_stock(user_message)
            return f"{response.text}\n\n📦 **Información de Inventario:**\n{stock_info}"
        
        return response.text
    
    def _get_odoo_stock(self, product_name: str) -> str:
        """Busca productos en el inventario interno de Odoo"""
        # Limpiar el mensaje para obtener el nombre del producto
        search_term = product_name.replace('stock', '').replace('inventario', '').replace('producto', '').strip()
        
        products = self.env['product.product'].sudo().search([
            ('name', 'ilike', search_term)
        ], limit=5)
        
        if not products:
            return "❌ No se encontraron productos que coincidan con la búsqueda"
        
        info = []
        for p in products:
            stock_info = f"- **{p.name}**: {p.qty_available} uds disponibles"
            if p.list_price:
                stock_info += f" | Precio: ${p.list_price:.2f}"
            info.append(stock_info)
        
        return "\n".join(info)


class AIAgentConfig(models.TransientModel):
    """Modelo para configuración del agente IA"""
    _inherit = 'res.config.settings'
    
    ai_agent_enabled = fields.Boolean(
        string="Habilitar Agente IA",
        config_parameter='modulo.ai_agent_enabled',
        default=False
    )
    
    ai_model_name = fields.Selection([
        ('gemini-pro', 'Gemini Pro'),
        ('gemini-1.5-flash', 'Gemini 1.5 Flash'),
    ], string="Modelo IA", default='gemini-pro', config_parameter='modulo.ai_model_name')