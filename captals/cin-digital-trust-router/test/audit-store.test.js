import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { AuditStore } from '../src/lib/audit-store.js';

function event() {
  return {
    audit_id: crypto.randomUUID(),
    transaction_id: crypto.randomUUID(),
    audit_token_hash: crypto.createHash('sha256').update(crypto.randomUUID()).digest('hex'),
    status: 'UNVERIFIED',
    gate: 'HOLD',
    reason: 'SANDBOX_NO_OFFICIAL_ASSURANCE',
    issuer: { country: 'BR', state_code: 'SP', agency_id: 'SANDBOX-SP-001' },
    verification: { proof_reference_accepted: true, issuer_trusted: true, signature_valid: false, source: 'sandbox' }
  };
}

test('chains records and detects integrity changes', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'trust-ledger-'));
  const ledgerPath = path.join(directory, 'events.jsonl');
  const ledger = new AuditStore({ ledgerPath });
  try {
    const first = await ledger.append(event());
    const second = await ledger.append(event());
    assert.equal(second.previous_event_hash, first.event_hash);
    assert.equal((await ledger.verify()).valid, true);
    const text = await fs.readFile(ledgerPath, 'utf8');
    await fs.writeFile(ledgerPath, text.replace('SANDBOX_NO_OFFICIAL_ASSURANCE', 'TAMPERED'), 'utf8');
    assert.equal((await ledger.verify()).valid, false);
  } finally {
    await fs.rm(directory, { recursive: true, force: true });
  }
});
