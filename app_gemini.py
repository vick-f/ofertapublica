import streamlit as st
import pdfplumber  
import google.generativeai as genai

st.set_page_config(page_title="Analisador de Ofertas - Gemini", layout="wide")
st.title("📄 Analisador de Ofertas Públicas")

st.markdown("Faça upload de um PDF e cole sua chave da API Gemini para gerar a ficha da oferta estruturada.")

# Entrada da chave da API
api_key = st.text_input("🔑 Cole sua Gemini API Key (começa com AIza...)", type="password")

# Upload do PDF
uploaded_file = st.file_uploader("📎 Upload do PDF da oferta", type=["pdf"])

# Prompt base de análise
prompt_base = """
Você é um analista financeiro. Receberá a íntegra do texto de uma oferta pública de CRI, CRA ou Debênture, incluindo cronogramas e anexos.

Seu papel é **extrair e organizar as informações específicas de cada série da oferta**. Preste atenção especial aos cronogramas (como o Anexo I), pois eles contêm **datas exatas de juros, amortização e vencimento** que devem ser copiadas exatamente.

⚠️ **Não escreva "ver anexo", nem resumos. Extraia e escreva as datas completas no formato DD/MM/AAAA, exatamente como aparecem no texto.**

Se algum campo não estiver no texto, escreva "não consta". Mas se a informação estiver, mesmo em anexo, você deve incluí-la.

---

🏷️ Identificação da Aplicação
- Título
- Classe (CRI, CRA, Debênture)

💰 Características por Série (para cada uma):
- Taxa de remuneração
- Juros: periodicidade e todas as datas
- Amortização: forma e todas as datas
- Vencimento final (data exata)
- Risco ou rating

🗓️ Cronograma da Oferta
- Início e fim da reserva
- Bookbuilding
- Divulgação do resultado
- Liquidação financeira

⚠️ Destaques relevantes
- Qualquer observação fora do padrão da estrutura
"""


# Função para extrair texto do PDF
from io import BytesIO
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image

def extract_text_from_pdf(file):
    text = ""

    # Primeiro, tentar extrair texto com pdfplumber
    with pdfplumber.open(BytesIO(file.read())) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

    # Reiniciar ponteiro do arquivo
    file.seek(0)

    # Agora OCR (caso algo tenha sido imagem)
    try:
        images = convert_from_bytes(file.read(), dpi=300)
        for i, img in enumerate(images[-3:]):  # Limita ao final (Anexo I geralmente está lá)
            ocr_text = pytesseract.image_to_string(img, lang="por")
            text += f"\n\n[OCR - Página {len(images)-2+i}]\n{ocr_text}"
    except Exception as e:
        text += f"\n\n[Erro no OCR: {e}]"

    return text



# Botão de análise
if st.button("🚀 Analisar Oferta"):
    if not api_key:
        st.error("Por favor, cole sua chave da API da Gemini.")
    elif not uploaded_file:
        st.error("Por favor, faça upload de um arquivo PDF.")
    else:
        try:
            with st.spinner("Lendo PDF e consultando Gemini..."):

                pdf_text = extract_text_from_pdf(uploaded_file)
               # Mostrar o texto extraído na tela para conferência
                st.markdown("### 📝 Texto extraído do PDF (pré-análise)")
                st.code(pdf_text[:4000])  # Mostra os primeiros 4000 caracteres

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt_base + "\n\n" + pdf_text)

                st.success("Análise concluída!")
                st.markdown("### 📋 Ficha da Oferta")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Erro ao processar: {str(e)}")
