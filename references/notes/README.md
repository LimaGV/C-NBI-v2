# Notas, verificação e claims

Usar source_note_template.md para registrar fonte, proveniência, hash, evidência,
cobertura de leitura e uso metodológico. Bibliografia e notas são seletivas.

Status de verificação: UNREAD, METADATA_VERIFIED, PARTIAL, FULLTEXT_VERIFIED,
CRITICAL_SOURCE. A importância CRITICAL_SOURCE não comprova leitura integral:
registrar separadamente cobertura e evidência de verificação.
FULLTEXT_VERIFIED exige inspeção efetiva do conteúdo completo.
Informação bibliográfica desconhecida fica vazia ou UNVERIFIED_METADATA.

Classes: LITERATURE, INTERNAL_EVIDENCE, MATHEMATICAL_DERIVATION, PROPOSED.
Derivação exige passos/pressupostos documentados e revisão, não fonte fictícia.
Experimento interno não é literatura; hipótese não é fato.
A claims_matrix preserva IDs e conecta evidências a ADR/MDR e limitações.
