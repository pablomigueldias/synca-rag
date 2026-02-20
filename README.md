# 🧠 Synca RAG - Assistente Executivo Autônomo

Synca é um agente autônomo e assistente executivo desenvolvido com **FastAPI** e **LangChain**, projetado para rodar localmente utilizando modelos open-source via **Ollama**. O sistema combina capacidades de RAG (Retrieval-Augmented Generation) com busca na internet, permitindo que o agente recupere conhecimentos privados e informações em tempo real.

## 🚀 Tecnologias Utilizadas

* **Backend:** Python 3.12, FastAPI, SQLAlchemy (Async)
* **IA / LLM:** Ollama (Llama 3.1 para raciocínio, Nomic-Embed-Text para embeddings)
* **Orquestração:** LangChain (Arquitetura ReAct)
* **Banco de Dados:** PostgreSQL (com pgvector para busca semântica)
* **Gerenciamento de Pacotes:** Poetry

## Arquitetura do Agente

O motor principal do Synca (`app/services/rag_service.py`) utiliza o paradigma **ReAct (Reasoning and Acting)**. Essa escolha arquitetural foi feita para estabilizar a execução de modelos locais (como a família Llama 3), garantindo que o agente siga um formato estrito de *Thought -> Action -> Observation*, evitando *parsing errors* comuns em *Tool Calling* nativo.

### Ferramentas (Tools) Disponíveis:
1.  **Pesquisa de Documentos Internos (`pesquisar_documentos_internos`):** Busca vetorial no banco de dados para recuperar tutoriais, currículo, portfólio de projetos e habilidades do usuário usando distância de cosseno.
2.  **Pesquisa na Internet (`pesquisar_internet`):** Busca em tempo real na web para responder a perguntas sobre notícias, cotações ou conhecimentos gerais.

## Estabilidade e Tratamento de Erros

Para garantir que o agente não entre em *loops* infinitos quando o LLM falhar na formatação da saída, o `AgentExecutor` está configurado com:
* `max_iterations=4`: Corta a execução se o modelo demorar demais para chegar a uma conclusão.
* `handle_parsing_errors`: Injeta instruções corretivas dinamicamente (ex: forçando o uso do prefixo `Final Answer:`) caso o modelo devolva um JSON malformado ou Markdown incorreto.

## Próximos Passos (Roadmap)

- [ ] **Integração de APIs Determinísticas:** Adicionar ferramentas dedicadas para extração de dados exatos, contornando as limitações de SEO dos motores de busca tradicionais.
- [ ] **Ingestão Automatizada:** Criar rotinas para varrer diretórios locais e retroalimentar o banco vetorial automaticamente.
- [ ] **Automação Ativa:** Desenvolver ferramentas que permitam ao Synca executar scripts locais no sistema operacional.
- [ ] **Interface de Usuário:** Consolidar o consumo da API FastAPI em um frontend reativo (React + Tailwind v4).

---
*Desenvolvido por Pablo Ortiz*