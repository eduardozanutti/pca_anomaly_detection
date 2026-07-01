#!/usr/bin/env python
"""
PCA Anomaly Detector — Tennessee Eastman Process
Simula monitoramento de processo industrial em tempo real.

Uso:
    python main.py                   # IDV(1) — falha detectável
    python main.py --fault 3         # IDV(3) — falha difícil de detectar
    python main.py --fault 0         # operação normal (sem falha)
    python main.py --fault 1 --fast  # sem delay de animação
"""

import argparse
import time
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA

ROOT = Path(__file__).parent

# ── Cores ANSI ───────────────────────────────────────────────────────────────

VERDE   = '\033[92m'
AMARELO = '\033[93m'
VERMELHO = '\033[91m'
NEGRITO = '\033[1m'
CINZA   = '\033[90m'
RESET   = '\033[0m'

# ── Detector PCA ─────────────────────────────────────────────────────────────

class PCAAnomalyDetector:
    """
    Detecta anomalias via Squared Prediction Error (SPE) do PCA.
    Treina apenas em dados normais (one-class). O threshold é calibrado
    em dados de validação não vistos no treino.
    """

    def __init__(self, fracao_variancia: float = 0.9):
        self.fracao_variancia = fracao_variancia
        self._pca = PCA()

    def fit(self, X: pd.DataFrame) -> None:
        self.mu_  = X.mean()
        self.std_ = X.std()
        Xs = self._normalizar(X)
        self._pca.fit(Xs)
        var_acum = np.cumsum(self._pca.explained_variance_ratio_)
        self.n_componentes_ = int(np.argmax(var_acum >= self.fracao_variancia) + 1)

    def calibrar_threshold(self, X_val: pd.DataFrame, percentil: float = 99.99) -> float:
        spe_val = self._calcular_spe(self._normalizar(X_val))
        self.threshold_ = float(np.percentile(spe_val, percentil))
        self.percentil_  = percentil
        return self.threshold_

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self._calcular_spe(self._normalizar(X))

    def _normalizar(self, X: pd.DataFrame) -> np.ndarray:
        return ((X - self.mu_) / self.std_).values

    def _calcular_spe(self, X: np.ndarray) -> np.ndarray:
        T = self._pca.transform(X)
        T[:, self.n_componentes_:] = 0
        X_rec = self._pca.inverse_transform(T)
        spe = np.sum((X - X_rec) ** 2, axis=1)
        spe[spe < 1e-10] = 0.0
        return spe

# ── Carregamento de dados ────────────────────────────────────────────────────

def carregar_dados() -> pd.DataFrame:
    normal = pd.read_feather(ROOT / 'data/processed/TEP_FaultFree_Training.feather')
    faulty = pd.read_feather(ROOT / 'data/processed/TEP_Faulty_Training.feather')
    return pd.concat([normal, faulty], ignore_index=True)

# ── Visualização no terminal ─────────────────────────────────────────────────

def linha_status(amostra: int, spe: float, threshold: float, pos_falha: bool) -> str:
    ratio = spe / threshold if threshold > 0 else 0.0
    BAR_W = 25

    if not pos_falha:
        icone = f"{CINZA}○{RESET}"
        cor_spe = CINZA
    elif ratio >= 1.0:
        icone = f"{VERMELHO}⚠{RESET}"
        cor_spe = VERMELHO
    else:
        icone = f"{VERDE}✓{RESET}"
        cor_spe = VERDE

    preenchido = min(int(ratio * BAR_W), BAR_W)
    cor_bar = VERMELHO if ratio >= 1.0 else VERDE
    barra = cor_bar + '█' * preenchido + RESET + '░' * (BAR_W - preenchido)

    status = f"{NEGRITO}{VERMELHO}ANOMALIA{RESET}" if ratio >= 1.0 and pos_falha else "normal  "
    return (
        f"  {icone} amostra {amostra:03d} | "
        f"SPE {cor_spe}{spe:8.3f}{RESET} | "
        f"[{barra}] {ratio:4.1f}x | {status}"
    )

def barra_spe(spe_series: np.ndarray, threshold: float, fault_at: int) -> None:
    print(f"\n  {NEGRITO}SPE ao longo do tempo:{RESET}")
    altura = 8
    n = len(spe_series)
    largura = min(n, 80)
    indices = np.linspace(0, n - 1, largura, dtype=int)
    valores = spe_series[indices]
    vmax = max(valores.max(), threshold) * 1.1

    for row in range(altura, 0, -1):
        linha = "  "
        limite = (row / altura) * vmax
        for idx, (i, v) in enumerate(zip(indices, valores)):
            if v >= limite:
                cor = VERMELHO if i >= fault_at and v > threshold else (AMARELO if i >= fault_at else VERDE)
                linha += cor + '█' + RESET
            else:
                linha += ' '
        if abs(limite - threshold) < vmax / altura:
            linha += f"  ← threshold ({threshold:.2f})"
        print(linha)

    ruler = "  " + "".join(
        str((i // 10) % 10) if i % 10 == 0 else " " for i in range(largura)
    )
    print(ruler)
    print(f"  {CINZA}0{' '*(fault_at * largura // n - 1)}↑ falha introduzida (amostra {fault_at}){RESET}")

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='PCA Anomaly Detector — Tennessee Eastman Process',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""exemplos:
  python main.py                   # IDV(1), detectável
  python main.py --fault 3         # IDV(3), difícil de detectar
  python main.py --fault 0         # operação normal (sem falha)
  python main.py --fault 1 --fast  # sem animação"""
    )
    parser.add_argument('--fault',    type=int,   default=1,    help='Número da falha IDV (0=normal, 1-20=falha)')
    parser.add_argument('--sim',      type=int,   default=1,    help='Número da simulação (padrão: 1)')
    parser.add_argument('--variance', type=float, default=0.9,  help='Fração de variância explicada (padrão: 0.9)')
    parser.add_argument('--delay',    type=float, default=0.04, help='Delay entre amostras em segundos (padrão: 0.04)')
    parser.add_argument('--fast',     action='store_true',      help='Sem delay (modo rápido)')
    args = parser.parse_args()

    delay = 0.0 if args.fast else args.delay
    fault_label = f"IDV({args.fault})" if args.fault > 0 else "Operação Normal (sem falha)"

    print(f"\n{NEGRITO}{'═'*62}{RESET}")
    print(f"{NEGRITO}  PCA Anomaly Detector — Tennessee Eastman Process{RESET}")
    print(f"{NEGRITO}{'═'*62}{RESET}")

    # ── Fase 1: Carregamento ─────────────────────────────────────────────────
    print(f"\n  {NEGRITO}[1/3] Carregando dados...{RESET}")
    df = carregar_dados()
    print(f"       {df.shape[0]:,} amostras | {df['faultNumber'].nunique()} condições operacionais")

    # ── Fase 2: Treino e calibração ──────────────────────────────────────────
    print(f"\n  {NEGRITO}[2/3] Treinando modelo PCA (variância alvo: {args.variance*100:.0f}%)...{RESET}")
    df_train = df[(df['faultNumber'] == 0) & (df['simulationRun'] == 1)].iloc[:, 3:]
    df_val   = df[(df['faultNumber'] == 0) & (df['simulationRun'].between(2, 4))].iloc[:, 3:]

    detector = PCAAnomalyDetector(fracao_variancia=args.variance)
    detector.fit(df_train)
    threshold = detector.calibrar_threshold(df_val, percentil=99.99)

    print(f"       Componentes selecionadas : {NEGRITO}{detector.n_componentes_}{RESET} de {df_train.shape[1]}")
    print(f"       Threshold SPE (99.99% val): {NEGRITO}{threshold:.4f}{RESET}")

    # ── Fase 3: Monitoramento ────────────────────────────────────────────────
    print(f"\n  {NEGRITO}[3/3] Monitorando: {fault_label} | Simulação {args.sim}{RESET}")
    if args.fault > 0:
        print(f"       {AMARELO}Falha será introduzida na amostra 20{RESET}")
    print(f"\n  {'─'*62}")

    df_test = df[(df['faultNumber'] == args.fault) & (df['simulationRun'] == args.sim)].iloc[:, 3:]
    if df_test.empty:
        print(f"  {VERMELHO}Erro: sem dados para fault={args.fault}, sim={args.sim}{RESET}")
        sys.exit(1)

    spe_series = detector.predict(df_test)
    primeira_deteccao = None
    n_anomalias = 0
    FAULT_AT = 20 if args.fault > 0 else len(spe_series)

    for i, spe in enumerate(spe_series):
        pos_falha = (i >= FAULT_AT) and (args.fault > 0)

        if i == FAULT_AT and args.fault > 0:
            print(f"\n  {NEGRITO}{AMARELO}  ▶ Falha introduzida (amostra {FAULT_AT}){RESET}\n")

        if pos_falha and spe > threshold:
            n_anomalias += 1
            if primeira_deteccao is None:
                primeira_deteccao = i + 1

        print(linha_status(i + 1, spe, threshold, pos_falha))
        time.sleep(delay)

    # ── Sumário ──────────────────────────────────────────────────────────────
    n_pos = max(len(spe_series) - FAULT_AT, 1) if args.fault > 0 else 1
    fdr = n_anomalias / n_pos if args.fault > 0 else 0.0
    far = float(np.mean(spe_series[:FAULT_AT] > threshold))

    barra_spe(spe_series, threshold, FAULT_AT)

    print(f"\n  {'═'*62}")
    print(f"\n  {NEGRITO}RESULTADO — {fault_label}{RESET}\n")
    print(f"    Componentes PCA         : {detector.n_componentes_}")
    print(f"    Threshold SPE           : {threshold:.4f}")

    if args.fault > 0:
        fdr_cor = VERDE if fdr > 0.5 else VERMELHO
        print(f"    Taxa de Detecção (FDR)  : {fdr_cor}{NEGRITO}{100*fdr:5.1f}%{RESET}  ({n_anomalias}/{n_pos} amostras pós-falha)")
        if primeira_deteccao:
            atraso = primeira_deteccao - FAULT_AT
            print(f"    Primeira detecção       : amostra {primeira_deteccao}  ({NEGRITO}+{atraso} amostras após a falha{RESET})")
        else:
            print(f"    Primeira detecção       : {VERMELHO}não detectado{RESET}")

    print(f"    Taxa de Falso Alarme    : {100*far:5.1f}%\n")

    if args.fault > 0:
        if fdr > 0.5:
            print(f"  {VERDE}{NEGRITO}✓  Falha detectada com sucesso pelo SPE.{RESET}\n")
        else:
            print(f"  {AMARELO}{NEGRITO}⚠  Baixa taxa de detecção — limitação do método SPE para {fault_label}.{RESET}")
            print(f"  {CINZA}   A falha não gera resíduo significativo fora do subespaço principal.{RESET}\n")


if __name__ == '__main__':
    main()
