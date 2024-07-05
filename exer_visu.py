import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do CSV
df = pd.read_csv("performance_results.csv")

# Calcular valores médios agrupados por dimensões e número de pinos
df_grouped_by_dimension = df.groupby("Dimensions").agg({
    'Pins': 'mean',
    'Distance': 'mean',
    'Time': 'mean'
}).reset_index()

df_grouped_by_pins = df.groupby("Pins").agg({
    'Distance': 'mean',
    'Time': 'mean'
}).reset_index()

# Ordenar as dimensões conforme solicitado
dim_order = ["10x10", "10x100", "100x100", "1000x100"]
df_grouped_by_dimension["Dimensions"] = pd.Categorical(df_grouped_by_dimension["Dimensions"], categories=dim_order, ordered=True)
df_grouped_by_dimension = df_grouped_by_dimension.sort_values("Dimensions")

# Convert Dimensions to string to avoid plotting issues
df_grouped_by_dimension["Dimensions"] = df_grouped_by_dimension["Dimensions"].astype(str)

# Tabela dos Resultados Agrupados por Dimensões
print("Resultados Agrupados por Dimensões:")
print(df_grouped_by_dimension)

# Tabela dos Resultados Agrupados por Número de Pinos
print("Resultados Agrupados por Número de Pinos:")
print(df_grouped_by_pins)

# Gráfico de Tempo de Execução por Número de Pinos (Média)
plt.figure(figsize=(10, 6))
plt.plot(df_grouped_by_pins["Pins"], df_grouped_by_pins["Time"], marker='o', color='blue')
plt.xlabel("Número de Pinos")
plt.ylabel("Tempo de Execução Médio (s)")
plt.title("Tempo de Execução Médio vs. Número de Pinos")
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfico de Tempo de Execução por Distância (Média)
plt.figure(figsize=(10, 6))
plt.plot(df["Distance"], df["Time"], marker='o', linestyle='None', color='green')
plt.xlabel("Distância Total")
plt.ylabel("Tempo de Execução (s)")
plt.title("Tempo de Execução vs. Distância Total")
plt.grid(True)
plt.tight_layout()
plt.show()

# Gráfico de Tempo de Execução por Dimensão (Média)
plt.figure(figsize=(10, 6))
plt.plot(df_grouped_by_dimension["Dimensions"], df_grouped_by_dimension["Time"], marker='o', color='purple')
plt.xlabel("Dimensão da Placa (Colunas x Linhas)")
plt.ylabel("Tempo de Execução Médio (s)")
plt.title("Tempo de Execução Médio por Dimensão da Placa")
plt.xticks(rotation=45)
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()
