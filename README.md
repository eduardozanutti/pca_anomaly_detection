# PCA Anomaly Detection — Tennessee Eastman Process

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Versão](https://img.shields.io/badge/versão-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5%2B-F7931E?logo=scikit-learn&logoColor=white)
![Licença](https://img.shields.io/badge/licença-acadêmica-green)

Projeto final da disciplina de **Fundamentos da Matemática Aplicada** — USP.

**Objetivo:** aplicar PCA (Principal Component Analysis) para detectar anomalias em dados multivariados do Processo Tennessee Eastman (TEP), usando apenas dados de operação normal no treino e detectando falhas por estatísticas de monitoramento (SPE e T² de Hotelling).

**Dataset:** Rieth, Amsel, Tran & Cook (2017), Harvard Dataverse, doi:[10.7910/DVN/6C3JR1](https://doi.org/10.7910/DVN/6C3JR1) — extensão do TEP clássico (Downs & Vogel, 1993) com simulações de operação normal e das 20 falhas (IDV 1-20) para treino e teste.

---

## Grupo

| Nº USP | Nome |
|--------|------|
| 15084023 | Fábio Luiz Souza Alves |
| 10413611 | Eduardo Soares Zanutti |
| 13490412 | Reynaldo Pereira Martins |
| —        | Victor Zoratti Ferreira |

---

## Estrutura do Repositório

```text
pca_anomaly_detection/
|-- data/
|   |-- raw/            # TEP_*.RData baixados (Harvard Dataverse)
|   |-- preprocessed/   # TEP_*.feather (conversão 1:1 de cada .RData)
|   |-- processed/      # TEP_Training.feather / TEP_Testing.feather (consolidados)
|-- docs/
|   |-- orientacao_apresentacao.md
|-- notebooks/
|   |-- PCA_anomaly_detection_TEP.ipynb
|   |-- 01_pca_tep_setup.ipynb
|   |-- 02_eda_tennessee_eastman.ipynb
|-- reports/
|-- results/
|   |-- figures/
|-- src/
|   |-- data/
|   |   |-- get_data.py        # download dos .RData
|   |   |-- process_data.py    # .RData -> .feather (1 arquivo por processo)
|   |   |-- build_processed.py # concat + column_name_map + fault_description
|   |-- pca_anomaly_detection/
|   |   |-- data/
|   |   |-- evaluation/
|   |   |-- models/
|   |   |-- config.py
|   |-- scripts/
|       |-- train_pca.py
|       |-- detect_anomalies.py
|-- tests/
|-- config.yaml
|-- requirements.txt
|-- pyproject.toml
```

---

## Setup Rápido

1. Criar ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
pip install -e .
```

---

## Pipeline

### 1. Baixar os dados brutos (`.RData`)

Script em `src/data/get_data.py` baixa os arquivos originais do Harvard Dataverse:

```powershell
python src/data/get_data.py --split all
```

| Split | Arquivos |
|-------|----------|
| `train` | `TEP_FaultFree_Training.RData`, `TEP_Faulty_Training.RData` |
| `test` | `TEP_FaultFree_Testing.RData`, `TEP_Faulty_Testing.RData` |
| `all` (padrão) | os 4 acima |

Arquivos ficam em `data/raw/`.

### 2. Converter `.RData` para `.feather`

`src/data/process_data.py` converte **um arquivo por execução**, para manter o pico de memória limitado a um único DataFrame (rode cada chamada como um processo separado):

```powershell
python src/data/process_data.py --file TEP_FaultFree_Training.RData
python src/data/process_data.py --file TEP_Faulty_Training.RData
python src/data/process_data.py --file TEP_FaultFree_Testing.RData
python src/data/process_data.py --file TEP_Faulty_Testing.RData
```

Saída em `data/preprocessed/`.

### 3. Consolidar em treino/teste

```powershell
python src/data/build_processed.py --split train
python src/data/build_processed.py --split test
```

Concatena FaultFree + Faulty de cada split (via Arrow, sem duplicar os DataFrames em memória — ver `build_split` em `build_processed.py`), renomeia `xmeas_*`/`xmv_*` para nomes legíveis usando `column_name_map` (`config.yaml`) e adiciona a coluna `fault_description` (derivada de `faultNumber`, ex.: `0` → `normal_operation`, `6` → `a_feed_loss_stream_1`). Gera:

| Arquivo | Linhas × Colunas |
|---------|-------------------|
| `data/processed/TEP_Training.feather` | 5.250.000 × 56 |
| `data/processed/TEP_Testing.feather` | 10.080.000 × 56 |

### 4. Treinar o detector PCA / 5. Detectar anomalias

`src/scripts/train_pca.py` e `src/scripts/detect_anomalies.py` ainda esperam um CSV genérico via `pca_anomaly_detection.data.io.load_tabular` e **não foram atualizados** para ler diretamente os `.feather` consolidados do passo 3 — ver [Próximos Passos](#próximos-passos).

```powershell
python src/scripts/train_pca.py \
  --train <arquivo_csv> \
  --model-out data/processed/pca_model.joblib \
  --n-components 0.95 \
  --alpha 0.99 \
  --header infer

python src/scripts/detect_anomalies.py \
  --model data/processed/pca_model.joblib \
  --input <arquivo_csv> \
  --output data/processed/scores.csv \
  --header infer
```

| Flag | Descrição |
|------|-----------|
| `--sep` | Separador de colunas (detecta automaticamente se omitido) |
| `--header` | `none` para arquivos sem cabeçalho ou `infer` para CSV com cabeçalho |
| `--start-col` / `--end-col` | Recorte do bloco de variáveis de processo |
| `--drop-col` | Remove coluna por índice (ex.: coluna de rótulo de falha) |

---

## Métricas de Anomalia

O detector calcula os seguintes índices por amostra:

| Coluna | Descrição |
|--------|-----------|
| `spe` | Erro de reconstrução no espaço residual (Squared Prediction Error) |
| `t2` | Distância de Hotelling no espaço principal |
| `is_anomaly_spe` | `True` se SPE excede o limiar de confiança |
| `is_anomaly_t2` | `True` se T² excede o limiar de confiança |
| `is_anomaly_combined` | `True` se SPE **ou** T² excedem o limiar |

Limiares calculados nos dados de treino com nível de confiança padrão de 99%.

---

## Próximos Passos

- [ ] Atualizar `train_pca.py` e `detect_anomalies.py` para ler `TEP_Training.feather` / `TEP_Testing.feather` diretamente, em vez de CSV genérico
- [ ] Atualizar `notebooks/02_eda_tennessee_eastman.ipynb` (ainda referencia o dataset mode1 removido)
- [ ] Completar notebook de treinamento e avaliação (`notebooks/01_pca_tep_setup.ipynb` / `PCA_anomaly_detection_TEP.ipynb`)
- [ ] Adicionar avaliação por taxa de detecção, falso alarme e atraso de detecção
- [ ] Comparar diferentes valores de `n_components` e `alpha`
- [ ] Gerar e salvar figuras finais em `results/figures/`
- [ ] Implementar testes unitários em `tests/`
