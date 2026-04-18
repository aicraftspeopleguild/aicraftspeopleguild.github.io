# ACG Build Scripts

Run the executable README for full help and dispatch:

```bash
./guild/Enterprise/L3/scripts/README.sh           # show help
./guild/Enterprise/L3/scripts/README.sh build     # run full build
./guild/Enterprise/L3/scripts/README.sh papers:regen
```

## Directory layout

```
scripts/
├── README.sh              ← executable dispatcher (this doc is run: ./README.sh)
├── build.sh               ← full pipeline orchestrator
├── build.js               ← Node view-tree → HTML renderer
├── white-papers/
│   ├── extract.py         ← HTML → originals/*.md
│   └── regen-index.py     ← UDT instances → dist/white-papers.html
├── members/
│   ├── extract.py         ← HTML → originals/*.md + Member UDTs
│   └── regen-index.py     ← UDT instances → dist/members.html
├── components/
│   ├── extract.py         ← engineering docs → components/udts/instances/*.json
│   └── build-catalog.py   ← category → component IDs inverted index
├── pages/
│   └── decompose.py       ← static HTML → views/*.view.json + data/*.data.json
└── docs/
    ├── split-catalog.py   ← split component-catalog/index.md into per-file docs
    └── split-udt-spec.py  ← split udt-system.md into per-type docs
```

See each script's top-of-file docstring for full behavior.
