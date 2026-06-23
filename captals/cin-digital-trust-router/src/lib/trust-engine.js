import crypto from 'node:crypto';

const VALID_STATES = new Set([
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
  'SP', 'SE', 'TO'
]);

export class TrustEngine {
  constructor({ mode = 'sandbox', trustedIssuerStates = [...VALID_STATES] } = {}) {
    this.mode = mode;
    this.trustedIssuerStates = new Set(trustedIssuerStates);
  }

  validateProofReference(reference) {
    return typeof reference === 'string' && /^[A-Za-z0-9._:-]{16,256}$/.test(reference);
  }

  generateAuditToken({ proofReference, sessionSalt, transactionId }) {
    if (!this.validateProofReference(proofReference)) {
      throw new Error('INVALID_PROOF_REFERENCE');
    }

    if (!/^[a-f0-9]{64}$/i.test(sessionSalt)) {
      throw new Error('INVALID_SESSION_SALT');
    }

    const hmac = crypto.createHmac('sha256', Buffer.from(sessionSalt, 'hex'));
    hmac.update(`${proofReference}:${transactionId}`, 'utf8');
    return hmac.digest('hex');
  }

  createStorageFingerprint(auditToken) {
    return crypto.createHash('sha256').update(auditToken, 'utf8').digest('hex');
  }

  verifyIssuer(issuerState) {
    const state = String(issuerState || '').toUpperCase();
    return VALID_STATES.has(state) && this.trustedIssuerStates.has(state);
  }

  async evaluate({ auditToken, issuerState }) {
    const issuerTrusted = this.verifyIssuer(issuerState);
    const tokenWellFormed = /^[a-f0-9]{64}$/i.test(auditToken);

    if (!issuerTrusted || !tokenWellFormed) {
      return {
        status: 'INVALID',
        gate: 'BLOCK',
        reason: !issuerTrusted ? 'UNTRUSTED_ISSUER' : 'INVALID_AUDIT_TOKEN',
        source: this.mode,
        issuerTrusted,
        signatureValid: false
      };
    }

    if (this.mode === 'sandbox') {
      return {
        status: 'UNVERIFIED',
        gate: 'HOLD',
        reason: 'SANDBOX_NO_OFFICIAL_ASSURANCE',
        source: 'sandbox',
        issuerTrusted,
        signatureValid: false
      };
    }

    return {
      status: 'UNVERIFIED',
      gate: 'HOLD',
      reason: 'OFFICIAL_CONNECTOR_REQUIRED',
      source: 'official-connector-required',
      issuerTrusted,
      signatureValid: false
    };
  }
}
