import pandas as pd

# Dicionário de alíquotas de imposto por UF
aliquotas = {
    'RO': 0.07, 'AC': 0.07, 'AM': 0.07, 'RR': 0.07, 'PA': 0.07,
    'AP': 0.07, 'TO': 0.07, 'MA': 0.07, 'PI': 0.07, 'CE': 0.07,
    'RN': 0.07, 'PB': 0.07, 'PE': 0.07, 'AL': 0.07, 'SE': 0.07,
    'BA': 0.07, 'MG': 0.18, 'ES': 0.07, 'RJ': 0.12, 'SP': 0.12,
    'PR': 0.12, 'SC': 0.12, 'RS': 0.12, 'MS': 0.07, 'MT': 0.07,
    'GO': 0.07, 'DF': 0.07
}

def aplicar_filtros(df, excluir_mg, excluir_ufini_fora_mg):
    """
    Aplica os filtros selecionados pelo usuário ao DataFrame.
    """
    if excluir_mg and "UF Emitente" in df.columns:
        df = df[df['UF Emitente'] != 'MG']
    if excluir_ufini_fora_mg and "UF de Início (UFIni)" in df.columns:
        df = df[df['UF de Início (UFIni)'] == 'MG']
    return df

def calcular_imposto_row(row):
    """
    Calcula o imposto linha a linha, conforme regras de UF e vPrest.
    """
    try:
        vprest = float(row.get("vPrest", 0))
        uf_ini = row.get("UF de Início (UFIni)", "")
        uf_emitente = row.get("UF Emitente", "")
        if uf_emitente != "MG" and uf_ini == "MG":
            aliquota_mg = aliquotas.get("MG", 0)
            return round(vprest * aliquota_mg, 2)
        return 0
    except Exception:
        return 0

def aplicar_calculo_imposto(df):
    """
    Adiciona a coluna 'ICMS Calculado' ao DataFrame.
    """
    if "vPrest" in df.columns and "UF de Início (UFIni)" in df.columns and "UF Emitente" in df.columns:
        df["ICMS Calculado"] = df.apply(calcular_imposto_row, axis=1)
    return df
