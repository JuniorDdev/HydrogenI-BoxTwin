function ensureToastContainer() {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  }
  return container;
}

function dismissToast(toast) {
  toast.classList.remove('visible');
  toast.addEventListener('transitionend', () => toast.remove(), { once: true });
}

function showToast(message, type = 'info', timeout = 4500) {
  const container = ensureToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
  const text = document.createElement('p');
  text.textContent = message;
  toast.appendChild(text);
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('visible'));
  const timer = setTimeout(() => dismissToast(toast), timeout);
  toast.addEventListener('click', () => { clearTimeout(timer); dismissToast(toast); });
  return toast;
}

function showConfirmToast(message, onConfirm, options = {}) {
  const container = ensureToastContainer();
  const toast = document.createElement('div');
  toast.className = 'toast toast-confirm';
  toast.setAttribute('role', 'alertdialog');
  const text = document.createElement('p');
  text.textContent = message;
  const actions = document.createElement('div');
  actions.className = 'toast-actions';
  const cancelButton = document.createElement('button');
  cancelButton.type = 'button';
  cancelButton.className = 'toast-cancel-btn';
  cancelButton.textContent = options.cancelLabel || 'Cancelar';
  const confirmButton = document.createElement('button');
  confirmButton.type = 'button';
  confirmButton.className = 'toast-confirm-btn';
  confirmButton.textContent = options.confirmLabel || 'Confirmar';
  confirmButton.addEventListener('click', () => { dismissToast(toast); onConfirm(); });
  cancelButton.addEventListener('click', () => dismissToast(toast));
  actions.append(cancelButton, confirmButton);
  toast.append(text, actions);
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('visible'));
  confirmButton.focus();
  return toast;
}
