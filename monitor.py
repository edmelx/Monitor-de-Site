# Coleta dados dos sites e salva no SQLite

import requests
import sqlite3
import time
import logging
import schedule  # biblioteca de agendamento
import smtplib # envia o e-mail
from email.mime.text import MIMEText # formata o e-mail
from datetime import datetime
from config import SITES, DB_PATH

# Configuração do log para registrar erros e eventos

logging.basicConfig(
    filename="monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def criar_banco():
    """Cria a tabela no SQLite se ainda não existir"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS verificacoes (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora      TEXT NOT NULL,
                site           TEXT NOT NULL,
                status_code    INTEGER,
                tempo_resposta REAL,
                resultado      TEXT
            )
        ''')
    conn.commit()
    conn.close()

def verificar_site(site):
    """Faz a requisição GET e retorna status e tempo de resposta."""

    # Dicionário com os códigos de status HTTP e tempo de resposta
    significados = {
        200: 'OK — Online',
        301: 'Redirecionamento permanente',
        302: 'Redirecionamento temporário',
        403: 'Acesso negado (bloqueio de bot)',
        404: 'Página não encontrada',
        429: 'Muitas requisições (rate limit)',
        500: 'Erro interno do servidor',
        503: 'Serviço indisponível', 
    }

    try:
        inicio   = time.time()
        resposta = requests.get(site, timeout=10)
        tempo_ms = round((time.time() - inicio) * 1000, 2)
        resultado = 'Online' if resposta.status_code == 200 else 'Problema'
        mensagem = significados.get(resposta.status_code, f'Código desconhecido')
        print(f'{resultado}: {site} - {resposta.status_code} ({mensagem}) - {tempo_ms}ms')
        return resposta.status_code, tempo_ms, resultado
    except requests.exceptions.RequestException as e:
        logging.error(f'Erro ao verificar {site}: {e}')
        return 0, 0, 'Offline'

def salvar_resultado(data_hora, site, status, tempo, resultado):
    """Insere uma linha na tabela verificacoes."""    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO verificacoes VALUES (NULL, ?, ?, ?, ?, ?)',
        (data_hora, site, status, tempo, resultado)
)
    conn.commit()
    conn.close()

def executar():
    """Percorre todos os sites, verifica e salva no banco de dados."""
    criar_banco()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for site in SITES:
        status, tempo, resultado = verificar_site(site)
        salvar_resultado(agora, site, status, tempo, resultado)
        logging.info(f'{resultado}: {site} - {status} - {tempo}ms')
        time.sleep(1)  # Pausa para não sobrecarregar

    print(f'Verificação concluída: {agora}')

if __name__ == "__main__":
    executar()

# Ponto de entrada do script
if __name__ == '__main__':

    # Executa imediatamente ao iniciar
    executar()

    # Agenda para rodar a cada 1 minuto
    schedule.every(1).minutes.do(executar)

    print('Monitor rodando. Pressione Ctrl+C para encerrar.')

    # Loop infinito — mantém o script ativo
    while True:
        schedule.run_pending()
        time.sleep(1)
