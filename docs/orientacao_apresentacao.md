# Resumo do Trabalho — Detecção de Anomalias com PCA no Processo Tennessee Eastman

**Grupo:**
Fábio Luiz Souza Alves · Eduardo Soares Zanutti · Reynaldo Pereira Martins · Victor Zoratti Ferreira

---

## 1. Contexto e Motivação

Processos industriais complexos, como plantas químicas, operam continuamente e podem desenvolver falhas sutis que, se não detectadas a tempo, causam paradas de produção, danos ao equipamento ou riscos à segurança. Monitorar dezenas de variáveis simultaneamente com regras manuais é inviável.

O **Processo Tennessee Eastman (TEP)** é um simulador industrial amplamente usado como benchmark na literatura de controle e monitoramento de processos. Ele modela uma planta química real com 41 variáveis de processo (temperatura, pressão, vazão, composição) e 21 tipos de falha catalogados.

**Problema:** Como detectar automaticamente quando o processo sai do comportamento normal?

---

## 2. Solução Proposta

Usamos **Análise de Componentes Principais (PCA)** como ferramenta de detecção de anomalias. A ideia central é:

1. Aprender o padrão de operação normal com dados históricos
2. Comprimir as 41 variáveis em um número menor de componentes que capturam a maior parte da variação normal
3. Quando o processo apresenta uma falha, os dados "escapam" desse padrão aprendido — e isso é detectável

**Por que PCA?**
- É um método clássico de álgebra linear (decomposição espectral de matrizes)
- Interpretável: sabemos exatamente o que cada componente representa
- Eficaz em dados de processo industrial com variáveis correlacionadas
- Bem documentado na literatura de monitoramento de processos

---

## 3. Como Funciona a Detecção

O detector calcula dois índices estatísticos em tempo real:

### SPE — Squared Prediction Error (Erro de Reconstrução)
Mede o quanto o ponto atual se distancia do subespaço PCA aprendido. Quando há uma falha, as variáveis se movem de forma inesperada e o erro de reconstrução dispara.

### T² de Hotelling
Mede se o ponto está dentro da "nuvem" normal no espaço comprimido pelo PCA. É como uma distância de Mahalanobis multivariada.

**Limiar de decisão:** Calculado nos dados de treinamento com nível de confiança de 99%. Se SPE **ou** T² ultrapassar o limiar → anomalia detectada.

---

## 4. Dados Utilizados

| Arquivo | Descrição |
|---|---|
| Normal 500h | 30.001 amostras de operação normal (base de treino) |
| Normal 50h | 6.001 amostras normais (validação) |
| Falha 1 | Variação na razão A/C de alimentação |
| Falha 2 | Variação na composição da alimentação B |
| Falha 6 | Perda de alimentação A |
| Falha 10 | Temperatura de alimentação C |
| Falha 14 | Válvula de reator emperrada |
| Falha 18 | Comportamento desconhecido |

Cada arquivo de falha tem ~1.000–3.000 amostras. As primeiras 160 amostras são operação normal antes da falha ser introduzida.

---

## 5. Resultados Esperados (EDA já realizada)

A análise exploratória mostrou:

- Com **~21 componentes principais**, capturamos 95% da variância do processo normal
- No espaço 2D do PCA, as falhas se separam claramente dos dados normais (especialmente falhas 1, 2 e 6)
- O índice SPE ultrapassa o limiar de 99% logo após a introdução da falha, com **latência de detecção de poucos minutos**
- Falhas mais sutis (ex.: falha 18 — causa desconhecida) são mais difíceis de detectar

---

## 6. Estrutura do Código

O projeto está organizado como um pacote Python reutilizável:

```
Dados brutos (.xlsx)
    ↓  get_data.py          → download automático do GitHub
Dados preprocessados (.csv)
    ↓  process_data.py      → padronização de nomes e metadados
Dados consolidados (.parquet)
    ↓  train_pca.py         → treina o detector e salva o modelo
Modelo treinado (.joblib)
    ↓  detect_anomalies.py  → aplica o detector em dados novos
Relatório de detecção (.csv) → métricas: taxa de detecção, falsos alarmes, atraso
```

---

## 7. Métricas de Avaliação

| Métrica | O que mede |
|---|---|
| Taxa de Detecção (DR) | % de amostras com falha corretamente identificadas |
| Taxa de Falso Alarme (FAR) | % de amostras normais erroneamente sinalizadas |
| Atraso de Primeira Detecção | Quantas amostras até detectar a falha pela primeira vez |

O objetivo é maximizar DR e minimizar FAR e atraso.

---

## 8. Divisão Sugerida de Slides

| Seção | Responsável sugerido |
|---|---|
| Contexto e motivação (slides 1–3) | Victor |
| Fundamentos de PCA (slides 4–6) | Reynaldo |
| Metodologia e índices SPE/T² (slides 7–9) | Fábio |
| Dados e resultados/gráficos (slides 10–13) | Eduardo (fornece os gráficos) |
| Conclusões e trabalhos futuros (slides 14–15) | Todos |

---

## 9. Mensagens-Chave para a Apresentação

1. **PCA não é só redução de dimensionalidade** — é uma ferramenta de monitoramento estatístico de processos
2. **Dois índices são complementares:** SPE captura o que está fora do modelo; T² captura o que está distante do centro normal
3. **O método é não-supervisionado:** não precisa de exemplos de falhas para treinar — só precisa de dados normais
4. **Resultado prático:** detecção em tempo real com baixo custo computacional e interpretabilidade alta

---

*Eduardo está desenvolvendo o código e os gráficos. Entrem em contato com ele para obter as figuras finais antes de montar os slides de resultados.*
