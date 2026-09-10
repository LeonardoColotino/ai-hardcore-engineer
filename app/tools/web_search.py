"""
Ferramenta de busca web.

Responsabilidade:
buscar informações gerais na internet
quando o RAG da Getnet não for suficiente.
"""

from ddgs import DDGS


def search_web(
    query: str,
    max_results: int = 3
) -> list[dict]:
    """
    Realiza uma busca na web.

    Args:
        query:
            Texto da busca.

        max_results:
            Quantidade máxima de resultados.

    Returns:
        Lista contendo título, URL e resumo.
    """

    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for result in search_results:
                results.append(
                    {
                        "title": result.get(
                            "title",
                            ""
                        ),
                        "url": result.get(
                            "href",
                            ""
                        ),
                        "snippet": result.get(
                            "body",
                            ""
                        )
                    }
                )

    except Exception as exc:
        raise RuntimeError(
            "Não foi possível realizar a busca web."
        ) from exc

    return results