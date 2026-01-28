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
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'ai.agent')],
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
        
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'ai.agent'),
            ('res_id', '=', self.id)
        ])

        extracted_content = []
        
        for attachment in attachments:
            content = self._extract_document_content(attachment)
            if content:
                extracted_content.append(f"--- {attachment.name} ---\n{content}\n")

        self.x_document_content = "\n".join(extracted_content)

    def _extract_document_content(self, attachment):
        """Extrae contenido según el tipo de archivo"""
        try:
            if attachment.mimetype == 'application/pdf':
                return self._extract_pdf_content(attachment)
            elif attachment.mimetype in ['text/plain', 'text/csv']:
                return base64.b64decode(attachment.datas).decode('utf-8')
            elif 'text' in attachment.mimetype:
                return base64.b64decode(attachment.datas).decode('utf-8')
            else:
                return f"[Tipo de archivo no soportado: {attachment.mimetype}]"
        except Exception as e:
            return f"[Error al leer archivo: {str(e)}]"

    def _extract_pdf_content(self, attachment):
        """Extrae texto de un PDF"""
        try:
            pdf_data = base64.b64decode(attachment.datas)
            pdf_file = BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
            
            return "\n".join(text_content)
        except Exception as e:
            return f"Error extrayendo PDF: {str(e)}"

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
            
            # Crear modelo
            model = genai.GenerativeModel(config.model)
            
            # Construir el prompt
            system_prompt = "Eres un asistente inteligente especializado en análisis de documentos."
            
            user_prompt = f"""{system_prompt}

Analiza el siguiente contenido de documento y proporciona un resumen detallado:

{document_content}

{self.x_agent_prompt if self.x_agent_prompt else ''}
"""
            
            # Llamar a Gemini con configuración actualizada
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