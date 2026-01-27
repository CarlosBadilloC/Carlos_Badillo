from odoo import models, fields, api # type: ignore
import base64
import PyPDF2
from io import BytesIO
from openai import OpenAI, APIError

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

    x_openai_config_id = fields.Many2one(
        'openai.config',
        string="Configuración OpenAI"
    )

    x_agent_response = fields.Text(
        string="Respuesta de IA",
        readonly=True
    )

    x_agent_prompt = fields.Text(
        string="Prompt Personalizado",
        help="Instrucciones adicionales para OpenAI"
    )

    @api.model
    def action_run_custom_logic(self):
        """Ejecuta lógica personalizada del agente"""
        for agent in self:
            if agent.x_can_read_documents:
                agent._read_documents()

    def _read_documents(self):
        """Lee y extrae contenido de documentos"""
        self.ensure_one()
        
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
        """Procesa documentos con OpenAI"""
        self.ensure_one()
        
        if not self.x_document_content:
            self._read_documents()
        
        if not self.x_openai_config_id:
            raise ValueError("Debe configurar una API Key de OpenAI primero")
        
        response = self._call_openai_api(self.x_document_content)
        self.x_agent_response = response

    def _call_openai_api(self, document_content):
        """Integración con OpenAI API"""
        self.ensure_one()
        
        if not self.x_openai_config_id:
            return "Error: No hay configuración de OpenAI"
        
        try:
            config = self.x_openai_config_id
            client = OpenAI(api_key=config.api_key)
            
            # Construir el prompt
            system_prompt = "Eres un asistente inteligente especializado en análisis de documentos."
            
            user_prompt = f"""Analiza el siguiente contenido de documento y proporciona un resumen detallado:

{document_content}

{self.x_agent_prompt if self.x_agent_prompt else ''}
"""
            
            # Llamar a OpenAI
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            return response.choices[0].message.content
            
        except APIError as e:
            return f"Error de OpenAI: {str(e)}"
        except Exception as e:
            return f"Error al procesar: {str(e)}"

    def action_ask_openai(self, question):
        """Realiza una pregunta a OpenAI sobre los documentos"""
        self.ensure_one()
        
        if not self.x_document_content:
            self._read_documents()
        
        if not self.x_openai_config_id:
            return "Error: No hay configuración de OpenAI"
        
        try:
            config = self.x_openai_config_id
            client = OpenAI(api_key=config.api_key)
            
            prompt = f"""Basándote en el siguiente contenido de documentos, responde la pregunta:

DOCUMENTOS:
{self.x_document_content}

PREGUNTA: {question}

Proporciona una respuesta clara y detallada basada únicamente en la información de los documentos."""
            
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"