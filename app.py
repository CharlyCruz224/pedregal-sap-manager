import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS
# ==========================================
st.set_page_config(page_title="SAP Manager - El Pedregal", page_icon="🍇", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    .stApp {
        background-color: #F8FAFC;
        font-family: 'Poppins', sans-serif;
        color: #1E293B;
    }
    
    h1 {
        color: #0F172A;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0px;
    }
    
    h2, h3 {
        color: #1E3A8A;
        font-weight: 600;
    }

    /* Botones principales corporativos */
    .stButton>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
        transition: all 0.3s ease;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(16, 185, 129, 0.3);
        color: #ffffff;
    }

    /* Cajas de texto y selectores limpios */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-family: 'Poppins', sans-serif !important;
        color: #0f172a !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
    }

    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #10B981;
        border-top: 1px solid #F1F5F9;
        border-right: 1px solid #F1F5F9;
        border-bottom: 1px solid #F1F5F9;
    }

    /* Pestañas (Tabs) modernos */
    div[data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        gap: 6px;
    }
    div[data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTIÓN DE BASES DE DATOS CSV
# ==========================================
USERS_FILE = 'usuarios.csv'
RESERVAS_FILE = 'historial_reservas.csv'

columnas_usuarios = ['usuario', 'password', 'rol']
if not os.path.exists(USERS_FILE):
    pd.DataFrame({'usuario': ['admin'], 'password': ['Pedregal2026'], 'rol': ['Administrador']}).to_csv(USERS_FILE, index=False, sep=';')
else:
    try:
        df_u_check = pd.read_csv(USERS_FILE, sep=None, engine='python', dtype=str)
        if not all(col in df_u_check.columns for col in columnas_usuarios):
            pd.DataFrame({'usuario': ['admin'], 'password': ['Pedregal2026'], 'rol': ['Administrador']}).to_csv(USERS_FILE, index=False, sep=';')
    except:
        pd.DataFrame({'usuario': ['admin'], 'password': ['Pedregal2026'], 'rol': ['Administrador']}).to_csv(USERS_FILE, index=False, sep=';')

columnas_requeridas = ['ID', 'Fecha', 'Hora', 'PEP', 'Area', 'Movimiento', 'Material', 'Cantidad']
if not os.path.exists(RESERVAS_FILE):
    pd.DataFrame(columns=columnas_requeridas).to_csv(RESERVAS_FILE, index=False, sep=';')
else:
    try:
        df_check = pd.read_csv(RESERVAS_FILE, sep=None, engine='python', dtype=str)
        if not all(col in df_check.columns for col in columnas_requeridas):
            pd.DataFrame(columns=columnas_requeridas).to_csv(RESERVAS_FILE, index=False, sep=';')
    except:
        pd.DataFrame(columns=columnas_requeridas).to_csv(RESERVAS_FILE, index=False, sep=';')

def check_login(username, password):
    try:
        df_users = pd.read_csv(USERS_FILE, sep=None, engine='python', dtype=str)
    except:
        df_users = pd.read_csv(USERS_FILE, sep=';', dtype=str)

    df_users.columns = df_users.columns.str.strip()

    if 'usuario' not in df_users.columns or 'password' not in df_users.columns:
        return False

    user_match = df_users[(df_users['usuario'].str.strip() == username.strip()) & (df_users['password'].str.strip() == password.strip())]
    if not user_match.empty:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['rol'] = user_match.iloc[0]['rol']
        return True
    return False

if 'editando_id' not in st.session_state:
    st.session_state['editando_id'] = None

# ==========================================
# PANTALLA DE LOGIN
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("🍇 Portal SAP - El Pedregal")
    st.markdown("<h4 style='text-align: center; color: #64748B;'>Sistema de Gestión de Lotes y Reservas Agrícolas</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        with st.container():
            st.markdown("### 🔐 Iniciar Sesión")
            usuario = st.text_input("👤 Usuario", placeholder="Ej: admin")
            contrasena = st.text_input("🔑 Contraseña", type="password", placeholder="Contraseña")
            
            if st.button("Ingresar al Sistema 🚀", use_container_width=True):
                if check_login(usuario, contrasena):
                    with st.spinner('Validando credenciales...'):
                        time.sleep(0.8)
                    st.toast('¡Bienvenido al sistema!', icon='✅')
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
else:
    # ==========================================
    # BARRA LATERAL (SIDEBAR)
    # ==========================================
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.markdown(f"### Hola, **{st.session_state['username']}** 👋")
        st.caption(f"Rol: {st.session_state['rol']}")
        st.divider()
        st.info("💡 **Consejo:** Utiliza los filtros en tiempo real para ubicar rápidamente lotes o solicitantes.")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.title("🍇 Dashboard de Operaciones SAP - El Pedregal")
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧩 Generador PEP", 
        "🏢 Buscador de Áreas",  
        "📝 Gestión de Reservas", 
        "📊 Métricas e Historial", 
        "⚙️ Ajustes"
    ])

    # ------------------------------------------
    # TAB 1: GENERADOR PEP & MAESTRO DE LOTES
    # ------------------------------------------
    with tab1:
        st.header("Generador Dinámico y Maestro de Lotes")
        
        with st.expander("ℹ️ Estructura del Código PEP", expanded=False):
            st.write("Formato oficial: **[Actividad]/[Campaña].[Fundo].[Lote].[Tipo_Activo].[Labor]**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            actividad = st.selectbox("📌 Actividad", ["PU", "IU"], help="PU: Producción Uva")
            campana = st.text_input("📅 Campaña", value="26")
            fundo = st.text_input("🚜 Fundo", value="T4")
        with col2:
            lote = st.text_input("📍 Lote", value="C04")
            tipo_activo = st.text_input("📦 Tipo Activo", value="111")
            labor = st.text_input("🛠️ Labor", value="041")
        
        with col3:
            st.markdown("### ✨ Código Generado:")
            codigo_pep = f"{actividad}/{campana}.{fundo}.{lote}.{tipo_activo}.{labor}"
            st.code(codigo_pep, language="markdown")
            if st.button("Copiar Código PEP 📋"):
                st.toast("¡Código listo para usar!", icon='📋')
            
        st.divider()
        st.subheader("🔍 Consultar Maestro de Lotes (Filtro en tiempo real)")
        try:
            df_lotes = pd.read_excel('MAESTRO DE LOTES 2026 al 27.04.2026 - copia.xlsm', sheet_name='MAESTRO DE LOTES 2026')
            
            b_variedad = st.text_input("🔍 Escribe variedad, lote o fundo para buscar de inmediato:", placeholder="Ej: Timpson, A01, T4...")
            if b_variedad:
                mask = df_lotes.astype(str).apply(lambda x: x.str.contains(b_variedad, case=False, na=False)).any(axis=1)
                df_lotes_filtrado = df_lotes[mask]
            else:
                df_lotes_filtrado = df_lotes
                
            st.dataframe(df_lotes_filtrado, use_container_width=True, height=320)
            st.caption(f"Mostrando {len(df_lotes_filtrado)} registros encontrados.")
        except Exception as e:
            st.error(f"⚠️ Error al leer 'MAESTRO DE LOTES 2026 al 27.04.2026 - copia.xlsm'. Detalle: {e}")

    # ------------------------------------------
    # TAB 2: BUSCADOR DE ÁREAS Y SOLICITANTES SAP
    # ------------------------------------------
    with tab2:
        st.header("Directorio de Solicitantes y Áreas SAP")
        try:
            df_sap = pd.read_excel('SOLICITANTES SAP - copia.xlsx', sheet_name=0)
            
            b_area = st.text_input("🔍 Digite el sub solicitante o área a buscar:", placeholder="Ej: Riego, Cosecha, G HIDRICA...")
            if b_area:
                mask_sap = df_sap.astype(str).apply(lambda x: x.str.contains(b_area, case=False, na=False)).any(axis=1)
                df_sap_filtrado = df_sap[mask_sap]
            else:
                df_sap_filtrado = df_sap
                
            st.dataframe(df_sap_filtrado, use_container_width=True, height=400)
            st.caption(f"Total de registros listados: {len(df_sap_filtrado)}")
        except Exception as e:
            st.error(f"⚠️ No se pudo cargar 'SOLICITANTES SAP - copia.xlsx'. Detalle: {e}")

    # ------------------------------------------
    # TAB 3: GESTIÓN DE RESERVAS
    # ------------------------------------------
    with tab3:
        st.header("Creación y Gestión de Reservas SAP")
        try:
            df_historial = pd.read_csv(RESERVAS_FILE, sep=None, engine='python', dtype=str)
            if not all(col in df_historial.columns for col in columnas_requeridas):
                df_historial = pd.DataFrame(columns=columnas_requeridas)
        except:
            df_historial = pd.DataFrame(columns=columnas_requeridas)
        
        id_a_editar = st.session_state['editando_id']
        datos_edit = {}
        if id_a_editar is not None and not df_historial.empty:
            match_row = df_historial[df_historial['ID'].astype(str) == str(id_a_editar)]
            if not match_row.empty:
                datos_edit = match_row.iloc[0].to_dict()
                st.info(f"✏️ Estás editando la reserva **#{id_a_editar}**")

        with st.container():
            with st.form("form_reserva", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    r_pep = st.text_input("Código PEP", value=str(datos_edit.get('PEP', 'PU/26.T4.C04.111.041')))
                    r_area = st.text_input("Área / Solicitante", value=str(datos_edit.get('Area', '')), placeholder="Ej: Riego y Nutrición")
                    r_material = st.text_input("Material", value=str(datos_edit.get('Material', '')), placeholder="Ej: Filtro de aceite / Abono")
                with c2:
                    default_mov = str(datos_edit.get('Movimiento', '221'))
                    idx_mov = 0 if '221' in default_mov else (1 if '311' in default_mov else 2)
                    r_movimiento = st.selectbox("Clase de Movimiento", ["221 (Consumo)", "311 (Traslado)", "Otros"], index=idx_mov)
                    
                    try:
                        def_cant = int(datos_edit.get('Cantidad', 1))
                        if pd.isna(def_cant): def_cant = 1
                    except:
                        def_cant = 1
                    
                    r_cantidad = st.number_input("Cantidad", min_value=1, step=1, value=def_cant)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    btn_label = "💾 Actualizar Reserva" if id_a_editar is not None else "💾 Guardar y Registrar"
                    submit_reserva = st.form_submit_button(btn_label, use_container_width=True)
                    
                if submit_reserva:
                    mov_str = str(r_movimiento)
                    mov_code = mov_str[:3] if len(mov_str) >= 3 else mov_str

                    if id_a_editar is not None:
                        mask = df_historial['ID'].astype(str) == str(id_a_editar)
                        if mask.any():
                            df_historial = df_historial.astype(object)
                            df_historial.loc[mask, 'PEP'] = str(r_pep)
                            df_historial.loc[mask, 'Area'] = str(r_area)
                            df_historial.loc[mask, 'Movimiento'] = str(mov_code)
                            df_historial.loc[mask, 'Material'] = str(r_material)
                            df_historial.loc[mask, 'Cantidad'] = str(r_cantidad)
                            
                            df_historial.to_csv(RESERVAS_FILE, index=False, sep=';')
                            st.session_state['editando_id'] = None
                            st.success(f"¡Reserva #{id_a_editar} actualizada con éxito!")
                            time.sleep(0.5)
                            st.rerun()
                    else:
                        # Cálculo seguro del próximo ID evitando errores por valores nulos o vacíos
                        nuevo_id = 1001
                        if not df_historial.empty and 'ID' in df_historial.columns:
                            ids_num = pd.to_numeric(df_historial['ID'], errors='coerce').dropna()
                            if not ids_num.empty:
                                nuevo_id = int(ids_num.max() + 1)
                        
                        nueva_reserva = {
                            'ID': str(nuevo_id),
                            'Fecha': datetime.datetime.now().strftime("%Y-%m-%d"),
                            'Hora': datetime.datetime.now().strftime("%H:%M:%S"),
                            'PEP': str(r_pep),
                            'Area': str(r_area),
                            'Movimiento': str(mov_code),
                            'Material': str(r_material),
                            'Cantidad': str(r_cantidad)
                        }
                        df_historial = pd.concat([df_historial, pd.DataFrame([nueva_reserva])], ignore_index=True)
                        df_historial.to_csv(RESERVAS_FILE, index=False, sep=';')
                        st.balloons()
                        st.toast('¡Reserva registrada con éxito!', icon='🎉')
                        st.rerun()

        st.divider()
        st.subheader("📋 Listado y Gestión de Reservas Actuales")
        st.caption("Desde aquí puedes modificar o eliminar cualquier reserva registrada.")
        
        if not df_historial.empty:
            for index, row in df_historial.iterrows():
                raw_id = row.get('ID', index + 1)
                try:
                    row_id = int(raw_id) if pd.notna(raw_id) else index + 1
                except:
                    row_id = index + 1

                cols = st.columns([1, 2, 2, 2, 1, 1, 1])
                cols[0].write(f"**#{row_id}**")
                cols[1].write(str(row.get('Fecha', 'N/A')))
                cols[2].write(str(row.get('Area', 'N/A')))
                cols[3].write(str(row.get('Material', 'N/A')))
                
                try:
                    cant_val = int(row.get('Cantidad', 1)) if pd.notna(row.get('Cantidad', 1)) else 1
                except:
                    cant_val = 1
                cols[4].write(f"Cant: {cant_val}")
                
                if cols[5].button("✏️ Editar", key=f"edit_res_{row_id}_{index}"):
                    st.session_state['editando_id'] = row_id
                    st.rerun()
                
                if cols[6].button("🗑️ Borrar", key=f"del_res_{row_id}_{index}"):
                    df_historial = df_historial.drop(index)
                    df_historial.to_csv(RESERVAS_FILE, index=False, sep=';')
                    if st.session_state['editando_id'] == row_id:
                        st.session_state['editando_id'] = None
                    st.toast(f"Reserva eliminada.", icon='⚠️')
                    st.rerun()
        else:
            st.info("No hay reservas registradas todavía.")

    # ------------------------------------------
    # TAB 4: MÉTRICAS E HISTORIAL
    # ------------------------------------------
    with tab4:
        st.header("Métricas de Operaciones e Historial")
        try:
            df_dash = pd.read_csv(RESERVAS_FILE, sep=None, engine='python', dtype=str)
            if not all(col in df_dash.columns for col in columnas_requeridas):
                df_dash = pd.DataFrame()
            else:
                df_dash['Cantidad_num'] = pd.to_numeric(df_dash['Cantidad'], errors='coerce').fillna(1)
        except:
            df_dash = pd.DataFrame()
        
        if not df_dash.empty:
            m1, m2, m3 = st.columns(3)
            hoy_str = datetime.datetime.now().strftime("%Y-%m-%d")
            total_hoy = len(df_dash[df_dash['Fecha'] == hoy_str]) if 'Fecha' in df_dash.columns else 0
            m1.metric("Total Reservas Hoy", total_hoy)
            m2.metric("Total Materiales Movidos", int(df_dash['Cantidad_num'].sum()) if 'Cantidad_num' in df_dash.columns else 0)
            
            top_area = df_dash['Area'].mode()[0] if not df_dash.empty and 'Area' in df_dash.columns and not df_dash['Area'].mode().empty else "N/A"
            m3.metric("Área con más pedidos", top_area)
            
            st.divider()
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### Distribución de Movimientos")
                if 'Movimiento' in df_dash.columns and not df_dash['Movimiento'].dropna().empty:
                    movs = df_dash['Movimiento'].value_counts()
                    if not movs.empty:
                        fig1, ax1 = plt.subplots(figsize=(4,3))
                        ax1.pie(movs, labels=movs.index, autopct='%1.1f%%', colors=['#1E3A8A', '#10B981', '#6EE7B7'])
                        fig1.patch.set_alpha(0)
                        st.pyplot(fig1)
                    else:
                        st.info("Sin datos de movimientos.")
                else:
                    st.info("Sin datos suficientes.")
                
            with col_chart2:
                st.markdown("#### Top Áreas Solicitantes")
                if 'Area' in df_dash.columns and not df_dash['Area'].dropna().empty:
                    areas = df_dash['Area'].value_counts().head(5)
                    if not areas.empty:
                        fig2, ax2 = plt.subplots(figsize=(4,3))
                        areas.plot(kind='barh', color='#10B981', ax=ax2)
                        ax2.set_xlabel('Cantidad de Reservas')
                        fig2.patch.set_alpha(0)
                        st.pyplot(fig2)
                    else:
                        st.info("Sin datos de áreas.")
                else:
                    st.info("Sin datos suficientes.")
                
            st.divider()
            st.subheader("📜 Historial Oficial de Registros (Solo Lectura)")
            df_display = df_dash.drop(columns=['Cantidad_num'], errors='ignore')
            st.dataframe(df_display, use_container_width=True, height=300)
        else:
            st.info("Aún no hay datos suficientes para mostrar métricas. Registra tu primera reserva. 🚀")

    # ------------------------------------------
    # TAB 5: ADMINISTRACIÓN
    # ------------------------------------------
    with tab5:
        if st.session_state['rol'] == 'Administrador':
            st.header("Panel de Administración de Usuarios")
            
            with st.expander("👥 Crear Nuevo Usuario"):
                with st.form("form_usuarios"):
                    n_usuario = st.text_input("Nombre de Usuario")
                    n_pass = st.text_input("Contraseña", type="password")
                    n_rol = st.selectbox("Nivel de Acceso", ["Estándar", "Administrador"])
                    
                    if st.form_submit_button("Crear Cuenta"):
                        try:
                            df_users = pd.read_csv(USERS_FILE, sep=None, engine='python', dtype=str)
                        except:
                            df_users = pd.read_csv(USERS_FILE, sep=';', dtype=str)
                            
                        if n_usuario in df_users['usuario'].values:
                            st.warning("Ese usuario ya está registrado.")
                        else:
                            nuevo_user = {'usuario': n_usuario, 'password': n_pass, 'rol': n_rol}
                            df_users = pd.concat([df_users, pd.DataFrame([nuevo_user])], ignore_index=True)
                            df_users.to_csv(USERS_FILE, index=False, sep=';')
                            st.toast(f"Usuario {n_usuario} creado exitosamente.", icon='✅')
                            
            st.markdown("#### Usuarios Activos del Sistema")
            try:
                df_u_show = pd.read_csv(USERS_FILE, sep=None, engine='python', dtype=str)[['usuario', 'rol']]
            except:
                df_u_show = pd.read_csv(USERS_FILE, sep=';', dtype=str)[['usuario', 'rol']]
            st.dataframe(df_u_show, use_container_width=True)
        else:
            st.error("⛔ Acceso Restringido solo para Administradores.")
