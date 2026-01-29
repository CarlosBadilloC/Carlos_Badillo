from odoo import models, fields, api
import logging
import requests
import traceback
import google.generativeai as genai
import json 

_logger = logging.getLogger(__name__)

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'
    
def message_new(self, msg_dict, custom_values=None):
    _logger.warning("🤖 Mensaje recibido por AI AGENT")

    message = super().message_new(msg_dict, custom_values)

    if self.name != 'AI AGENT':
        return message

    body = msg_dict.get('body')
    if not body:
        return message

    try:
        response = self._process_ai_message(body)
        if response:
            self.with_user(self.env.ref('base.user_admin')).message_post(
                body=response,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )
    except Exception as e:
        _logger.error(f"Error IA: {e}", exc_info=True)

    return message
    
def _process_ai_message(self, user_message):
    api_key = self.env['ir.config_parameter'].sudo().get_param('modulo.ai_api_key')

    if not api_key:
        return "⚠️ No se ha configurado la API Key."

    # Configurar Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    # PROMPT ESTRICTO
    prompt = f"""
Eres un agente IA para Odoo.

Responde SOLO en JSON válido.
No escribas texto fuera del JSON.

Acciones disponibles:
- get_stock (requiere product_name)
- none

Ejemplo:
{{
  "action": "get_stock",
  "product_name": "Laptop"
}}

Pregunta del usuario:
{user_message}
"""

        # Generar respuesta
    response = model.generate_content(prompt)
        
        # Si la IA necesita buscar stock, ejecutar la función
    if 'stock' in user_message.lower() or 'inventario' in user_message.lower() or 'producto' in user_message.lower():
            # Extraer nombre del producto del mensaje
            stock_info = self._get_odoo_stock(user_message)
            return f"{response.text}\n\n📦 **Información de Inventario:**\n{stock_info}"
        
    return response.text
    
def _get_odoo_stock(self, product_name):
    products = self.env['product.product'].sudo().search([
        ('name', 'ilike', product_name)
    ], limit=5)

    if not products:
        return f"❌ No encontré productos llamados '{product_name}'."

    lines = []
    for p in products:
        lines.append(
            f"📦 **{p.name}**\n"
            f"   Stock: {p.qty_available} uds\n"
            f"   Precio: ${p.list_price:.2f}"
        )

    return "\n\n".join(lines)


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