/* ============================================================
   PROMPTOSAURUS — script.js
   Vanilla JS: nav, tabs, copy, mermaid, D3, search, animations
   ============================================================ */

'use strict';

/* ────────────────────────────────────────────────────────────
   UTILITY
──────────────────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function debounce(fn, delay) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

/* ────────────────────────────────────────────────────────────
   NAVIGATION: sticky + hamburger
──────────────────────────────────────────────────────────── */
(function initNav() {
  const navbar    = $('#navbar');
  const hamburger = $('#nav-hamburger');
  const navMenu   = $('#nav-menu');
  const navLinks  = $$('.nav-links a');

  // Sticky scroll styling
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });

  // Hamburger toggle
  hamburger.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close menu when link clicked
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && navMenu.classList.contains('open')) {
      navMenu.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      hamburger.focus();
    }
  });
})();

/* ────────────────────────────────────────────────────────────
   BACK TO TOP
──────────────────────────────────────────────────────────── */
(function initBackToTop() {
  const btn = $('#back-to-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

/* ────────────────────────────────────────────────────────────
   COPY TO CLIPBOARD
──────────────────────────────────────────────────────────── */
(function initCopyButtons() {
  async function copyText(text, btn) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Fallback
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }

    const originalHTML = btn.innerHTML;
    btn.classList.add('copied');
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = originalHTML;
    }, 2000);
  }

  // Buttons with data-copy attribute (inline text)
  $$('[data-copy]').forEach(btn => {
    btn.addEventListener('click', () => copyText(btn.dataset.copy, btn));
  });

  // Buttons inside code-block-wrapper (copy sibling pre > code text)
  $$('.code-block-wrapper .copy-btn:not([data-copy])').forEach(btn => {
    btn.addEventListener('click', () => {
      const pre = btn.closest('.code-block-wrapper').querySelector('pre code');
      if (pre) copyText(pre.textContent, btn);
    });
  });
})();

/* ────────────────────────────────────────────────────────────
   TABS (Getting Started section)
──────────────────────────────────────────────────────────── */
(function initTabs() {
  const tabBtns   = $$('.tab-btn');
  const tabPanels = $$('.tab-panel');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('aria-controls');

      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      tabPanels.forEach(p => {
        p.classList.remove('active');
        p.hidden = true;
      });

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const panel = $('#' + targetId);
      if (panel) {
        panel.classList.add('active');
        panel.hidden = false;
        // Re-highlight Prism in the newly shown panel
        if (window.Prism) Prism.highlightAllUnder(panel);
      }
    });

    // Keyboard nav
    btn.addEventListener('keydown', e => {
      const tabs = $$('[role="tab"]');
      const idx  = tabs.indexOf(e.target);
      let next;
      if (e.key === 'ArrowRight') next = tabs[(idx + 1) % tabs.length];
      if (e.key === 'ArrowLeft')  next = tabs[(idx - 1 + tabs.length) % tabs.length];
      if (next) { next.focus(); next.click(); }
    });
  });
})();

/* ────────────────────────────────────────────────────────────
   DOCS SEARCH (client-side filter)
──────────────────────────────────────────────────────────── */
(function initDocsSearch() {
  const input      = $('#docs-search');
  const categories = $$('.docs-category');
  const links      = $$('.docs-link');

  if (!input) return;

  // Focus with / key
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });

  const filterDocs = debounce(() => {
    const q = input.value.trim().toLowerCase();

    if (!q) {
      categories.forEach(c => { c.hidden = false; });
      links.forEach(l => { l.parentElement.hidden = false; });
      return;
    }

    categories.forEach(cat => {
      const catLinks = $$('.docs-link', cat);
      let anyVisible = false;
      catLinks.forEach(link => {
        const text    = link.textContent.toLowerCase();
        const matches = text.includes(q);
        link.parentElement.hidden = !matches;
        if (matches) anyVisible = true;
      });
      cat.hidden = !anyVisible;
    });
  }, 150);

  input.addEventListener('input', filterDocs);
})();

/* ────────────────────────────────────────────────────────────
   INTERSECTION OBSERVER — animate sections on scroll
──────────────────────────────────────────────────────────── */
(function initScrollAnimations() {
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

  $$('.feature-card, .builder-card, .example-item, .docs-category, .pipeline-step').forEach(el => {
    observer.observe(el);
  });
})();

/* ────────────────────────────────────────────────────────────
   HERO PARTICLES
──────────────────────────────────────────────────────────── */
(function initHeroParticles() {
  const container = $('#hero-particles');
  if (!container) return;

  const NUM = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 40;

  for (let i = 0; i < NUM; i++) {
    const dot = document.createElement('div');
    dot.style.cssText = `
      position: absolute;
      width: ${Math.random() * 2 + 1}px;
      height: ${Math.random() * 2 + 1}px;
      background: hsl(${Math.random() > 0.5 ? 150 : 190}, 100%, 70%);
      border-radius: 50%;
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 100}%;
      opacity: ${Math.random() * 0.4 + 0.05};
      animation: particle-float ${Math.random() * 20 + 15}s linear ${Math.random() * -20}s infinite;
    `;
    container.appendChild(dot);
  }

  // Inject particle keyframes if not already present
  if (!document.getElementById('particle-style')) {
    const style = document.createElement('style');
    style.id = 'particle-style';
    style.textContent = `
      @keyframes particle-float {
        0%   { transform: translateY(0) translateX(0); opacity: 0.1; }
        25%  { transform: translateY(-30px) translateX(10px); opacity: 0.3; }
        50%  { transform: translateY(-60px) translateX(-10px); opacity: 0.15; }
        75%  { transform: translateY(-30px) translateX(15px); opacity: 0.25; }
        100% { transform: translateY(0) translateX(0); opacity: 0.1; }
      }
    `;
    document.head.appendChild(style);
  }
})();

/* ────────────────────────────────────────────────────────────
   MERMAID — lazy-load diagrams on scroll
──────────────────────────────────────────────────────────── */
(function initMermaid() {
  if (!window.mermaid) return;

  mermaid.initialize({
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {
      background:      '#0d0d1a',
      primaryColor:    '#111126',
      primaryTextColor: '#f0f0ff',
      primaryBorderColor: '#2a2a50',
      lineColor:       '#00ff88',
      secondaryColor:  '#161630',
      tertiaryColor:   '#1a1a36',
      edgeLabelBackground: '#0d0d1a',
      fontFamily:      'JetBrains Mono, Fira Code, monospace',
    },
    flowchart: { curve: 'basis', htmlLabels: true },
    sequence: {
      mirrorActors: false,
      messageMargin: 40,
      actorMargin: 60,
    },
  });

  const diagramEls = $$('.lazy-diagram');
  if (!diagramEls.length) return;

  const rendered = new Set();

  async function renderDiagram(el) {
    const id = el.dataset.diagram;
    if (rendered.has(id)) return;
    rendered.add(id);
    el.dataset.loaded = 'true';

    const mermaidEl = el.querySelector('.mermaid');
    if (!mermaidEl) return;

    try {
      const def   = mermaidEl.textContent.trim();
      const uid   = 'mermaid-render-' + id + '-' + Date.now();
      const { svg } = await mermaid.render(uid, def);
      mermaidEl.innerHTML = svg;
      // Make SVGs responsive
      const svgEl = mermaidEl.querySelector('svg');
      if (svgEl) {
        svgEl.style.maxWidth = '100%';
        svgEl.removeAttribute('height');
      }
    } catch (err) {
      console.warn('Mermaid render error for', id, err);
      mermaidEl.innerHTML = `<p style="color:var(--text-muted);font-family:var(--font-mono);padding:16px;font-size:0.8rem;">Diagram unavailable in this environment.</p>`;
    }
  }

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          renderDiagram(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '200px' });

    diagramEls.forEach(el => {
      if (el.querySelector('.mermaid')) obs.observe(el);
    });
  } else {
    // Fallback: render all immediately
    diagramEls.forEach(el => {
      if (el.querySelector('.mermaid')) renderDiagram(el);
    });
  }
})();

/* ────────────────────────────────────────────────────────────
   D3 FORCE GRAPH — Component Dependency
──────────────────────────────────────────────────────────── */
(function initD3Graph() {
  const container = $('#d3-force-graph');
  if (!container || !window.d3) return;

  const parentEl = container.closest('.lazy-diagram');
  if (!parentEl) { renderGraph(); return; }

  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        renderGraph();
        obs.unobserve(parentEl);
      }
    }, { rootMargin: '200px' });
    obs.observe(parentEl);
  } else {
    renderGraph();
  }

  function renderGraph() {
    const nodes = [
      // Core
      { id: 'Registry',        group: 'core',    label: 'Registry' },
      { id: 'BuilderFactory',  group: 'core',    label: 'BuilderFactory' },
      { id: 'CLI',             group: 'cli',     label: 'CLI' },
      // IR
      { id: 'IRLoader',        group: 'ir',      label: 'IR Loader' },
      { id: 'IRParser',        group: 'ir',      label: 'IR Parser' },
      { id: 'Agent',           group: 'ir',      label: 'Agent' },
      { id: 'Skill',           group: 'ir',      label: 'Skill' },
      { id: 'Workflow',        group: 'ir',      label: 'Workflow' },
      { id: 'PersonaFilter',   group: 'core',    label: 'PersonaFilter' },
      // Builders
      { id: 'KiloBuilder',     group: 'builder', label: 'KiloBuilder' },
      { id: 'ClineBuilder',    group: 'builder', label: 'ClineBuilder' },
      { id: 'ClaudeBuilder',   group: 'builder', label: 'ClaudeBuilder' },
      { id: 'CopilotBuilder',  group: 'builder', label: 'CopilotBuilder' },
      { id: 'CursorBuilder',   group: 'builder', label: 'CursorBuilder' },
      { id: 'TemplateHandler', group: 'core',    label: 'TemplateHandler' },
    ];

    const links = [
      { source: 'CLI',            target: 'Registry' },
      { source: 'CLI',            target: 'BuilderFactory' },
      { source: 'CLI',            target: 'IRLoader' },
      { source: 'IRLoader',       target: 'IRParser' },
      { source: 'IRParser',       target: 'Agent' },
      { source: 'IRParser',       target: 'Skill' },
      { source: 'IRParser',       target: 'Workflow' },
      { source: 'Agent',          target: 'PersonaFilter' },
      { source: 'PersonaFilter',  target: 'BuilderFactory' },
      { source: 'BuilderFactory', target: 'KiloBuilder' },
      { source: 'BuilderFactory', target: 'ClineBuilder' },
      { source: 'BuilderFactory', target: 'ClaudeBuilder' },
      { source: 'BuilderFactory', target: 'CopilotBuilder' },
      { source: 'BuilderFactory', target: 'CursorBuilder' },
      { source: 'KiloBuilder',    target: 'TemplateHandler' },
      { source: 'ClineBuilder',   target: 'TemplateHandler' },
      { source: 'ClaudeBuilder',  target: 'TemplateHandler' },
      { source: 'CopilotBuilder', target: 'TemplateHandler' },
      { source: 'CursorBuilder',  target: 'TemplateHandler' },
      { source: 'Registry',       target: 'BuilderFactory' },
    ];

    const colors = {
      core:    '#00ff88',
      builder: '#00d4ff',
      ir:      '#f59e0b',
      cli:     '#a78bfa',
    };

    const width  = container.clientWidth  || 760;
    const height = container.clientHeight || 400;

    const svg = d3.select(container)
      .attr('width', width)
      .attr('height', height);

    // Arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', 'rgba(255,255,255,0.15)');

    const sim = d3.forceSimulation(nodes)
      .force('link',   d3.forceLink(links).id(d => d.id).distance(90).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(36));

    const linkEl = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('class', 'd3-link')
      .attr('marker-end', 'url(#arrow)');

    const nodeEl = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'd3-node')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) sim.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
          if (!event.active) sim.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
      );

    nodeEl.append('circle')
      .attr('r', 14)
      .attr('fill', d => colors[d.group] + '22')
      .attr('stroke', d => colors[d.group])
      .attr('stroke-width', 1.5);

    nodeEl.append('text')
      .text(d => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', '2.4em')
      .attr('fill', d => colors[d.group])
      .style('font-size', '10px')
      .style('font-family', 'JetBrains Mono, monospace')
      .style('pointer-events', 'none');

    // Tooltip on hover
    const tooltip = d3.select('body').append('div')
      .style('position', 'fixed')
      .style('background', 'rgba(10,10,20,0.95)')
      .style('border', '1px solid rgba(0,255,136,0.3)')
      .style('border-radius', '6px')
      .style('padding', '6px 12px')
      .style('font-family', 'JetBrains Mono, monospace')
      .style('font-size', '0.75rem')
      .style('color', '#00ff88')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 9999)
      .style('white-space', 'nowrap');

    nodeEl.on('mouseover', (event, d) => {
        tooltip.text(d.id)
          .style('opacity', 1)
          .style('left', (event.clientX + 12) + 'px')
          .style('top',  (event.clientY - 24) + 'px');
      })
      .on('mousemove', (event) => {
        tooltip
          .style('left', (event.clientX + 12) + 'px')
          .style('top',  (event.clientY - 24) + 'px');
      })
      .on('mouseleave', () => tooltip.style('opacity', 0));

    sim.on('tick', () => {
      linkEl
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      nodeEl.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Responsive resize
    const ro = new ResizeObserver(debounce(() => {
      const w = container.clientWidth;
      const h = container.clientHeight || 400;
      svg.attr('width', w).attr('height', h);
      sim.force('center', d3.forceCenter(w / 2, h / 2));
      sim.alpha(0.3).restart();
    }, 200));
    ro.observe(container.parentElement);
  }
})();

/* ────────────────────────────────────────────────────────────
   ACTIVE NAV LINK — highlight on scroll
──────────────────────────────────────────────────────────── */
(function initActiveNavLink() {
  const sections = $$('section[id]');
  const navLinks = $$('#nav-menu a');

  if (!sections.length || !navLinks.length) return;

  const highlight = debounce(() => {
    const scrollY = window.scrollY + 80;

    let current = '';
    sections.forEach(sec => {
      if (sec.offsetTop <= scrollY) current = sec.id;
    });

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      link.classList.toggle('nav-active', href === '#' + current);
    });
  }, 50);

  window.addEventListener('scroll', highlight, { passive: true });
  highlight();
})();

/* ────────────────────────────────────────────────────────────
   PRISM — re-run after DOM ready
──────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (window.Prism) {
    Prism.highlightAll();
  }
});

/* ────────────────────────────────────────────────────────────
   ACTIVE NAV STYLE INJECTION
──────────────────────────────────────────────────────────── */
(function injectActiveStyle() {
  const s = document.createElement('style');
  s.textContent = `
    #nav-menu a.nav-active {
      color: var(--accent-green) !important;
      background: rgba(0,255,136,0.06) !important;
    }
  `;
  document.head.appendChild(s);
})();
