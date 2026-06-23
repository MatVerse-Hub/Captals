import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import express from 'express';
import helmet from 'helmet';
import pino from 'pino';
import Ajv from 'ajv';
import dotenv from 'dotenv';
import { SessionManager, SessionStoreUnavailableError } from './lib/session-manager.js';
import { TrustEngine } from './lib/trust-engine.js';
import { AuditStore } from './lib/audit-store.js';
import { createSafeLogger } from './lib/log-sanitizer.js';

dotenv.config();

const moduleDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(moduleDirectory, '../frontend');

function loadConfig() {
  const configPath = process.env.CIN_ROUTER_CONFIG || './config.example.json';
  return fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')) : {};
}

function responseStatus(gate) {
  if (gate === 'PASS') return 200;
  if (gate === 'HOLD') return 202;
  if (gate === 'ESCALATE') return 409;
  return 400;
}

const config = loadConfig();
const mode = process.env.TRUST_ROUTER_MODE || config.trust_router_mode || 'sandbox';
const port = Number(process.env.PORT || config.port || 3001);
const logger = createSafeLogger(pino({ level: process.env.LOG_LEVEL || 'info' }));
const sessions = new SessionManager({ redisUrl: process.env.REDIS_URL || config.redis_url || '' });
const engine = new TrustEngine({ mode, trustedIssuerStates: config.trusted_issuer_states });
const ledger = new AuditStore({ ledgerPath: process.env.AUDIT_LEDGER_PATH || config.audit_ledger_path || './audit/events.jsonl' });
const ajv = new Ajv({ allErrors: true });
const requestValidator = ajv.compile({
  type: 'object',
  additionalProperties: false,
  required: ['sessionId', 'proofReference', 'issuerState'],
  properties: {
    sessionId: { type: 'string', pattern: '^[0-9a-fA-F-]{36}$' },
    proofReference: { type: 'string', pattern: '^[A-Za-z0-9._:-]{16,256}$' },
    issuerState: { type: 'string', pattern: '^[A-Za-z]{2}$' }
  }
});

const app = express();
app.disable('x-powered-by');
app.use(helmet());
app.use(express.json({ limit: '16kb', strict: true }));
app.get('/', (_req, res) => res.redirect(302, '/demo/'));
app.use('/demo', express.static(frontendDirectory, { index: 'wallet-demo.html', maxAge: '1h' }));

app.get('/health', (_req, res) => res.json({ ok: true, service: 'cin-digital-trust-router', mode }));
app.get('/api/ledger/verify', async (_req, res) => {
  try {
    return res.json(await ledger.verify());
  } catch (error) {
    logger.error('ledger verification failed', error);
    return res.status(409).json({ valid: false, gate: 'ESCALATE', reason: 'AUDIT_EVIDENCE_UNAVAILABLE' });
  }
});

app.post('/api/session/start', async (_req, res) => {
  try {
    const session = await sessions.createSession();
    return res.status(201).json({ sessionId: session.sessionId, ttlSeconds: session.ttlSeconds });
  } catch (error) {
    logger.error('session creation held', error);
    return res.status(503).json({ status: 'UNVERIFIED', gate: 'HOLD', reason: 'SESSION_STORE_UNAVAILABLE' });
  }
});

app.post('/api/trust/evaluate', async (req, res) => {
  const body = req.body ?? {};
  if (!requestValidator(body)) {
    logger.warn('trust request schema rejected', { errors: requestValidator.errors });
    return res.status(400).json({ status: 'INVALID', gate: 'BLOCK', reason: 'INVALID_REQUEST_SCHEMA' });
  }

  const transactionId = crypto.randomUUID();
  const auditId = crypto.randomUUID();
  try {
    const salt = await sessions.consumeSalt(body.sessionId);
    if (!salt) return res.status(401).json({ status: 'UNVERIFIED', gate: 'BLOCK', reason: 'SESSION_EXPIRED_OR_REUSED' });

    const auditToken = engine.generateAuditToken({
      proofReference: body.proofReference,
      sessionSalt: salt,
      transactionId
    });
    const outcome = await engine.evaluate({ auditToken, issuerState: body.issuerState.toUpperCase() });
    const audit_token_hash = engine.createStorageFingerprint(auditToken);
    const issuer = {
      country: 'BR',
      state_code: body.issuerState.toUpperCase(),
      agency_id: mode === 'sandbox' ? `SANDBOX-${body.issuerState.toUpperCase()}-001` : `OFFICIAL-${body.issuerState.toUpperCase()}`
    };
    const verification = {
      proof_reference_accepted: true,
      issuer_trusted: outcome.issuerTrusted,
      signature_valid: outcome.signatureValid,
      source: outcome.source
    };
    const audit = await ledger.append({
      audit_id: auditId,
      transaction_id: transactionId,
      audit_token_hash,
      status: outcome.status,
      gate: outcome.gate,
      reason: outcome.reason,
      issuer,
      verification
    });

    return res.status(responseStatus(outcome.gate)).json({
      status: outcome.status,
      gate: outcome.gate,
      reason: outcome.reason,
      issuer,
      verification,
      audit: { audit_id: auditId, transaction_id: transactionId, audit_token_hash, ...audit }
    });
  } catch (error) {
    if (error instanceof SessionStoreUnavailableError) {
      return res.status(503).json({ status: 'UNVERIFIED', gate: 'HOLD', reason: 'SESSION_STORE_UNAVAILABLE' });
    }
    logger.error('trust evaluation failed', error, { transactionId, auditId });
    return res.status(409).json({ status: 'UNVERIFIED', gate: 'ESCALATE', reason: 'AUDIT_EVIDENCE_UNAVAILABLE' });
  } finally {
    if (typeof body.proofReference === 'string') body.proofReference = '';
  }
});

app.listen(port, () => logger.info('trust router started', { port, mode, demo: '/demo/' }));
