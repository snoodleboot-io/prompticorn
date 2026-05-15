/* ============================================================
   PROMPTICORN — Multi-Mode script.js
   ============================================================ */

'use strict';

/* ── Mode switching ── */
const MODES = ['startup', 'enterprise', 'engineer'];
const DEFAULT_MODE = 'startup';

function getInitialMode() {
  const hash = window.location.hash.replace('#', '');
  return MODES.includes(hash) ? hash : DEFAULT_MODE;
}

function applyMode(mode, animate) {
  if (!MODES.includes(mode)) mode = DEFAULT_MODE;
  const body = document.body;

  // Update data-mode
  body.dataset.mode = mode;

  // Update pill buttons
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
    btn.setAttribute('aria-selected', btn.dataset.mode === mode ? 'true' : 'false');
  });

  // Update URL hash without scrolling
  history.replaceState(null, '', '#' + mode);

  // Animate main content
  if (animate) {
    const main = document.querySelector('main');
    if (main) {
      main.classList.add('mode-transition');
      setTimeout(() => main.classList.remove('mode-transition'), 260);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // Re-trigger reveal for newly visible elements
  setTimeout(() => {
    document.querySelectorAll('[data-show-mode="' + mode + '"] .reveal').forEach(el => {
      if (!el.classList.contains('visible')) revealObserver.observe(el);
    });
  }, 50);
}

// Attach mode switcher buttons
document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => applyMode(btn.dataset.mode, true));
});

// Init on load
applyMode(getInitialMode(), false);

/* ── Nav scroll state ── */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
  updateActiveNavLink();
}, { passive: true });

/* ── Hamburger menu ── */
const hamburger = document.getElementById('nav-hamburger');
const mobileMenu = document.getElementById('nav-mobile');
hamburger?.addEventListener('click', () => {
  const open = hamburger.classList.toggle('open');
  mobileMenu.classList.toggle('open', open);
  hamburger.setAttribute('aria-expanded', String(open));
});
mobileMenu?.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileMenu.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  });
});

/* ── Active nav link on scroll ── */
function updateActiveNavLink() {
  const sections = document.querySelectorAll('section[id]');
  const scrollY = window.scrollY + 120;
  sections.forEach(sec => {
    const top = sec.offsetTop;
    const bottom = top + sec.offsetHeight;
    const link = document.querySelector(`.nav-links a[href="#${sec.id}"]`);
    if (link) link.classList.toggle('active', scrollY >= top && scrollY < bottom);
  });
}

/* ── Scroll reveal ── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

/* ── Copy to clipboard ── */
document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const wrap = btn.closest('.code-wrap') || btn.closest('.hero-install-strip');
    const pre = wrap?.querySelector('pre') || wrap?.querySelector('.install-cmd');
    const text = pre ? pre.innerText : '';
    if (!text) return;
    navigator.clipboard.writeText(text.trim()).then(() => {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = orig; btn.classList.remove('copied'); }, 2000);
    });
  });
});

/* ── Builder tabs ── */
document.querySelectorAll('.builder-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.target;
    const container = tab.closest('section');
    container?.querySelectorAll('.builder-tab').forEach(t => t.classList.remove('active'));
    container?.querySelectorAll('.builder-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(target)?.classList.add('active');
  });
});

/* ── Install tabs ── */
document.querySelectorAll('.install-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.target;
    document.querySelectorAll('.install-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.install-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(target)?.classList.add('active');
  });
});

/* ── Docs search ── */
const docsSearch = document.getElementById('docs-search');
docsSearch?.addEventListener('input', () => {
  const q = docsSearch.value.toLowerCase().trim();
  document.querySelectorAll('.doc-link').forEach(link => {
    link.classList.toggle('hidden', q.length > 0 && !link.textContent.toLowerCase().includes(q));
  });
});

/* ── D3.js Force Graph ── */
function initD3Graph() {
  const container = document.getElementById('d3-graph');
  if (!container || !window.d3 || container.querySelector('svg')) return;

  const W = container.clientWidth || 480;
  const H = 300;

  const nodes = [
    { id: 'IR Layer', group: 'core' },
    { id: 'Registry', group: 'core' },
    { id: 'BuilderFactory', group: 'core' },
    { id: 'KiloBuilder', group: 'builder' },
    { id: 'ClineBuilder', group: 'builder' },
    { id: 'ClaudeBuilder', group: 'builder' },
    { id: 'CopilotBuilder', group: 'builder' },
    { id: 'CursorBuilder', group: 'builder' },
    { id: 'Persona Filter', group: 'filter' },
    { id: 'Template Engine', group: 'engine' },
  ];

  const links = [
    { source: 'IR Layer', target: 'BuilderFactory' },
    { source: 'Registry', target: 'BuilderFactory' },
    { source: 'BuilderFactory', target: 'KiloBuilder' },
    { source: 'BuilderFactory', target: 'ClineBuilder' },
    { source: 'BuilderFactory', target: 'ClaudeBuilder' },
    { source: 'BuilderFactory', target: 'CopilotBuilder' },
    { source: 'BuilderFactory', target: 'CursorBuilder' },
    { source: 'Persona Filter', target: 'IR Layer' },
    { source: 'Template Engine', target: 'KiloBuilder' },
    { source: 'Template Engine', target: 'ClineBuilder' },
    { source: 'Template Engine', target: 'ClaudeBuilder' },
    { source: 'Template Engine', target: 'CopilotBuilder' },
    { source: 'Template Engine', target: 'CursorBuilder' },
  ];

  const color = { core: '#cc0000', builder: '#555580', filter: '#886600', engine: '#004488' };

  const svg = d3.select(container)
    .append('svg')
    .attr('width', W).attr('height', H)
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%').style('height', 'auto')
    .style('background', 'transparent');

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collision', d3.forceCollide(38));

  const link = svg.append('g').selectAll('line').data(links).join('line')
    .attr('class', 'd3-link').attr('stroke', '#1a1a28').attr('stroke-width', 1.5);

  const node = svg.append('g').selectAll('g').data(nodes).join('g')
    .attr('class', 'd3-node')
    .call(d3.drag()
      .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
      .on('end', (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

  node.append('circle')
    .attr('r', d => d.group === 'core' ? 16 : 12)
    .attr('fill', d => color[d.group] + '33')
    .attr('stroke', d => color[d.group])
    .attr('stroke-width', 1.5);

  node.append('text')
    .attr('text-anchor', 'middle').attr('dy', '0.35em')
    .attr('y', d => (d.group === 'core' ? 16 : 12) + 14)
    .style('fill', '#8888a0').style('font-size', '10px')
    .text(d => d.id);

  sim.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  const ro = new ResizeObserver(() => {
    const w = container.clientWidth;
    if (w > 0) {
      svg.attr('viewBox', `0 0 ${w} ${H}`);
      sim.force('center', d3.forceCenter(w / 2, H / 2)).alpha(0.15).restart();
    }
  });
  ro.observe(container);
}

/* ── Mermaid init ── */
function initMermaid() {
  if (!window.mermaid) return;
  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {
      background: '#050508',
      primaryColor: '#1a1a28',
      primaryTextColor: '#f0f0f5',
      primaryBorderColor: '#cc0000',
      lineColor: '#cc0000',
      secondaryColor: '#0a0a0f',
      tertiaryColor: '#0f0f16',
      edgeLabelBackground: '#050508',
      fontFamily: 'Inter, Space Grotesk, system-ui, sans-serif',
      fontSize: '13px',
    },
    securityLevel: 'loose',
  });

  document.querySelectorAll('.mermaid').forEach(async (el) => {
    const graphDef = el.getAttribute('data-content');
    if (!graphDef || el.dataset.rendered) return;
    el.dataset.rendered = '1';
    try {
      const id = 'mermaid-' + Math.random().toString(36).slice(2);
      const { svg } = await mermaid.render(id, graphDef);
      el.innerHTML = svg;
    } catch (e) {
      el.innerHTML = '<p style="color:#886600;font-size:0.8rem;padding:1rem;">Diagram unavailable</p>';
    }
  });
}

/* ── Lazy-load diagrams ── */
let d3Loaded = false;
let mermaidLoaded = false;

function loadScript(src, cb) {
  const s = document.createElement('script');
  s.src = src;
  s.onload = cb;
  s.onerror = () => console.warn('Failed to load:', src);
  document.head.appendChild(s);
}

const diagramObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    if (e.target.id === 'd3-graph' && !d3Loaded) {
      d3Loaded = true;
      if (window.d3) { initD3Graph(); }
      else { loadScript('https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js', initD3Graph); }
    }
    if (e.target.classList.contains('mermaid-wrap') && !mermaidLoaded) {
      mermaidLoaded = true;
      if (window.mermaid) { initMermaid(); }
      else {
        loadScript('https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js', () => {
          window.mermaid = window.mermaid || mermaid;
          initMermaid();
        });
      }
    }
    diagramObserver.unobserve(e.target);
  });
}, { threshold: 0.1 });

document.querySelectorAll('#d3-graph, .mermaid-wrap').forEach(el => diagramObserver.observe(el));

/* ── Prism highlight ── */
document.addEventListener('DOMContentLoaded', () => {
  if (window.Prism) Prism.highlightAll();
});

/* ── Accessible colours toggle ── */
const accessibleColorsBtn = document.getElementById('accessible-colors-btn');
const ACCESSIBLE_COLORS_KEY = 'prompticorn-accessible-colors';

function applyAccessibleColors(enabled, persist) {
  document.body.toggleAttribute('data-accessible-colors', enabled);
  accessibleColorsBtn?.classList.toggle('active', enabled);
  accessibleColorsBtn?.setAttribute('aria-pressed', String(enabled));
  if (persist) localStorage.setItem(ACCESSIBLE_COLORS_KEY, enabled ? '1' : '0');
}

accessibleColorsBtn?.addEventListener('click', () => {
  applyAccessibleColors(!document.body.hasAttribute('data-accessible-colors'), true);
});

applyAccessibleColors(localStorage.getItem(ACCESSIBLE_COLORS_KEY) === '1', false);

/* ── Smooth scroll for anchor links ── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const href = a.getAttribute('href');
    // Don't intercept mode-hash links
    if (MODES.includes(href.replace('#', ''))) return;
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      const y = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  });
});
