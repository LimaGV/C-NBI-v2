# C-NBI v2

Fase7: construção de referência Pareto **empírica** multi-família e
leave-one-family-out, com RSMs atuais, esfera e normalização global congelados.
H5 é o baseline operacional definido pelo responsável (492 subproblemas,
411 decisões únicas,408 ND); H20 é auxiliar da mesma família CNBI.
[Definição](docs/mathematics/pareto_reference_leave_one_out.md),
[auditoria prévia](docs/mathematics/reference_source_audit.md), ADR0011 ACCEPTED.
A calibração aplicada V1 foi autorizada para os operadores de NSGA-III/MOEA-D;
pymoo0.6.2, orçamento comum132000 e30 seeds por família. VRF entra somente por
decisões históricas reavaliadas. H5 usa referência sem qualquer origem CNBI.
Sem verdade Pareto, superioridade ou benchmark final. O texto seguinte mantém
o histórico das fases anteriores.

Fase6: Simplex-Lattice e NBI local determinístico sobre os37 subsets congelados
de B=2000. Normalização local por subset, normal unitária orientada ao ideal e
SLSQP com Jacobianos analíticos/aceitação independente. H2,4,5,10,20 por
membership inteiro da malha-mãe20; cobertura/ND full-space somente para
sensibilidade interna. [Definição](docs/mathematics/local_nbi.md), ADR0010
ACCEPTED no escopo solicitado; nenhum H final aceito ou benchmark externo.
Aplicação concluída:4557/4557 aceitos; zero falhas finais. H20:4417 ND full-space.
[Resultados e limites](docs/mathematics/turning_local_nbi_h_sensitivity.md).
O texto abaixo preserva o estado anterior da Fase5.

Fase 5: normalização fixa nominal, CHIM centralizado e screening espectral
PA inspirado, calibrado pela incerteza do ensemble congelado da Fase 4.
Ver [formulação/API](docs/mathematics/chim_parallel_analysis.md),
[resultados](docs/mathematics/turning_chim_pa.md) e
[validação](docs/phase_5_verification.md). ADR 0008 ACCEPTED no escopo solicitado;
política de early stop original preservada e v2 de gaps espectrais
PROPOSED_REVISED, post hoc. Revisão no mesmo PR #8: stop retrospectivo em1300,
mesma dimensão2 e37 IDs até2000; B=2000 continua referência. ADR 0009 PROPOSED.
A planilha original define um caso codificado distinto do modelo físico;
nenhuma resposta experimental foi alterada. NBI/C-NBI ainda não implementados.

Reimplementação limpa e independente do Combinatorial Normal Boundary
Intersection. Versão **0.1.0.dev0**. Estado: centered CHIM / local PA da Fase 5.
Fase 0 integrada em main; Fase 0.5 adiciona infraestrutura de dados/referências.
Fase 0.5 integrada pelo PR #2; Fase 0.6 preserva o dataset real de torneamento e
os expected outputs publicados, com lacunas explícitas e sem ajuste de modelos.
Fase 0.6 integrada pelo PR #3. A Fase 1 implementa base quadrática, OLS
multivariado e incerteza analítica, validados sinteticamente. O CCD atualizado
foi ajustado com valores literais integrais; a Table 3 tem reprodução parcial
condicional (70/80), com divergência de WR e da nota de escala explícitas.
Ver [validação aplicada](docs/mathematics/turning_real_validation.md).

A [v1](https://github.com/LimaGV/C-NBI/tree/cnbi-v1.0) é referência histórica.
Não foram herdados módulos, arquitetura ou ambiente. A transferência explícita
de parâmetros na Fase7 é delimitada na auditoria e no protocolo versionado.

## Ambiente
Python **3.12.15** e uv **0.12.23**. Na raiz:

~~~sh
uv sync --locked
uv run python -c "import sys, cnbi_v2; print(sys.executable); print(cnbi_v2.__file__)"
uv run pytest
uv run pytest --cov=cnbi_v2
uv run ruff check .
uv run mypy src
uv run python scripts/verify_environment.py
~~~

.venv é local; o pacote editável vem de src/cnbi_v2. Importar cnbi_v2,
nunca cnbi. Não apontar PYTHONPATH para a v1. O lock acompanha o projeto;
a CI repete os quatro checks obrigatórios em Windows e Ubuntu.

## Dados experimentais e referências
Excel é registro primário aceito. Seguir [data/README.md](data/README.md):
raw imutável → validação/hash → snapshot se necessário → transformação
versionada → processed. Resultados computacionais ficam em results/.

~~~sh
uv run python scripts/data/verify_workbook.py "caminho/arquivo.xlsx"
~~~

Inspeção não recalcula fórmulas, resolve links ou certifica caches.
Ver [opções e limites](scripts/data/README.md). Não incorpora dataset ou snapshot.
Zotero/local documents → verificação → notas/BibTeX → claims → ADR/MDR.
Documentos locais protegidos ficam fora do Git por padrão.
O raw de torneamento foi autorizado especificamente no repositório privado.
Ver [metadata e lacunas](data/metadata/turning_application/README.md) e
[golden reference publicada](tests/reference_cases/turning_8responses/README.md).

## RSM e incerteza analítica
`cnbi_v2.model` fornece `quadratic_design`, `quadratic_term_names`,
`fit_multivariate_rsm`, `RSMFit` e as covariâncias analíticas dos coeficientes,
das médias preditas e de diferenças. Não há codificação ou normalização implícita.

```python
from cnbi_v2.model import fit_multivariate_rsm, mean_prediction_covariance

# Exemplo inteiramente sintético; Y vetorial conserva um eixo de resposta.
fit = fit_multivariate_rsm([[-2], [-1], [0], [1], [2]], [1, 2, 1, 3, 5])
mean = fit.predict([0.5])
estimated_mean_covariance = mean_prediction_covariance(fit, [0.5])
```

Ver [definição e API](docs/mathematics/multivariate_rsm.md),
[derivações da incerteza](docs/mathematics/rsm_uncertainty.md) e
[ADR 0003](docs/decisions/0003-multivariate-rsm-and-uncertainty-foundation.md).
Há otimização individual nominal de quadráticas e ablação de região de respostas.
`cnbi_v2.uncertainty` fornece amostragem conjunta dos coeficientes, diagnósticos
de prefixos e reotimização por réplica com payoff natural e certificados.
`cnbi_v2.chim` acrescenta normalização fixa, SVD e seleção PA local, com todos
os prefixos até B=2000. Shrinkage, H da malha e NBI/C-NBI não implementados.

## Governança
Usar feature/*, experiment/*, fix/*, docs/* ou release/*.
main é destino de PR aprovado. A Fase 0 entrou pelo PR #1 após CI verde;
as Fases 0.5 e 0.6 foram integradas pelos PRs #2 e #3. A Fase 1 usa
feature/01-multivariate-rsm-foundation, integrada pelo PR #4 com autorização.
A Fase 2 foi integrada por squash no PR #5 com autorização para a Fase 3.
A Fase 3 foi integrada por squash no PR #6 com autorização para a Fase 4.
A Fase 4 foi integrada por squash no PR #7 com autorização para a Fase 5.
A Fase 5 usa feature/05-chim-svd-local-pa; novo PR sem merge automático.

- [Contrato dos agentes](AGENTS.md)
- [Arquitetura](docs/architecture.md) e [roadmap](ROADMAP.md)
- [Decisões](docs/decisions/) e [estado metodológico](docs/methodology_status.md)
- [Reprodutibilidade](docs/reproducibility.md)
- [Integridade](docs/data_integrity.md) e [gestão dos dados](docs/data_management.md)
- [Verificação do ambiente](docs/environment_verification.md)
- [Inventário MCP](docs/integrations/mcp_inventory.md)
- [Referências](references/README.md)

Licença pendente: LICENSE_DECISION_PENDING.md. CITATION.cff descreve software
em desenvolvimento, sem DOI ou publicação inventados.
