# Controle de versão e rastreabilidade

Remoto exclusivo: https://github.com/LimaGV/C-NBI-v2 (privado nesta fase).
Nunca configurar LimaGV/C-NBI como remoto.

main recebe somente estados testados, documentados, reproduzíveis e
metodologicamente rastreáveis. Trabalhar em feature/*, experiment/*, fix/*,
docs/*, release/*. Proibidos nomes final, final2, test, temp, new.
Branch inicial: feature/00-project-foundation.
main nasce com commit vazio 63dd373 para fornecer ancestral ao primeiro PR;
não contém implementação.

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
