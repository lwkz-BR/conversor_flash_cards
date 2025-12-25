import streamlit as st
import pandas as pd
import json
import io
import re

# Configuração da página e estilo
st.set_page_config(page_title="Conversor JSON para Anki Pro", page_icon="🎓", layout="wide")

def extract_json_from_text(text):
    """
    Localiza o primeiro '[' e o último ']' no texto para isolar o array JSON.
    Isso permite copiar a resposta completa do NotebookLM sem erros.
    """
    if not text:
        return ""
    
    start_index = text.find('[')
    end_index = text.rfind(']')
    
    if start_index != -1 and end_index != -1 and end_index > start_index:
        return text[start_index : end_index + 1]
    
    return text

def markdown_to_html(text):
    """
    Converte sintaxe Markdown para tags HTML compatíveis com o Anki.
    Trata negritos, itálicos e quebras de linha.
    """
    if not isinstance(text, str):
        return text
    
    # 1. Negrito: **texto** ou __texto__ -> <b>texto</b>
    text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', text)
    
    # 2. Itálico: *texto* ou _texto_ -> <i>texto</i>
    text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', text)
    
    # 3. Quebras de linha: \n -> <br>
    text = text.replace('\n', '<br>')
    
    return text

# Interface do Utilizador
st.title("⚖️ Conversor de Flashcards: JSON ➔ HTML Anki")
st.markdown("""
Esta ferramenta processa a saída do **NotebookLM**, limpa o texto desnecessário e converte a formatação 
para que o **Anki** exiba negritos e itálicos corretamente.
""")

# Formulário para entrada de dados
with st.form("conversor_form"):
    st.subheader("Entrada de Dados")
    raw_input = st.text_area(
        "Cole aqui a resposta completa (incluindo textos e blocos de código):", 
        height=400, 
        placeholder='Cole aqui a saída do NotebookLM que contém o [ { ... } ]'
    )
    
    submitted = st.form_submit_button("🚀 Processar e Gerar Flashcards")

# Processamento após clique no botão
if submitted:
    if raw_input:
        try:
            # 1. Extração do conteúdo JSON
            json_content = extract_json_from_text(raw_input)
            
            # 2. Parsing para lista de dicionários
            data = json.loads(json_content)
            
            # 3. Criação do DataFrame e validação
            df = pd.DataFrame(data)
            
            if 'frente' in df.columns and 'verso' in df.columns:
                # 4. Limpeza e conversão para HTML
                df['frente'] = df['frente'].apply(markdown_to_html)
                df['verso'] = df['verso'].apply(markdown_to_html)
                
                st.success(f"✅ Sucesso! {len(df)} flashcards identificados e convertidos.")
                
                # 5. Pré-visualização dos cards
                with st.expander("🔍 Ver Pré-visualização (Como aparecerá no Anki)"):
                    for i, row in df.head(10).iterrows():
                        c1, c2 = st.columns(2)
                        with c1:
                            st.info(f"**Frente {i+1}**")
                            st.markdown(row['frente'], unsafe_allow_html=True)
                        with c2:
                            st.success(f"**Verso {i+1}**")
                            st.markdown(row['verso'], unsafe_allow_html=True)
                        st.divider()
                
                # 6. Preparação do ficheiro CSV para download
                # Nota: Usamos ';' como separador para evitar conflitos com vírgulas no texto
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, header=False, sep=';', encoding='utf-8-sig')
                csv_output = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Descarregar Ficheiro para Importar no Anki",
                    data=csv_output,
                    file_name="flashcards_concurso.csv",
                    mime="text/csv",
                )
                
                st.warning("""
                **Instruções para o Anki:**
                1. No Anki, vá a 'Importar Ficheiro'.
                2. Selecione o ficheiro descarregado.
                3. Configure o separador para **Ponto e Vírgula ( ; )**.
                4. Ative a opção **'Permitir HTML nos campos'** (Allow HTML in fields).
                """)
                
            else:
                st.error("Erro: O JSON encontrado não contém as colunas obrigatórias 'frente' e 'verso'.")
                
        except json.JSONDecodeError as e:
            st.error("Não foi possível validar o JSON. Certifique-se de que a lista de cards está completa.")
            st.code(str(e))
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
    else:
        st.warning("Por favor, cole o conteúdo antes de submeter.")

st.divider()
st.caption("Desenvolvido por Lucas Bem para otimizar o estudo com Inteligência Artificial.")