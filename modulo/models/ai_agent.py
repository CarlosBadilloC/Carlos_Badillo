from odoo import models, fields, api # type: ignore
import base64
from io import BytesIO

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class AIAgent(models.Model):
    _inherit = 'ai.agent'

    x_custom_capability = fields.Char(
        string="Custom Capability"
    )

    x_can_read_documents = fields.Boolean(
        string="Can Read Documents",
        default=False
    )

    x_document_ids = fields.One2many(
        'agent.document',
        'agent_id',
        string="Documentos Adjuntos"
    )

    x_document_content = fields.Text(
        string="Contenido Extraído",
        readonly=True
    )

    x_gemini_config_id = fields.Many2one(
        'gemini.config',
        string="Configuración Gemini"
    )

    x_agent_response = fields.Text(
        string="Respuesta de IA",
        readonly=True
    )

    x_agent_prompt = fields.Text(
        string="Prompt Personalizado",
        help="Instrucciones adicionales para Gemini"
    )

    @api.onchange('x_can_read_documents')
    def _onchange_can_read_documents(self):
        """Se ejecuta cuando cambia el checkbox"""
        if self.x_can_read_documents and not self.x_document_content:
            self._read_documents()

    def action_run_custom_logic(self):
        """Ejecuta lógica personalizada del agente"""
        for agent in self:
            if agent.x_can_read_documents:
                agent._read_documents()

    def _read_documents(self):
        """Lee y extrae contenido de documentos"""
        self.ensure_one()
        
        if not HAS_PYPDF2:
            self.x_document_content = "Error: PyPDF2 no está instalado. Instala con: pip install PyPDF2"
            return
        
        extracted_content = []
        
        for doc in self.x_document_ids:
            content = self._extract_document_content(doc)
            if content:
                extracted_content.append(f"--- {doc.name} ---\n{content}\n")

        self.x_document_content = "\n".join(extracted_content)

    def _extract_document_content(self, document):
        """Extrae contenido según el tipo de archivo"""
        try:
            file_type = document.file_type or ''
            
            if 'pdf' in file_type.lower():
                return self._extract_pdf_content(document.document_file)
            elif 'text' in file_type.lower() or 'csv' in file_type.lower():
                return base64.b64decode(document.document_file).decode('utf-8')
            else:
                return f"[Tipo de archivo no soportado: {file_type}]"
        except Exception as e:
            return f"[Error al leer archivo: {str(e)}]"

    def _extract_pdf_content(self, file_data):
        """Extrae texto de un PDF"""
        try:
            pdf_data = base64.b64decode(file_data)
            pdf_file = BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            return "\n".join(text_content)
        except Exception as e:
            return f"Error extrayendo PDF: {str(e)}"
    def _get_inventory_summary(self):
        """Resumen de stock de productos"""
        products = self.env['product.product'].search([])
        summary = []
        for product in products:
            qty = sum(product.stock_quant_ids.mapped('quantity'))
            summary.append(f"{product.display_name}: {qty}")
        return "\n".join(summary) if summary else "No hay productos en inventario."

    def _get_crm_today(self):
        """Resumen de actividades CRM para hoy"""
        today = fields.Date.today()
        leads = self.env['crm.lead'].search([('date_deadline', '=', today)])
        events = self.env['calendar.event'].search([
            ('start', '>=', fields.Datetime.now()),
            ('stop', '<=', fields.Datetime.now().replace(hour=23, minute=59, second=59))
        ])
        res = []
        if leads:
            res.append("Oportunidades para hoy:")
            for lead in leads:
                res.append(f"- {lead.name} ({lead.stage_id.name})")
        if events:
            res.append("Reuniones para hoy:")
            for event in events:
                res.append(f"- {event.name} ({event.start} - {event.stop})")
        return "\n".join(res) if res else "No hay actividades CRM para hoy."

    def action_process_documents_with_llm(self):
        """Procesa documentos con Google Gemini"""
        self.ensure_one()
        
        if not self.x_document_content:
            self._read_documents()
        
        if not self.x_gemini_config_id:
            raise ValueError("Debe configurar una API Key de Gemini primero")
        
        response = self._call_gemini_api(self.x_document_content)
        self.x_agent_response = response

    def _call_gemini_api(self, document_content):
        """Integración con Google Gemini API"""
        self.ensure_one()
        
        if not HAS_GEMINI:
            return "Error: google-generativeai no está instalado. Instala con: pip install google-generativeai"
        
        if not self.x_gemini_config_id:
            return "Error: No hay configuración de Gemini"
        
        try:
            config = self.x_gemini_config_id
            genai.configure(api_key=config.api_key)
            
            model = genai.GenerativeModel(config.model)
            
            system_prompt = "Eres un asistente inteligente especializado en análisis de documentos."
            
            user_prompt = f"""{system_prompt}

Analiza el siguiente contenido de documento y proporciona un resumen detallado:

{document_content}

{self.x_agent_prompt if self.x_agent_prompt else ''}
"""
            
            response = model.generate_content(
                user_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                ),
                stream=False
            )
            
            return response.text if response.text else "Sin respuesta de Gemini"
            
        except Exception as e:
            return f"Error al procesar: {str(e)}"

    def action_ask_gemini(self, question):
        """Realiza una pregunta a Gemini sobre los documentos"""
        self.ensure_one()
        # Respuestas directas para inventario y CRM
        q_lower = question.lower()
        if "stock" in q_lower or "inventario" in q_lower:
            return self._get_inventory_summary()
        if "crm" in q_lower or "oportunidad" in q_lower or "hoy" in q_lower:
            return self._get_crm_today()
        
        if not HAS_GEMINI:
            return "Error: google-generativeai no está instalado"
        
        if not self.x_document_content:
            self._read_documents()
        
        if not self.x_gemini_config_id:
            return "Error: No hay configuración de Gemini"
        
        try:
            config = self.x_gemini_config_id
            genai.configure(api_key=config.api_key)
            
            model = genai.GenerativeModel(config.model)
            
            prompt = f"""Basándote en el siguiente contenido de documentos, responde la pregunta:

DOCUMENTOS:
{self.x_document_content}

PREGUNTA: {question}

Proporciona una respuesta clara y detallada basada únicamente en la información de los documentos."""
            
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                ),
                stream=False
            )
            
            return response.text if response.text else "Sin respuesta de Gemini"
            
        except Exception as e:
            return f"Error: {str(e)}"