import streamlit as st
import pandas as pd
import io
from utils.xml_parser import processar_xmls
from utils.processamento import aplicar_filtros

# --- Definindo campos disponíveis e filtros ---
CAMPOS = [
    "Nome do Arquivo", "Chave NFe", "cUF", "cCT", "CFOP", "Natureza da Operação", "nCT", "dhEmi",
    "Emitente", "CNPJ Emitente", "UF Emitente", "Destinatario", "CNPJ Destinatario", "vPrest",
    "vBC", "pICMS", "vICMS", "CST", "Toma", "Município de Início (xMunIni)", "Município de Fim (xMunFim)",
    "UF de Início (UFIni)", "UF de Fim (UFFim)", "UF toma4", "UF Receb_Exped"
]

st.set_page_config("Confronto CTE", layout="centered")
st.title("Processamento de CTEs")

# --- Upload dos arquivos ---
uploaded_files = st.file_uploader(
    "Selecione os arquivos XML para processar", type=["xml"], accept_multiple_files=True
)

# --- Seleção dos campos (checkboxes individuais, sem “selecionar todos”) ---
st.subheader("Campos a importar")
colunas = st.columns(5)
checkbox_states = {}
for idx, campo in enumerate(CAMPOS):
    with colunas[idx % 5]:
        checkbox_states[campo] = st.checkbox(campo, value=True, key=campo)

# --- Filtros ---
st.markdown("### Filtros")
col1, col2 = st.columns(2)
with col1:
    excluir_mg = st.checkbox("Excluir UF 'MG'", key="excluir_mg")
with col2:
    excluir_ufini_fora_mg = st.checkbox("Excluir UFIni fora de 'MG'", key="excluir_ufini")

# --- Checkbox: Exibir debug dos XMLs na tela (apenas para visualizar, relatório sempre gerado) ---
exibir_debug = st.checkbox(
    "Exibir debug dos XMLs na tela (apenas 3 primeiros, campo rolável)", key="exibir_debug"
)
modo_debug = st.checkbox(
    "Gerar relatório detalhado de debug para download (Excel)", key="modo_debug"
)

# --- Reset dos dados salvos, se trocar o upload ---
if uploaded_files is not None and len(uploaded_files) > 0:
    if "arquivos_previos" not in st.session_state or st.session_state["arquivos_previos"] != [f.name for f in uploaded_files]:
        st.session_state["df"] = None
        st.session_state["df_debug"] = None
        st.session_state["arquivos_previos"] = [f.name for f in uploaded_files]

# --- Botão de processamento ---
if st.button("Iniciar Processamento"):
    if not uploaded_files:
        st.warning("Selecione ao menos um arquivo XML.")
    elif not any(checkbox_states.values()):
        st.warning("Selecione ao menos um campo para importar.")
    else:
        total = len(uploaded_files)
        progresso = st.progress(0)
        contador_text = st.empty()

        st.info(f"Processando {total} arquivos...")

        resultados = []
        erros = []
        debug_logs = []
        debug_visual = []  # Para visualização rolável

        for idx, file in enumerate(uploaded_files, 1):
            try:
                if modo_debug or exibir_debug:
                    data, debug_log = processar_xmls(file, campos=checkbox_states, modo_debug=True)
                    # Salva tudo para relatório final
                    debug_logs.append({'arquivo': getattr(file, "name", ""), **{
                        f"{campo}__valor": info.get('valor')
                        for campo, info in debug_log.items()
                    }, **{
                        f"{campo}__ok": info.get('ok')
                        for campo, info in debug_log.items()
                    }, **{
                        f"{campo}__xpath": info.get('xpath')
                        for campo, info in debug_log.items()
                    }})
                    # Só exibe visualmente se marcado e até 3 primeiros
                    if exibir_debug and idx <= 3:
                        debug_visual.append(
                            {
                                "Arquivo": getattr(file, "name", ""),
                                "Campos": debug_log
                            }
                        )
                else:
                    data = processar_xmls(file, campos=checkbox_states)
                resultados.append(data)
            except Exception as e:
                erros.append({"arquivo": getattr(file, "name", "Desconhecido"), "erro": str(e)})

            progresso.progress(idx / total)
            contador_text.write(f"Arquivos: {total} - {total - idx} restantes")

        # Montando DataFrame final
        df = pd.DataFrame(resultados)
        df = aplicar_filtros(df, excluir_mg, excluir_ufini_fora_mg)

        st.session_state["df"] = df  # <--- Salva na sessão!
        # Relatório de debug, se ativado
        if (modo_debug or exibir_debug) and debug_logs:
            st.session_state["df_debug"] = pd.DataFrame(debug_logs)
        else:
            st.session_state["df_debug"] = None

        st.session_state["debug_visual"] = debug_visual if debug_visual else None

        st.success("Processamento concluído!")

# --- Exibe debug visual rolável, se ativado ---
if exibir_debug and st.session_state.get("debug_visual"):
    with st.expander("Visualização do Debug dos 3 primeiros XMLs (campo rolável)", expanded=False):
        st.markdown("Abaixo a extração detalhada de cada campo dos 3 primeiros arquivos enviados:")
        for debug_info in st.session_state["debug_visual"]:
            st.markdown(f"**Arquivo:** {debug_info['Arquivo']}")
            st.json(debug_info["Campos"])

# --- Exibe resultados e botões de download, se houver dados salvos ---
if "df" in st.session_state and st.session_state["df"] is not None:
    st.dataframe(st.session_state["df"], use_container_width=True)

    # Download do Excel via BytesIO
    output = io.BytesIO()
    st.session_state["df"].to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Baixar Excel Processado",
        data=output,
        file_name="CTEs_Importados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Download relatório debug, se houver
if modo_debug and "df_debug" in st.session_state and st.session_state["df_debug"] is not None:
    output_debug = io.BytesIO()
    st.session_state["df_debug"].to_excel(output_debug, index=False, engine='openpyxl')
    output_debug.seek(0)
    st.download_button(
        label="Baixar Debug dos XMLs (Excel)",
        data=output_debug,
        file_name="Debug_CTEs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Exibe erros encontrados (se houver)
if "df" in st.session_state and st.session_state["df"] is not None:
    if "erros" in locals() and erros:
        st.warning("Erros encontrados nos seguintes arquivos:")
        st.dataframe(pd.DataFrame(erros), use_container_width=True)

st.caption(
    "Selecione os campos, os filtros desejados e faça upload dos arquivos XML para processar. "
    "No navegador, os arquivos gerados serão salvos na sua pasta padrão de downloads. "
    "Após baixar, mova para a pasta que desejar no seu computador."
)
