# Detecção de Anomalias via PCA — Tennessee Eastman Process

![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)

Projeto final da disciplina **Fundamentos da Matemática Aplicada** — ICMC/USP São Carlos.

**Objetivo:** Demonstrar a aplicação de PCA para detecção de anomalias em dados multivariados do Processo Tennessee Eastman (TEP), usando a decomposição espectral da matriz de covariância como fundamento matemático.

**Dataset:** Rieth, Amsel, Tran & Cook (2017), Harvard Dataverse — doi:[10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1)

---

## Grupo

| Nome | nº USP | Papel na Apresentação |
|---|---|---|
| Reynaldo Pereira Martins | 13490412 | Parte I — Introdução |
| Victor Zoratti Ferreira | 08006115 | Parte II — Metodologia |
| Eduardo Soares Zanutti | 10413611 | Parte III — Resultados |
| Fábio Luiz Souza Alves | 15084023 | Parte IV — Conclusões |

---

## Estrutura do Repositório

```
pca_anomaly_detection/
├── data/
│   ├── raw/              # .RData baixados (não versionados — ver ETL)
│   └── processed/        # .feather gerados (não versionados — ver ETL)
├── docs/
│   └── orientacao_apresentacao.md
├── notebooks/
│   └── PCA_Fault_Detection_TEP.ipynb   # análise principal
├── references/                          # PDFs e references.bib
├── src/
│   └── data/
│       ├── get_data.py      # download dos .RData do Harvard Dataverse
│       └── process_data.py  # converte .RData → .feather
├── config.yaml              # mapeamento de colunas e descrições de falhas
├── main.py                  # CLI — monitor de anomalias em tempo real
├── pyproject.toml
└── requirements.txt
```

---

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Pipeline ETL

Os dados brutos não estão versionados (~5 GB). Para gerá-los:

### 1. Download dos dados brutos

```powershell
python src/data/get_data.py --split train
```

Baixa `TEP_FaultFree_Training.RData` e `TEP_Faulty_Training.RData` para `data/raw/`.

| Flag | Opções | Descrição |
|---|---|---|
| `--split` | `train`, `test`, `all` | Quais splits baixar |

### 2. Conversão `.RData` → `.feather`

Execute um arquivo por vez (limita o pico de memória a um único DataFrame):

```powershell
python src/data/process_data.py --file TEP_FaultFree_Training.RData
python src/data/process_data.py --file TEP_Faulty_Training.RData
```

Saída em `data/processed/`. Os `.RData` são deletados automaticamente após a conversão (use `--keep-raw` para manter).

---

## Notebook Principal

```
notebooks/PCA_Fault_Detection_TEP.ipynb
```

Estruturado em 4 partes correspondentes à divisão da apresentação:

| Parte | Apresentador | Conteúdo |
|---|---|---|
| I — Introdução | Reynaldo | Dataset TEP — 52 variáveis, 21 condições, protocolo de falha |
| II — Metodologia | Victor | Decomposição espectral $C = V\Lambda V^T$, SPE, interpretação geométrica |
| III — Resultados | Eduardo | Treino/validação, IDV(1) vs IDV(3), curva ROC, visualizações 2D/3D |
| IV — Conclusões | Fábio | Síntese, limitações do SPE, trabalhos futuros com autoencoders |

---

## Monitor em Tempo Real (CLI)

`main.py` simula o monitoramento amostra a amostra de uma simulação do TEP:

```powershell
python -X utf8 main.py                    # IDV(1) — falha detectável
python -X utf8 main.py --fault 3          # IDV(3) — falha difícil de detectar
python -X utf8 main.py --fault 0          # operação normal (sem falha)
python -X utf8 main.py --fault 1 --fast   # sem delay de animação
python -X utf8 main.py --fault 1 --sim 2  # simulação 2
```

| Argumento | Padrão | Descrição |
|---|---|---|
| `--fault` | `1` | Número da falha IDV (0 = normal, 1–20 = falha) |
| `--sim` | `1` | Número da simulação |
| `--variance` | `0.9` | Fração de variância explicada pelo PCA |
| `--delay` | `0.04` | Delay em segundos entre amostras (0 = instantâneo) |
| `--fast` | — | Atalho para `--delay 0` |

> **Nota:** use `python -X utf8` no Windows para suporte correto a Unicode no terminal.

---

## Referências

- Downs, J.J. & Vogel, E.F. (1993). A plant-wide industrial process control problem. *Computers & Chemical Engineering*, 17(3), 245–255.
- Rieth, C.A., Amsel, B.D., Tran, R. & Cook, M.B. (2017). Additional Tennessee Eastman Process Simulation Data for Anomaly Detection Evaluation. Harvard Dataverse. doi:10.7910/DVN/6C3JR1
- Spina, D.E., Campos, L.F.O., Arruda, W.F., Melo, A., Alves, M.F.S., Rabello, G.L., Anzai, T.K. & Pinto, J.C. (2024). Comparison of autoencoder architectures for fault detection in industrial processes. *Digital Chemical Engineering*, 12, 100162. doi:10.1016/j.dche.2024.100162
- Nonato, L.G. — Material da disciplina: Autovalores, Autovetores e PCA. ICMC/USP São Carlos.
