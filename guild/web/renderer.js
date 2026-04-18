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
   * @param {Object} node - { type, props, children, repeat, when }
   * @param {Object} ctx  - Data context for binding resolution
   * @returns {HTMLElement|null}
   */
  function renderNode(node, ctx) {
    if (!node || !node.type) return null;

    // Conditional: skip if when is falsy
    if (node.when !== undefined) {
      var whenVal = resolve(node.when, ctx);
      if (isFalsy(whenVal)) return null;
    }

    // Resolve props
    var boundProps = {};
    if (node.props) {
      var keys = Object.keys(node.props);
      for (var i = 0; i < keys.length; i++) {
        boundProps[keys[i]] = resolve(node.props[keys[i]], ctx);
      }
    }

    // Look up component
    var comp = _componentCache[node.type];
    if (!comp) {
      console.warn('ACGRenderer: unknown component "' + node.type + '"');
      var err = document.createElement('div');
      err.className = 'render-error';
      err.textContent = '[Unknown: ' + node.type + ']';
      return err;
    }

    var tag = comp.parameters.tag || 'div';
    var cssClass = comp.parameters.cssClass || '';
    if (boundProps.cssVariant) cssClass += ' ' + boundProps.cssVariant;
    if (boundProps.bodyClass) cssClass += ' ' + boundProps.bodyClass;
    cssClass = cssClass.trim();

    // Render children first — so they can fill {{ slot:default }}
    var childrenHTML = '';
    if (Array.isArray(node.children)) {
      for (var c = 0; c < node.children.length; c++) {
        var ch = renderNode(node.children[c], ctx);
        if (ch) childrenHTML += nodeToHTML(ch);
      }
    }
    if (node.repeat) {
      var items = resolve('{{ ' + node.repeat.source + ' }}', ctx);
      if (Array.isArray(items)) {
        for (var r = 0; r < items.length; r++) {
          var childCtx = Object.assign({}, ctx);
          childCtx[node.repeat.as] = items[r];
          var rn = renderNode(node.repeat.template, childCtx);
          if (rn) childrenHTML += nodeToHTML(rn);
        }
      }
    }

    // Compute inner HTML — from template (with slot injection) or children
    var inner;
    if (comp.parameters.template) {
      inner = interpolate(comp.parameters.template, boundProps);
      inner = inner.replace(/\{\{\s*slot:default\s*\}\}/g, childrenHTML);
    } else {
      inner = childrenHTML;
    }

    // "fragment" tag — emit inner only, no wrapping element
    if (tag === 'fragment') {
      return htmlToFragment(inner);
    }

    var el = document.createElement(tag);
    if (cssClass) el.className = cssClass;
    el.innerHTML = inner;
    return el;
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
      fetchJSON(_config.siteMap || 'guild/web/site-map.json'),
      fetchJSON(_config.components || 'guild/web/components/registry.json')
    ]).then(function (results) {
      _siteMap = results[0];
      _registry = results[1].components || {};

      // Navigate to current route (hash takes priority over pathname)
      navigate(currentRoute());
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

  // Resolve the active route. Hash form "#/slug" takes priority over pathname.
  function currentRoute() {
    var h = window.location.hash || '';
    if (h.indexOf('#/') === 0) return h.substring(1);        // "#/charter" → "/charter"
    if (h.length > 1) return '/' + h.substring(1);           // "#charter" → "/charter"
    return window.location.pathname;
  }

  function navigate(pathname) {
    // Home route: hide #app, show static landing
    if (!pathname || pathname === '/' || pathname === '') {
      document.body.classList.remove('has-route');
      return;
    }
    document.body.classList.add('has-route');

    var match = matchRoute(pathname);
    if (!match) {
      _mountPoint.innerHTML = '<div class="loading"><h2>Page Not Found</h2><p><a href="#/">Back to Home</a></p></div>';
      return;
    }

    // Fetch the page definition
    var pageUrl = (_siteMap.base || '') + match.route.page;
    fetchJSON(pageUrl).then(function (page) {
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
    }

    // Update document title
    if (dataCtx.page && dataCtx.page.title) {
      document.title = dataCtx.page.title + ' — AI Craftspeople Guild';
    }
  }

  function refresh() {
    navigate(window.location.pathname);
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
