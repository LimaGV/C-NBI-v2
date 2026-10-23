# Turning application — published expected outputs

## Estado aplicado atual
A revisão literal do CCD foi ajustada preservando a precisão das células.
O [relatório](../../../docs/mathematics/turning_real_validation.md) registra
50/80 pela nota de escala e 70/80 com escala diagnóstica, sob CCD nominal
rotacional. WR diverge com precisão integral; não se declara reprodução completa.
Os coeficientes e source.yaml abaixo permanecem como originalmente registrados.
As descrições documentais/futuras seguintes registram o estado da Fase 0.6.

Golden reference documental da Table 3 de Pereira et al. (2025),
DOI 10.1016/j.engappai.2025.112510, página impressa/PDF 13.
PDF local conferido; metadados correspondentes ao item Zotero SMMX47JT.
Fonte e hash: source.yaml. Não é teste de ajuste RSM nesta fase.

expected_coefficients.csv contém 10 termos × 8 respostas originais = 80 valores.
VRF1/VRF2/VRF3 foram excluídas. Os números foram transcritos diretamente da tabela,
conferidos visualmente, mantendo casas decimais; somente o sinal tipográfico
negativo foi representado pelo sinal ASCII. Não houve OLS ou rescaling.

expected_model_summary.csv preserva S, R2, R2_adj, R2_pred, classificação,
direção e avaliação residual para as oito respostas. São referências secundárias,
sujeitas aos arredondamentos da publicação; não foram recalculadas ou endossadas
como estatísticas obtidas neste projeto. A nota da tabela dá S em 10^-2.

## Definição publicada, sem implementação
Eq. (17), seção 2.3, página 6, descreve o modelo quadrático completo. Para três
fatores, os termos esperados, com a ordem de Eq. (19)/Table 6, são:

~~~text
y = beta0
  + beta1*x1 + beta2*x2 + beta3*x3
  + beta11*x1^2 + beta22*x2^2 + beta33*x3^2
  + beta12*x1*x2 + beta13*x1*x3 + beta23*x2*x3

1, x1, x2, x3, x1^2, x2^2, x3^2, x1*x2, x1*x3, x2*x3
N=19, n_x=3, m=8, p=10
X: 19 x 10; Y: 19 x 8; B: 10 x 8; E: 19 x 8
~~~

São definições documentais para fase futura: não existe função de design matrix,
ajuste OLS, reconstrução de Y ou implementação de modelos nesta fase.
A notação p=10 é local para número de termos; a publicação reutiliza símbolos
em contextos diferentes.

## Escala, codificação e precisão
A nota da Table 3 declara WR, ROI e OEE em 10^-2; source.yaml guarda essa
declaração separadamente. As entradas CSV permanecem exatamente na escala
numérica impressa. Não aplicar os fatores automaticamente.
A nota da Table 2 usa 10^-3 para WR, e a convenção precisa de reconciliação.

CODING_SCHEME_PENDING_VERIFICATION: Table 6 é explicitamente codificada, mas
outras tabelas usam x1/x2/x3 físicos. A Table 1 difere do workbook em vários
níveis físicos. A ligação exata da convenção da Table 3 aos fatores raw e seus
constantes de codificação deve ser confirmada antes de comparar coeficientes.
A ordem candidata Vc/f/ap é registrada, sem assumir silenciosamente beta1/beta2/beta3.

Published coefficients are reference values rounded to the precision shown in the source.
Future validation must distinguish:
- numerical implementation error;
- data mismatch;
- coding/scaling mismatch;
- published rounding.

Não exigir igualdade bitwise. Tolerância será definida somente na Fase 1, com
justificativa; nenhum limite numérico foi adotado aqui.

## Separação de evidências
CCD_original.xlsx é input experimental preservado, atualmente com links externos.
Table 3 é expected reference output publicado, nunca observação experimental.
É proibido gerar Y, preencher células, estimar respostas faltantes ou otimizar
dados a partir desses coeficientes. A reprodutibilidade numérica permanece
PROPOSED/UNVERIFIED. Não criar snapshot a partir de caches não comprovados.
Código de produção não importa estes arquivos; somente testes de integridade.
