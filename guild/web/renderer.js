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

    // Section blocks: {{ #key }}...{{ /key }}
    let result = template.replace(
      /\{\{\s*#(\w+)\s*\}\}([\s\S]*?)\{\{\s*\/\1\s*\}\}/g,
      function (_, key, inner) {
        const val = props[key];
        if (isFalsy(val)) return '';
        if (Array.isArray(val)) {
          return val.map(function (item) {
            return inner.replace(/\{\{\s*\.\s*\}\}/g, escapeHtml(String(item)));
          }).join('');
        }
        return inner;
      }
    );

    // Inverted blocks: {{ ^key }}...{{ /key }}
    result = result.replace(
      /\{\{\s*\^(\w+)\s*\}\}([\s\S]*?)\{\{\s*\/\1\s*\}\}/g,
      function (_, key, inner) {
        return isFalsy(props[key]) ? inner : '';
      }
    );

    // Simple value substitution: {{ key }}
    result = result.replace(/\{\{\s*(\w+)\s*\}\}/g, function (_, key) {
      const val = props[key];
      return val == null ? '' : escapeHtml(String(val));
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
      var el = document.createElement('div');
      el.className = 'render-error';
      el.textContent = '[Unknown: ' + node.type + ']';
      return el;
    }

    // Create element
    var tag = comp.parameters.tag || 'div';
    var el = document.createElement(tag);

    // Apply CSS classes
    var cssClass = comp.parameters.cssClass || '';
    if (boundProps.cssVariant) cssClass += ' ' + boundProps.cssVariant;
    if (boundProps.bodyClass) cssClass += ' ' + boundProps.bodyClass;
    if (cssClass.trim()) el.className = cssClass.trim();

    // Render via template string or children
    if (comp.parameters.template) {
      el.innerHTML = interpolate(comp.parameters.template, boundProps);
    }

    // Render explicit children
    if (node.children && Array.isArray(node.children)) {
      for (var c = 0; c < node.children.length; c++) {
        var childEl = renderNode(node.children[c], ctx);
        if (childEl) el.appendChild(childEl);
      }
    }

    // Render repeat blocks
    if (node.repeat) {
      var items = resolve('{{ ' + node.repeat.source + ' }}', ctx);
      if (Array.isArray(items)) {
        for (var r = 0; r < items.length; r++) {
          var childCtx = Object.assign({}, ctx);
          childCtx[node.repeat.as] = items[r];
          var repEl = renderNode(node.repeat.template, childCtx);
          if (repEl) el.appendChild(repEl);
        }
      }
    }

    return el;
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

        // Load required components, then render
        return loadComponents(view.tags.component_ids || []).then(function () {
          renderView(view, dataCtx);
        });
      });
    }).catch(function (err) {
      console.error('ACGRenderer navigate failed:', err);
      _mountPoint.innerHTML = '<p>Error loading page.</p>';
    });
  }

  function loadComponents(componentIds) {
    var fetches = [];
    for (var i = 0; i < componentIds.length; i++) {
      var id = componentIds[i];
      if (_componentCache[id]) continue;

      // Find in registry by matching id to PascalCase name
      var keys = Object.keys(_registry);
      for (var k = 0; k < keys.length; k++) {
        var regId = keys[k].replace(/([A-Z])/g, '-$1').toLowerCase().replace(/^-/, '');
        if (regId === id && !_componentCache[keys[k]]) {
          (function (name, src) {
            fetches.push(
              fetchJSON((_siteMap.base || '') + src).then(function (comp) {
                _componentCache[name] = comp;
              })
            );
          })(keys[k], _registry[keys[k]].src);
        }
      }
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
