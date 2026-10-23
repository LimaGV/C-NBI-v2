# Metadados

dataset_template.yaml e variable_dictionary_template.yaml são templates vazios,
não datasets nem validação automática de schema. YAML null significa desconhecido.
Não preencher unidades, direções, desenho, contagens ou hashes por inferência.

Documentar origem, datas, fatores/respostas, desenho, acesso, hashes e cadeia de
transformações. Cada arquivo raw/snapshot/processed relevante tem seu SHA-256.
Registrar source_commit completo e source_script; novas versões preservam a
proveniência anterior. Histórico Git complementa, não substitui, a identificação
dos dados e do ambiente.

Papéis futuros: factor, response, identifier, auxiliary.
Direção de resposta: minimize/maximize somente quando sustentada por evidência.
run_id explícito é requisito para futuras importações; linha Excel não é ID.

Metadata pode revelar informação restrita: revisar antes de enviar ao GitHub.
Schemas poderão ser adicionados futuramente em data/schemas/ sem ignorar a árvore.
