const FORBIDDEN_FIELD_NAMES = new Set([
  'personal_identifier',
  'document_number',
  'national_id',
  'raw_identifier',
  'identity_number'
]);

function normalizedKey(key) {
  return String(key).trim().toLowerCase();
}

function isForbiddenFieldName(key) {
  return FORBIDDEN_FIELD_NAMES.has(normalizedKey(key));
}

export function sanitizeValue(value, key = '') {
  if (isForbiddenFieldName(key)) {
    return '[REDACTED]';
  }

  if (Array.isArray(value)) {
    return value.map((item) => sanitizeValue(item));
  }

  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([entryKey, item]) => [entryKey, sanitizeValue(item, entryKey)])
    );
  }

  return value;
}

export function assertNoSensitiveFields(value) {
  if (Array.isArray(value)) {
    value.forEach((item) => assertNoSensitiveFields(item));
    return;
  }

  if (!value || typeof value !== 'object') {
    return;
  }

  for (const [key, item] of Object.entries(value)) {
    if (isForbiddenFieldName(key)) {
      throw new Error(`SENSITIVE_FIELD_BLOCKED:${key}`);
    }
    assertNoSensitiveFields(item);
  }
}

export function assertSafeAuditPayload(payload) {
  assertNoSensitiveFields(payload);
}

export function createSafeLogger(baseLogger) {
  return {
    info(message, data = {}) {
      baseLogger.info(sanitizeValue(data), message);
    },
    warn(message, data = {}) {
      baseLogger.warn(sanitizeValue(data), message);
    },
    error(message, error, data = {}) {
      baseLogger.error(sanitizeValue({ ...data, error: error?.message ?? String(error) }), message);
    }
  };
}
