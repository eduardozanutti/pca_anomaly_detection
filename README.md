# PCA Anomaly Detection — Tennessee Eastman Process

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Versão](https://img.shields.io/badge/versão-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5%2B-F7931E?logo=scikit-learn&logoColor=white)
![Licença](https://img.shields.io/badge/licença-acadêmica-green)

Projeto final da disciplina de **Fundamentos da Matemática Aplicada** — USP.

**Objetivo:** aplicar PCA (Principal Component Analysis) para detectar anomalias em dados multivariados do Processo Tennessee Eastman (TEP), usando apenas dados de operação normal no treino e detectando falhas por estatísticas de monitoramento (SPE e T² de Hotelling).

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
|   |-- raw/
|   |-- preprocessed/
|   |-- processed/
|-- docs/
|   |-- orientacao_apresentacao.md
|-- notebooks/
|   |-- 01_pca_tep_setup.ipynb
|   |-- 02_eda_tennessee_eastman.ipynb
|-- reports/
|-- results/
|   |-- figures/
|-- src/
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

### 1. Baixar dados do Tennessee Eastman

Script utilitário em `src/data/get_data.py`:

```powershell
python src/data/get_data.py
```

Perfis disponíveis:

| Perfil | Conteúdo |
|--------|----------|
| `quick` (padrão) | `mode1_normal_500.xlsx` + falha 1 |
| `eda` | Normal + subconjunto de falhas (fáceis/intermediárias/difíceis) |
| `all` | Todas as 21 falhas × 5 batches (105 cenários) |

Para baixar com conversão simultânea para CSV:

```powershell
python src/data/get_data.py --profile eda --to-csv
```

Arquivos brutos ficam em `data/raw/` e os CSVs convertidos em `data/preprocessed/`.

### 2. Consolidar dados em Parquet

```powershell
python src/data/process_data.py
```

Gera os seguintes arquivos em `data/processed/`:

- `normal_operation_50_hours.parquet`
- `normal_operation_500_hours.parquet`
- `abnormal_operation_50_hours.parquet`

Metadados incluídos: `type_fault`, `n_type_fault`, `batch_number`, `batch_name`.

Para validar que todas as 105 simulações de falha estão presentes:

```powershell
python src/data/process_data.py --strict
```

### 3. Treinar o detector PCA

```powershell
python src/scripts/train_pca.py \
  --train data/preprocessed/mode1_normal_500.csv \
  --model-out data/processed/pca_model.joblib \
  --n-components 0.95 \
  --alpha 0.99 \
  --header infer
```

### 4. Detectar anomalias

```powershell
python src/scripts/detect_anomalies.py \
  --model data/processed/pca_model.joblib \
  --input data/preprocessed/faults/mode1_1_1.csv \
  --output data/processed/mode1_1_1_scores.csv \
  --header infer
```

### Opções de formato (TEP)

| Flag | Descrição |
|------|-----------|
| `--sep` | Separador de colunas (detecta automaticamente se omitido) |
| `--header` | `none` para arquivos sem cabeçalho (TEP bruto) ou `infer` para CSV com cabeçalho |
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

- [ ] Completar notebook de treinamento e avaliação (`notebooks/01_pca_tep_setup.ipynb`)
- [ ] Adicionar avaliação por taxa de detecção, falso alarme e atraso de detecção
- [ ] Comparar diferentes valores de `n_components` e `alpha`
- [ ] Gerar e salvar figuras finais em `results/figures/`
- [ ] Implementar testes unitários em `tests/`
