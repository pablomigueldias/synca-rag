from langchain_core.tools import tool
from ddgs import DDGS

@tool
def pesquisar_internet(query: str) -> str:
    """
    Use esta ferramenta SEMPRE que precisar buscar na internet por informações recentes, 
    clima, notícias, esportes ou fatos do mundo atual que você não tem na sua base de dados.
    """
    try:
        resultados = DDGS().text(query, max_results=3)
        texto_formatado = ""
        for r in resultados:
            texto_formatado += f"Título: {r.get('title', '')}\nConteúdo: {r.get('body', '')}\n\n"
        return texto_formatado if texto_formatado else "Nenhum resultado encontrado."
    except Exception as e:
        return f"Erro ao pesquisar na internet: {str(e)}"