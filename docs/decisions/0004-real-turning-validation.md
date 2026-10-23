# 0004 — Validação aplicada com valores literais do CCD

- Tipo: ADR/MDR de protocolo de validação
- Status: EXPERIMENTAL
- Validation gate: PARTIAL (70/80 condicionais; WR e nota de escala não reconciliados)
- Responsável: solicitação explícita do usuário para ajustar o CCD real sem alterar células
- Data: 2026-10-23
- Branch: feature/01-multivariate-rsm-foundation, complemento no PR #4 aberto
- Versão RSM: 0.1.0.dev0; commit de implementação 6d1108c29916cb6a850c29ea15654e245da06e4a
- Commit de execução e incorporação: manifesto/proveniência após existir; sem SHA inventado

## Decisão e limites

Preservar a nova revisão byte a byte, junto do raw histórico; ler somente
literais numéricos e preservar os tokens exatos em CSV. Ajustar os oito RSMs
com o módulo existente, sem mudar sua matemática, coordenadas físicas ou Y.
Comparar separadamente hipóteses de codificação fundamentadas na estrutura do
arquivo e na Table 6. Não escolher codificação/escala por otimização de erros.

Usar intervalos da precisão publicada, sem igualdade bitwise. Tolerância:
meia unidade na última casa impressa, incluindo empates, mais somente margem
de fronteira 16*eps*max(1,abs(calculado),abs(publicado)). Regra derivada da
representação decimal da fonte; não é regularização ou tolerância do solver.

Escala declarada pela Table 3 e multiplicador diagnóstico conflitante são
relatados em separado. A fonte/golden reference não é corrigida.
Uma cópia de WR arredondada pode ser investigada apenas como diagnóstico
explicitamente solicitado via flag, sem entrar no ajuste real ou em seus totais.
Não transformar dados para alcançar 80/80.

## Evidência e consequência

[Relatório](../mathematics/turning_real_validation.md), metadados da revisão e
artefatos do experimento distinguem input experimental e expected output.
R001, Table 3 p.13 e Table 6 p.18, foi diretamente inspecionada na fase anterior;
Table 2 p.12 foi reconferida nesta etapa. O NIST/SEMATECH fundamenta a fórmula
rotacional, não confirma os parâmetros internos dos autores.

O ajuste real é executável e autocontido. A hipótese de reprodução integral
permanece não confirmada; C011 passa a PARTIALLY_SUPPORTED. A concordância de
sete respostas é forte evidência condicional da ordem dos termos e do desenho
nominal, mas não valida automaticamente a escala impressa ou o coding físico.
Pré-arredondar WR explica numericamente a discrepância e viola a equivalência
com os valores integrais: não foi adotado como preprocessing oficial.
