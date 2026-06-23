const api = window.location.origin;
const sessionButton = document.getElementById('sessionButton');
const evaluateButton = document.getElementById('evaluateButton');
const sessionOut = document.getElementById('sessionOut');
const evaluateOut = document.getElementById('evaluateOut');
const sessionIdInput = document.getElementById('sessionId');
const proofReferenceInput = document.getElementById('proofReference');
const issuerStateInput = document.getElementById('issuerState');

async function readResponse(response) {
  const payload = await response.json().catch(() => ({ reason: 'INVALID_JSON_RESPONSE' }));
  if (!response.ok && !payload.reason) payload.reason = `HTTP_${response.status}`;
  return payload;
}

sessionButton.addEventListener('click', async () => {
  sessionButton.disabled = true;
  try {
    const response = await fetch(`${api}/api/session/start`, { method: 'POST' });
    const payload = await readResponse(response);
    if (!response.ok) throw new Error(payload.reason);
    sessionIdInput.value = payload.sessionId;
    sessionOut.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    sessionOut.textContent = JSON.stringify({ gate: 'HOLD', reason: error.message }, null, 2);
  } finally {
    sessionButton.disabled = false;
  }
});

evaluateButton.addEventListener('click', async () => {
  evaluateButton.disabled = true;
  const body = {
    sessionId: sessionIdInput.value.trim(),
    proofReference: proofReferenceInput.value.trim(),
    issuerState: issuerStateInput.value.trim().toUpperCase()
  };
  try {
    const response = await fetch(`${api}/api/trust/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    evaluateOut.textContent = JSON.stringify(await readResponse(response), null, 2);
  } catch (error) {
    evaluateOut.textContent = JSON.stringify({ gate: 'HOLD', reason: error.message }, null, 2);
  } finally {
    proofReferenceInput.value = '';
    evaluateButton.disabled = false;
  }
});
