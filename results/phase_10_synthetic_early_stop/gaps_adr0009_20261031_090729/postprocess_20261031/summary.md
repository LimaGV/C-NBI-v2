# C-NBI-ES versus B=2000 — resumo descritivo

- Integridade: 135/135 PASS; falhas: 0. API10C congelada; alias C-NBI apenas na validação do nome.
- 27 cenários com cinco réplicas; Δ=ES−original; sinais estritos, sem tolerância nova, inferência ou equivalência formal.
- IGD: n=27, mediana Δ=0, V/D/E=4/5/18
- HV: n=27, mediana Δ=0, V/D/E=3/3/21
- Cardinalidade ND: 53/135 casos mudaram; total 156789→156909.
- Kernels: 16048.056→17040.190s (+6.182%); mediana das razões por caso=0.79412.
- Tempos históricos, não controlados; kernel inclui I/O incremental ES; worker ES inclui persistência final.
- Valores indefinidos: 0 casos; HV sem precisão válida: 0 casos (excluídos apenas do resumo HV).
- nx=2: IGD [n=9, mediana Δ=0, V/D/E=1/1/7]; HV [n=9, mediana Δ=0, V/D/E=2/1/6]; tempo -36.78%; ΔND=-5.
- nx=3: IGD [n=9, mediana Δ=0, V/D/E=0/2/7]; HV [n=9, mediana Δ=0, V/D/E=1/1/7]; tempo -4.68%; ΔND=76.
- nx=5: IGD [n=9, mediana Δ=0, V/D/E=3/2/4]; HV [n=9, mediana Δ=0, V/D/E=0/1/8]; tempo +11.76%; ΔND=49.
- IGD/HV: medianas globais preservadas descritivamente; houve perdas em alguns cenários. Não há demonstração de equivalência.
- Custo: não reduziu o tempo agregado dos kernels.
- Adoção: manter experimental; não adotar como padrão por economia de tempo neste resultado.
- Falhas/indefinições estão identificadas no CSV; nenhuma métrica original foi recalculada.
