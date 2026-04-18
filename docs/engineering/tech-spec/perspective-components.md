# Perspective Component Types — `acg.*` Namespace

Every component type is registered in `guild/web/perspective/components/registry.json` mapping the type string (e.g. `acg.display.heading`) to its renderer definition (HTML tag, CSS class, prop → attribute mapping).

## Containers

| Type                       | Purpose                              | Renders as          |
|----------------------------|--------------------------------------|---------------------|
| `acg.container.page`       | Page shell (head + body + footer)    | `<html>…</html>`    |
| `acg.container.section`    | Semantic section wrapper             | `<section>`         |
| `acg.container.main`       | Main content column                  | `<main>`            |
| `acg.container.grid`       | Responsive card grid                 | `<div class="grid">`|
| `acg.container.flex`       | Horizontal/vertical flex row         | `<div class="flex">`|

## Display

| Type                    | Purpose                      | Renders as            |
|-------------------------|------------------------------|-----------------------|
| `acg.display.heading`   | h1–h6                        | `<h{level}>`          |
| `acg.display.text`      | Paragraph or span            | `<p>` or `<span>`     |
| `acg.display.markdown`  | Server-rendered markdown     | `<div>` w/ HTML       |
| `acg.display.html`      | Raw HTML fragment            | inline                |
| `acg.display.badge`     | Label pill                   | `<span class="badge">`|
| `acg.display.link`      | Hyperlink                    | `<a>`                 |
| `acg.display.image`     | Image                        | `<img>`               |
| `acg.display.emblem`    | Guild mark / emblem          | `<div class="emblem">`|

## Cards

| Type                    | Purpose                      |
|-------------------------|------------------------------|
| `acg.card.paper`        | White paper card             |
| `acg.card.member`       | Member profile card          |
| `acg.card.entry`        | Generic list entry card      |
| `acg.card.manifesto`    | Manifesto card                |
| `acg.card.future-slot`  | Placeholder for planned content |

## Navigation

| Type                   | Purpose                   |
|------------------------|---------------------------|
| `acg.nav.top`          | Top-of-page nav bar       |
| `acg.nav.article`      | In-article section links  |
| `acg.nav.back-link`    | Back-to-parent link       |
| `acg.nav.cta`          | Call-to-action block      |
