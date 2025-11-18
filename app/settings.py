LIMIT_PLAYLISTS = 40

PARAMS = {
    'vector_size': 128,      # ✅ Mayor dimensionalidad = más información semántica
    'window': 5,             # ✅ Contexto razonable para playlists (5 canciones alrededor)
    'min_count': 1,  # ✅ Filtra canciones raras
    'sg': 1,                 # ✅ Skip-gram (mejor que CBOW para vocabularios medianos)
    'negative': 15,          # ✅ Más muestras negativas = mejor calidad
    'ns_exponent': 0.75,     # ✅ Exponente de sampling (estándar)
    'epochs': 20,            # ✅ Más épocas = mejor convergencia
    'seed': 42,              # ✅ Reproducibilidad
    'workers': 4,            # ✅ Paralelización
    'alpha': 0.025,          # ✅ Learning rate inicial
    'min_alpha': 0.0001,     # ✅ Learning rate final
}