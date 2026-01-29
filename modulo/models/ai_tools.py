from odoo import models, api
import json

class AIToolsRegistry(models.AbstractModel):
    """
    Registro de herramientas (tools) para AI Agents.
    Define qué métodos pueden ser ejecutados por el agente de IA.
    Escalable: fácil agregar más tools en el futuro.
    """
    _name = 'ai.tools.registry'
    _description = 'AI Tools Registry - Herramientas para Agentes IA'

    @api.model
    def get_available_tools(self):
        """
        Retorna la lista de tools disponibles para el AI Agent.
        Cada tool describe qué hace, parámetros, y cómo llamarlo.
        
        Returns:
            list: Lista de herramientas disponibles con sus esquemas
        """
        tools = [
            {
                'id': 'get_product_count',
                'name': 'Contar Productos',
                'category': 'inventory',
                'description': 'Retorna el total de productos almacenables en el sistema.',
                'method': 'ai.query.handler.get_product_count',
                'parameters': {},
                'return_type': 'dict',
                'example_response': {
                    'total_products': 150,
                    'status': 'success'
                }
            },
            {
                'id': 'get_inventory_summary',
                'name': 'Resumen de Inventario',
                'category': 'inventory',
                'description': 'Retorna resumen completo del inventario: total de productos, stock disponible y productos con bajo stock.',
                'method': 'ai.query.handler.get_inventory_summary',
                'parameters': {},
                'return_type': 'dict',
                'example_response': {
                    'total_products': 150,
                    'total_stock_quantity': 5000.0,
                    'low_stock_products': [
                        {
                            'id': 1,
                            'name': 'Producto X',
                            'qty_available': 3,
                            'uom': 'Units'
                        }
                    ],
                    'status': 'success'
                }
            },
            {
                'id': 'get_open_opportunities_count',
                'name': 'Contar Oportunidades Abiertas',
                'category': 'crm',
                'description': 'Retorna el total de oportunidades activas (no ganadas ni perdidas).',
                'method': 'ai.query.handler.get_open_opportunities_count',
                'parameters': {},
                'return_type': 'dict',
                'example_response': {
                    'open_opportunities': 25,
                    'status': 'success'
                }
            },
            {
                'id': 'get_crm_summary',
                'name': 'Resumen de CRM',
                'category': 'crm',
                'description': 'Retorna resumen completo de CRM: total de oportunidades, abiertas, ganadas, perdidas, e ingresos esperados.',
                'method': 'ai.query.handler.get_crm_summary',
                'parameters': {},
                'return_type': 'dict',
                'example_response': {
                    'total_opportunities': 100,
                    'open_opportunities': 25,
                    'won_opportunities': 50,
                    'lost_opportunities': 25,
                    'total_expected_revenue': 150000.0,
                    'currency': 'USD',
                    'status': 'success'
                }
            },
            {
                'id': 'get_opportunities_by_stage',
                'name': 'Oportunidades por Etapa',
                'category': 'crm',
                'description': 'Retorna el conteo de oportunidades agrupadas por etapa del pipeline (Prospecting, Negotiation, Win, etc.).',
                'method': 'ai.query.handler.get_opportunities_by_stage',
                'parameters': {},
                'return_type': 'dict',
                'example_response': {
                    'stages': [
                        {
                            'stage_id': 1,
                            'stage_name': 'Prospecting',
                            'count': 10,
                            'expected_revenue': 50000.0,
                            'sequence': 1
                        }
                    ],
                    'total_stages': 5,
                    'currency': 'USD',
                    'status': 'success'
                }
            }
        ]
        
        return {
            'tools': tools,
            'total_tools': len(tools),
            'status': 'success'
        }

    @api.model
    def get_tools_by_category(self, category):
        """
        Retorna tools filtradas por categoría.
        Útil para el agente si necesita solo tools de inventario o CRM.
        
        Args:
            category (str): 'inventory' o 'crm'
        
        Returns:
            dict: Tools de la categoría especificada
        """
        all_tools = self.get_available_tools()['tools']
        filtered = [t for t in all_tools if t['category'] == category]
        
        return {
            'category': category,
            'tools': filtered,
            'count': len(filtered),
            'status': 'success'
        }

    @api.model
    def call_tool(self, tool_id, parameters=None):
        """
        Ejecuta una herramienta (tool) por su ID.
        Método genérico que permite al AI Agent ejecutar cualquier tool.
        Patrón: reutilizable para agregar más tools en el futuro.
        
        Args:
            tool_id (str): ID de la herramienta (ej: 'get_product_count')
            parameters (dict): Parámetros para el método (opcional)
        
        Returns:
            dict: Resultado de la ejecución de la tool
        """
        if parameters is None:
            parameters = {}
        
        # Mapeo: tool_id → (modelo, método)
        tool_mapping = {
            'get_product_count': ('ai.query.handler', 'get_product_count'),
            'get_inventory_summary': ('ai.query.handler', 'get_inventory_summary_answer'),
            'get_open_opportunities_count': ('ai.query.handler', 'get_open_opportunities_count'),
            'get_crm_summary': ('ai.query.handler', 'get_crm_summary'),
            'get_opportunities_by_stage': ('ai.query.handler', 'get_opportunities_by_stage'),
        }
        
        if tool_id not in tool_mapping:
            return {
                'status': 'error',
                'message': f'Tool "{tool_id}" not found. Available tools: {", ".join(tool_mapping.keys())}'
            }
        
        model_name, method_name = tool_mapping[tool_id]
        
        try:
            model = self.env[model_name]
            method = getattr(model, method_name)
            result = method()
            return result
        except AttributeError as e:
            return {
                'status': 'error',
                'message': f'Method "{method_name}" not found in model "{model_name}": {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error executing tool "{tool_id}": {str(e)}'
            }