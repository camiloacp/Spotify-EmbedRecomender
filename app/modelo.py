import pickle
import pandas as pd
from gensim.models import Word2Vec
import numpy as np
from settings import PARAMS
from recommendations import print_recommendations

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
print(songs_df)

model = Word2Vec(
    playlists_tokenizadas, **PARAMS
)

with open('model/modelo.pkl', 'wb') as f:
    pickle.dump(model, f)

print(print_recommendations(1))