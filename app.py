import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from PIL import Image

from database.connection import get_db, init_db, engine
from controllers.vision_controller import VisionController
from utils.exporter import export_to_csv, export_to_json
from utils.logger import get_logger

logger = get_logger("app_main")

# Configuração da página Streamlit
st.set_page_config(
    page_title="Computer Vision Pro",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar CSS customizado
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar Banco de Dados
@st.cache_resource
def setup_database():
    init_db()

setup_database()

# Inicializador de Controller com Gerenciamento de Sessão DB
db_gen = get_db()
db_session = next(db_gen)
controller = VisionController(db_session)

# Menu Lateral (Sidebar)
st.sidebar.title("📷 Vision Analytics")
st.sidebar.markdown("---")

# Status da Conexão
try:
    with engine.connect() as conn:
        st.sidebar.success("🟢 Banco: Neon.tech Conectado")
except Exception as e:
    st.sidebar.error("🔴 Banco: Desconectado")
    logger.error(f"Status Conexão DB: {str(e)}")

menu_option = st.sidebar.radio(
    "Navegação",
    ["Captura & Análise", "Histórico de Análises", "Dashboard Completo"]
)

st.sidebar.markdown("---")
st.sidebar.info("Framework: Python 3.12+ | Streamlit | OpenCV | PostgreSQL")

# -----------------------------------------------------------------------------
# ABA 1: CAPTURA & ANÁLISE
# -----------------------------------------------------------------------------
if menu_option == "Captura & Análise":
    st.title("🎥 Captura e Análise de Imagem")
    st.caption("Acesse sua webcam, tire uma foto e execute diagnósticos em tempo real.")

    col_cam, col_res = st.columns([1, 1])

    with col_cam:
        st.subheader("Câmera ao Vivo")
        camera_image = st.camera_input("Tirar uma foto")

    with col_res:
        st.subheader("Resultado da Análise")
        if camera_image is not None:
            image_bytes = camera_image.getvalue()
            
            with st.spinner("Processando visão computacional e salvando no Neon.tech..."):
                try:
                    analysis_record = controller.process_and_save(image_bytes)
                    st.success("Análise executada e persistida com sucesso!")

                    # Exibição de Métricas
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Rostos / Pessoas", analysis_record.rostos)
                    m2.metric("Luminosidade", analysis_record.luminosidade.split()[0])
                    m3.metric("Nitidez", analysis_record.nitidez.split()[0])

                    st.markdown("**Descrição Detalhada:**")
                    st.write(analysis_record.descricao)

                    st.markdown("**Objetos / Estruturas Detectadas:**")
                    st.write(", ".join(analysis_record.objetos))

                    st.markdown("**Paleta de Cores Predominantes:**")
                    color_cols = st.columns(len(analysis_record.cores))
                    for idx, hex_code in enumerate(analysis_record.cores):
                        with color_cols[idx]:
                            st.markdown(
                                f"<div style='background-color:{hex_code};height:35px;border-radius:5px;text-align:center;line-height:35px;color:#fff;font-weight:bold;'>{hex_code}</div>",
                                unsafe_allow_html=True
                            )

                    with st.expander("Ver JSON Completo de Saída"):
                        st.json(analysis_record.json_resultado)

                except Exception as e:
                    st.error(f"Falha ao processar imagem: {str(e)}")
        else:
            st.info("Aguardando captura de foto na câmera ao lado...")

# -----------------------------------------------------------------------------
# ABA 2: HISTÓRICO DE ANÁLISES
# -----------------------------------------------------------------------------
elif menu_option == "Histórico de Análises":
    st.title("📜 Histórico de Análises")

    # Filtros de Pesquisa
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Pesquisar por texto na descrição", "")
    with f_col2:
        filter_date = st.date_input("📅 Filtrar por Data", value=None)

    records = controller.fetch_history(
        search_query=search_query if search_query else None,
        filter_date=filter_date
    )

    # Botões de Exportação
    if records:
        e_col1, e_col2, _ = st.columns([1, 1, 2])
        with e_col1:
            csv_data = export_to_csv(records)
            st.download_button(
                "📥 Exportar CSV",
                data=csv_data,
                file_name=f"analises_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with e_col2:
            json_data = export_to_json(records)
            st.download_button(
                "📥 Exportar JSON",
                data=json_data,
                file_name=f"analises_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

    st.markdown("---")

    if not records:
        st.warning("Nenhuma análise encontrada com os filtros aplicados.")
    else:
        for rec in records:
            with st.container():
                c_img, c_info, c_actions = st.columns([1, 2.5, 1])

                with c_img:
                    if os.path.exists(rec.image_path):
                        img = Image.open(rec.image_path)
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("Imagem não encontrada no disco.")

                with c_info:
                    st.markdown(f"**ID:** #{rec.id} | **Data:** {rec.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Descrição:** {rec.descricao}")
                    st.write(f"**Objetos:** {', '.join(rec.objetos)}")
                    st.write(f"**Pessoas:** {rec.quantidade_pessoas} | **Nitidez:** {rec.nitidez}")

                with c_actions:
                    if os.path.exists(rec.image_path):
                        with open(rec.image_path, "rb") as file:
                            st.download_button(
                                "💾 Imagem",
                                data=file,
                                file_name=os.path.basename(rec.image_path),
                                mime="image/jpeg",
                                key=f"dl_{rec.id}"
                            )

                    if st.button("🗑️ Excluir", key=f"del_{rec.id}"):
                        if controller.delete_analysis(rec.id):
                            st.success("Excluído com sucesso!")
                            st.rerun()

                st.divider()

# -----------------------------------------------------------------------------
# ABA 3: DASHBOARD COMPLETO
# -----------------------------------------------------------------------------
elif menu_option == "Dashboard Completo":
    st.title("📊 Dashboard e Métricas de Capturas")

    records = controller.fetch_history()

    if not records:
        st.info("Nenhum dado disponível no momento para gerar o Dashboard.")
    else:
        data = [r.to_dict() for r in records]
        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])

        # Métricas Globais
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Análises", len(df))
        m2.metric("Total de Pessoas/Rostos", int(df["rostos"].sum()))
        m3.metric("Média Rostos/Foto", f"{df['rostos'].mean():.1f}")
        m4.metric("Última Captura", df["created_at"].max().strftime("%d/%m %H:%M"))

        st.markdown("---")

        # Gráficos Plotly
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Capturas ao Longo do Tempo")
            df_time = df.set_index("created_at").resample("D").size().reset_index(name="quantidade")
            fig_line = px.line(df_time, x="created_at", y="quantidade", markers=True, title="Frequência Diária")
            st.plotly_chart(fig_line, use_container_width=True)

        with g2:
            st.subheader("Distribuição de Rostos Identificados")
            fig_pie = px.pie(df, names="rostos", title="Contagem de Rostos por Foto")
            st.plotly_chart(fig_pie, use_container_width=True)