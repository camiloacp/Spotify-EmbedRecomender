from autentication import sp
import pandas as pd
from utils import buscar_playlist_genero, limpiar_parentesis
import pickle

# Lista de géneros musicales
generos = [
    'Reggaeton', 
    'Rock', 'Pop', 'Rap', 'Metal', 'Salsa', 'Cumbia', 
    'Norteña', 'Popular', 'Vallenato', 'House', 'Electronica', 'Indie'
]

# Buscar playlists dinámicamente por género
print("=== BUSCANDO PLAYLISTS POR GÉNERO ===\n")
playlists_generos = {}

for genero in generos:
    playlists = buscar_playlist_genero(genero, limite=20)
    if playlists:
        playlists_generos[genero] = playlists
        print(f"✓ {genero}: {len(playlists)} playlists encontradas\n")

total_playlists = sum(len(playlists) for playlists in playlists_generos.values())
print(f"\n✓ Total de playlists encontradas: {total_playlists}\n")

# Obtener tracks de las playlists por género
all_tracks = []

print("\n=== OBTENIENDO CANCIONES DE PLAYLISTS POR GÉNERO ===\n")
for genero, playlists in playlists_generos.items():
    for playlist_info in playlists:
        try:
            print(f"Obteniendo canciones de {genero} ({playlist_info['name']})...")
            tracks = sp.playlist_tracks(playlist_info['id'])
            
            if tracks and 'items' in tracks:
                print(f"✓ {len(tracks['items'])} canciones obtenidas")
                all_tracks.extend(tracks['items'])
            else:
                print(f"⚠ No se encontraron canciones")
                
        except Exception as e:
            print(f"✗ Error al obtener canciones: {e}")

print(f"\n✓ Total de canciones recopiladas: {len(all_tracks)}")

# Extraer nombres de canciones por género
print("\n=== EXTRAYENDO NOMBRES DE CANCIONES POR GÉNERO ===\n")
playlists_canciones = {}

for genero, playlists in playlists_generos.items():
    nombres_canciones = []
    for playlist_info in playlists:
        try:
            tracks = sp.playlist_tracks(playlist_info['id'])
            
            if tracks and 'items' in tracks:
                # Extraer solo los nombres de las canciones
                for item in tracks['items']:
                    if item and item['track']:
                        nombre_cancion = item['track']['name']
                        nombres_canciones.append(nombre_cancion)
                
        except Exception as e:
            print(f"✗ Error procesando playlist {playlist_info['name']}: {e}")
    
    if nombres_canciones:
        playlists_canciones[genero] = nombres_canciones
        print(f"✓ {genero}: {len(nombres_canciones)} canciones totales")

# Mostrar las canciones de cada género
print("\n=== LISTAS DE CANCIONES POR GÉNERO ===\n")
for genero, canciones in playlists_canciones.items():
    print(f"\n{genero}:")
    print("-" * 50)
    for idx, cancion in enumerate(canciones, 1):
        print(f"{idx}. {cancion}")
    print()

# Crear DataFrame con todas las canciones
print("\n=== CREANDO DATAFRAME CON TODAS LAS CANCIONES ===\n")
datos_canciones = []
for genero, playlists in playlists_generos.items():
    for playlist_info in playlists:
        try:
            tracks = sp.playlist_tracks(playlist_info['id'])
            
            if tracks and 'items' in tracks:
                for item in tracks['items']:
                    if item and item['track']:
                        track = item['track']
                        
                        # Limpiar nombres de paréntesis
                        nombre_cancion = limpiar_parentesis(track['name'])
                        nombre_artistas = ', '.join([limpiar_parentesis(artist['name'].title()) for artist in track['artists']])
                        
                        datos_canciones.append({
                            'genero': genero,
                            'playlist': playlist_info['name'].title(),
                            'cancion': nombre_cancion.title(),
                            'artista': nombre_artistas,
                            'popularidad': track['popularity'],
                            'id': track['id']
                        })
        except Exception as e:
            print(f"✗ Error procesando playlist {playlist_info['name']}: {e}")

df_canciones = pd.DataFrame(datos_canciones)
print(f"✓ DataFrame creado con {len(df_canciones)} canciones")
print("\nMuestra de canciones:")
print(df_canciones.sample(min(60, len(df_canciones))))

print("\n=== TOKENIZANDO CANCIONES ===\n")

# Estructura principal: lista de listas (cada sublista es una playlist tokenizada)
playlists_tokenizadas = []

# Diccionario de mapeo: "cancion - artista" -> token_id
canciones_a_tokens = {}

# Diccionario inverso: token_id -> {'cancion': nombre, 'artista': artista}
tokens_a_canciones = {}

token = 0

# Iterar sobre cada género y cada playlist individual
for genero, playlists in playlists_generos.items():
    print(f"\n--- Tokenizando playlists de {genero} ---")
    
    for playlist_info in playlists:
        try:
            # Obtener canciones de esta playlist específica
            tracks = sp.playlist_tracks(playlist_info['id'])
            
            if tracks and 'items' in tracks:
                tokens_playlist_actual = []
                
                print(f"\nPlaylist: {playlist_info['name']}")
                
                for item in tracks['items']:
                    if item and item['track']:
                        nombre_cancion = item['track']['name'].lower()
                        # Obtener artistas (puede haber múltiples)
                        artistas = ', '.join([artist['name'] for artist in item['track']['artists']])
                        
                        # Crear clave única: cancion + artista
                        clave_unica = f"{nombre_cancion} - {artistas.lower()}"
                        
                        # Si la canción NO ha sido tokenizada, crear nuevo token
                        if clave_unica not in canciones_a_tokens:
                            token += 1
                            canciones_a_tokens[clave_unica] = token
                            tokens_a_canciones[token] = {
                                'cancion': nombre_cancion,
                                'artista': artistas
                            }
                            tokens_playlist_actual.append(token)
                            print(f"  ✓ Nueva: '{nombre_cancion}' - {artistas} -> Token {token}")
                        else:
                            # Si ya existe, reutilizar el token existente
                            token_existente = canciones_a_tokens[clave_unica]
                            tokens_playlist_actual.append(token_existente)
                            print(f"  ↻ Repetida: '{nombre_cancion}' - {artistas} -> Token {token_existente}")
                
                # Agregar esta playlist tokenizada a la lista principal
                playlists_tokenizadas.append(tokens_playlist_actual)
                print(f"  ✓ Playlist tokenizada: {len(tokens_playlist_actual)} canciones, {len(set(tokens_playlist_actual))} únicas")
                
        except Exception as e:
            print(f"  ✗ Error tokenizando playlist {playlist_info['name']}: {e}")

print(f"\n{'='*60}")
print(f"✓ Total de playlists tokenizadas: {len(playlists_tokenizadas)}")
print(f"✓ Total de canciones únicas: {len(canciones_a_tokens)}")
print(f"✓ Total de tokens en todas las playlists: {sum(len(p) for p in playlists_tokenizadas)}")
print(f"{'='*60}")

# Mostrar ejemplos de uso
print("\n=== EJEMPLOS DE USO ===\n")

print("1. Primera playlist tokenizada (primeros 10 tokens):")
print(f"   {playlists_tokenizadas[0][:10]}")

print(f"\n2. Buscar canción y artista por token (ej: token {list(tokens_a_canciones.keys())[0]}):")
primer_token = list(tokens_a_canciones.keys())[0]
info = tokens_a_canciones[primer_token]
print(f"   Token {primer_token} ->")
print(f"      Canción: '{info['cancion']}'")
print(f"      Artista: {info['artista']}")

print(f"\n3. Buscar token por canción-artista:")
ejemplo_clave = list(canciones_a_tokens.keys())[0]
print(f"   '{ejemplo_clave}' -> Token {canciones_a_tokens[ejemplo_clave]}")

print(f"\n4. Estructura completa:")
print(f"   - playlists_tokenizadas: lista con {len(playlists_tokenizadas)} sublistas")
print(f"   - canciones_a_tokens: diccionario con {len(canciones_a_tokens)} canciones")
print(f"   - tokens_a_canciones: diccionario con {len(tokens_a_canciones)} tokens")
print(f"     Cada token mapea a: {{'cancion': '...', 'artista': '...'}}")

# Guardar a CSV
csv_filename = 'data/canciones_playlists_generos.csv'
df_canciones.to_csv(csv_filename, index=False, encoding='utf-8')
print(f"\n✓ Datos guardados en: {csv_filename}")

# Guardar
datos_tokenizacion = {
    'playlists_tokenizadas': playlists_tokenizadas,
    'canciones_a_tokens': canciones_a_tokens,
    'tokens_a_canciones': tokens_a_canciones
}

with open('data/datos_tokenizacion.pkl', 'wb') as f:
    pickle.dump(datos_tokenizacion, f)

print(f"✓ Datos guardados en: datos_tokenizacion.pkl")