const ALLOWED_FIELDS = new Set([
  'audit_id',
  'transaction_id',
  'audit_token_hash',
  'status',
  'gate',
  'reason',
  'issuer',
  'verification',
  'created_at',
  'schema_version',
  'previous_event_hash',
  'event_hash'
]);

export function assertLedgerFields(value) {
  for (const key of Object.keys(value)) {
    if (!ALLOWED_FIELDS.has(key)) {
      throw new Error(`LEDGER_FIELD_BLOCKED:${key}`);
    }
  }
}

export function assertCallerDoesNotSetHashes(value) {
  if ('event_hash' in value || 'previous_event_hash' in value) {
    throw new Error('LEDGER_HASH_FIELDS_SYSTEM_MANAGED');
  }
}
