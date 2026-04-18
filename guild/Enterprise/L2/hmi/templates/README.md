# controls/hmi/templates

Copy-and-fill template library for the HMI subsystem.  Each file follows
the **Konomi dense-token** shape (see `/controls/scada/00-legend.json` for
glyph / type shorthand) and the **/index/** udt + tags schema.

```
templates/
  udts.template.json        reference shape of /{sub}/udts.json — HMI-flavoured
  tags.template.json        reference shape of /{sub}/tags.json — HMI-flavoured
  faceplate/                ISA-101 faceplate library — one file per equipment type
    motor.faceplate.json    DOL motor faceplate
    valve.faceplate.json    two-position valve with limit-switch feedback
    analog.faceplate.json   scaled AI / AO with alarm badges
    pid.faceplate.json      closed-loop PID controller
    vfd.faceplate.json      variable-frequency drive
  badges/
    alarm.badge.json        ISA-18.2 alarm-summary badge (P1-P4 counts)
    state.badge.json        semantic-color state pill (Running/Stopped/Faulted…)
    quality.badge.json      OPC-UA tag-quality pill
  layers/
    L1.overview.json        L1 Overview (Plant/Site) — KPIs, alarms, status
    L2.area.json            L2 Area — flows, states, trends
    L3.unit.json            L3 Unit — faceplate grid + control
    L4.detail.json          L4 Detail — config, tuning, diagnostic
    L5.support.json         L5 Support — calibration, history
```

## Anatomy of a faceplate template

Every faceplate is a compact JSON that binds a physical equipment UDT
(from `/controls/plc/git/cm/`) to a tag set the operator sees:

```jsonc
{
  "$schema":   "hmi/faceplate/v1",
  "name":      "<Motor|Valve|PID|...>_Faceplate",
  "udt":       "CM_Motor",                // source UDT in plc/git/cm/
  "isaLayer":  "L3",                      // where it lives in the screen stack
  "bindings": {
    "pv":   ["sts.running", "sts.current", "sts.runtime"],
    "sp":   ["cmd.start",   "cmd.stop",    "cmd.reset"],
    "mode": "mode.current",
    "state":"state.current",
    "alarm":"fault.active"
  },
  "palette": ["Running","Stopped","Faulted","Manual"],
  "commands":[{"cmd":"cmd.start","label":"START","confirm":false},
              {"cmd":"cmd.stop", "label":"STOP", "confirm":true}]
}
```

## Token budget

Every file is kept **under 250 tokens** so any single faceplate or
layer definition can be dropped into an LLM prompt whole.
