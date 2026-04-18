/**
 * ACG Widget Runtime
 *
 * Post-mount behaviors for interactive / live widgets.
 * ACGRenderer calls WidgetRuntime.init(mountEl) after each view is rendered.
 *
 * Modules:
 *   TagPoller   — polls tags.json, updates [data-tag-path] spans
 *   AlarmPoller — polls state.json, updates [data-alarm-src] badges
 *   TabWidget   — wires .tabbed-panel click switching
 *
 * Usage:
 *   <script src="guild/Enterprise/L2/hmi/web/widget-runtime.js"></script>
 *   (load before renderer.js so WidgetRuntime is available at renderView time)
 */
const WidgetRuntime = (function () {
  'use strict';

  // WeakMap so intervals are GC'd when elements are removed from DOM
  const _intervals = new WeakMap();

  // ── Tag Poller ──────────────────────────────────────────────────────────
  /**
   * Scans mountEl for [data-tag-path] elements and starts polling each.
   *
   * Attributes on the element:
   *   data-tag-path       dot-path into tags.json, e.g. "enterprise.memberCount"
   *   data-tag-src        URL of tags.json (default: guild/Enterprise/L4/runtime/tags.json)
   *   data-tag-interval   poll seconds (default: 30, min: 5)
   *   data-tag-format     raw | number | datetime | boolean (default: raw)
   *   data-tag-unit       suffix appended after value
   */
  const TagPoller = {
    init(el) {
      el.querySelectorAll('[data-tag-path]').forEach(span => {
        if (_intervals.has(span)) return; // already wired

        const path     = span.getAttribute('data-tag-path');
        const src      = span.getAttribute('data-tag-src')
                         || 'guild/Enterprise/L4/runtime/tags.json';
        const secs     = Math.max(5, parseInt(span.getAttribute('data-tag-interval') || '30', 10));
        const format   = span.getAttribute('data-tag-format') || 'raw';
        const unit     = span.getAttribute('data-tag-unit') || '';

        const poll = () => {
          fetch(src + '?_t=' + Date.now())
            .then(r => r.json())
            .then(data => {
              const entry = TagPoller._path(data, path);
              if (entry == null) { span.textContent = '—'; return; }
              const raw = (entry !== null && typeof entry === 'object' && 'value' in entry)
                          ? entry.value : entry;
              span.textContent = TagPoller._fmt(raw, format) + (unit ? '\u202f' + unit : '');
              const q = entry && entry.quality;
              span.classList.toggle('tag-q-good',      q === 'good');
              span.classList.toggle('tag-q-stale',     q === 'stale');
              span.classList.toggle('tag-q-bad',       q === 'bad');
              span.classList.toggle('tag-q-uncertain', q === 'uncertain');
            })
            .catch(() => { span.textContent = '⚠'; });
        };

        poll();
        _intervals.set(span, setInterval(poll, secs * 1000));
      });
    },

    _path(obj, dotPath) {
      return dotPath.split('.').reduce((cur, k) => (cur == null ? undefined : cur[k]), obj);
    },

    _fmt(val, format) {
      if (val == null) return '—';
      if (format === 'number')   return Number(val).toLocaleString();
      if (format === 'datetime') { try { return new Date(val).toLocaleString(); } catch (_) { return String(val); } }
      if (format === 'boolean')  return val ? 'true' : 'false';
      return String(val);
    }
  };

  // ── Alarm Poller ────────────────────────────────────────────────────────
  /**
   * Scans mountEl for [data-alarm-src] badges and polls state.json.
   * Updates badge text with active fault count and toggles .alarm-badge-active.
   *
   * Attributes:
   *   data-alarm-src    URL of state.json
   *   data-alarm-href   optional click destination (e.g. alarms screen)
   */
  const AlarmPoller = {
    init(el) {
      el.querySelectorAll('[data-alarm-src]').forEach(badge => {
        if (_intervals.has(badge)) return;

        const src  = badge.getAttribute('data-alarm-src');
        const href = badge.getAttribute('data-alarm-href') || '';

        const poll = () => {
          fetch(src + '?_t=' + Date.now())
            .then(r => r.json())
            .then(data => {
              const count =
                (Array.isArray(data.faults_active) ? data.faults_active.length : 0) ||
                (data.summary && data.summary.faults_active) || 0;
              badge.textContent  = count + ' alarm' + (count === 1 ? '' : 's');
              badge.title        = count + ' active fault' + (count === 1 ? '' : 's');
              badge.classList.toggle('alarm-badge-active', count > 0);
              if (href) badge.style.cursor = 'pointer';
            })
            .catch(() => { badge.textContent = '? alarms'; });
        };

        if (href) badge.addEventListener('click', () => { window.location.href = href; });
        poll();
        _intervals.set(badge, setInterval(poll, 10_000));
      });
    }
  };

  // ── Tab Widget ──────────────────────────────────────────────────────────
  /**
   * Scans mountEl for .tabbed-panel elements and wires click-to-show tabs.
   * First tab is activated on init.
   */
  const TabWidget = {
    init(el) {
      el.querySelectorAll('.tabbed-panel').forEach(panel => {
        if (panel.dataset.tabWidgetInit) return;
        panel.dataset.tabWidgetInit = '1';

        const btns  = Array.from(panel.querySelectorAll('.tab-btn'));
        const panes = Array.from(panel.querySelectorAll('.tab-pane'));

        const activate = idx => {
          btns.forEach((b, i)  => b.classList.toggle('tab-btn-active', i === idx));
          panes.forEach((p, i) => { p.hidden = (i !== idx); });
        };

        activate(0);
        btns.forEach((btn, idx) => btn.addEventListener('click', () => activate(idx)));
      });
    }
  };

  // ── Public API ──────────────────────────────────────────────────────────

  /**
   * Initialize all widget behaviors on a mounted DOM subtree.
   * Called by ACGRenderer.renderView() after each navigation.
   */
  function init(mountEl) {
    if (!mountEl) return;
    TagPoller.init(mountEl);
    AlarmPoller.init(mountEl);
    TabWidget.init(mountEl);
  }

  /**
   * Clear all polling intervals for the given mount point.
   * Call before unmounting / navigating away to avoid memory leaks.
   */
  function teardown(mountEl) {
    if (!mountEl) return;
    mountEl.querySelectorAll('[data-tag-path], [data-alarm-src]').forEach(el => {
      const id = _intervals.get(el);
      if (id != null) { clearInterval(id); _intervals.delete(el); }
    });
  }

  return { init, teardown, TagPoller, AlarmPoller, TabWidget };
})();
