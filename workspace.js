(() => {
  const sidebar = document.getElementById('appSidebar');
  const toggle = document.getElementById('sidebarToggle');
  const close = document.getElementById('sidebarClose');
  const backdrop = document.getElementById('sidebarBackdrop');
  if (!sidebar || !toggle || !backdrop) return;
  const setOpen = (open) => {
    sidebar.classList.toggle('is-open', open);
    backdrop.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('nav-open', open);
  };
  toggle.addEventListener('click', () => setOpen(!sidebar.classList.contains('is-open')));
  close?.addEventListener('click', () => setOpen(false));
  backdrop.addEventListener('click', () => setOpen(false));
  sidebar.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setOpen(false)));
  window.addEventListener('keydown', (event) => { if (event.key === 'Escape') setOpen(false); });
  window.addEventListener('resize', () => { if (window.innerWidth > 980) setOpen(false); }, { passive:true });
})();