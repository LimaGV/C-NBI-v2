# 0001 — Reimplementação limpa da v2

- Tipo: ADR
- Status: ACCEPTED
- Responsável pela diretriz: Gabriel Lima
- Data: 2026-10-23
- Branch: feature/00-project-foundation
- Commit/PR: rastreados pelo histórico desta decisão e pelo PR de fundação
- Versão: 0.1.0.dev0
- Validation gate: NOT_APPLICABLE (diretriz de escopo, não hipótese científica)
- Substitui: nenhuma decisão desta v2

## Contexto e decisão
O responsável solicitou base nova e independente da v1.
Criar C-NBI-v2 como diretório/Git independentes, pacote cnbi_v2, .venv própria
Python 3.12/uv e remoto LimaGV/C-NBI-v2 privado.
A v1 cnbi-v1.0 é somente referência. Não copiar módulos, importar cnbi,
reutilizar ambiente, arquitetura ou parâmetros por continuidade.
Instituir decisões, claims, dados e CI antes de ciência.
uv_build pinado é dependência de build para instalação editável src.
Não há runtime além das quatro bibliotecas solicitadas.

## Alternativas e evidência
Reutilizar código ou ambiente antigo foi explicitamente excluído na tarefa.
A implementação histórica não foi consultada.
Fonte da diretriz: instruções explícitas do responsável.
Verificação local e CI evidenciam infraestrutura, não validade científica.

## Consequências
ACCEPTED refere-se somente à diretriz de escopo já autorizada.
Hipóteses científicas futuras percorrem proposta, experimento, gate e revisão.
Nenhum algoritmo nesta fundação. Contextos científicos ficam PROPOSED/UNVERIFIED.
Licença e Fase 1 permanecem pendentes.
