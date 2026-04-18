# HTMX Patterns

## Basic Partial Swap

```html
<button hx-get="/posts" hx-target="#post-list" hx-swap="innerHTML">
  Load Posts
</button>
<div id="post-list"></div>
```

Server returns an HTML fragment — just the list items, no wrapping page.

## Form Submission

```html
<form hx-post="/posts" hx-target="#post-list" hx-swap="afterbegin">
  <input name="title" required />
  <button type="submit">Add</button>
</form>
```

On success, server returns the new item partial prepended into `#post-list`.  
On validation failure, server returns `422` with `partials/error`.

## Delete with Target Removal

```html
<li id="post-42">
  Post title
  <button hx-delete="/posts/42" hx-target="#post-42" hx-swap="outerHTML">
    Delete
  </button>
</li>
```

Server returns an empty `200` response to remove the element.

## Server-Sent Events via HX-Trigger

Instead of writing JavaScript, set a response header:

```js
res.setHeader('HX-Trigger', 'postsUpdated');
res.render('partials/posts/item', { post });
```

Other elements on the page can react:

```html
<div hx-get="/posts/count" hx-trigger="postsUpdated from:body" hx-target="#count">
```

## Progressive Enhancement

Every `hx-*` action must have a non-JS fallback:

- Use `<a href="...">` or `<form action="..." method="...">` as the base element
- HTMX intercepts these and upgrades them to partial swaps
- Without JS, the browser follows the native href/action and receives a full page

## Detecting HTMX in Route Handlers

```js
if (req.headers['hx-request']) {
  return res.render('partials/posts/list', { posts });
}
res.render('posts/index', { posts });
```

## Swap Strategies

| Strategy | Use case |
|----------|----------|
| `innerHTML` | Replace contents of target |
| `outerHTML` | Replace the target element itself |
| `afterbegin` | Prepend into target (new items at top) |
| `beforeend` | Append into target (new items at bottom) |
| `delete` | Remove the target element |
| `none` | No DOM change (side-effect only) |
