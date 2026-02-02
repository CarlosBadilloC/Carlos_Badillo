from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class AIAgentExtended(models.Model):
    _inherit = 'ai.agent'

    @api.model
    def get_default_agent(self):
        """Obtiene el agente IA por defecto"""
        return self.search([('name', '=', 'AI Asistente Virtual')], limit=1)

    def handle_chat(self, message):
        """
        Maneja mensajes del chat con fallback automático a BD
        si la API de IA falla
        """
        self.ensure_one()
        
        try:
            # Intentar procesar con el agente IA
            response = self._process_with_ai(message)
            return response
            
        except Exception as e:
            # Si falla la API, usar fallback a BD
            _logger.warning(f"API de IA no disponible: {str(e)}. Usando fallback a BD.")
            return self._fallback_to_database(message)

    def _process_with_ai(self, message):
        """Procesa el mensaje usando el agente IA"""
        # Aquí se ejecuta la lógica normal del agente IA
        # Este método debe existir en el módulo 'ai' de Odoo
        return self.process_message(message)

    def _fallback_to_database(self, message):
        """
        Fallback: responde consultas básicas usando directamente la BD
        cuando la API de IA no está disponible
        """
        message_lower = message.lower()
        
        try:
            # Detección de consultas de productos
            if any(word in message_lower for word in ['producto', 'stock', 'precio', 'buscar', 
                                                        'busco', 'necesito', 'quiero', 'pelota', 
                                                        'futbol', 'marca', 'raqueta', 'balon']):
                return self._search_products_fallback(message)
            
            # Detección de consultas de CRM
            elif any(word in message_lower for word in ['lead', 'oportunidad', 'cliente', 
                                                          'contacto', 'pipeline', 'venta']):
                return self._crm_fallback(message)
            
            # Consultas de inventario general
            elif any(word in message_lower for word in ['inventario', 'resumen', 'total', 'estado']):
                return self._inventory_summary_fallback()
            
            else:
                return (
                    '⚠️ En este momento el servicio de IA no está disponible.\n\n'
                    'Sin embargo, puedo ayudarte con:\n'
                    '• 📦 Consultar productos y stock\n'
                    '• 🏷️ Buscar por marca o categoría\n'
                    '• 📊 Resumen de inventario\n'
                    '• 📋 Información sobre leads y oportunidades\n\n'
                    '¿En qué puedo ayudarte?'
                )
                
        except Exception as e:
            _logger.error(f"Error en fallback: {str(e)}")
            return 'Lo siento, no puedo procesar tu consulta en este momento. Por favor, intenta nuevamente.'

    def _search_products_fallback(self, message):
        """Busca productos directamente en la BD (modo fallback)"""
        keywords = self._extract_keywords(message)
        
        if not keywords:
            return 'Por favor, especifica qué producto estás buscando.'
        
        # Usar el modelo de acciones de inventario
        inv_actions = self.env['ai.inventory.actions']
        
        # Intentar búsqueda por palabra clave primero
        response = inv_actions.search_products_by_keyword(keywords, limit=10)
        
        return f"💡 Respondiendo desde la base de datos:\n\n{response}"

    def _crm_fallback(self, message):
        """Consulta información de CRM directamente (modo fallback)"""
        crm_actions = self.env['ai.crm.actions']
        
        # Si pregunta por oportunidades
        if 'oportunidad' in message.lower() or 'pipeline' in message.lower():
            response = crm_actions.list_open_opportunities(limit=5)
        else:
            response = crm_actions.get_pipeline_summary()
        
        return f"💡 Respondiendo desde la base de datos:\n\n{response}"

    def _inventory_summary_fallback(self):
        """Obtiene resumen de inventario directamente (modo fallback)"""
        inv_actions = self.env['ai.inventory.actions']
        response = inv_actions.get_inventory_summary()
        
        return f"💡 Respondiendo desde la base de datos:\n\n{response}"

    def _extract_keywords(self, message):
        """Extrae palabras clave relevantes del mensaje"""
        stop_words = {
            'el', 'la', 'los', 'las', 'de', 'en', 'un', 'una', 'por', 'para', 'con',
            'que', 'busco', 'necesito', 'quiero', 'tengo', 'hay', 'tiene', 'tienes',
            'me', 'tu', 'su', 'al', 'del', 'y', 'o', 'pero', 'si', 'no'
        }
        
        words = message.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return ' '.join(keywords) if keywords else ''