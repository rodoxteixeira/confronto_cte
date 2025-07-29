import xml.etree.ElementTree as ET

# XPaths mapeados igual antes
XPATHS = {
    "Nome do Arquivo": None,
    "Chave NFe": ".//cte:infDoc/cte:infNFe/cte:chave",
    "cUF": ".//cte:ide/cte:cUF",
    "cCT": ".//cte:ide/cte:cCT",
    "CFOP": ".//cte:ide/cte:CFOP",
    "Natureza da Operação": ".//cte:ide/cte:natOp",
    "nCT": ".//cte:ide/cte:nCT",
    "dhEmi": ".//cte:ide/cte:dhEmi",
    "Emitente": ".//cte:emit/cte:xNome",
    "CNPJ Emitente": ".//cte:emit/cte:CNPJ",
    "UF Emitente": ".//cte:emit/cte:enderEmit/cte:UF",
    "Destinatario": ".//cte:dest/cte:xNome",
    "CNPJ Destinatario": ".//cte:dest/cte:CPF",  # Ajude aqui se precisa ser CNPJ também!
    "vPrest": ".//cte:vPrest/cte:vTPrest",
    "vBC": [
        ".//cte:imp/cte:ICMS/cte:ICMS00/cte:vBC",
        ".//cte:imp/cte:ICMS/cte:ICMSOutraUF/cte:vBC"
    ],
    "pICMS": [
        ".//cte:imp/cte:ICMS/cte:ICMS00/cte:pICMS",
        ".//cte:imp/cte:ICMS/cte:ICMSOutraUF/cte:pICMS"
    ],
    "vICMS": [
        ".//cte:imp/cte:ICMS/cte:ICMS00/cte:vICMS",
        ".//cte:imp/cte:ICMS/cte:ICMSOutraUF/cte:vICMS"
    ],
    "CST": [
        ".//cte:imp/cte:ICMS/cte:ICMS00/cte:CST",
        ".//cte:imp/cte:ICMS/cte:ICMSOutraUF/cte:CST"
    ],
    "Toma": ".//cte:ide/cte:toma3/cte:toma",
    "Município de Início (xMunIni)": ".//cte:ide/cte:xMunIni",
    "Município de Fim (xMunFim)": ".//cte:ide/cte:xMunFim",
    "UF de Início (UFIni)": ".//cte:ide/cte:UFIni",
    "UF de Fim (UFFim)": ".//cte:ide/cte:UFFim",
    "UF toma4": ".//cte:toma4/cte:enderToma/cte:UF",
    "UF Receb_Exped": None
}

NAMESPACE = {'cte': 'http://www.portalfiscal.inf.br/cte'}

def get_node_text_with_namespace(root, xpath, namespace):
    try:
        node = root.find(xpath, namespaces=namespace)
        return node.text if node is not None else "Não encontrado"
    except Exception as e:
        return f"Erro: {str(e)}"

def get_first_available(root, xpaths, namespace):
    for xp in xpaths:
        val = get_node_text_with_namespace(root, xp, namespace)
        if val != "Não encontrado":
            return val, xp
    return "Não encontrado", None

def get_uf_receb_exped(root, namespace):
    uf = get_node_text_with_namespace(root, './/cte:enderReceb/cte:UF', namespace)
    if uf != "Não encontrado":
        return f"{uf} - receb", './/cte:enderReceb/cte:UF'
    uf = get_node_text_with_namespace(root, './/cte:enderExped/cte:UF', namespace)
    if uf != "Não encontrado":
        return f"{uf} - exped", './/cte:enderExped/cte:UF'
    return "Não encontrado", None

def processar_xmls(file, campos, modo_debug=False):
    """
    Recebe um arquivo XML e um dict {campo: True/False}.
    Retorna dict {campo: valor}.
    Se modo_debug=True, retorna também dict de debug de cada campo: XPath, valor extraído, erros.
    """
    debug_log = {}
    try:
        root = ET.parse(file).getroot()
    except Exception as e:
        # Caso não consiga ler o XML, retorna erro direto
        if modo_debug:
            return {}, {'_erro_geral': str(e)}
        else:
            raise Exception(f"Erro ao ler XML: {str(e)}")

    resultado = {}
    for campo, marcado in campos.items():
        if not marcado:
            continue

        # Nome do arquivo
        if campo == "Nome do Arquivo":
            val = getattr(file, "name", "desconhecido")
            resultado[campo] = val
            if modo_debug:
                debug_log[campo] = {'xpath': None, 'valor': val, 'ok': True}

        # UF Receb_Exped (regra especial)
        elif campo == "UF Receb_Exped":
            val, xpath = get_uf_receb_exped(root, NAMESPACE)
            resultado[campo] = val
            if modo_debug:
                debug_log[campo] = {'xpath': xpath, 'valor': val, 'ok': val != "Não encontrado"}

        # vBC, pICMS, vICMS, CST podem vir de 2 caminhos
        elif isinstance(XPATHS[campo], list):
            val, xpath = get_first_available(root, XPATHS[campo], NAMESPACE)
            resultado[campo] = val
            if modo_debug:
                debug_log[campo] = {'xpath': xpath, 'valor': val, 'ok': val != "Não encontrado"}

        # Demais campos
        elif XPATHS[campo]:
            val = get_node_text_with_namespace(root, XPATHS[campo], NAMESPACE)
            resultado[campo] = val
            if modo_debug:
                debug_log[campo] = {'xpath': XPATHS[campo], 'valor': val, 'ok': val != "Não encontrado"}
        else:
            resultado[campo] = "Não encontrado"
            if modo_debug:
                debug_log[campo] = {'xpath': None, 'valor': "Não encontrado", 'ok': False}

    if modo_debug:
        return resultado, debug_log
    else:
        return resultado
