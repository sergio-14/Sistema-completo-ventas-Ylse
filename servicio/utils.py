import io
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    # Convierte el HTML en PDF usando pisaDocument
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None
