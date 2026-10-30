# Reprodutibilidade

## Fase10D — campanha ordenada e avaliação externa

Fonte numérica congelada:8f9d60f89fc06814a78d1a1cd9c42ea3ac37fbee.
Protocolo:19dff29411ad39293f4e429f8f77babd424213a5da61baf7e69855c0ea7209cf.
Diretório:results/phase_10_synthetic_benchmark/benchmark_20261029/campaign_v2/.
Seu README fornece a sequência piloto → gate → campanha → avaliação → auditoria.
O agendador usa barreiras completas C-NBI, VRF-NBI, NSGA-III e MOEA/D;
máximo6 processos em núcleos físicos distintos, um thread numérico por processo.
Seeds pertencem à identidade cenário/réplica/método, nunca à ordem ou ao núcleo.
O piloto corrigido12/12 reproduziu X/Y bitwise contra o piloto sequencial.

Para uma nova execução numérica independente, usar um checkout/worktree vazio
e separado no commit8f9d60f89fc06814a78d1a1cd9c42ea3ac37fbee: nesse commit,
campaign_v2/ ainda não existe. Após uv sync --locked, preparar com
`uv run python scripts/validation/synthetic_benchmark_audit.py --legacy <repo_v1>`
e validar a migração com
`uv run python scripts/validation/validate_synthetic_benchmark_migration.py --legacy <repo_v1>`.
Usar a v1 fixada em7bd4915; as rotinas leem blobs desse commit. Seguir então
a sequência piloto/gate/campanha/avaliação do README do caso. A preparação
recusa sobrescrever diretório existente. As ferramentas finais de relatório
e auditoria, versionadas depois da fonte numérica, podem ser usadas separadamente;
os hashes do protocolo verificam os mesmos arquivos numéricos. O pacote
arquivado permite recarga e verificação sem executar uma segunda campanha.

Checkpoint concluído somente recarrega após validar hashes. Não sobrescrever
payload nem repetir execução para melhorar métricas. Recuperação operacional
exige motivo e histórico; resultado científico retido não pode ser substituído.
As24 execuções piloto anteriores e77 tentativas oficiais iniciais permanecem
separadas, incluindo duas falhas do adaptador Varimax corrigidas na nova versão.
500 iterações/1e-5 continuam iguais à v1; não convergência é explicitamente registrada.

Avaliação independente usa somente a API10C congelada após terminar as buscas.
Referência5000/célula comum às cinco réplicas, ideal/nadir analíticos, sem clipping,
reparo externo ou feedback. Preservar decisões brutas, flags de precisão HV e
métricas indefinidas. Auditor read-only:audit_phase10d_outputs.py. Somente
descrição por célula estrutural; sem tratar réplicas como cenários independentes.
Relatório:phase_10d_verification.md. Ciência0–10C e licenças excluídas preservadas.

## Fase10C — referência analítica independente

Base47a0e4d integra10B e preserva todos os SHAs anteriores por merge commit.
Após checkout limpo da fonte congelada:
`uv run python scripts/validation/generate_synthetic_pareto.py --output <pasta_vazia>`.
Nunca sobrescrever uma campanha. Oficial:results/phase_10_synthetic_pareto/analytical_20261029/.
Verificação read-only:`uv run python scripts/validation/verify_synthetic_pareto.py`.
NPZs primários têm27 IDs/5000 linhas;2500 é prefixo,10000 usa extensão arquivada.
load_reference e load_evaluation_context ficam em synthetic.pareto.serialization;
esta API é externa à busca. Seeds,probes,witnesses,origens,fonte,ambiente e hashes
garantem rastreabilidade sem recalibração/refit. Arquivos novos em LF canônico.
Fonte numérica congelada:d982c01f7753152e5961093d0e6de809362c595c.
Após gerar,refine_synthetic_pareto_layout.py reproduz a apresentação final sem
alterar qualquer CSV/NPZ. Seu SHA/commit e hashes anteriores estão no manifesto.
Todos27 casos reproduzidos em ordem inversa no ambiente registrado;51 checksums.
HV validado nas referências com4×65536;flags de precisão individuais continuam
obrigatórias para futuros conjuntos. Nenhuma execução10D ou equalização.

## Fase10B — geração e verificação independentes

Protocolo docs/policies/synthetic_generation_10b.json,matemática e MDR0014.
Após checkout limpo do commit de implementação:
`uv run python scripts/validation/generate_synthetic_rsm.py --output <nova_pasta_vazia>`.
Nunca sobrescrever uma campanha. A campanha oficial está preservada em
results/phase_10_synthetic_rsm/rsm_20261029/. Verificação read-only:
`uv run python scripts/validation/verify_synthetic_rsm.py`.
Modelos:cnbi_v2.synthetic.rsm.rsm_serialization.load_models(campaign_directory),sem OLS
ou acesso ao oráculo analítico. Todos135 compartilhados por métodos futuros.
Seeds,arrays float64,dependências/BLAS,fonte e todas entradas0–10A são hashed.
Source final800076f4c5cac3f651cdb875cf01135f1eddb561,checkout limpo/LF canônico.
Todos16 CSV/NPZ numéricos são byte-identical à geração inicial09d469e;receipt
em docs/phase_10b_initial_generation_receipt.json. O subpacote10B preserva o teste
de escopo histórico10A sem alterações. Não recalibrar/retunar para reproduzir.

## Ambiente
Checkout limpo, Python de .python-version, uv 0.12.23 e uv sync --locked.
Executar checks do README. Não copiar .venv nem alterar lock silenciosamente.
O lock atende Windows/Ubuntu. Registrar também bibliotecas nativas/BLAS e hardware;
seed fixa não garante identidade bitwise entre plataformas. Os testes abrangem
infraestrutura, matemática, otimização e integridade dos resultados congelados.

```powershell
uv sync --locked
uv run pytest --cov=cnbi_v2 --cov-report=term-missing
uv run ruff check .
uv run mypy src
```

## Pipeline e resultados aplicados

CCD literal/códigos originais → oito RSMs → covariância residual/coeficientes →
ensemble2000 → reotimização âncoras/payoff → normalização fixa/CHIM/PA →37 subsets
→ Simplex-Lattice/NBI local → oito objetivos/ND → benchmark empírico → figuras.
Os scripts/protocolos estão em scripts/validation/ e docs/mathematics/policies.
Não reexecutar campanhas para verificar hashes ou produzir figuras.

data/raw/turning_application/ contém os dois workbooks imutáveis. Results das
Fases2–7 permanecem preservados. A Fase8 mantém tanto o arquivo histórico
turning_reference_sensitivity_20261024 quanto a correção oficial independente
turning_standalone_correction_20261025 (H5 standalone409 ND).
Figuras em results/applied_case_visualizations/turning_visuals_20261025/:
index.html,catálogo,captions,33 tabelas e331 hashes. Não alterar documentos
hashados para atualizar a narrativa atual; eles registram o lançamento.

Base científica:d938695b7fdaf9c871d331a42ff277e0c3fbd2d1.
Plotting:d4db09332b81bd6a11aa0750125670dd8d53541f.
Entrega das figuras:c6e97db8cf18b1927821b386231fb64a8342b431.
Integrações:PR11=39069f3f9abb51af94f9044c1d3c668264590638;
PR12=bb5d6f215c6465777dd395bb8448329327f49c3b. Merge commits preservam a
ancestralidade desses SHAs. Ver consolidation_20261029.md.

Reproduzir gráficos em uma saída nova, sem nova execução científica:

```powershell
uv run python -m scripts.visualization.generate_applied_case_figures --language both --set all --output experiments/runs/visual_reproduction --dpi 600
```

Sem grades de eixos; contornos/domínio/limiares são referências explícitas.
Transformações PCA/elipses são documentadas. Diferenças mínimas de antialiasing
entre processos não equivalem a mudança científica; ver auditoria do run.

## Referência empírica e cenários sintéticos

Os18.503 pontos sem CNBI são referência Pareto **empírica** finita, sem certificado
de frente verdadeira. Alvos comuns,exclusões por família e sensibilidades têm
escopos distintos. A Fase10A desta branch gera somente27 configurações para funções
verdadeiras isotrópicas f_j=||x-a_j||² em bolas2**(nx/4). Seus mínimos analíticos
não são a referência empírica do torneamento. Não se constrói agora referência
Pareto sintética,135 instâncias RSM ou540 runs de benchmark.
MIT cobre apenas código próprio; ver LICENSE_SCOPE.md e data_publication_permissions.md.

Geração estrutural reproduzível em saída nova,com protocolo já congelado:

```powershell
uv run python -m scripts.validation.generate_synthetic_scenarios --output experiments/runs/synthetic_reproduction
uv run pytest tests/synthetic -q
```

Artefatos oficiais:results/phase_10_synthetic_generation/structural_20261029/.
O teste/recibo de reprodutibilidade confirma todos os27 cenários em ordem inversa,
sem alterar âncoras/matrizes. Não confundir calibração numérica de coordenadas
com ajuste RSM ou execução de algoritmos multiobjetivo.

## Manifesto de execução científica
Registrar: identificador, data UTC, branch, SHA, versão, dirty, lock SHA256,
Python, uv, SO/arquitetura, bibliotecas/BLAS relevantes; entradas/hashes;
protocolo/MDR; configuração completa; seed/gerador; solver/versão; thresholds,
tolerâncias, normalização, H, número de Monte Carlos e covariância quando
aplicáveis; comandos, logs, saídas/hashes, status, testes e resultados afetados.

Os valores científicos das Fases0–9 estão congelados. Seed fixa não basta como prova
de reprodutibilidade numérica. Reexecução compara ambiente, hashes e critérios
previamente documentados. Árvore dirty deve ser identificada, não tratada como release.
