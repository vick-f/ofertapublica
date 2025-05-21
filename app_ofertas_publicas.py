import streamlit as st
import fitz  # PyMuPDF
import openai

st.set_page_config(page_title="Analisador de Ofertas Públicas", layout="wide")
st.title("📄 Analisador de Ofertas Públicas (CRI, CRA, Debêntures)")

# Instrução para o usuário
st.markdown("Faça o upload de um PDF da oferta pública e cole sua chave da OpenAI para gerar a ficha completa da aplicação.")

# Input da chave da API
api_key = st.text_input("🔑 Cole sua OpenAI API Key (começa com sk-...)", type="password")

# Upload do PDF
uploaded_file = st.file_uploader("📎 Upload do PDF da oferta", type=["pdf"])

# Prompt base para análise
prompt_base = """
Quero que você atue como um especialista em finanças e analise uma nova oferta pública (CRI, CRA ou Debênture).

Para o conteúdo abaixo, organize as informações de forma clara, separando por série sempre que houver mais de uma:

🏷️ Identificação da Aplicação
- Título da aplicação
- Classe (CRI, CRA, Debênture)

💰 Características por Série
- Taxa de remuneração (prefixada, IPCA+, CDI+, etc.)
- Juros: periodicidade e datas exatas de pagamento
- Amortização: forma (bullet, parcelas) e datas exatas
- Vencimento final (data exata)
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
        st.error("Por favor, cole sua chave da API da OpenAI.")
    elif not uploaded_file:
        st.error("Por favor, faça upload de um arquivo PDF.")
    else:
        try:
            with st.spinner("Extraindo texto e consultando GPT-4..."):
                pdf_text = extract_text_from_pdf(uploaded_file)

                # Enviar para OpenAI
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é um analista de investimentos especializado em ofertas públicas."},
                        {"role": "user", "content": prompt_base + "\n\n" + pdf_text}
                    ],
                    temperature=0.3,
                    max_tokens=3500
                )

                output = response["choices"][0]["message"]["content"]
                st.success("Análise concluída!")
                st.markdown("### 📋 Ficha da Oferta")
                st.markdown(output)

        except Exception as e:
            st.error(f"Erro ao processar: {str(e)}")
