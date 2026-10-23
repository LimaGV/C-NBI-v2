# NNNN — Título

- Tipo: ADR (arquitetura) ou MDR (metodologia)
- Status: PROPOSED
- Autor/responsável:
- Data:
- Branch:
- Commit/PR: registrar após commit no PR/manifesto; não inventar SHA
- Versão:
- Substitui / substituída por:
- Validation gate: NOT_STARTED / IN_PROGRESS / PASSED / FAILED

## Contexto e problema
O que muda, por quê e resultados afetados.

## Definição
MDR: matemática, símbolos, domínios, pressupostos e unidades.
ADR: interfaces, fronteiras e implicações de software.

## Evidência e alternativas
Fontes verificáveis com Zotero key/citekey, DOI somente se conferido,
METADATA_VERIFIED/FULLTEXT_VERIFIED e localização de passagens.
Distinguir LITERATURE, INTERNAL_EVIDENCE, PROPOSED e limitações.

## Decisão proposta
Explicitar parâmetros/defaults, sem herdar a v1. Documentar efeitos em seed,
threshold, solver, normalização, Monte Carlos, H, covariância, Pareto,
tolerância e regularização quando aplicáveis.

## Validação
Critérios definidos antes dos resultados; testes, dados/hashes, protocolo,
configuração, comparação, evidências, scripts e commits.

## Consequências
Reexecuções, resultados afetados, compatibilidade e limitações.

## Revisão e histórico
Transição, responsável, data, razão e evidências.
Estados: PROPOSED, EXPERIMENTAL, ACCEPTED, REJECTED, SUPERSEDED.
Fluxo: PROPOSED → EXPERIMENTAL → VALIDATION → ACCEPTED.
VALIDATION é gate dentro de EXPERIMENTAL, não sexto estado persistido.
PASSED não aceita automaticamente: revisão explícita é obrigatória.
