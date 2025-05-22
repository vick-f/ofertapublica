import streamlit as st
import fitz  # PyMuPDF
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
Quero que você atue como um especialista em finanças e analise uma nova oferta pública (CRI, CRA ou Debênture).

Para o conteúdo abaixo, organize as informações de forma clara, separando por série sempre que houver mais de uma:

🏷️ Identificação da Aplicação
- Título da aplicação
- Classe (CRI, CRA, Debênture)

💰 Características por Série
- Taxa de remuneração (prefixada, IPCA+, CDI+, etc.)
- Juros: periodicidade e liste todas as datas em formato dia/mês/ano exatamente como aparecem no PDF, sem usar frases como 'ver anexo' de pagamento, se a informação não estiver clara, diga explicitamente: 'não consta'
- Amortização: forma (bullet, parcelas) e liste todas as datas em formato dia/mês/ano exatamente como aparecem no PDF, sem usar frases como 'ver anexo', se a informação não estiver clara, diga explicitamente: 'não consta'
- Vencimento final (liste todas as datas em formato dia/mês/ano exatamente como aparecem no PDF, sem usar frases como 'ver anexo',se a informação não estiver clara, diga explicitamente: 'não consta')
- Risco: rating ou análise qualitativa se não houver nota

🗓️ Cronograma da Oferta
- Início e fim do período de reserva (datas exatas)
- Data do bookbuilding
- Resultado da alocação
- Data da liquidação (dinheiro sai da conta)

⚠️ Destaques
- Apontar qualquer detalhe fora do padrão, como carência longa, ausência de rating, série subordinada, etc.
"""

# Função para extrair texto do PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
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

                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt_base + "\n\n" + pdf_text)

                st.success("Análise concluída!")
                st.markdown("### 📋 Ficha da Oferta")
                st.markdown(response.text)

        except Exception as e:
            st.error(f"Erro ao processar: {str(e)}")
