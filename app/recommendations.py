import pickle
import pandas as pd

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

songs_df = pd.DataFrame(songs_df)

with open('model/modelo.pkl', 'rb') as f:
    model = pickle.load(f)

def buscar_cancion(query):
    """
    Busca una canción por nombre (parcial o completo)
    
    Args:
        query: Nombre de la canción a buscar (str)
    
    Returns:
        Lista de diccionarios con coincidencias encontradas
    """
    query_lower = query.lower().strip()
    
    # Buscar coincidencias parciales en el nombre de la canción
    coincidencias = songs_df[
        songs_df['cancion'].str.lower().str.contains(query_lower, na=False)
    ]
    
    if coincidencias.empty:
        return []
    
    return coincidencias.to_dict('records')


def seleccionar_cancion(query):
    """
    Busca y permite seleccionar una canción si hay múltiples resultados
    
    Args:
        query: Nombre de la canción (str) o token (int)
    
    Returns:
        Token de la canción seleccionada o None si no se encuentra
    """
    # Si ya es un token (int), retornarlo directamente
    if isinstance(query, int):
        if query in songs_df['token'].values:
            return query
        else:
            print(f"❌ Token {query} no encontrado en el vocabulario")
            return None
    
    # Buscar por nombre
    coincidencias = buscar_cancion(query)
    
    if len(coincidencias) == 0:
        print(f"❌ No se encontró ninguna canción con '{query}'")
        return None
    
    elif len(coincidencias) == 1:
        # Una sola coincidencia, usar automáticamente
        cancion = coincidencias[0]
        print(f"✅ Canción encontrada: '{cancion['cancion'].title()}' - {cancion['artista']}")
        return cancion['token']
    
    else:
        # Múltiples coincidencias, mostrar opciones
        print(f"\n🔍 Se encontraron {len(coincidencias)} canciones con '{query}':\n")
        
        for idx, cancion in enumerate(coincidencias[:10], 1):  # Limitar a 10 resultados
            print(f"   {idx}. '{cancion['cancion'].title()}' - {cancion['artista']} (Token: {cancion['token']})")
        
        if len(coincidencias) > 10:
            print(f"\n   ... y {len(coincidencias) - 10} más")
        
        print(f"\n💡 Usa el token directamente o especifica mejor el nombre de la canción")
        print(f"   Ejemplo: print_recommendations({coincidencias[0]['token']})")
        
        # Retornar el primer resultado por defecto
        return coincidencias[0]['token']


def print_recommendations(query, top_n=5, auto_select=True):
    """
    Imprime recomendaciones de canciones similares
    
    Args:
        query: Token (int) o nombre de canción (str)
        top_n: Número de recomendaciones (default: 5)
        auto_select: Si es True y hay múltiples coincidencias, usa la primera automáticamente
    
    Returns:
        DataFrame con las canciones recomendadas
    """
    # Obtener token
    if isinstance(query, str):
        song_id = seleccionar_cancion(query)
        if song_id is None:
            return None
    else:
        song_id = query
        if song_id not in songs_df['token'].values:
            print(f"❌ Token {song_id} no encontrado")
            return None
    
    # Verificar que el token existe en el modelo
    if song_id not in model.wv:
        print(f"❌ Token {song_id} no está en el vocabulario del modelo")
        return None
    
    # Obtener canciones similares con sus scores
    similar_songs = model.wv.most_similar(positive=[song_id], topn=top_n)
    
    # Extraer tokens y scores
    tokens_similares = [int(token) for token, score in similar_songs]
    scores_similares = {int(token): score for token, score in similar_songs}
    
    # Filtrar DataFrame
    recomendaciones = songs_df[songs_df.token.isin(tokens_similares)].copy()
    
    # Agregar columna de similitud
    recomendaciones['similitud'] = recomendaciones['token'].map(scores_similares)
    
    # Ordenar por similitud
    recomendaciones = recomendaciones.sort_values('similitud', ascending=False)
    
    # Mostrar canción original
    cancion_original = songs_df[songs_df['token'] == song_id][['cancion', 'artista']]
    if not cancion_original.empty:
        print(f"\n{'='*80}")
        print(f"🎵 Canción original:")
        print(f"   '{cancion_original.iloc[0]['cancion'].title()}' - {cancion_original.iloc[0]['artista']}")
        print(f"   Token: {song_id}")
    
    print(f"\n✨ Top {top_n} recomendaciones:\n")
    
    for idx, row in enumerate(recomendaciones.itertuples(), 1):
        print(f"   {idx}. [{row.similitud:.4f}] '{row.cancion.title()}' - {row.artista}")
    
    print(f"{'='*80}\n")
    
    return recomendaciones

print(print_recommendations(1))
print_recommendations("tití me preguntó", top_n=5)
print_recommendations("el sol", top_n=5)