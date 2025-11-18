from recommendations import print_recommendations
import streamlit as st
import pickle
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Spotify EmbedRecommender",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS STYLES
# ============================================
st.markdown("""
    <style>
    /* Fondo oscuro estilo Spotify */
    .stApp {
        background-color: #121212;
    }
    
    /* Header principal */
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1DB954 0%, #1ed760 50%, #1DB954 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0;
    }
    
    .sub-header {
        text-align: center;
        color: #b3b3b3;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    
    /* Mejorar el input */
    .stTextInput input {
        background-color: #282828;
        color: #ffffff;
        border: 2px solid #1DB954;
        border-radius: 25px;
        padding: 15px 25px;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .stTextInput input:focus {
        border-color: #1ed760;
        box-shadow: 0 0 15px rgba(29, 185, 84, 0.3);
    }
    
    /* Botón estilo Spotify */
    .stButton button {
        background-color: #1DB954;
        color: white;
        border-radius: 25px;
        font-weight: bold;
        border: none;
        padding: 15px 30px;
        transition: all 0.3s;
        font-size: 16px;
    }
    
    .stButton button:hover {
        background-color: #1ed760;
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(29, 185, 84, 0.4);
    }
    
    /* Cards de recomendaciones */
    .song-card {
        background: linear-gradient(135deg, #282828 0%, #181818 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-left: 4px solid #1DB954;
        transition: all 0.3s;
    }
    
    .song-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(29, 185, 84, 0.3);
    }
    
    .song-title {
        color: white;
        margin: 0;
        font-size: 1.3rem;
        font-weight: bold;
    }
    
    .song-artist {
        color: #b3b3b3;
        margin: 5px 0;
        font-size: 1rem;
    }
    
    /* Mejorar el dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #181818;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #282828;
        border-radius: 10px;
        color: white;
    }
    
    /* Métricas */
    .stMetric {
        background-color: #282828;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #1DB954;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #1DB954;
        color: white;
        border-radius: 10px;
    }
    
    .stError {
        background-color: #e22134;
        color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE CARGA CON CACHE
# ============================================
@st.cache_resource
def load_model():
    """Carga el modelo con cache para mejor performance"""
    try:
        with open('model/modelo.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

@st.cache_data
def load_data():
    """Carga los datos con cache"""
    try:
        with open('data/datos_tokenizacion.pkl', 'rb') as f:
            datos = pickle.load(f)
            playlists_tokenizadas = datos['playlists_tokenizadas']
            canciones_a_tokens = datos['canciones_a_tokens']
            tokens_a_canciones = datos['tokens_a_canciones']

        # Crear DataFrame con columnas separadas: cancion, artista, token
        songs_df = []
        for token, info in tokens_a_canciones.items():
            songs_df.append({
                'cancion': info['cancion'],
                'artista': info['artista'],
                'token': token
            })

        return pd.DataFrame(songs_df), canciones_a_tokens, tokens_a_canciones
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

# ============================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

if 'last_recommendations' not in st.session_state:
    st.session_state.last_recommendations = None

# ============================================
# CARGAR DATOS
# ============================================
model = load_model()
songs_df, canciones_a_tokens, tokens_a_canciones = load_data()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # Número de recomendaciones
    num_recommendations = st.slider(
        "Number of recommendations",
        min_value=5,
        max_value=20,
        value=10,
        help="Select how many songs you want to receive as recommendations"
    )
    
    st.markdown("---")
    
    # Modo de visualización
    st.markdown("### 🎨 Display Mode")
    view_mode = st.radio(
        "Choose how to display results:",
        ["Cards", "Table", "Both"],
        index=0
    )
    
    st.markdown("---")
    
    # Historial de búsqueda
    if st.session_state.search_history:
        st.markdown("### 📜 Recent Searches")
        for i, search in enumerate(reversed(st.session_state.search_history[-5:])):
            if st.button(f"🔍 {search}", key=f"history_{i}"):
                st.session_state.selected_from_history = search
        
        if st.button("🗑️ Clear History"):
            st.session_state.search_history = []
            st.rerun()
    
    st.markdown("---")
    
    # Favoritos
    if st.session_state.favorites:
        st.markdown("### ⭐ Favorites")
        for i, fav in enumerate(st.session_state.favorites[-5:]):
            st.text(f"♥ {fav}")
        
        if st.button("🗑️ Clear Favorites"):
            st.session_state.favorites = []
            st.rerun()
    
    st.markdown("---")
    
    # Información
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Spotify EmbedRecommender** uses advanced 
        machine learning algorithms to find songs 
        similar to your favorites.
        
        **How it works:**
        1. Enter a song name
        2. Our AI analyzes patterns
        3. Get personalized recommendations
        
        **Version:** 2.0  
        **Last Update:** 2024
        """)

# ============================================
# MAIN HEADER
# ============================================
st.markdown('<h1 class="main-header">🎧 Spotify EmbedRecommender</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover your next favorite song powered by AI</p>', unsafe_allow_html=True)

# ============================================
# EXAMPLE QUESTIONS
# ============================================
with st.expander("💡 Example Songs to Try"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **Rock Classics:**
        - Bohemian Rhapsody
        - Nothing Else Matters
        - In the End
        """)
    with col2:
        st.markdown("""
        **Latin Hits:**
        - Tití Me Preguntó
        - Pedro Navaja
        - La Plena
        """)
    with col3:
        st.markdown("""
        **Pop Favorites:**
        - Shape of You
        - Blinding Lights
        - Levitating
        """)

st.markdown("---")

# ============================================
# BÚSQUEDA SIMPLE
# ============================================
st.markdown("### 🔍 Find Your Song")

col1, col2 = st.columns([5, 1])

with col1:
    # Verificar si hay una selección del historial
    default_value = ""
    if hasattr(st.session_state, 'selected_from_history'):
        default_value = st.session_state.selected_from_history
        delattr(st.session_state, 'selected_from_history')
    
    text_input = st.text_input(
        "Song name:",
        value=default_value,
        placeholder="e.g., Bohemian Rhapsody, Tití Me Preguntó...",
        label_visibility="collapsed"
    )

with col2:
    recommend_button = st.button("🎧 Get Recommendations", use_container_width=True, type="primary")

search_query = text_input

# ============================================
# PROCESAMIENTO DE RECOMENDACIONES
# ============================================
if recommend_button:
    if not search_query or search_query.strip() == "":
        st.warning("⚠️ Please enter a song name")
    else:
        # Agregar al historial
        if search_query not in st.session_state.search_history:
            st.session_state.search_history.append(search_query)
        
        try:
            with st.spinner('🎵 Analyzing and finding perfect recommendations...'):
                recommendations = print_recommendations(search_query)
                
                if recommendations is not None and not recommendations.empty:
                    # Limitar al número seleccionado
                    recommendations = recommendations.head(num_recommendations)
                    recommendations['cancion'] = recommendations['cancion'].str.title()
                    recommendations['artista'] = recommendations['artista'].str.title()
                    
                    # Guardar en session state
                    st.session_state.last_recommendations = recommendations
                    
                    st.success(f"✅ Found {len(recommendations)} amazing recommendations for you!")
                    
                    # Mostrar canción buscada
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
                            padding: 20px;
                            border-radius: 15px;
                            margin: 20px 0;
                            text-align: center;
                        ">
                            <h3 style="color: white; margin: 0;">🎵 Based on: {search_query.title()}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # VISUALIZACIÓN EN CARDS
                    if view_mode in ["Cards", "Both"]:
                        st.markdown("### 🎵 Your Personalized Recommendations")
                        
                        # Mostrar en grid de 3 columnas
                        for i in range(0, len(recommendations), 3):
                            cols = st.columns(3)
                            for j, col in enumerate(cols):
                                if i + j < len(recommendations):
                                    row = recommendations.iloc[i + j]
                                    with col:
                                        # Card con botón de favorito
                                        card_id = f"{row['cancion']}_{row['artista']}"
                                        is_favorite = card_id in st.session_state.favorites
                                        
                                        st.markdown(f"""
                                            <div class="song-card">
                                                <h3 class="song-title">🎵 {row['cancion']}</h3>
                                                <p class="song-artist">👤 {row['artista']}</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Botón de favorito
                                        fav_button_label = "💚 Favorited" if is_favorite else "🤍 Add to Favorites"
                                        if st.button(fav_button_label, key=f"fav_{i}_{j}", use_container_width=True):
                                            if is_favorite:
                                                st.session_state.favorites.remove(card_id)
                                            else:
                                                st.session_state.favorites.append(card_id)
                                            st.rerun()
                    
                    # VISUALIZACIÓN EN TABLA
                    if view_mode in ["Table", "Both"]:
                        if view_mode == "Both":
                            st.markdown("---")
                        
                        st.markdown("### 📋 Detailed View")
                        
                        # Agregar índice personalizado
                        recommendations_display = recommendations.copy()
                        recommendations_display.insert(0, '#', range(1, len(recommendations_display) + 1))
                        
                        st.dataframe(
                            recommendations_display,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "#": st.column_config.NumberColumn(
                                    "#",
                                    width="small"
                                ),
                                "cancion": st.column_config.TextColumn(
                                    "Song",
                                    width="large"
                                ),
                                "artista": st.column_config.TextColumn(
                                    "Artist",
                                    width="large"
                                )
                            }
                        )
                    
                    st.markdown("---")
                    
                    # OPCIONES DE EXPORTACIÓN
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Descargar CSV
                        csv = recommendations.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"recommendations_{search_query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Copiar al portapapeles
                        songs_list = "\n".join([f"{row['cancion']} - {row['artista']}" for _, row in recommendations.iterrows()])
                        st.download_button(
                            label="📋 Copy List",
                            data=songs_list,
                            file_name=f"playlist_{search_query}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Compartir (placeholder)
                        if st.button("🔗 Share", use_container_width=True):
                            st.info("💡 Share feature coming soon!")
                    
                    # RATING SYSTEM
                    st.markdown("---")
                    st.markdown("### ⭐ Rate These Recommendations")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        rating = st.slider(
                            "How satisfied are you with these recommendations?",
                            1, 5, 3,
                            format="%d ⭐"
                        )
                    
                    with col2:
                        if st.button("Submit Rating", use_container_width=True):
                            st.success("Thanks for your feedback! 🎉")
                            # Aquí podrías guardar el rating en una base de datos
                
                else:
                    st.error("❌ No recommendations found for this song.")
                    st.info("💡 Try with a different song name or check the spelling.")
                    
                    # Sugerencias
                    if songs_df is not None:
                        st.markdown("### 🔍 Did you mean?")
                        # Buscar canciones similares
                        similar = songs_df[songs_df['cancion'].str.contains(search_query, case=False, na=False)]
                        if not similar.empty:
                            for _, row in similar.head(5).iterrows():
                                st.text(f"• {row['cancion'].title()} - {row['artista'].title()}")
        
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please try again with a different song or contact support if the problem persists.")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #b3b3b3; padding: 20px;">
        <p>Made with ❤️ using Streamlit | Powered by Machine Learning</p>
        <p style="font-size: 0.8rem;">© 2024 Spotify EmbedRecommender - All rights reserved</p>
    </div>
""", unsafe_allow_html=True)