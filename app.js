// ============================================
// SOS HAMMOUDI — Schema Maker — app.js
// ============================================

// TODO: Remplacer par l'URL réelle du webhook n8n
const WEBHOOK_URL = 'https://n8n.thomashammoudi.com/webhook/schema-maker';

// --- DOM refs ---
const form = document.getElementById('schema-form');
const emailInput = document.getElementById('email');
const descriptionInput = document.getElementById('description');
const fileInput = document.getElementById('file-input');
const uploadZone = document.getElementById('upload-zone');
const filePreview = document.getElementById('file-preview');
const fileName = document.getElementById('file-name');
const fileRemove = document.getElementById('file-remove');
const submitBtn = document.getElementById('submit-btn');
const submitText = submitBtn.querySelector('.form__submit-text');
const submitLoading = submitBtn.querySelector('.form__submit-loading');
const resultDiv = document.getElementById('result');
const resultSuccess = document.getElementById('result-success');
const resultError = document.getElementById('result-error');
const errorMessage = document.getElementById('error-message');

// --- Tabs ---
document.querySelectorAll('.tabs__btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;

    // Toggle active button
    document.querySelectorAll('.tabs__btn').forEach(b => b.classList.remove('tabs__btn--active'));
    btn.classList.add('tabs__btn--active');

    // Toggle active panel
    document.querySelectorAll('.tabs__panel').forEach(p => p.classList.remove('tabs__panel--active'));
    document.getElementById(`panel-${tab}`).classList.add('tabs__panel--active');
  });
});

// --- File upload ---
fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    showFilePreview(fileInput.files[0].name);
  }
});

// Drag & drop
uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('form__upload--dragover');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('form__upload--dragover');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('form__upload--dragover');
  if (e.dataTransfer.files.length > 0) {
    fileInput.files = e.dataTransfer.files;
    showFilePreview(e.dataTransfer.files[0].name);
  }
});

function showFilePreview(name) {
  uploadZone.hidden = true;
  filePreview.hidden = false;
  fileName.textContent = name;
}

fileRemove.addEventListener('click', () => {
  fileInput.value = '';
  uploadZone.hidden = false;
  filePreview.hidden = true;
});

// --- Form submit ---
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideResults();

  const email = emailInput.value.trim();
  if (!email) return;

  // Determine active mode
  const activeTab = document.querySelector('.tabs__btn--active').dataset.tab;
  const engine = form.querySelector('input[name="engine"]:checked').value;
  const colors = form.querySelector('input[name="colors"]:checked').value;
  const style = form.querySelector('input[name="style"]:checked').value;

  // Validate: need either description or file
  if (activeTab === 'describe' && !descriptionInput.value.trim()) {
    showError('Décris ton schéma avant de générer !');
    return;
  }
  if (activeTab === 'upload' && !fileInput.files.length) {
    showError('Charge un fichier avant de générer !');
    return;
  }

  setLoading(true);

  try {
    const body = new FormData();
    body.append('email', email);
    body.append('mode', activeTab);
    body.append('engine', engine);
    body.append('colors', colors);
    body.append('style', style);

    if (activeTab === 'describe') {
      body.append('description', descriptionInput.value.trim());
    } else {
      body.append('file', fileInput.files[0]);
    }

    const response = await fetch(WEBHOOK_URL, {
      method: 'POST',
      body,
    });

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
