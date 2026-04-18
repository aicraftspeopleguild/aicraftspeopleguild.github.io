# API Design Conventions

## URL Structure

```
GET    /<resources>          → list
GET    /<resources>/:id      → detail
POST   /<resources>          → create
PUT    /<resources>/:id      → full update
PATCH  /<resources>/:id      → partial update
DELETE /<resources>/:id      → delete
```

Resource names are lowercase plural nouns (`/posts`, `/users`).

## Request / Response

- All request bodies are `application/x-www-form-urlencoded` (HTML form default) or `application/json` from non-browser clients.
- All responses are `text/html` — never `application/json`.
- HTMX requests (`HX-Request: true`) receive HTML fragments; plain requests receive full pages.

## Status Codes

| Situation | Code |
|-----------|------|
| Successful GET / full-page render | 200 |
| Successful POST (HTMX swap) | 200 |
| Successful POST (redirect) | 303 See Other |
| Validation failure | 422 Unprocessable Entity |
| Not found | 404 |
| Unauthenticated | 401 |
| Unauthorised | 403 |
| Server error | 500 |

## Validation

Validate all incoming data at the route level before touching models. Return `422` with an error partial on failure:

```js
res.status(422).render('partials/error', { message: 'Title is required' });
```

## HTMX Response Headers

Use response headers to communicate with HTMX instead of JavaScript:

| Header | Purpose |
|--------|---------|
| `HX-Redirect` | Navigate the full page |
| `HX-Trigger` | Fire a named event on the client |
| `HX-Retarget` | Override the swap target |
| `HX-Reswap` | Override the swap strategy |
