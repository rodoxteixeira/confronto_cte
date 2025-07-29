import pandas as pd

def aplicar_filtros(df: pd.DataFrame, excluir_mg: bool, excluir_ufini_fora_mg: bool) -> pd.DataFrame:
    """
    Aplica filtros no DataFrame conforme checkboxes marcados pelo usuário.
    - excluir_mg: Remove linhas onde 'UF Emitente' == 'MG'
    - excluir_ufini_fora_mg: Mantém apenas linhas onde 'UF de Início (UFIni)' == 'MG'
    """
    df_filtrado = df.copy()

    # Filtrar UF Emitente != MG
    if excluir_mg and 'UF Emitente' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['UF Emitente'] != 'MG']

    # Filtrar UFIni == MG
    if excluir_ufini_fora_mg and 'UF de Início (UFIni)' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['UF de Início (UFIni)'] == 'MG']

    return df_filtrado.reset_index(drop=True)
