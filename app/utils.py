from autentication import sp
import re
from settings import LIMIT_PLAYLISTS

# Función para buscar múltiples playlists por género
def buscar_playlist_genero(genero, limite=LIMIT_PLAYLISTS):
    """Busca múltiples playlists de un género musical"""
    query = f'Top {genero}'
    playlists_encontradas = []
    
    try:
        results = sp.search(q=query, type='playlist', limit=LIMIT_PLAYLISTS)  # Buscar más resultados
        
        if results and results['playlists']['items']:
            for playlist in results['playlists']['items']:
                if playlist and genero.lower() in playlist['name'].lower():
                    es_oficial = 'spotify' in playlist['owner']['id'].lower()
                    tipo = "oficial" if es_oficial else "popular"
                    print(f"✓ Playlist {tipo}: {playlist['name']} - ID: {playlist['id']}")
                    
                    playlists_encontradas.append({
                        'id': playlist['id'], 
                        'name': playlist['name'],
                        'oficial': es_oficial
                    })
                    
                    # Limitar cantidad de playlists
                    if len(playlists_encontradas) >= limite:
                        break
                
    except Exception as e:
        print(f"Error buscando playlists de {genero}: {e}")
    
    return playlists_encontradas if playlists_encontradas else []

# Función para limpiar paréntesis
def limpiar_parentesis(texto):
    """Elimina paréntesis y su contenido de un string"""
    if texto:
        # Elimina paréntesis y su contenido, y espacios extra
        texto_limpio = re.sub(r'\s*\([^)]*\)', '', texto)
        # Elimina espacios múltiples y espacios al inicio/final
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        return texto_limpio
    return texto