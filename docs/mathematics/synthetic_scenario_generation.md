# Fase10A — geração estrutural de cenários sintéticos

## Definição e desenho

Modelo oficial do responsável: f_j(x)=||x-a_j||², todos MIN. Não há anisotropia,
transformação de respostas ou ajuste de coeficientes. Gradiente2(x-a_j), Hessiana2I,
f_j>=0 e mínimo global f_j(a_j)=0. Âncoras finais devem estar estritamente dentro
ou na bola Ω={x:||x||<=alpha},alpha=2**(nx/4). Não se usa1.682 em todas dimensões.

Fatorial completo nx∈{2,3,5},delta∈{1,3,5},m=nx+1+delta e alvos de correlação
absoluta .25/.60/.85:27 células,uma configuração final por célula. Linhas de A
armazenam a_j; isso é a transposta da notação matemática A=[a1,...,am] por colunas.
O único critério de calibração é J=(rho_abs-target)²,com
rho_abs=2/[m(m-1)] sum_{i<j}|rho_ij|. A média assinada usa os mesmos pares sem
módulo e é apenas covariável observada. Não se criam níveis positivo/misto/negativo.

## Amostragem uniforme em volume

Sobol embaralhado com nx+1 coordenadas,32 bits e N=2**power,sem descartar pontos.
Um deslocamento de meia célula digital2**-33 coloca coordenadas no intervalo
aberto. Para as nx primeiras, g_k=Phi^-1(u_k),d=g/||g||. A última dá
r=alpha*u_last**(1/nx),x=r*d. Pela simetria angular da normal,d é uniforme na
esfera; P(r<=t)=(t/alpha)**nx é a distribuição radial de volume. O mapa usa a
medida produto, com a aproximação finita própria da rede QMC. Não é amostragem
do cubo, nem somente da superfície. Não há clipping,thinning ou recalculo de dados.

Protocolo congelado em docs/policies/synthetic_generation_10a.json:
N_cal=16.384,N_val=65.536,seeds distintas. Cada candidato usa exatamente a mesma
amostra de calibração da célula. O holdout só é gerado depois da seleção final.

## Álgebra empírica para o calibrador

Escrever U=||X||² e H=[U,X1,...,Xnx]. Então
f_j=U-2*a_j^T X+||a_j||². A constante desaparece na covariância centralizada.
Com Q_j=[1,-2*a_j^T] e C_H a covariância amostral ddof1:

```text
Cov(F) = Q C_H Q^T
rho_ij = Cov(F)_ij / sqrt(Cov(F)_ii Cov(F)_jj)
```

Isso é identidade para os valores das funções na amostra fixa, não OLS/RSM,
redução de objetivos ou uma matriz que altere a função verdadeira. Permite
avaliar J sem reavaliar milhares de pontos em cada iteração. A validação usa
diretamente as distâncias quadráticas e np.corrcoef(rowvar=False).

Se v_i=Q_i C_H Q_i^T e b_i=C_H Q_i^T, a derivada em a_i é
-2*(b_j[1:]/sqrt(v_i v_j)-rho_ij*b_i[1:]/v_i). Somar sign(rho_ij) nos pares,
com fator2/[m(m-1)],e multiplicar por2*(rho_abs-target) dá a derivada de J.
Em rho_ij=0 usa-se sign(0)=0 como convenção de subgradiente. Não se suaviza |rho|.

## Correlação populacional e precisão numérica

Para X uniforme na bola, simetria dá E[X]=0,Cov(X)=alpha²/(nx+2) I e
Cov(||X||²,X)=0. Integrando a densidade radial:
E[r²]=nx*alpha²/(nx+2),E[r⁴]=nx*alpha⁴/(nx+4). Portanto

```text
v0 = Var(r²) = 4*nx*alpha^4 / ((nx+4)*(nx+2)^2)
s  = 4*alpha²/(nx+2)
c  = v0/s = nx*alpha²/((nx+4)*(nx+2))
rho_ij(pop) = (c+a_i·a_j)/sqrt((c+||a_i||²)*(c+||a_j||²))
```

Esta derivação é uma checagem independente da precisão amostral, não substitui
a calibração amostral solicitada nem seleciona candidatos. Após seleção,
exige-se máximo erro absoluto por entrada<=0.005 nas duas matrizes amostrais
contra essa referência exata. Esse orçamento é10% da tolerância0.05; não é
um intervalo de confiança estatístico. Registrar também diferenças dos resumos.
Não adaptar tamanhos/seeds/configuração usando o holdout. Falha de precisão
invalida a configuração e fica registrada, sem escolher outro candidato.

As respostas centralizadas pertencem ao espaço gerado por nx+1 variáveis de H.
Logo rank(R)<=nx+1<m: a correlação pode e normalmente deve ser singular. A
checagem exige PSD dentro de1e-10,simetria e diagonal unitária,sem regularização
ou correção de autovalores. O posto afim das âncoras deve ser nx.

## Calibração, seeds e seleção

SLSQP,8 inícios,maxiter400,ftol1e-10,Jacobianos analíticos. As variáveis são
coordenadas das âncoras em unidades de alpha; a função continua nas coordenadas
originais. Restrições:1-||u_j||²>=0 e ||u_i-u_j||²-(1e-4)²>=0. Certificar a
viabilidade final exatamente pelo norm<=alpha,sem projetar/reparar o resultado.

Start0 usa posições de um simplex regular balanceado,repetidas e perturbadas
com jitter gaussiano0.01 em unidades de raio; os demais usam posições aleatórias
uniformes na bola. São inicializações do solver, não fatores/classes geométricas
extras. Sua construção não modifica a Hessiana2I ou impõe sinal às correlações.
Guarda-se a melhor avaliação estruturalmente viável de cada início,com o status
de convergência do solver separado. Escolhe-se menor erro de calibração entre
inícios convergidos/viáveis,desempate por índice. Sem convergidos,guardar o melhor
disponível e marcar inválido. Não se usa correlação assinada ou validação na escolha.

Ordinal lexicográfico=9*index(nx)+3*index(delta)+index(target). Masterseed20261029;
init/cal/val=master+10*ordinal+1/2/3. Start_seed=init+100000*start. PCG64 explícito,
sem estado global. Executar células em outra ordem não muda suas streams.

Aceitação requer:convergência,âncoras distintas/viáveis,posto afim completo,
mínimos analíticos certificados,matrizes válidas,erro<=0.05 em calibração **e**
validação,e precisão amostral acima. Falhas não relaxam a tolerância; arquivar
melhor configuração e diagnósticos. Não há certificado de ótimo global de J.

## Evidência e limites

Definição/modelo/fatores/tolerância: METHODOLOGICAL_DECISION do responsável.
Fórmulas acima: MATHEMATICAL_DERIVATION explícita. Testes e calibrações:
INTERNAL_EVIDENCE,registrada em phase_10a_verification.md após execução.
Não se atribui esta definição a uma publicação ou à V1.
Context7 /scipy/scipy e /numpy/numpy fundamentam somente APIs; fontes primárias:
[Sobol](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html),
[SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html).

Não há ruído,CCD,ajuste RSM,Monte Carlo de coeficientes,CHIM/PA,C-NBI,VRF-NBI,
EAs,referência Pareto,métricas ou estatística de benchmark. Quatro diagnósticos
em inglês,PNG600dpi/PDF vetorial,sem grades. Dados/figuras das Fases0–9 permanecem
byte a byte preservados; cada execução registra hashes e o commit de código.
