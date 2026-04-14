// Modal management
const backdrop = document.getElementById('modalBackdrop');

function openModal(id) {
  document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add('active');
    if (backdrop) backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeAllModals() {
  document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
  if (backdrop) backdrop.classList.remove('open');
  document.body.style.overflow = '';
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeAllModals();
});

// Flash message auto-dismiss
document.querySelectorAll('.flash').forEach(function(el) {
  setTimeout(function() {
    el.style.opacity = '0';
    setTimeout(function() { el.remove(); }, 400);
  }, 3500);
});
