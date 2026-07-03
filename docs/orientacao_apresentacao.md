# Orientação da Apresentação — Detecção de Anomalias com PCA no TEP

**Grupo:** Reynaldo · Victor · Eduardo · Fábio  
**Disciplina:** Fundamentos da Matemática Aplicada — ICMC/USP São Carlos

---

## Divisão das Partes

| Parte | Apresentador | Tema | Seções do notebook |
|---|---|---|---|
| **I** | Reynaldo | Introdução | Título, Seção 1 (Dataset) |
| **II** | Victor | Metodologia | Seções 2 e 2b (PCA, Espectral, SPE, Interpretação Geométrica) |
| **III** | Eduardo | Resultados | Seções 3–6 (Treino, Detecção, ROC, Visualizações) |
| **IV** | Fábio | Conclusões | Seção 7 (Síntese, Limitações, Trabalhos Futuros) |

---

## Parte I — Introdução · *Reynaldo*

**Objetivo:** Apresentar o problema, o contexto industrial e o dataset.

**Pontos a cobrir:**

1. **Contexto:** plantas industriais geram dados de dezenas de sensores em tempo real. Monitorar manualmente é inviável.
2. **O Processo Tennessee Eastman (TEP):** simulador industrial clássico — 52 variáveis (temperatura, pressão, vazão, composição) e 20 modos de falha catalogados.
3. **O problema:** como detectar automaticamente quando o processo sai do comportamento normal?
4. **Protocolo do dataset:** falha introduzida na amostra 20; amostras 1–20 são pré-falha (normais), 21–500 são pós-falha.

**Mensagem-chave:** o problema é difícil porque as variáveis são altamente correlacionadas e a falha nem sempre é visível em variáveis individuais.

---

## Parte II — Metodologia · *Victor*

**Objetivo:** Explicar como o PCA detecta anomalias usando decomposição espectral.

**Pontos a cobrir:**

1. **PCA como mudança de base:** encontramos uma nova base onde as coordenadas são descorrelacionadas.
2. **Decomposição espectral:** $C = V\Lambda V^T$ — os autovetores definem direções de máxima variância; os autovalores medem quanta variância cada direção captura.
3. **Subespaço de operação normal $\mathcal{S}_k$:** retemos os $k$ primeiros autovetores que explicam fração $\alpha$ da variância.
4. **SPE — Squared Prediction Error:** mede o erro de reconstrução ao projetar no subespaço. Operação normal → SPE pequeno; falha → SPE grande.
5. **Interpretação geométrica:** $C\mathbf{x} = V(\Lambda(V^T\mathbf{x}))$ — projeção → escala → reconstrução. O SPE captura o "resto" que não foi explicado.
6. **Threshold:** calibrado no conjunto de validação (dados normais não usados no treino), percentil 99,99%.

**Mensagem-chave:** a decomposição espectral da covariância dá direções naturais para o processo normal. O que sai dessas direções é anomalia.

---

## Parte III — Resultados · *Eduardo*

**Objetivo:** Mostrar o desempenho do detector nas duas falhas selecionadas.

**Pontos a cobrir:**

1. **Divisão treino/validação/teste:** 1 simulação normal para treino, 3 para calibrar threshold, simulação com falha para teste.
2. **Componentes selecionadas:** 30 de 52 para $\alpha = 90\%$ de variância explicada.
3. **IDV(1) — falha detectável:** SPE ultrapassa o threshold logo após a amostra 20. FDR alta.
4. **IDV(3) — falha difícil:** SPE permanece abaixo do threshold. FDR baixa. Por quê? A falha fica dentro do subespaço normal.
5. **Curva ROC:** AUC varia com $\alpha$. Sensibilidade ao número de componentes.
6. **Visualizações:** séries temporais mostrando a mudança no processo; scatter 2D (PC1 × PC2) mostrando geometricamente a diferença entre IDV(1) e IDV(3); 3D interativo (Plotly).

**Mensagem-chave:** o gráfico PC1 × PC2 é o argumento visual central — mostra por que IDV(1) é detectada (sai da elipse) e IDV(3) não (fica dentro).

---

## Parte IV — Conclusões · *Fábio*

**Objetivo:** Sintetizar os resultados, explicar as limitações e propor extensões.

**Pontos a cobrir:**

1. **Síntese:**
   - IDV(1): alta FDR, detecção rápida após a introdução da falha
   - IDV(3): baixa FDR, limitação conhecida na literatura
2. **Por que o SPE falha para IDV(3)?** A falha se manifesta dentro do subespaço $\mathcal{S}_k$ — o erro de reconstrução é insensível. Essa limitação decorre da natureza **linear** do PCA: $\mathcal{S}_k$ é sempre um hiperplano.
3. **Trabalhos futuros — autoencoders:** Spina et al. (2024) comparam PCA com arquiteturas de autoencoders (AE, VAE, DAE) no mesmo benchmark TEP, com metodologia semelhante (SPE + AUC). Para a Falha 3, o PCA tem o menor AUC (0,718) entre os métodos comparados, enquanto os autoencoders alcançam até 0,763 — evidência de que uma projeção não linear captura parte do que o PCA deixa passar.
4. **Mensagens-chave:**
   - PCA não é só redução de dimensionalidade — é monitoramento estatístico fundamentado em álgebra linear
   - O método é semi-supervisionado: treina apenas com dados normais
   - A limitação do SPE para falhas "internas" ao subespaço motiva extensões não lineares (autoencoders)
   - Baixo custo computacional, alta interpretabilidade

---

## Estrutura Visual Sugerida para os Slides

| Slide(s) | Conteúdo | Apresentador |
|---|---|---|
| 1 | Título, grupo, contexto | Reynaldo |
| 2–3 | O processo TEP — 52 variáveis, modos de falha | Reynaldo |
| 4 | Ideia central: PCA como detector | Reynaldo → Victor |
| 5–6 | Decomposição espectral — $C = V\Lambda V^T$ | Victor |
| 7 | Subespaço normal e SPE | Victor |
| 8 | Interpretação geométrica (projeção → escala → reconstrução) | Victor |
| 9 | Divisão treino/validação/teste, threshold | Eduardo |
| 10 | SPE ao longo do tempo — IDV(1) vs IDV(3) | Eduardo |
| 11 | FDR e FAR — tabela de resultados | Eduardo |
| 12 | Curva ROC — sensibilidade ao número de componentes | Eduardo |
| 13 | Scatter PC1×PC2 — nuvem normal vs. IDV(1) vs. IDV(3) | Eduardo |
| 14 | Síntese e limitação do SPE | Fábio |
| 15 | Trabalhos futuros — autoencoders (Spina et al., 2024) | Fábio |

---

## Sobre os Gráficos

Todos os gráficos são gerados pelo notebook `notebooks/PCA_Fault_Detection_TEP.ipynb`.  
Eduardo fornece as figuras finais para os demais montarem os slides.

Figuras principais:
- `plot_variancia_explicada()` — curva de variância acumulada com corte em 90%
- `plot_distribuicao_SPE()` — distribuição do SPE de validação com threshold
- Subplot SPE log-escala — IDV(1) vs IDV(3)
- Curva ROC — AUC por fração de variância
- Grid 6×3 séries temporais
- Scatter 2D PC1×PC2 — nuvem normal vs. IDV(1) vs. IDV(3)
- Visualização 3D Plotly (interativa, para notebook — exportar como HTML se necessário)
