# Arquitetura inicial

Estado: infraestrutura, sem arquitetura científica escolhida.
A única API de cnbi_v2 é __version__. _version.py contém a versão de
desenvolvimento. Não existem solvers, RSM, Monte Carlo, âncoras, normalização,
Pareto ou Simplex-Lattice implementados.

O layout src separa o pacote dos testes e evita mascarar instalação incorreta.
c-nbi-v2 usa module-name = cnbi_v2 explicitamente: a normalização automática
produziria c_nbi_v2. uv_build==0.12.23 é dependência exclusivamente de build,
justificada pela instalação editável e empacotamento; não é runtime científico.
O backend acompanha o uv local. O lock fixa versões de runtime e desenvolvimento.

Não foram criados módulos científicos antecipados. references/ organiza
proveniência; experiments/ receberá protocolos; results/ contém saídas derivadas;
notebooks/ é exploração; scripts/ tem somente verificação de ambiente.
Documentação de software não justifica metodologia: ver
integrations/software_documentation.md.
