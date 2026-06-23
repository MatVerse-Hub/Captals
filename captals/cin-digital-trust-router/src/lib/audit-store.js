import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeAuditPayload } from './log-sanitizer.js';
import { assertCallerDoesNotSetHashes, assertLedgerFields } from './ledger-policy.js';

const GENESIS = '0'.repeat(64);

function canon(value) {
  if (Array.isArray(value)) return `[${value.map(canon).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canon(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

export class AuditStore {
  constructor({ ledgerPath = './audit/events.jsonl' } = {}) {
    this.ledgerPath = ledgerPath;
    this.serial = Promise.resolve();
  }

  digest(value) {
    return crypto.createHash('sha256').update(canon(value), 'utf8').digest('hex');
  }

  async append(event) {
    const work = this.serial.then(async () => {
      assertCallerDoesNotSetHashes(event);
      assertLedgerFields(event);
      assertSafeAuditPayload(event);
      await fs.mkdir(path.dirname(this.ledgerPath), { recursive: true, mode: 0o700 });

      const integrity = await this.verify();
      if (!integrity.valid) throw new Error('LEDGER_INTEGRITY_INVALID');

      const payload = {
        ...event,
        schema_version: 'audit-event.v1',
        created_at: new Date().toISOString(),
        previous_event_hash: integrity.head
      };
      assertLedgerFields(payload);
      assertSafeAuditPayload(payload);

      const event_hash = this.digest(payload);
      const record = { ...payload, event_hash };
      assertLedgerFields(record);
      assertSafeAuditPayload(record);

      const file = await fs.open(this.ledgerPath, 'a', 0o600);
      try {
        await file.writeFile(`${JSON.stringify(record)}\n`, 'utf8');
        await file.sync();
      } finally {
        await file.close();
      }
      return { recorded: true, previous_event_hash: integrity.head, event_hash };
    });
    this.serial = work.catch(() => undefined);
    return work;
  }

  async verify() {
    let text = '';
    try {
      text = await fs.readFile(this.ledgerPath, 'utf8');
    } catch (error) {
      if (error?.code === 'ENOENT') return { valid: true, records: 0, head: GENESIS };
      throw error;
    }

    let previous = GENESIS;
    let records = 0;
    for (const line of text.split('\n').map((item) => item.trim()).filter(Boolean)) {
      try {
        const record = JSON.parse(line);
        assertLedgerFields(record);
        assertSafeAuditPayload(record);
        const { event_hash, ...payload } = record;
        if (!/^[a-f0-9]{64}$/.test(event_hash || '')) return { valid: false, records, head: previous, reason: 'EVENT_HASH_INVALID' };
        if (payload.previous_event_hash !== previous) return { valid: false, records, head: previous, reason: 'CHAIN_LINK_MISMATCH' };
        if (this.digest(payload) !== event_hash) return { valid: false, records, head: previous, reason: 'EVENT_HASH_MISMATCH' };
        previous = event_hash;
        records += 1;
      } catch (error) {
        return { valid: false, records, head: previous, reason: error.message };
      }
    }
    return { valid: true, records, head: previous };
  }
}
