# Captals Fusion — Ω-Capitals + Metabolismo de Valor

## Status

`IMPLEMENTED_ON_BRANCH / NOT_YET_MERGED`

Esta integração preserva duas linhagens reais do projeto em vez de substituir uma pela outra.

## 1. Linhagem econômica histórica — Ω-Capitals

A superfície legada continua responsável por mecanismos econômicos e de mercado já presentes no repositório:

- contratos Solidity;
- Ω-Score de ativos/risco;
- Ω-Funds / pools / governança;
- Evidence Notes;
- LUA-PAY;
- FastAPI;
- React;
- Telegram bot;
- Web3 e liquidez.

Ela permanece uma superfície válida do Captals, mas não é elevada automaticamente a mecanismo de verdade, evidência ou autorização constitucional.

## 2. Linhagem canônica — Captals como metabolismo

Captals passa a representar o sistema multidimensional que observa se transformações aumentam, preservam ou degradam capitais e capacidades do organismo.

Dimensões iniciais de capital:

- financeiro;
- informacional;
- científico;
- tecnológico;
- humano;
- relacional;
- operacional.

Dimensões iniciais de custo/restrição:

- computacional;
- energia;
- tempo;
- memória;
- risco;
- humano;
- cognitivo;
- institucional;
- dívida.

Nenhuma dessas dimensões é reduzida automaticamente a moeda ou a uma nota única.

## 3. Invariantes

```text
TRUST != VALUE != QUALITY != PRICE != CAPITAL

Gate não financia.
Captals não decide verdade científica.
Ciência não libera recurso sozinha.
Ω-Score não substitui Gate, Evidence ou Replay.
Preço é uma expressão econômica possível, não a ontologia do valor.
Perda em uma dimensão não é compensada automaticamente por ganho em outra.
```

## 4. Fusão arquitetural

```text
                         MATVERSE / ORGANISMO
                                  |
                    hipótese / capacidade / ação
                                  |
                                  v
                               URANO
                         experimento/evidência
                                  |
                                  v
                              Ω-GATE
                         PASS | HOLD | BLOCK
                                  |
                    evidence + replay + receipt
                                  |
                                  v
                              CAPTALS
                  metabolismo de valor e recursos
                 /        |        |        |       \
                v         v        v        v        v
            ciência    tecnologia  info   pessoas  operação
                 \        |        |        |       /
                  \-------+--------+--------+------/
                                  |
                            alocação elegível
                                  |
                                  v
                              SYMBIOS
                               execução
                                  |
                                  v
                         produto / API / mercado
                                  |
                                  v
                         Ω-CAPITALS / LUA-PAY
                   mercado, liquidez, preço, receita
                                  |
                                  v
                       realização econômica parcial
                                  |
                                  +-------> CAPTALS
                                            feedback
```

Ω-Capitals deixa de ser "o Captals inteiro" e passa a ser uma de suas superfícies econômicas.

## 5. Relação com MNB / mem-bit / m-bit

A integração preserva o cânone atual dessas primitivas e não as redefine:

```text
MNB      = mem-nano-bit = informacional = substrato
mem-bit  = digital      = contrato
m-bit    = físico       = item
```

Captals pode observar consequências de valor, custo e capacidade associadas a qualquer uma dessas primitivas sem convertê-las automaticamente em preço ou capital financeiro.

O campo `m_bit_ref`, quando presente em um evento metabólico, referencia explicitamente um **m-bit físico/item**; ele não representa uma nota, um score ou um marco abstrato.

## 6. Regra de instrumentação

Uma dimensão só entra no runtime quando possui observação com:

```json
{
  "value": 1.0,
  "unit": "validated_milestone",
  "instrument": "evidence_pack_validator"
}
```

Sem instrumento e unidade, a dimensão deve permanecer em especificação e não participar da decisão operacional.

## 7. Avaliação metabólica

A implementação não calcula um "super score".

Ela classifica o vetor de capitais:

- `ACCUMULATING`: pelo menos uma dimensão melhora e nenhuma piora;
- `DEGRADING`: pelo menos uma piora e nenhuma melhora;
- `TRADEOFF`: há ganhos e perdas em dimensões diferentes;
- `NEUTRAL`: nenhuma mudança instrumentada.

Depois aplica as fronteiras externas e orçamentárias:

```text
BLOCK externo                         -> INELIGIBLE
HOLD externo                          -> HOLD
evidência não verificada              -> HOLD
replay não exato                      -> HOLD
orçamento dimensional excedido        -> INELIGIBLE
degradação sem dimensão positiva      -> INELIGIBLE
tradeoff entre dimensões              -> HOLD até política explícita
mudança nula                          -> HOLD
acumulação não-negativa instrumentada -> ELIGIBLE
```

`ELIGIBLE` significa elegível para alocação pelo Captals; não significa execução automática.

## 8. Adapter Ω-Capitals

O endpoint legado normaliza sinais como:

- Ω-Score;
- TVL;
- volume;
- fees;
- APR.

A saída declara explicitamente:

```text
classification               = LEGACY_MARKET_SIGNAL
trust_implication             = NONE
authorization_implication     = NONE
canonical_use                 = CAPTALS_MARKET_CONTEXT
```

Isso permite reaproveitar a engenharia histórica sem promover métricas financeiras a evidência científica ou autorização constitucional.

## 9. API adicionada

```text
GET  /api/captals/schema
POST /api/captals/evaluate
POST /api/captals/legacy/omega
```

## 10. Arquivos

```text
backend/services/captals_metabolism.py
backend/routes/captals.py
backend/test_captals_metabolism.py
backend/main.py
CAPTALS_FUSION.md
```

## 11. Próxima evolução

A fusão atual fecha o contrato sem destruir o legado. As extensões seguintes devem ser incrementais:

1. persistência de eventos metabólicos e lineage;
2. integração com EvidenceOS/receipts reais;
3. referências verificáveis a MNB, mem-bit e m-bit sem colapsar seus tipos;
4. Trail Registry e alocação por eventos/transformações governadas;
5. adapters para custos reais de CPU, energia, tempo e memória;
6. ingestão dos resultados Ω-Capitals como contexto de mercado;
7. integração com Bridge para capital/capacidade externos;
8. dashboard multidimensional sem escalarização prematura.

A regra de evolução é: **consertar e incorporar, não podar o passado.**
