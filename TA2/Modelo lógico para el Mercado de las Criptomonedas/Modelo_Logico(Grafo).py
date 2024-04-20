import pandas as pd
import networkx as nx
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import ast
import time

# Leer archivos CSV de proyectos de criptomonedas y exchanges
df_criptomonedas = pd.read_csv("data_coins.csv")
df_exchanges = pd.read_csv("exchanges_limpio.csv")

# Calcular puntajes de similitud basados en volumen de operaciones entre proyectos y exchanges
def calcular_similitud_proyecto_exchange(proyecto, exchange):
    # Iterar sobre cada fila del DataFrame df_criptomonedas
    for indice, fila in df_criptomonedas.iterrows():
        # Verificar si el nombre del proyecto coincide
        if fila['name'] == proyecto:
            # Obtener la cadena de la columna 'quote'
            cadena_quote = fila['quote']

            # Convertir la cadena en un diccionario utilizando ast.literal_eval
            diccionario_quote = ast.literal_eval(cadena_quote)

            # Extraer el precio y el volumen en USD
            precio_usd = diccionario_quote['USD']['price']
            volumen_usd = diccionario_quote['USD']['volume_24h']

            # Verificar si alguno de los valores es None y asignar 0 si es así
            precio_usd = precio_usd if precio_usd is not None else 0
            volumen_usd = volumen_usd if volumen_usd is not None else 0

            # Obtener el volumen de operaciones del exchange
            volumen_exchange = df_exchanges.loc[df_exchanges['name'] == exchange, "trade_volume_24h_btc"].iloc[0]
            # Calcular similitud (por ejemplo, usando el producto del precio y el volumen)
            similitud = 1 + precio_usd * volumen_usd * volumen_exchange
            return similitud

    # Si el proyecto no se encuentra en el DataFrame
    print(f"El proyecto '{proyecto}' no está presente en el DataFrame.")
    return None

# Construir grafo bipartito ponderado
G = nx.Graph()

# Agregar nodos de proyectos de criptomonedas
for index, row in df_criptomonedas.iterrows():
    G.add_node(row["name"], bipartite=0)
    print(f"Se agregó el nodo {row['name']}")

# Agregar nodos de exchanges
for index, row in df_exchanges.iterrows():
    G.add_node(row["name"], bipartite=1)
    print(f"Se agregó el nodo {row['name']}")

# Iniciar contador de tiempo
start_time = time.time()

# Calcular todas las similitudes y agregar nodos y aristas al grafo
for proyecto_nombre in df_criptomonedas["name"]:
    for exchange_nombre in df_exchanges["name"]:
        similitud = calcular_similitud_proyecto_exchange(proyecto_nombre, exchange_nombre)
        if similitud is not None:
            G.add_edge(proyecto_nombre, exchange_nombre, weight=similitud)  # Agregar arista ponderada al grafo
            print(f"Se estableció una relación entre {proyecto_nombre} y {exchange_nombre} con una similitud de {similitud}")

# Finalizar contador de tiempo
end_time = time.time()

# Imprimir tiempo de ejecución
print("Tiempo total de ejecución:", end_time - start_time, "segundos")

# Crear figura Plotly
fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'scatter3d'}]])

# Obtener posiciones de nodos
pos_proj = nx.spring_layout(G, subset=df_criptomonedas["name"], dim=3)
pos_exch = nx.spring_layout(G, subset=df_exchanges["name"], dim=3)

# Dibujar nodos de proyectos de criptomonedas
for node in df_criptomonedas["name"]:
    x, y, z = pos_proj[node]
    fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode="markers", marker=dict(color="blue"), name=node))

# Dibujar nodos de exchanges
for node in df_exchanges["name"]:
    x, y, z = pos_exch[node]
    fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z], mode="markers", marker=dict(color="red"), name=node))

# Dibujar aristas ponderadas
for u, v, d in G.edges(data=True):
    x1, y1, z1 = pos_proj[u]
    x2, y2, z2 = pos_exch[v]
    similitud = d['weight']
    fig.add_trace(go.Scatter3d(x=[x1, x2], y=[y1, y2], z=[z1, z2], mode="lines", line=dict(color="gray", width=1),
                               name=f"Similitud: {similitud}"))

# Configurar diseño de la figura
fig.update_layout(scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"), showlegend=False)

# Mostrar figura
fig.show()
