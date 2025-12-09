import requests  # O carteiro que busca dados na internet

# --- CONFIGURAÇÕES (PARÂMETROS DO ROBÔ) ---
MOEDA_ORIGEM = "USD"
MOEDA_DESTINO = "BRL"
LIMITE_ALERTA = 6.00  # Nosso gatilho de negócio

print("Iniciando o Robô de Monitoramento...")

# 1. BUSCAR A COTAÇÃO (GET)
# Estamos acessando a URL da API da AwesomeAPI
url = f"https://economia.awesomeapi.com.br/last/{MOEDA_ORIGEM}-{MOEDA_DESTINO}"
resposta = requests.get(url)

# 2. TRATAR OS DADOS (A "Tradução")
if resposta.status_code == 200: # 200 significa "OK, consegui os dados"
    dados = resposta.json() # Transforma o texto da internet em um Dicionário Python
    
    # Navegando no Dicionário: USDBRL -> bid (preço de compra)
    cotacao_atual = float(dados['USDBRL']['bid'])
    
    print(f"Cotação capturada: R$ {cotacao_atual:.2f}")

    # 3. TOMADA DE DECISÃO (Regra de Negócio)
    if cotacao_atual > LIMITE_ALERTA:
        print("ALERTA: Dólar acima do limite! Preparando e-mail...")
        
        # Montando o E-mail
        print(f"🚨 URGENTE: Dólar a R$ {cotacao_atual:.2f}")
        
        print(f"""
        Olá,
        
        O sistema de monitoramento detectou uma alta no câmbio.
        Valor Atual: R$ {cotacao_atual:.2f}
        Limite Definido: R$ {LIMITE_ALERTA:.2f}
        
        Recomendação: Segurar a compra.
        
        Att,
        Robô Python
        """)
    
    else:
        print("Cotação dentro do esperado. Nenhuma ação necessária.")

else:
    print("Erro ao conectar na API. Verifique a internet.")