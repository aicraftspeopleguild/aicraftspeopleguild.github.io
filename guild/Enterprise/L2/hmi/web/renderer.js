/**
 * ACG View Renderer
 *
 * Lightweight client-side engine that reads JSON view templates,
 * resolves data bindings, and renders component trees to the DOM.
 * Inspired by Ignition Perspective's tag/view/component model.
 *
 * Boot: ACGRenderer.init(config) from index.html
 * Navigate: ACGRenderer.navigate(path)
 */
const ACGRenderer = (function () {
  'use strict';

  let _config = {};
  let _siteMap = null;
  let _registry = {};
  let _componentCache = {};
  let _viewCache = {};    // sub-view JSON cache for acg.view.embed
  let _mountPoint = null;

  // ── Binding Resolution ──────────────────────────────────────────

  /**
   * Resolve a {{ path.to.value }} binding against a data context.
   * Returns the raw value (string, array, object) — not stringified.
   */
  function resolve(expr, ctx) {
    if (typeof expr !== 'string') return expr;
    // Check for pure binding: entire string is one {{ ... }}
    const pureBind = /^\{\{\s*(.+?)\s*\}\}$/.exec(expr);
    if (pureBind) {
      return getPath(ctx, pureBind[1].trim());
    }
    // Mixed string with inline bindings
    return expr.replace(/\{\{\s*(.+?)\s*\}\}/g, function (_, path) {
      const val = getPath(ctx, path.trim());
      return val == null ? '' : String(val);
    });
  }

  /** Walk a dotted path into an object. Supports numeric indexes. */
  function getPath(obj, path) {
    const parts = path.split('.');
    let cur = obj;
    for (let i = 0; i < parts.length; i++) {
      if (cur == null) return undefined;
      cur = cur[parts[i]];
    }
    return cur;
  }

  /** Check if a value is falsy for conditional rendering. */
  function isFalsy(val) {
    if (val == null || val === false || val === 0 || val === '') return true;
    if (Array.isArray(val) && val.length === 0) return true;
    return false;
  }

  // ── Mustache-Lite Template Interpolation ────────────────────────

  /**
   * Interpolate a template string with mustache-lite syntax.
   * Supports {{ prop }}, {{ #prop }}...{{ /prop }}, {{ #arr }}...{{ . }}...{{ /arr }}
   */
  function interpolate(template, props) {
    if (!template) return '';
    var result = template;
    // Section blocks: {{ #key }}...{{ /key }} — loop for nested sections
    for (var guard = 0; guard < 10; guard++) {
      var before = result;
      result = result.replace(
        /\{\{\s*#(\w+)\s*\}\}((?:(?!\{\{\s*#\w+\s*\}\})[\s\S])*?)\{\{\s*\/\1\s*\}\}/g,
        function (_, key, inner) {
          var val = props[key];
          if (isFalsy(val)) return '';
          if (Array.isArray(val)) {
            return val.map(function (item) {
              return inner.replace(/\{\{\s*\.\s*\}\}/g, escapeHtml(String(item)));
            }).join('');
          }
          return inner;
        }
      );
      if (result === before) break;
    }
    // Inverted blocks: {{ ^key }}...{{ /key }}
    result = result.replace(
      /\{\{\s*\^(\w+)\s*\}\}([\s\S]*?)\{\{\s*\/\1\s*\}\}/g,
      function (_, key, inner) { return isFalsy(props[key]) ? inner : ''; }
    );
    // Unescaped {{{ key }}} — emits raw string (for pre-rendered HTML)
    result = result.replace(/\{\{\{\s*(\w+)\s*\}\}\}/g, function (_, key) {
      var v = props[key];
      return v == null ? '' : String(v);
    });
    // Escaped {{ key }} — HTML-escape
    result = result.replace(/\{\{\s*(\w+)\s*\}\}/g, function (_, key) {
      var v = props[key];
      return v == null ? '' : escapeHtml(String(v));
    });
    return result;
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  // ── Component Rendering ─────────────────────────────────────────

  /**
   * Render a component tree node to a DOM element.
   *
   * node shape (superset of original):
   *   type        — component name or 'acg.view.embed'
   *   props       — key/value bindings resolved against ctx
   *   params      — merged into ctx as ctx.params.* (view.params pattern)
   *   children    — child nodes; each may carry a `slot` field for named slots
   *   repeat      — { source, as, template } loop
   *   when        — falsy → skip; supports path, negation, comparisons
   *   style       — { cssProperty: binding } applied via el.style.setProperty
   *   attrs       — { data-*|aria-*: binding } applied as DOM attributes
   *   events      — { click|change: { action, ...args } } safe dispatchers
   *   src         — (acg.view.embed only) URL of sub-view JSON
   *
   * @param {Object} node
   * @param {Object} ctx  Data context
   * @returns {HTMLElement|DocumentFragment|null}
   */
  function renderNode(node, ctx) {
    if (!node || !node.type) return null;

    // ── Conditional ────────────────────────────────────────────────
    if (node.when !== undefined) {
      if (isFalsy(resolveExpr(node.when, ctx))) return null;
    }

    // ── View embed: sub-view with passed params ────────────────────
    if (node.type === 'acg.view.embed') {
      return renderEmbed(node, ctx);
    }

    // ── Resolve props against parent ctx ──────────────────────────
    var boundProps = {};
    if (node.props) {
      var keys = Object.keys(node.props);
      for (var i = 0; i < keys.length; i++) {
        boundProps[keys[i]] = resolve(node.props[keys[i]], ctx);
      }
    }

    // ── Build child ctx: node.params → ctx.params.* ────────────────
    var childCtx = buildParamCtx(node, ctx);

    // ── Look up component ──────────────────────────────────────────
    var comp = _componentCache[node.type];
    if (!comp) {
      console.warn('ACGRenderer: unknown component "' + node.type + '"');
      var err = document.createElement('div');
      err.className = 'render-error';
      err.textContent = '[Unknown: ' + node.type + ']';
      return err;
    }

    var tag = comp.parameters.tag || 'div';

    // ── CSS class: base + propsToClass + explicit overrides ────────
    var cssClass = comp.parameters.cssClass || '';
    if (comp.parameters.propsToClass) {
      var pcArr = Array.isArray(comp.parameters.propsToClass)
        ? comp.parameters.propsToClass : [comp.parameters.propsToClass];
      for (var pc = 0; pc < pcArr.length; pc++) {
        if (boundProps[pcArr[pc]]) cssClass += ' ' + String(boundProps[pcArr[pc]]);
      }
    }
    if (boundProps.cssVariant) cssClass += ' ' + boundProps.cssVariant;
    if (boundProps.bodyClass)  cssClass += ' ' + boundProps.bodyClass;
    cssClass = cssClass.trim();

    // ── Distribute children into named slots ───────────────────────
    var slotMap = { 'default': [] };
    if (Array.isArray(node.children)) {
      for (var c = 0; c < node.children.length; c++) {
        var slotName = node.children[c].slot || 'default';
        if (!slotMap[slotName]) slotMap[slotName] = [];
        slotMap[slotName].push(node.children[c]);
      }
    }

    // Render each slot's children with the child ctx
    var slotHTML = {};
    for (var sn in slotMap) {
      if (!Object.prototype.hasOwnProperty.call(slotMap, sn)) continue;
      var sHTML = '';
      for (var si = 0; si < slotMap[sn].length; si++) {
        var sch = renderNode(slotMap[sn][si], childCtx);
        if (sch) sHTML += nodeToHTML(sch);
      }
      slotHTML[sn] = sHTML;
    }

    // Render repeat items into the default slot
    if (node.repeat) {
      var items = resolve('{{ ' + node.repeat.source + ' }}', childCtx);
      if (Array.isArray(items)) {
        for (var r = 0; r < items.length; r++) {
          var repeatCtx = Object.assign({}, childCtx);
          repeatCtx[node.repeat.as] = items[r];
          repeatCtx['$index'] = r;
          var rn = renderNode(node.repeat.template, repeatCtx);
          if (rn) slotHTML['default'] += nodeToHTML(rn);
        }
      }
    }

    // ── Compute inner HTML from template (named slot injection) ────
    var inner;
    if (comp.parameters.template) {
      inner = interpolate(comp.parameters.template, boundProps);
      // Replace {{ slot:name }} placeholders with rendered slot content
      inner = inner.replace(/\{\{\s*slot:([\w-]+)\s*\}\}/g, function (_, name) {
        return slotHTML[name] || '';
      });
    } else {
      inner = slotHTML['default'] || '';
    }

    // "fragment" tag — unwrap, return DocumentFragment
    if (tag === 'fragment') {
      return htmlToFragment(inner);
    }

    var el = document.createElement(tag);
    if (cssClass) el.className = cssClass;
    el.innerHTML = inner;

    // ── propsToAttr: map prop values onto HTML attributes ──────────
    if (comp.parameters.propsToAttr) {
      var attrMap = comp.parameters.propsToAttr;
      var attrKeys = Object.keys(attrMap);
      for (var a = 0; a < attrKeys.length; a++) {
        var attrVal = boundProps[attrKeys[a]];
        if (attrVal != null) el.setAttribute(attrMap[attrKeys[a]], String(attrVal));
      }
    }

    // ── node.attrs: safe data-*/aria-* attribute overrides ─────────
    if (node.attrs) {
      var nodeAttrKeys = Object.keys(node.attrs);
      for (var na = 0; na < nodeAttrKeys.length; na++) {
        var naKey = nodeAttrKeys[na];
        var naVal = resolve(node.attrs[naKey], childCtx);
        // Allow only data-*, aria-*, and a short list of safe global attrs
        if (naVal != null && /^(data-|aria-|id$|title$|lang$|tabindex$)/.test(naKey)) {
          el.setAttribute(naKey, String(naVal));
        }
      }
    }

    // ── node.style: CSS custom property / inline style bindings ────
    if (node.style) {
      var styleKeys = Object.keys(node.style);
      for (var sk = 0; sk < styleKeys.length; sk++) {
        var sv = resolve(node.style[styleKeys[sk]], childCtx);
        if (sv != null) el.style.setProperty(styleKeys[sk], String(sv));
      }
    }

    // ── node.events: safe event dispatch ──────────────────────────
    if (node.events) {
      wireEvents(el, node.events, childCtx);
    }

    return el;
  }

  /**
   * Build a child context inheriting from ctx with node.params merged as
   * ctx.params.* — analogous to Perspective's view.params binding.
   * Bindings in node.params are resolved against the PARENT ctx.
   */
  function buildParamCtx(node, ctx) {
    if (!node.params) return ctx;
    var childCtx = Object.assign({}, ctx);
    childCtx.params = Object.assign({}, ctx.params || {});
    var pk = Object.keys(node.params);
    for (var p = 0; p < pk.length; p++) {
      childCtx.params[pk[p]] = resolve(node.params[pk[p]], ctx);
    }
    return childCtx;
  }

  /**
   * Wire safe event handlers onto a DOM element.
   * Only predefined action types are allowed — no eval, no arbitrary JS.
   * Actions: navigate | refresh | open
   */
  function wireEvents(el, events, ctx) {
    var evtNames = Object.keys(events);
    for (var e = 0; e < evtNames.length; e++) {
      (function (evtName, action, ctx) {
        el.addEventListener(evtName, function (evt) {
          evt.preventDefault();
          var act = typeof action === 'string' ? action : action.action;
          if (act === 'navigate') {
            navigate(resolve(action.to, ctx));
          } else if (act === 'refresh') {
            refresh();
          } else if (act === 'open') {
            var url = resolve(action.url, ctx);
            // Validate: relative paths or https only — reject javascript: data:
            if (url && /^(https?:\/\/|\/[^/])/.test(url)) {
              window.open(url, action.target || '_blank', 'noopener,noreferrer');
            }
          }
        });
      })(evtNames[e], events[evtNames[e]], ctx);
    }
  }

  /**
   * Handle acg.view.embed nodes — fetch a sub-view JSON file and render it
   * with passed params. Returns a placeholder div when the fetch is async.
   */
  function renderEmbed(node, ctx) {
    var viewSrc = resolve(node.src || '', ctx);
    if (!viewSrc) return null;
    var embedCtx = buildParamCtx(node, ctx);
    var base = (_siteMap && _siteMap.base) ? _siteMap.base : '';
    var cached = _viewCache[viewSrc];
    if (cached) {
      return renderNode(cached.parameters && cached.parameters.root, embedCtx);
    }
    // Async path: placeholder filled on resolve
    var ph = document.createElement('div');
    ph.className = 'embed-pending';
    ph.setAttribute('data-embed-src', viewSrc);
    fetchJSON(base + viewSrc)
      .then(function (view) {
        _viewCache[viewSrc] = view;
        if (view.parameters && view.parameters.root) {
          var embedEl = renderNode(view.parameters.root, embedCtx);
          if (embedEl && ph.parentNode) ph.replaceWith(embedEl);
        }
      })
      .catch(function () {
        ph.textContent = '[embed error: ' + viewSrc + ']';
        ph.className = 'embed-error render-error';
      });
    return ph;
  }

  /**
   * Safe expression evaluator for `when` bindings.
   * Supports: path lookups, string/number literals,
   * comparisons (===, !==, >, <, >=, <=), prefix negation (!path).
   */
  function resolveExpr(expr, ctx) {
    if (typeof expr !== 'string') return expr;
    var s = expr.trim();
    // Negation: !path
    if (s.charAt(0) === '!') return !resolveExpr(s.slice(1), ctx);
    // Comparison: lhs op rhs
    var cmp = s.match(/^(.+?)\s*(===|!==|>=|<=|>|<)\s*(.+)$/);
    if (cmp) {
      var lhs = resolveExpr(cmp[1].trim(), ctx);
      var rhs = resolveExpr(cmp[3].trim(), ctx);
      switch (cmp[2]) {
        case '===': return lhs === rhs;
        case '!==': return lhs !== rhs;
        case '>':   return lhs >   rhs;
        case '<':   return lhs <   rhs;
        case '>=':  return lhs >=  rhs;
        case '<=':  return lhs <=  rhs;
      }
    }
    // Numeric literal
    if (/^-?\d+(\.\d+)?$/.test(s)) return Number(s);
    // String literal
    if ((s.charAt(0) === '"' && s.charAt(s.length - 1) === '"') ||
        (s.charAt(0) === "'" && s.charAt(s.length - 1) === "'")) {
      return s.slice(1, -1);
    }
    // Mustache binding {{ path }}
    if (/^\{\{.+\}\}$/.test(s)) return resolve(s, ctx);
    // Plain dot-path
    return resolve(s, ctx);
  }

  /** Serialize a DOM node or DocumentFragment to an HTML string. */
  function nodeToHTML(node) {
    if (!node) return '';
    if (node.nodeType === 11 /* DocumentFragment */) {
      var wrap = document.createElement('div');
      wrap.appendChild(node.cloneNode(true));
      return wrap.innerHTML;
    }
    if (node.outerHTML) return node.outerHTML;
    return '';
  }

  /** Parse an HTML string into a DocumentFragment (so fragment components
   *  unwrap cleanly into their parent). */
  function htmlToFragment(html) {
    var tpl = document.createElement('template');
    tpl.innerHTML = html;
    return tpl.content;
  }

  // ── Router ──────────────────────────────────────────────────────

  /** Match a URL path against site-map routes. */
  function matchRoute(pathname) {
    if (!_siteMap || !_siteMap.routes) return null;

    var basePath = _siteMap.base || '/';
    var relPath = pathname;
    if (relPath.indexOf(basePath) === 0) {
      relPath = relPath.substring(basePath.length);
    }
    relPath = '/' + relPath.replace(/^\/+/, '').replace(/\.html$/, '');
    if (relPath !== '/' && relPath.endsWith('/')) {
      relPath = relPath.slice(0, -1);
    }

    for (var i = 0; i < _siteMap.routes.length; i++) {
      var route = _siteMap.routes[i];
      if (route.dynamic) {
        var pattern = route.path.replace(/:(\w+)/g, '([^/]+)');
        var re = new RegExp('^' + pattern + '$');
        var match = relPath.match(re);
        if (match) {
          return { route: route, params: { slug: match[1] } };
        }
      } else if (route.path === relPath) {
        return { route: route, params: {} };
      }
    }
    return null;
  }

  // ── Data Fetching ───────────────────────────────────────────────

  function fetchJSON(url) {
    return fetch(url).then(function (res) {
      if (!res.ok) throw new Error('Fetch failed: ' + url + ' (' + res.status + ')');
      return res.json();
    });
  }

  // ── Public API ──────────────────────────────────────────────────

  // Queue any navigate() calls received before the initial fetches settle,
  // so clicks during load don't 404 on a null _siteMap.
  var _pendingRoute = null;

  function init(config) {
    _config = config || {};
    _mountPoint = document.querySelector(_config.mountPoint || '#app');
    if (!_mountPoint) {
      console.warn('ACGRenderer: mount point not found');
      return;
    }

    // Show loading state
    _mountPoint.innerHTML = '<div class="loading"><div class="emblem">⚒ ACG ⚒</div><p>Loading...</p></div>';

    // Fetch site map and component registry in parallel
    Promise.all([
      fetchJSON(_config.siteMap || 'guild/Enterprise/L2/hmi/web/site-map.json'),
      fetchJSON(_config.components || 'guild/Enterprise/L2/hmi/web/components/registry.json')
    ]).then(function (results) {
      _siteMap = results[0];
      _registry = results[1].components || {};

      // If a click landed during load, honour that over the startup route
      var routeOnLoad = _pendingRoute || currentRoute();
      _pendingRoute = null;
      navigate(routeOnLoad);
    }).catch(function (err) {
      console.error('ACGRenderer init failed:', err);
      _mountPoint.innerHTML = '<p>Failed to load site configuration.</p>';
    });

    // Hash route navigation — href="#/charter" triggers hashchange
    window.addEventListener('hashchange', function () {
      navigate(currentRoute());
    });

    window.addEventListener('popstate', function () {
      navigate(currentRoute());
    });
  }

  // Resolve the active route. Only hash form "#/slug" is treated as a route;
  // plain anchor hashes like "#sign" or "#manifesto" are left to the browser
  // (they scroll in-page and must NOT hijack the SPA router). No hash at all
  // means the landing page — independent of pathname, so this works whether
  // the site is served at / or under a GitHub Pages project sub-path.
  function currentRoute() {
    var h = window.location.hash || '';
    if (h.indexOf('#/') === 0) return h.substring(1);        // "#/charter" → "/charter"
    return '/';                                               // no hash or plain "#foo" → landing
  }

  // Update the persistent dock-north heading + subtitle to reflect the active
  // route. Falls back to the data-default values on home so the landing page
  // always shows the guild title. Never injects HTML — textContent only.
  function setDockHeading(title, subtitle) {
    var t = document.getElementById('dock-title');
    var s = document.getElementById('dock-subtitle');
    if (t) t.textContent = title || t.getAttribute('data-default') || '';
    if (s) s.textContent = subtitle || s.getAttribute('data-default') || '';
  }

  // Strip a leading <h1>/<h2> inside a body HTML blob when its text duplicates
  // the page title — the dock already shows that heading, so repeating it in
  // the body is visual noise. Only touches the FIRST matching heading.
  function stripDuplicateTitleHeading(body, title) {
    if (!body || !title) return body;
    var t = String(title).toLowerCase().trim();
    return body.replace(/<h[12][^>]*>\s*([^<]*?)\s*<\/h[12]>\s*/i, function (match, text) {
      var h = String(text).toLowerCase().trim();
      return (h === t || h.indexOf(t) > -1 || t.indexOf(h) > -1) ? '' : match;
    });
  }

  function navigate(pathname) {
    // If init hasn't resolved yet, buffer the requested route. The init
    // then-callback will replay it once _siteMap + _registry are loaded.
    if (!_siteMap) {
      _pendingRoute = pathname;
      return;
    }
    // Home route: hide #app, show static landing, restore dock heading defaults
    if (!pathname || pathname === '/' || pathname === '') {
      document.body.classList.remove('has-route');
      setDockHeading(null, null);
      return;
    }
    document.body.classList.add('has-route');

    var match = matchRoute(pathname);
    if (!match) {
      console.warn('[ACGRenderer] no route match for', pathname,
                   '— registered routes:',
                   (_siteMap && _siteMap.routes) ? _siteMap.routes.map(function(r){return r.path;}) : 'sitemap-not-loaded');
      _mountPoint.innerHTML =
        '<div class="loading"><h2>Page Not Found</h2>' +
        '<p>No route registered for <code>' + pathname + '</code>.</p>' +
        '<p>If you see this unexpectedly, try a hard refresh (Ctrl+Shift+R / Cmd+Shift+R) — your browser may be caching an older renderer.</p>' +
        '<p><a href="#/">Back to Home</a></p></div>';
      return;
    }

    // Fetch the page definition
    var pageUrl = (_siteMap.base || '') + match.route.page;
    fetchJSON(pageUrl).then(function (page) {
      // Sync the persistent dock heading with the active page
      setDockHeading(page.parameters.title, page.parameters.subtitle);
      // Fetch view template
      var viewUrl = (_siteMap.base || '') + page.parameters.view;
      var dataPromises = {};
      var dataKeys = [];

      // Fetch all data sources
      if (page.parameters.data) {
        var keys = Object.keys(page.parameters.data);
        for (var i = 0; i < keys.length; i++) {
          var dataPath = page.parameters.data[keys[i]];
          // Replace :slug with actual param
          if (match.params.slug) {
            dataPath = dataPath.replace(':slug', match.params.slug);
          }
          dataKeys.push(keys[i]);
          dataPromises[keys[i]] = fetchJSON((_siteMap.base || '') + dataPath);
        }
      }

      // Fetch view + all data in parallel
      var allFetches = [fetchJSON(viewUrl)];
      for (var d = 0; d < dataKeys.length; d++) {
        allFetches.push(dataPromises[dataKeys[d]]);
      }

      return Promise.all(allFetches).then(function (results) {
        var view = results[0];
        var dataCtx = { page: page.parameters };
        for (var d = 0; d < dataKeys.length; d++) {
          dataCtx[dataKeys[d]] = results[d + 1];
        }
        // If the page data carries a `body` HTML blob whose first heading
        // echoes the page title, strip it so only the dock title shows.
        var title = page.parameters.title;
        for (var k = 0; k < dataKeys.length; k++) {
          var ref = dataCtx[dataKeys[k]];
          if (ref && typeof ref === 'object' && typeof ref.body === 'string') {
            ref.body = stripDuplicateTitleHeading(ref.body, title);
          }
        }
        if (dataCtx.page && typeof dataCtx.page.body === 'string') {
          dataCtx.page.body = stripDuplicateTitleHeading(dataCtx.page.body, title);
        }

        // Load all registered components (upfront — no per-view lookup).
        // The first call fills _componentCache; subsequent calls no-op.
        return loadAllComponents().then(function () {
          renderView(view, dataCtx);
        });
      });
    }).catch(function (err) {
      console.error('ACGRenderer navigate failed:', err);
      _mountPoint.innerHTML = '<p>Error loading page.</p>';
    });
  }

  /** Load all components from the registry into _componentCache keyed by
   *  PascalCase name (same key used in view nodes' `type` field). Idempotent. */
  function loadAllComponents() {
    var keys = Object.keys(_registry);
    var fetches = [];
    for (var k = 0; k < keys.length; k++) {
      var name = keys[k];
      if (_componentCache[name]) continue;
      (function (name, src) {
        fetches.push(
          fetchJSON((_siteMap.base || '') + src).then(function (comp) {
            _componentCache[name] = comp;
          })
        );
      })(name, _registry[name].src);
    }
    return fetches.length > 0 ? Promise.all(fetches) : Promise.resolve();
  }

  function renderView(view, dataCtx) {
    if (!view.parameters || !view.parameters.root) {
      _mountPoint.innerHTML = '<p>Invalid view template.</p>';
      return;
    }

    var rootEl = renderNode(view.parameters.root, dataCtx);
    if (rootEl) {
      _mountPoint.innerHTML = '';
      _mountPoint.appendChild(rootEl);
      // Kick off widget runtime if loaded (tag polling, tab wiring, alarm badges)
      if (window.WidgetRuntime && typeof window.WidgetRuntime.init === 'function') {
        window.WidgetRuntime.init(_mountPoint);
      }
    }

    // Update document title
    if (dataCtx.page && dataCtx.page.title) {
      document.title = dataCtx.page.title + ' — AI Craftspeople Guild';
    }
  }

  function refresh() {
    navigate(currentRoute());
  }

  return {
    init: init,
    navigate: navigate,
    refresh: refresh,
    // Exposed for testing
    _resolve: resolve,
    _interpolate: interpolate,
    _renderNode: renderNode
  };
})();
