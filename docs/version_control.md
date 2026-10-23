# Controle de versão e rastreabilidade

Remoto exclusivo: https://github.com/LimaGV/C-NBI-v2 (privado nesta fase).
Nunca configurar LimaGV/C-NBI como remoto.

main recebe somente estados testados, documentados, reproduzíveis e
metodologicamente rastreáveis. Trabalhar em feature/*, experiment/*, fix/*,
docs/*, release/*. Proibidos nomes final, final2, test, temp, new.
Branch inicial: feature/00-project-foundation.
main nasceu com commit vazio 63dd373 para fornecer ancestral ao primeiro PR.
O PR #1 foi integrado por squash autorizado em 2026-10-23, após CI verde e
ausência de conflitos: 777a8fd07d6edf901acb46fcec6f97f2a0d1e7a4.
A árvore desse squash foi conferida como idêntica ao HEAD revisado da Fase 0.
A Fase 0.5 partiu dessa main limpa em feature/00-5-data-reference-foundation.

## Registro mínimo de mudança científica
- O que mudou, por quê e definição matemática anterior/nova.
- Branch, SHA completo, PR, versão e estado dirty.
- ADR/MDR, estado e evidências de aceitação ou de experimento.
- Testes, plataforma, lock e comandos.
- Dados/hashes, configuração, seeds e resultados afetados.
- Reexecuções necessárias e limitações.

0.1.0.dev0 sozinho não identifica experimento. Registrar git rev-parse HEAD e
git status --short. Tags/releases são posteriores à validação; não criadas aqui.
Não reescrever histórico compartilhado nem commitar credenciais.
Tentar proteção de main quando suportada e registrar limitações do plano;
não tornar o repositório público para contornar restrições.
