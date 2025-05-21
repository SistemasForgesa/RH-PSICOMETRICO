from bs4 import BeautifulSoup
import mammoth

async def convert_docx_to_html(file):
    docx_bytes = await file.read()
    result = mammoth.convert_to_html(docx_bytes)
    raw_html = result.value

    # Mejorar formato básico (puedes personalizar más aquí)
    soup = BeautifulSoup(raw_html, 'html.parser')
    for p in soup.find_all('p'):
        p['class'] = 'mb-2 text-gray-700'

    return str(soup)