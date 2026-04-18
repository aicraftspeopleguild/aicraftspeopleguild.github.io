// UDT custom elements for the ACG-TEST site.
// Every expectation-bearing element requires a reason attribute.
// Elements render a readable summary derived from their attributes.

const REASON = "reason";

function row(label, value) {
  if (value === undefined || value === null || value === "") return "";
  return `<div><span class="k">${label}</span> <span class="v">${escape(value)}</span></div>`;
}

function escape(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

class UdtBase extends HTMLElement {
  connectedCallback() {
    if (!this.hasAttribute(REASON) && this.requiresReason) {
      this.setAttribute("data-missing-reason", "true");
    }
    this.render();
  }
  get requiresReason() { return true; }
  render() { /* override */ }
}

class UdtExpectation extends UdtBase {
  render() {
    const expect = this.getAttribute("expect") || "present";
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("expect", expect)}
      ${row("reason", reason)}
    `;
  }
}

class UdtEventTrigger extends UdtBase {
  render() {
    const event = this.getAttribute("event");
    const types = this.getAttribute("types");
    const paths = this.getAttribute("paths");
    const expect = this.getAttribute("expect") || "triggered";
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("event", event)}
      ${row("types", types)}
      ${row("paths", paths)}
      ${row("expect", expect)}
      ${row("reason", reason)}
    `;
  }
}

class UdtPathWatch extends UdtBase {
  render() {
    const path = this.getAttribute("path");
    const expect = this.getAttribute("expect") || "triggered";
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("path", path)}
      ${row("expect", expect)}
      ${row("reason", reason)}
    `;
  }
}

class UdtGuardrail extends UdtBase {
  render() {
    const condition = this.getAttribute("condition");
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("condition", condition)}
      ${row("expect", "not triggered")}
      ${row("reason", reason)}
    `;
  }
}

class UdtSecret extends UdtBase {
  render() {
    const name = this.getAttribute("name");
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("name", name)}
      ${row("expect", "configured")}
      ${row("reason", reason)}
    `;
  }
}

class UdtNotification extends UdtBase {
  get requiresReason() { return false; }
  render() {
    const type = this.getAttribute("type") || "email";
    const header = `<div><span class="k">type</span> <span class="v">${escape(type)}</span></div>`;
    // Preserve nested udt-field children inside the element.
    const fields = Array.from(this.querySelectorAll(":scope > udt-field"));
    const fieldsMarkup = fields.map(f => f.outerHTML).join("");
    this.innerHTML = header + fieldsMarkup;
  }
}

class UdtField extends UdtBase {
  render() {
    const name = this.getAttribute("name");
    const address = this.getAttribute("address");
    const contains = this.getAttribute("contains");
    const expect = this.getAttribute("expect") || "present";
    const reason = this.getAttribute(REASON) || "(missing reason)";
    this.innerHTML = `
      ${row("field", name)}
      ${row("address", address)}
      ${row("contains", contains)}
      ${row("expect", expect)}
      ${row("reason", reason)}
    `;
  }
}

class UdtWorkflowTest extends UdtBase {
  get requiresReason() { return false; }
  render() {
    // Root container — children are rendered as-is; we only stamp the header via ::before.
  }
}

customElements.define("udt-expectation", UdtExpectation);
customElements.define("udt-eventtrigger", UdtEventTrigger);
customElements.define("udt-pathwatch", UdtPathWatch);
customElements.define("udt-guardrail", UdtGuardrail);
customElements.define("udt-secret", UdtSecret);
customElements.define("udt-notification", UdtNotification);
customElements.define("udt-field", UdtField);
customElements.define("udt-workflowtest", UdtWorkflowTest);
