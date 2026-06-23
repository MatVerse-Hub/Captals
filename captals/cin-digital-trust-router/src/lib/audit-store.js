import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeAuditPayload } from './log-sanitizer.js';

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

  async head() {
    try {
      const text = await fs.readFile(this.ledgerPath, 'utf8');
      const line = text.split('\n').map((item) => item.trim()).filter(Boolean).at(-1);
      return line ? JSON.parse(line).event_hash : GENESIS;
    } catch (error) {
      if (error?.code === 'ENOENT') return GENESIS;
      throw error;
    }
  }

  async append(event) {
    const work = this.serial.then(async () => {
      assertSafeAuditPayload(event);
      await fs.mkdir(path.dirname(this.ledgerPath), { recursive: true, mode: 0o700 });
      const previous_event_hash = await this.head();
      const payload = {
        ...event,
        schema_version: 'audit-event.v1',
        created_at: new Date().toISOString(),
        previous_event_hash
      };
      const event_hash = this.digest(payload);
      const record = { ...payload, event_hash };
      assertSafeAuditPayload(record);
      const file = await fs.open(this.ledgerPath, 'a', 0o600);
      try {
        await file.writeFile(`${JSON.stringify(record)}\n`, 'utf8');
        await file.sync();
      } finally {
        await file.close();
      }
      return { recorded: true, previous_event_hash, event_hash };
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
      const record = JSON.parse(line);
      const { event_hash, ...payload } = record;
      if (payload.previous_event_hash !== previous || this.digest(payload) !== event_hash) {
        return { valid: false, records, head: previous };
      }
      previous = event_hash;
      records += 1;
    }
    return { valid: true, records, head: previous };
  }
}
