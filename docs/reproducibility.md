# Reprodutibilidade

## Ambiente
Checkout limpo, Python de .python-version, uv 0.12.23 e uv sync --locked.
Executar checks do README. Não copiar .venv nem alterar lock silenciosamente.
O lock atende Windows/Ubuntu; equivalência numérica futura ainda exigirá
validação de bibliotecas nativas e hardware. Os testes atuais são de infraestrutura.

## Manifesto de execução científica futura
Registrar: identificador, data UTC, branch, SHA, versão, dirty, lock SHA256,
Python, uv, SO/arquitetura, bibliotecas/BLAS relevantes; entradas/hashes;
protocolo/MDR; configuração completa; seed/gerador; solver/versão; thresholds,
tolerâncias, normalização, H, número de Monte Carlos e covariância quando
aplicáveis; comandos, logs, saídas/hashes, status, testes e resultados afetados.

Nenhum valor científico é definido nesta fase. Seed fixa não basta como prova
de reprodutibilidade numérica. Reexecução compara ambiente, hashes e critérios
previamente documentados. Árvore dirty deve ser identificada, não tratada como release.
