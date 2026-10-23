# Arquitetura — Fases 0/0.5

Nenhuma arquitetura ou algoritmo científico escolhido.
cnbi_v2 exporta __version__; _version.py mantém 0.1.0.dev0.
cnbi_v2.data contém SHA-256 e inspeção .xlsx sem transformar dados.

- data/hashing.py: hash em blocos, somente leitura.
- data/workbooks.py: relatórios via dataclasses, leitura openpyxl e OOXML.
- scripts/data/verify_workbook.py: JSON em stdout; sem save, recálculo ou snapshot.
- data/: documentação/templates sem dataset real.
- references/: fontes/notas/claims seletivos.
- results/: saídas futuras, nunca dados brutos.

Layout src evita mascarar instalação incorreta. uv_build==0.12.23 é dependência
de build; module-name é explicitamente cnbi_v2.
Runtime original: numpy, scipy, pandas, scikit-learn.
Única dependência direta nova: openpyxl>=3.1,<4, resolvida como 3.1.5.
et-xmlfile é transitiva; nenhum outro engine Excel adicionado.

openpyxl não fornece stubs na distribuição instalada. mypy permanece strict;
ignore_missing_imports é limitado a openpyxl/openpyxl.* e a ponte de worksheet
usa Any explicitamente. Relatórios e APIs públicas próprios são anotados.

Não há solver, RSM, regressão, Monte Carlo, âncoras, SVD metodológica, PA,
Simplex-Lattice, payoff matrix, escolha de H, Pareto ou métricas multiobjetivo.
Contagens estruturais de células não são resultados científicos.
