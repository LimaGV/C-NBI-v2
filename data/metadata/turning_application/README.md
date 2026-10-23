# Turning application — proveniência experimental

Fonte exata fornecida pelo usuário, relativa a Documents:
Dissertação/02_REFERENCIAS/Dados/CCD.xlsx.
Cópia local/Git: data/raw/turning_application/CCD_original.xlsx.
SHA-256: fd9c463efdcd62ff3d7eaa7eec18d9e112543675c30b1f36838beeb38deebf4a.
A cópia de 15427 bytes foi conferida como byte-identical ao original.

dataset.yaml registra desenho/layout e estados; variables.yaml registra aliases,
unidades verificadas e lacunas; provenance.yaml descreve cópia, hashes, commit
e fontes; checksums.sha256 enumera os artefatos cobertos.
workbook_inspection.json vem da CLI existente, com --detail-limit 1000 para
registrar as 152 fórmulas. Somente o segmento de diretório pessoal de um target
externo foi substituído por <USER_HOME>, com redaction explícita no relatório.
A alteração é de privacidade do relatório, nunca do workbook.

## Estado e lacunas
RAW_NOT_SELF_CONTAINED: Plan1!A1:L20, 19 IDs experimentais, fatores cs/f/md,
oito respostas T/MTTF/WR/Ra/Rt/Kp/ROI/OEE.
E2:L20 contém 152 referências a [1]Data de NBI Revisão.xlsm, linhas 4–22.
Nenhuma dependência foi aberta, resolvida ou copiada.

Existem 152 números em cache quando o arquivo é lido com data_only=True.
Isso não comprova que correspondam à versão experimental correta. Nenhum
cache foi promovido a observação computacional validada ou snapshot.
SNAPSHOT_PENDING_EXTERNAL_SOURCE permanece até prova de origem/versão/frescor.

O workbook tem cinco repetições de fatores em linhas 16–20; a publicação
descreve cinco centros. Há divergências de níveis físicos entre Table 1 e raw:
por exemplo, centro Vc publicado 150.000 versus raw 162.5; f publicado 0.150
versus raw 0.16; ap publicado 0.225 versus raw 0.24.
Não escolher automaticamente qual fonte corrigir. Nenhum fator foi recodificado.

Table 6 é codificada, mas Table 3 não estabelece aqui uma conversão inequívoca
raw→coeficientes diante dessas divergências. Manter
CODING_SCHEME_PENDING_VERIFICATION e mapear beta1/beta2/beta3 somente após
confirmação explícita. A ordem candidata Vc/f/ap não é regra implementada.

## Permissão e separação
O usuário autorizou explicitamente versionar este workbook no repositório privado.
A exceção no .gitignore cobre somente esse arquivo; não concede licença pública,
não classifica automaticamente PUBLIC_SMALL e não libera outros dados.
O PDF não foi copiado/versionado.

A Table 3 é expected output independente, em tests/reference_cases/turning_8responses.
Não foi usada para construir Y, preencher respostas ou modificar raw.
