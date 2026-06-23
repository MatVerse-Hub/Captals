# CIN Digital Trust Router

Infraestrutura Captals para validação autorizada, minimização de dados, evidência e replay em fluxos de identidade digital.

## Escopo

O módulo não emite documento, não cria artefato estatal e não guarda identificadores civis brutos. A entrada operacional é uma `proofReference` opaca, recebida apenas após um fluxo autorizado.

```text
Proof Reference
→ Trust Router
→ Session Salt one-time
→ Audit Token Hash
→ Chained Evidence Ledger
→ Trust Response
```

## Decisão Captals

| Gate | Significado |
|---|---|
| PASS | somente com conector autorizado, assinatura/cadeia confirmadas e evidência válida |
| HOLD | sandbox, conector ausente ou assurance parcial |
| BLOCK | política violada, emissor não confiável ou sessão reutilizada |
| ESCALATE | falha de evidência ou ambiguidade operacional |

No sandbox, a resposta correta é `UNVERIFIED` + `HOLD`.

## Execução

```bash
cd captals/cin-digital-trust-router
npm install
npm test
npm start
```

Abra o demo em `http://localhost:3001/demo/`.

Verifique a cadeia de evidência:

```bash
npm run verify:ledger
```

## Docker

```bash
docker compose up --build
```

O serviço é exposto apenas em `127.0.0.1:3001`. Redis permanece interno e usa armazenamento temporário para salts de sessão.

## Endpoints

```text
GET  /health
POST /api/session/start
POST /api/trust/evaluate
GET  /api/ledger/verify
```

## Requisito para validação oficial

A habilitação de `PASS` exige integração institucional autorizada, validação criptográfica e confirmação de emissor/status. Sem essas provas, o sistema permanece em `HOLD`.
