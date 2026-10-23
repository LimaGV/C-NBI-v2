# Regras de desenvolvimento

1. Confirmar tarefa, escopo, branch e contrato AGENTS.md.
2. Entender ciência existente com Serena quando disponível; registrar fallback.
3. Antes de ciência: matemática, fontes, MDR, testes e critérios de validação.
4. Context7 para APIs/CLIs; indisponibilidade exige registro e fonte oficial.
5. Não herdar módulos, .venv ou arquitetura da v1; alterar só o necessário.
6. Executar checks, documentar evidências e efeitos nos resultados.
7. Commit/PR vinculam decisão, versão, dados e validação.
8. main somente por PR e CI verde. Não mergear esta fundação automaticamente.

Somente escolhas de infraestrutura foram feitas: Python 3.12.15, uv 0.12.23,
layout src, ferramentas de qualidade e CI. Nenhum parâmetro científico.
Novas dependências exigem justificativa explícita.
