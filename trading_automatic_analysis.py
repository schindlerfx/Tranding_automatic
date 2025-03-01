import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# Configuração para evitar avisos de atribuição encadeada
pd.options.mode.chained_assignment = None

# Passo 1: Escolher um ativo
ativo = 'PETR4.SA'

# Passo 2: Puxar os dados do Yahoo Finance
print("Baixando dados do Yahoo Finance...")
dados_ativo = yf.download(ativo)
print("Dados baixados com sucesso!")

# Passo 3: Calcular os retornos
dados_ativo['retornos'] = dados_ativo['Adj Close'].pct_change().dropna()

# Passo 4: Separar os retornos positivos dos negativos
dados_ativo['retornos_postivos'] = dados_ativo['retornos'].apply(lambda x: x if x > 0 else 0)
dados_ativo['retornos_negativos'] = dados_ativo['retornos'].apply(lambda x: abs(x) if x < 0 else 0)

# Passo 5: Calcular a média de retornos positivos e negativos dos últimos 22 dias
dados_ativo['media_retornos_positivos'] = dados_ativo['retornos_postivos'].rolling(window=22).mean()
dados_ativo['media_retornos_negativos'] = dados_ativo['retornos_negativos'].rolling(window=22).mean()
dados_ativo = dados_ativo.dropna()

# Passo 6: Calcular o RSI
dados_ativo['RSI'] = 100 - 100 / (1 + dados_ativo['media_retornos_positivos'] / dados_ativo['media_retornos_negativos'])

# Passo 7: Gerar sinais de compra ou venda
dados_ativo.loc[dados_ativo['RSI'] < 30, 'compra'] = 'sim'
dados_ativo.loc[dados_ativo['RSI'] > 30, 'compra'] = 'nao'

# Passo 8: Identificar datas de compra e venda
data_compra = []
data_venda = []

for i in range(len(dados_ativo)):
    if "sim" in dados_ativo['compra'].iloc[i]:
        data_compra.append(dados_ativo.iloc[i + 1].name)  # Compra no dia seguinte
        for j in range(1, 11):  # Verifica os próximos 10 dias
            if i + j < len(dados_ativo):  # Evita erro de índice
                if dados_ativo['RSI'].iloc[i + j] > 40:  # Vende se o RSI passar de 40
                    data_venda.append(dados_ativo.iloc[i + j + 1].name)  # Vende no dia seguinte
                    break
                elif j == 10:  # Vende após 10 dias
                    data_venda.append(dados_ativo.iloc[i + j + 1].name)

# Passo 9: Visualização dos pontos de compra
plt.figure(figsize=(12, 5))
plt.scatter(dados_ativo.loc[data_compra].index, dados_ativo.loc[data_compra]['Adj Close'], marker='^', c='g', label='Compra')
plt.plot(dados_ativo['Adj Close'], alpha=0.7, label='Preço de Fechamento Ajustado')
plt.title(f"Pontos de Compra para {ativo}")
plt.xlabel("Data")
plt.ylabel("Preço Ajustado (R$)")
plt.legend()
plt.show()

# Passo 10: Calculando lucros
if len(data_compra) == len(data_venda):
    lucros = dados_ativo.loc[data_venda]['Open'].values / dados_ativo.loc[data_compra]['Open'].values - 1
    print(f"Lucros das operações: {lucros}")
else:
    print("Erro: Número de compras e vendas não coincide.")
    exit()

# Passo 11: Análise dos lucros
operacoes_vencedoras = len(lucros[lucros > 0]) / len(lucros)
media_ganhos = np.mean(lucros[lucros > 0])
media_perdas = abs(np.mean(lucros[lucros < 0]))
expectativa_matematica_modelo = (operacoes_vencedoras * media_ganhos) - ((1 - operacoes_vencedoras) * media_perdas)
performance_acumulada = (np.cumprod((1 + lucros)) - 1)

print(f"Operações vencedoras: {operacoes_vencedoras * 100:.2f}%")
print(f"Média de ganhos: {media_ganhos * 100:.2f}%")
print(f"Média de perdas: {media_perdas * 100:.2f}%")
print(f"Expectativa matemática do modelo: {expectativa_matematica_modelo * 100:.2f}%")

# Passo 12: Comparação com Buy and Hold
retorno_buy_and_hold = dados_ativo['Adj Close'].iloc[-1] / dados_ativo['Adj Close'].iloc[0] - 1
print(f"Retorno do Buy and Hold: {retorno_buy_and_hold * 100:.2f}%")

# Passo 13: Visualização do retorno acumulado
plt.figure(figsize=(12, 5))
plt.plot(data_compra, performance_acumulada, label='Retorno Acumulado da Estratégia')
plt.title(f"Retorno Acumulado da Estratégia para {ativo}")
plt.xlabel("Data")
plt.ylabel("Retorno Acumulado")
plt.legend()
plt.show()