# Detecção de Anomalias em Processos Industriais via Análise de Componentes Principais: uma Aplicação ao Processo Tennessee Eastman

**Reynaldo Pereira Martins¹, Victor Zoratti Ferreira¹, Eduardo Soares Zanutti¹, Fábio Luiz Souza Alves¹**

¹ Instituto de Ciências Matemáticas e de Computação — Universidade de São Paulo (ICMC/USP), São Carlos, SP, Brasil.

`{13490412, 08006115, 10413611, 15084023}@usp.br`

---

## Resumo

Este trabalho apresenta a aplicação de Análise de Componentes Principais (PCA) para detecção de anomalias em processos industriais multivariados, explorando a decomposição espectral da matriz de covariância como fundamento matemático. O método é avaliado no dataset Tennessee Eastman Process (TEP), benchmark clássico da literatura de monitoramento de processos, com 52 variáveis de processo e 20 modos de falha catalogados. O detector é treinado exclusivamente em dados de operação normal e utiliza o índice Squared Prediction Error (SPE) como estatística de monitoramento, com limiar calibrado em conjunto de validação independente. Os experimentos demonstram alta taxa de detecção para falhas que se manifestam fora do subespaço principal (IDV(1), FDR > 95%) e ilustram geometricamente a limitação do SPE para falhas que permanecem dentro do subespaço (IDV(3), FDR < 5%), motivando o uso complementar do índice T² de Hotelling.

---

## 1. Introdução

Processos industriais modernos operam com dezenas a centenas de sensores, gerando séries temporais multivariadas de alta dimensionalidade. Identificar manualmente quando o processo sai do comportamento normal é inviável na escala de dados industriais, tornando os métodos automáticos de detecção de anomalias essenciais para a segurança operacional e a qualidade de produto.

O **Monitoramento Estatístico de Processos** (Statistical Process Control — SPC) baseado em PCA constitui uma abordagem clássica e amplamente adotada na indústria química e petroquímica [1]. A ideia central é aprender, a partir de dados históricos, uma representação comprimida do comportamento normal do processo. Novas observações que não se encaixam nessa representação são sinalizadas como anômalas.

O **Processo Tennessee Eastman** (TEP) [2] é o simulador industrial mais utilizado como benchmark na literatura de monitoramento de processos. Ele modela uma planta química real com reações, separação e reciclo, gerando 52 variáveis de processo (temperatura, pressão, vazão, composição) sob 20 condições de falha distintas. O dataset de Rieth et al. [3] estende o TEP original com 500 simulações por condição, totalizando 5.250.000 observações de treino.

---

## 2. Fundamentação Matemática

### 2.1 Decomposição Espectral e PCA

Seja $X \in \mathbb{R}^{n \times p}$ a matriz de dados normalizados com zero médio e desvio unitário. A matriz de covariância amostral $C = \frac{1}{n-1}X^TX$ é simétrica e semi-definida positiva; pelo **Teorema Espectral**, admite decomposição única:

$$C = V \Lambda V^T$$

onde $V = [v_1, \ldots, v_p] \in \mathbb{R}^{p \times p}$ é a matriz ortonormal de **autovetores** (componentes principais) e $\Lambda = \mathrm{diag}(\lambda_1, \ldots, \lambda_p)$ a matriz diagonal de **autovalores**, com $\lambda_1 \geq \cdots \geq \lambda_p \geq 0$.

A transformação $C\mathbf{x} = V(\Lambda(V^T\mathbf{x}))$ se decompõe em três operações: (1) **projeção** de $\mathbf{x}$ na base dos autovetores; (2) **escala** de cada coordenada pelo autovalor correspondente; (3) **reconstrução** no espaço original. Os autovalores correspondem às variâncias das coordenadas na nova base, e os autovetores definem as direções de máxima variância dos dados.

### 2.2 Subespaço de Operação Normal

Retendo os $k$ maiores autovetores $V_k = [v_1, \ldots, v_k]$ tal que

$$\frac{\sum_{i=1}^{k} \lambda_i}{\sum_{i=1}^{p} \lambda_i} \geq \alpha,$$

define-se o **subespaço de operação normal** $\mathcal{S}_k = \mathrm{span}(V_k)$. O parâmetro $\alpha \in (0, 1]$ controla a capacidade do modelo: valores menores produzem subespaços mais compactos e detectores mais sensíveis a desvios gerais; valores maiores retêm mais variabilidade normal.

### 2.3 Squared Prediction Error (SPE)

Para uma nova observação $\mathbf{x} \in \mathbb{R}^p$, o **SPE** mede o erro de reconstrução ao projetar no subespaço principal:

$$\mathrm{SPE}(\mathbf{x}) = \|\mathbf{x} - \hat{\mathbf{x}}\|^2, \quad \hat{\mathbf{x}} = V_k V_k^T \mathbf{x}.$$

Geometricamente, o SPE é a distância quadrada de $\mathbf{x}$ ao subespaço $\mathcal{S}_k$. A regra de decisão é:

$$\begin{cases} \mathrm{SPE}(\mathbf{x}) \leq \delta^2 & \Rightarrow \text{operação normal,} \\ \mathrm{SPE}(\mathbf{x}) > \delta^2 & \Rightarrow \text{anomalia detectada.} \end{cases}$$

O limiar $\delta^2$ é o percentil 99,99% da distribuição do SPE em dados de validação independentes (operação normal não utilizada no treino), evitando o viés de estimativa nos próprios dados de ajuste.

---

## 3. Metodologia Experimental

### 3.1 Dados e Pré-processamento

Utilizamos o subconjunto de treino do dataset TEP de Rieth et al. [3], restringindo a análise às primeiras 10 simulações de cada condição operacional (105.000 observações). As 52 variáveis de processo são padronizadas com média e desvio calculados no conjunto de treino.

A divisão adotada é:

| Conjunto | Condição | Simulações | Finalidade |
|---|---|---|---|
| Treino | Normal (`faultNumber = 0`) | 1 | Estimação de $V$ e $\Lambda$ via PCA |
| Validação | Normal (`faultNumber = 0`) | 2–4 | Calibração do limiar $\delta^2$ |
| Teste | Falha IDV(1) e IDV(3) | 1 | Avaliação da detecção |

A introdução da falha ocorre na amostra 20 de cada simulação de teste. As amostras 1–20 são pré-falha (normais) e as amostras 21–500 são pós-falha.

### 3.2 Falhas Analisadas

Selecionamos duas falhas com comportamentos contrastantes:

- **IDV(1):** variação em degrau na razão de alimentação A/C (corrente 4). Espera-se alta taxa de detecção, pois a falha altera variáveis de processo que residem fora do subespaço normal.
- **IDV(3):** variação em degrau na temperatura de alimentação D (corrente 2). Falha de difícil detecção reportada na literatura: seu efeito projeta-se majoritariamente dentro de $\mathcal{S}_k$.

### 3.3 Métricas

- **FDR** (Fault Detection Rate): fração das amostras pós-falha corretamente sinalizadas.
- **FAR** (False Alarm Rate): fração das amostras pré-falha erroneamente sinalizadas.
- **AUC** (Área sob a curva ROC): capacidade discriminativa do score SPE bruto, avaliada varrendo todas as 20 falhas do dataset.

---

## 4. Resultados

### 4.1 Ajuste do Modelo

Com $\alpha = 0{,}90$, o PCA seleciona $k = 30$ componentes principais (de 52) para explicar 90% da variância de operação normal. O limiar SPE calibrado na validação é $\delta^2 = 25{,}45$.

### 4.2 Detecção por SPE

| Falha | Descrição | FDR | FAR |
|---|---|---|---|
| **IDV(1)** | Variação degrau razão A/C | **> 95%** | < 1% |
| **IDV(3)** | Variação degrau temp. alim. D | **< 5%** | < 1% |

Para IDV(1), o SPE ultrapassa o limiar consistentemente nas primeiras amostras pós-falha, demonstrando detecção rápida e confiável. Para IDV(3), o SPE permanece abaixo do limiar durante praticamente toda a janela pós-falha.

### 4.3 Interpretação Geométrica

A projeção das trajetórias no espaço PC1 × PC2 revela a causa geométrica da diferença:

- **IDV(1):** os pontos pós-falha deslocam-se para fora da elipse de controle T² (que delimita a região normal com 99% de confiança), gerando alto SPE.
- **IDV(3):** os pontos pós-falha permanecem dentro da elipse, indicando que a falha se manifesta inteiramente dentro do subespaço $\mathcal{S}_k$ — o SPE é estruturalmente insensível a esse tipo de desvio.

A elipse de controle decorre do Teorema Espectral: a equação $\mathbf{y}^T \Lambda_k^{-1} \mathbf{y} = \chi^2_{0{,}99}(k)$ define um elipsoide cujos eixos são os autovetores $v_i$ e cujos comprimentos são $\sqrt{\chi^2_{0,99}(k) \cdot \lambda_i}$.

### 4.4 Análise de Sensibilidade — Curva ROC

A variação de $\alpha \in \{0{,}1; 0{,}2; \ldots; 0{,}9\}$ mostra que a AUC sobre as 20 falhas é relativamente estável para $\alpha \geq 0{,}3$, com leve queda para valores muito baixos (modelos com poucas componentes perdem sensibilidade a falhas mais sutis). Para $\alpha = 0{,}9$, a AUC é de aproximadamente 0,80, refletindo o conjunto heterogêneo de falhas — algumas difíceis de detectar por qualquer método baseado apenas no SPE.

---

## 5. Limitações e Extensão com T² de Hotelling

O SPE captura apenas desvios **fora** do subespaço principal. Falhas que produzem deslocamentos **dentro** de $\mathcal{S}_k$ — como IDV(3) — requerem o índice complementar **T² de Hotelling**:

$$T^2(\mathbf{x}) = \mathbf{x}^T V_k \Lambda_k^{-1} V_k^T \mathbf{x}.$$

O T² mede a distância de Mahalanobis no espaço comprimido, sendo sensível a desvios da média dentro do subespaço. A combinação SPE + T² cobre os dois tipos fundamentais de anomalia e é o padrão adotado na literatura de Monitoramento Estatístico de Processos [1].

---

## 6. Conclusão

Demonstramos que o PCA fundamentado na decomposição espectral da matriz de covariância é uma ferramenta eficaz e interpretável para detecção de anomalias em processos industriais. A aplicação ao TEP evidencia tanto a capacidade do método (IDV(1): FDR > 95%) quanto sua limitação estrutural (IDV(3): FDR < 5%), explicada geometricamente pela projeção no espaço de componentes principais. O desenvolvimento de um monitor em tempo real — implementado como aplicação de linha de comando com saída ANSI — ilustra a viabilidade prática da abordagem.

---

## Referências

[1] Qin, S.J. (2003). Statistical process monitoring: basics and beyond. *Journal of Chemometrics*, 17(8–9), 480–502.

[2] Downs, J.J. & Vogel, E.F. (1993). A plant-wide industrial process control problem. *Computers & Chemical Engineering*, 17(3), 245–255.

[3] Rieth, C.A., Amsel, B.D., Tran, R. & Cook, M.B. (2017). Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation. Harvard Dataverse. doi:10.7910/DVN/6C3JR1

[4] Nonato, L.G. — Material da disciplina: Autovalores, Autovetores e PCA. ICMC/USP São Carlos, 2025.
