// ============================================
// SOS HAMMOUDI — Schema Maker — app.js
// ============================================

// TODO: Remplacer par l'URL réelle du webhook n8n
const WEBHOOK_URL = 'https://n8n.thomashammoudi.com/webhook/schema-maker';

// --- DOM refs ---
const form = document.getElementById('schema-form');
const emailInput = document.getElementById('email');
const descriptionInput = document.getElementById('description');
const submitBtn = document.getElementById('submit-btn');
const submitText = submitBtn.querySelector('.form__submit-text');
const submitLoading = submitBtn.querySelector('.form__submit-loading');
const resultDiv = document.getElementById('result');
const resultSuccess = document.getElementById('result-success');
const resultError = document.getElementById('result-error');
const errorMessage = document.getElementById('error-message');

// --- Form submit ---
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideResults();

  const email = emailInput.value.trim();
  if (!email) return;

  const engine = form.querySelector('input[name="engine"]:checked').value;
  const colors = form.querySelector('input[name="colors"]:checked').value;
  const style = form.querySelector('input[name="style"]:checked').value;

  if (!descriptionInput.value.trim()) {
    showError('Décris ton schéma avant de générer !');
    return;
  }

  setLoading(true);

  try {
    const body = new FormData();
    body.append('email', email);
    body.append('mode', 'describe');
    body.append('engine', engine);
    body.append('colors', colors);
    body.append('style', style);
    body.append('description', descriptionInput.value.trim());

    const minDelay = new Promise(resolve => setTimeout(resolve, 3000));

    const [response] = await Promise.all([
      fetch(WEBHOOK_URL, { method: 'POST', body }),
      minDelay,
    ]);

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 403) {
        showError('Email non autorisé. Contacte l\'admin pour obtenir un accès.');
      } else if (response.status === 429) {
        showError('Quota quotidien atteint ! Reviens demain.');
      } else {
        showError(data.message || 'Une erreur est survenue. Réessaie plus tard.');
      }
      return;
    }

    showSuccess();
  } catch (err) {
    showError('Impossible de contacter le serveur. Vérifie ta connexion.');
  } finally {
    setLoading(false);
  }
});

// --- UI helpers ---
function setLoading(loading) {
  submitBtn.disabled = loading;
  submitText.hidden = loading;
  submitLoading.hidden = !loading;
}

function hideResults() {
  resultDiv.hidden = true;
  resultSuccess.hidden = true;
  resultError.hidden = true;
}

function showSuccess() {
  resultDiv.hidden = false;
  resultSuccess.hidden = false;
  resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showError(msg) {
  resultDiv.hidden = false;
  resultError.hidden = false;
  errorMessage.textContent = msg;
  resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
