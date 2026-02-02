from odoo import http
from odoo.http import request
import json

class ChatController(http.Controller):
    
    @http.route('/web/chat/send_message', type='json', auth='public', methods=['POST'], csrf=False)
    def send_message(self, message, **kwargs):
        """Procesa mensajes del chat y usa el agente IA"""
        try:
            # Obtener el agente IA
            agent = request.env['ai.agent'].sudo().search([
                ('name', '=', 'AI Asistente Virtual')
            ], limit=1)
            
            if not agent:
                return {
                    'success': False,
                    'response': 'El agente IA no está configurado correctamente.'
                }
            
            # Procesar el mensaje con el agente
            response = agent.with_context(user_input=message).process_message(message)
            
            # Lógica para manejar la consulta de productos
            if "pregunta por un producto" in message.lower():
                product_name = self.extract_product_name(message)  # Implementa esta función para extraer el nombre del producto
                product_info = request.env['product.product'].sudo().search([('name', 'ilike', product_name)], limit=1)
                
                if product_info:
                    product_price = product_info.list_price
                    follow_up_question = f"El precio de {product_info.name} es ${product_price}. ¿Desea comprar este producto u otros?"
                    return {
                        'success': True,
                        'response': follow_up_question
                    }
                else:
                    return {
                        'success': False,
                        'response': 'No se encontró el producto solicitado.'
                    }

            # Manejar la respuesta del cliente sobre la compra
            if "sí" in message.lower():
                customer_data = self.collect_customer_data(message)  # Implementa esta función para recopilar datos del cliente
                self.create_opportunity(customer_data)  # Implementa esta función para crear una oportunidad en CRM
                return {
                    'success': True,
                    'response': 'Sus datos han sido guardados y será contactado por un humano.'
                }

            return {
                'success': True,
                'response': response
            }
        except Exception as e:
            return {
                'success': False,
                'response': f'Error procesando mensaje: {str(e)}'
            }

    def extract_product_name(self, message):
        # Implementa la lógica para extraer el nombre del producto de la consulta del cliente
        return "nombre_del_producto"

    def collect_customer_data(self, message):
        # Implementa la lógica para recopilar los datos del cliente
        return {
            'name': 'Nombre del Cliente',
            'email': 'email@ejemplo.com',
            'phone': '123456789'
        }

    def create_opportunity(self, customer_data):
        # Implementa la lógica para crear una oportunidad en CRM
        opportunity_vals = {
            'name': f"Oportunidad de {customer_data['name']}",
            'partner_id': self.get_or_create_partner(customer_data),
            'email_from': customer_data['email'],
            'phone': customer_data['phone'],
            'type': 'opportunity',
        }
        request.env['crm.lead'].sudo().create(opportunity_vals)

    def get_or_create_partner(self, customer_data):
        # Implementa la lógica para obtener o crear un socio (partner) en Odoo
        partner = request.env['res.partner'].sudo().search([('email', '=', customer_data['email'])], limit=1)
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': customer_data['name'],
                'email': customer_data['email'],
                'phone': customer_data['phone'],
            })
        return partner.id