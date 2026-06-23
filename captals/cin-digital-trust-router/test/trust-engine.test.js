import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { TrustEngine } from '../src/lib/trust-engine.js';

const reference = 'sandbox:proof:reference:0001';

test('generates a stable token for an opaque reference and transaction', () => {
  const engine = new TrustEngine();
  const sessionSalt = crypto.randomBytes(32).toString('hex');
  const transactionId = crypto.randomUUID();
  const first = engine.generateAuditToken({ proofReference: reference, sessionSalt, transactionId });
  const second = engine.generateAuditToken({ proofReference: reference, sessionSalt, transactionId });
  assert.equal(first, second);
  assert.match(first, /^[a-f0-9]{64}$/);
});

test('sandbox holds until official assurance exists', async () => {
  const engine = new TrustEngine({ mode: 'sandbox', trustedIssuerStates: ['SP'] });
  const outcome = await engine.evaluate({ auditToken: 'a'.repeat(64), issuerState: 'SP' });
  assert.equal(outcome.status, 'UNVERIFIED');
  assert.equal(outcome.gate, 'HOLD');
});

test('untrusted issuer blocks evaluation', async () => {
  const engine = new TrustEngine({ mode: 'sandbox', trustedIssuerStates: ['SP'] });
  const outcome = await engine.evaluate({ auditToken: 'a'.repeat(64), issuerState: 'ZZ' });
  assert.equal(outcome.gate, 'BLOCK');
});
