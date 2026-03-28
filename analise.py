# Lê os dados do banco SQLite, calcula métricas e gera gráficos

import sqlite3  # para conectar ao banco de dados
import pandas as pd # para manipular os dados em tabelas
import matplotlib.pyplot as plt # para gerar os gráficos
import os # para criar pastas
from config import DB_PATH

# Cria a pasta se ainda não existir

os.makedirs('graficos', exist_ok=True)

def carregar_dados():
    """Busca todos os registros do banco e retorna como tabela DataFrame"""

    # Abre a conexão com o banco de dados
    conn = sqlite3.connect(DB_PATH)
    # Busca os registros válidos e ordena por data

    query = query = "SELECT data_hora, site, status_code, tempo_resposta, resultado FROM verificacoes WHERE tempo_resposta > 0 ORDER BY data_hora ASC"

    # Executa a query e carrega o resultado em Dataframe pandas

    df = pd.read_sql(query, conn)
    conn.close()

    # Converte a coluna de data para o formato datetime do pandas
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    return df

def calcular_metricas(df):
    """Calcula métricas de disponibilidade e tempo médio de resposta por site"""

    # Agrupa os dados por site e calcula as métricas
    metricas = df.groupby('site').agg(
        total        = ('resultado', 'count'),
        online       = ('resultado', lambda x: (x == 'Online').sum()),
        tempo_medio_ms  = ('tempo_resposta', 'mean'),
        tempo_max_ms = ('tempo_resposta', 'max'),

    ).reset_index()

    # Calcula a disponibilidade em porcentagem
    metricas['disponibilidade'] = (metricas['online'] / metricas['total'] * 100).round(2)
    metricas['tempo_medio_ms'] = metricas['tempo_medio_ms'].round(2)
    return metricas

def grafico_disponibilidade(metricas):
    """Gráfico de barras: disponibilidade por site"""
    
    fig, ax = plt.subplots(figsize=(10, 5))

    # Verde = 99% disponível, vermelho se estiver abaixo disso
    cores = ['#2e7d32' if d >= 99 else '#c62828' for d in metricas['disponibilidade']]

    # Remove https:// e www. para deixar o nome mais limpo no gráfico
    sites_curtos = [s.replace('https://', '').replace('www.', '') for s in metricas['site']]

    ax.bar(sites_curtos, metricas['disponibilidade'], color=cores)

    # Linha pontilhada indicando a meta de 99% de disponibilidade
    ax.axhline(y=99, color='orange', linestyle='--', label='Meta 99%')

    ax.set_title('Disponibilidade por site (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Disponibilidade (%)')
    ax.set_ylim(0, 105)
    ax.legend()
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('graficos/disponibilidade.png', dpi=150)
    plt.close()
    print('Gráfico salvo: graficos/disponibilidade.png')

def grafico_tempo_resposta(df):
    """Gráfico de linha: tempo de resposta ao longo do tempo por site"""

    fig, ax = plt.subplots(figsize=(12, 5))

    # Plota uma linha pra cada site

    for site, grupo in df.groupby('site'):
        nome = site.replace('https://', '').replace('www.', '')
        ax.plot(grupo['data_hora'], grupo['tempo_resposta'], label=nome, linewidth=1.5)

    ax.set_title('Tempo de Resposta por Site (ms)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Tempo de Resposta (ms)')
    ax.set_xlabel('Data/Hora')
    ax.legend(fontsize=8)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig('graficos/tempo_resposta.png', dpi=150)
    plt.close()
    print('Gráfico salvo: graficos/tempo_resposta.png')

def grafico_status(df):
    """Gráfico de pizza: proporção de online, offline e problema."""

    # Quantidade de vezes que cada status apareceu
    contagem = df['resultado'].value_counts()

    # Define cores pra cada status
    cores = {'Online': '#2e7d32', 'Offline': '#c62828', 'Problema': '#f57c00'}

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        contagem.values,
        labels=contagem.index,
        autopct='%1.1f%%', # Porcentagem em cada fatia
        colors=[cores.get(k, '#aaa') for k in contagem.index],
        startangle=90
    )

    ax.set_title('Distribuição de status', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('graficos/status.png', dpi=150)
    plt.close()
    print('Gráfico salvo: graficos/status.png')

# Executa quando o script é rodado diretamente
if __name__ == '__main__':
    # Carrega os dados do banco
    df = carregar_dados()

    # Calcula métricas por site
    metricas = calcular_metricas(df)

    # Imprime a tabela de métricas no terminal
    print('\n=== MÉTRICAS DE DISPONIBILIDADE ===')
    print(metricas[['site', 'disponibilidade', 'tempo_medio_ms']].to_string(index=False))
    
    # Gera os três gráficos
    grafico_disponibilidade(metricas)
    grafico_tempo_resposta(df)
    grafico_status(df)

    print('\nAnálise concluída!')


