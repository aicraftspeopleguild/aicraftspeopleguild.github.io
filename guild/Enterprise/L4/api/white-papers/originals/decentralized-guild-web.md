---
title: "ACG-NET: Decentralized Guild Web"
slug: decentralized-guild-web
authors: [ACG-NET, Federated GitHub Pages, Bloom Prompt]
publication_date: March 2026
summary: Bloom Prompt · Federated GitHub Pages · P2P Member Sites
status: published
site_href: decentralized-guild-web.html
---

**"The guild site is a hub, not a host. Your page is yours. The network is ours."**

This paper proposes a federated network of GitHub Pages sites where each Guild member owns their own public node, while the main Guild site acts as the discovery hub and index. The hub does not host member content. It discovers it, ranks it, and routes traffic back to member-owned repos.

## 1. What This Builds

ACG-NET defines a decentralized Guild web built from static hosting, Git repos, JSON manifests, and GitHub Actions. Each member forks a template repo, customizes a personal site, and registers that site with the main Guild hub. The hub aggregates manifests into a live network index, leaderboards, and content feeds without taking ownership of the underlying pages.

The central design decision is architectural rather than cosmetic: the Guild site is a **router**, not a **server**. Member content stays in member repos. The Guild hub acts as a portal into a constellation of nodes.

**Deploy as:** GitHub Pages for the hub and GitHub Pages for each member node.

**Backend:** zero. Git is the backend. JSON files are the database.

**Discovery:** cross-repo fetch via GitHub Pages CORS and `raw.githubusercontent`.

**Extra layer:** onlybrains-style gamification with achievements, rankings, brain tiers, and visible progression through the Guild.

## 2. Origin (Discord, March 2026)

The architecture originated in Guild discussion around how to scale visibility and participation without centralizing member output into a single owned platform.

```
thomas_the_tank_engineer:
  - "i like my site onlybrains.io maybe can think of a similar way
     to gamify and rank guild members with like achievements"
  - "galaxy brain lol"
  - "each member should have a like ACG fork of some template repo,
     then registered members get their github page tied back into
     the main one"
  - "So the guild site becomes a hub for accessing decentralized
     member content versus centralizing processing within the guild"

v:
  - "the guild has already been through an evolution and is now
     coherent and in agreement about many important things"
  - "Raising awareness of the Guild is the first step"
  - "lol onlybrains"

core_insight: |
  Thomas nailed the architecture: the guild site is a ROUTER,
  not a SERVER. Each member owns their node. The hub discovers
  nodes and builds a live map. This is how you scale a guild
  without centralizing it. This is the web architecture that
  matches the manifesto's decentralization values.

  And the gamification makes it FUN. OnlyBrains energy.
  Galaxy brain achievements. Visible progression. The kind of
  thing that makes people WANT to participate, not just sign up.
```

## 3. Architecture: How GitHub Pages Talk to Each Other

### The Problem

GitHub Pages are static sites. They do not run application servers, store conventional databases, or offer direct inter-site mutation. So the problem is not how to build a centralized platform on static hosting. The problem is how to define a protocol that lets static nodes discover one another and share enough state to behave like a network.

### The Solution

The paper's answer is blunt: you do not need a server. You need a protocol. Git repos become databases. GitHub Pages become HTTPS-readable APIs. GitHub Actions become cron jobs. Pull requests become the registration workflow.

```
problem: |
  GitHub Pages are static sites. They can't run servers.
  They can't have databases. They can't POST to each other.
  So how do you build a federated network on static hosting?

solution: |
  You don't need a server. You need a PROTOCOL.

  Git repos ARE databases (JSON files committed to repos).
  GitHub Pages ARE APIs (fetch any file via HTTPS).
  GitHub Actions ARE cron jobs (scheduled builds).
  Pull Requests ARE registration (member submits PR to hub).

  The "P2P" layer is:
  1. Each member site publishes a manifest.json at a known URL
  2. The hub site fetches all registered manifests at build time
  3. The hub builds an aggregate index from all manifests
  4. Member sites fetch the hub index for network-wide data
  5. GitHub Actions rebuilds the hub on a schedule (hourly/daily)

  No server. No database. No API keys. Just HTTPS GETs
  between static files that are rebuilt by git automation.
```

### The Protocol

```
discovery_protocol:
  name: "ACG-DISCOVER"
  version: 1

  step_1_fork:
    action: "Member forks acg-member-template repo"
    result: "username.github.io/acg-member/ goes live"
    auto: "GitHub Pages deploys on fork"

  step_2_manifest:
    action: "Member edits their manifest.json"
    location: "https://username.github.io/acg-member/manifest.json"
    content: |
      {
        "acg_protocol": "ACG-DISCOVER-v1",
        "member": {
          "handle": "ThomasTheTankEngineer",
          "github": "ThomasTheTankEngineer",
          "joined": "2026-03-01",
          "tagline": "is the human conscious",
          "avatar_url": "https://...github.io/acg-member/avatar.png",
          "site_url": "https://thomasthetankengineer.github.io/acg-member/"
        },
        "achievements": [],
        "stats": {
          "contributions": 0,
          "publications": 0,
          "vettings_passed": 0,
          "refusals_filed": 0,
          "audits_served": 0,
          "sessions_attended": 0
        },
        "content": {
          "posts": [],
          "projects": [],
          "resources": []
        },
        "updated": "2026-03-15T12:00:00Z"
      }

  step_3_register:
    action: "Member submits PR to hub repo adding their URL to registry.json"
    file: "data/registry.json"
    addition: |
      {
        "handle": "ThomasTheTankEngineer",
        "manifest_url": "https://thomasthetankengineer.github.io/acg-member/manifest.json",
        "registered": "2026-03-15"
      }
    review: "Any existing member can approve (PR review)"
    merge: "On merge, GitHub Action triggers hub rebuild"

  step_4_discovery:
    action: "Hub GitHub Action runs hourly"
    process: |
      1. Read data/registry.json (list of all member manifest URLs)
      2. Fetch each manifest.json via HTTPS GET
      3. Validate schema (reject malformed manifests)
      4. Aggregate into data/network.json (the full network state)
      5. Compute rankings, achievements, leaderboards
      6. Rebuild hub site with fresh data
      7. Commit updated data/network.json + site files
      8. GitHub Pages deploys automatically

    failure_handling: |
      If a member's manifest is unreachable:
      - Mark as "offline" in network.json (don't remove)
      - After 30 days offline: mark as "dormant"
      - After 90 days: move to "inactive" (still in registry)
      - Never auto-delete. Members can come back.

  step_5_backfeed:
    action: "Member sites fetch hub's network.json"
    process: |
      Member's site can show:
      - Their rank in the guild
      - Network-wide stats
      - Other members' public profiles
      - Achievement leaderboard
      All by fetching one file from the hub.
      The hub is the index. The members are the content.
```

### Data Flow Diagram

```
MEMBER A's REPO                    HUB REPO                     MEMBER B's REPO
(GitHub Pages)                     (GitHub Pages)               (GitHub Pages)

manifest.json --GET-------------> GitHub Action
                                   | fetches all
                                   | manifests                  <--GET-- manifest.json
                                   v
                                   network.json
                                   (aggregated)
                                   |
              <----GET-------------|--------GET-------------->
              network.json         |              network.json
              (for my rank,        |              (for my rank,
               leaderboard)        |               leaderboard)
                                   |
                                   v
                                   HUB SITE
                                   (portal to all members)

NO SERVERS. NO DATABASES. JUST STATIC FILES AND HTTPS GETS.
```

## 4. The Template Repo: `acg-member-template`

The member template is the onboarding vehicle. It gives each participant a working Guild-shaped node with a known manifest schema, a customizable profile page, content folders, and automation hooks for keeping their node fresh.

```
acg-member-template/
├── index.html              # Member's public profile page
├── manifest.json           # Machine-readable identity + stats
├── achievements.html       # Achievement showcase
├── content/
│   ├── posts/              # Member's blog posts (markdown)
│   │   └── 2026-03-15-my-first-post.md
│   ├── projects/           # Project showcases
│   │   └── my-project.md
│   └── resources/          # Shared resources, tools, guides
├── assets/
│   ├── avatar.png          # Member avatar
│   ├── banner.png          # Profile banner (optional)
│   └── style.css           # Customizable theme
├── data/
│   ├── local-stats.json    # Auto-updated by GitHub Actions
│   └── achievements.json   # Unlocked achievements
├── .github/
│   └── workflows/
│       ├── update-manifest.yml  # Rebuilds manifest from content
│       └── verify-content.yml   # Validates post format
├── CUSTOMIZE.md            # "Edit these files to make it yours"
└── README.md               # Setup instructions
```

### Member Profile Page

```
design: |
  Dark terminal aesthetic matching ELIZA and Guild Ops.
  IBM Plex Mono + Crimson Pro. Green guild accents.
  BUT: members can customize their theme via assets/style.css.
  The template is a starting point, not a cage.

sections:
  header:
    - "⚒ ACG Member badge"
    - "Member handle + avatar"
    - "Tagline"
    - "Brain tier indicator (see gamification)"

  stats_bar:
    - "Guild rank"
    - "Brain tier"
    - "Achievement count"
    - "Contribution score"
    - "Member since date"

  achievements:
    - "Visual achievement grid (unlocked = bright, locked = dim)"
    - "Hover for achievement details"

  content_feed:
    - "Latest posts, projects, resources"
    - "Rendered from markdown files in content/"

  network_widget:
    - "Fetches network.json from hub"
    - "Shows member's position in guild leaderboard"
    - "Links to other members' pages"
    - "Live network stats (total members, total posts)"

  footer:
    - "ACG Manifesto principles (rotating)"
    - "Link back to hub"
    - "Verify on ACG-KCC chain link (future)"
```

## 5. Gamification: OnlyBrains Energy

The paper does not treat gamification as decorative fluff. It treats it as participation infrastructure. The hub can surface movement through the Guild in a way that is visible, playful, and aligned with contribution rather than shallow vanity metrics.

### Brain Tiers

```
description: |
  Thomas's onlybrains.io inspiration. Members progress through
  brain tiers based on participation, contribution, and demonstrated
  alignment with the manifesto. Not just activity — quality.

tiers:
  tier_0:
    name: "Smooth Brain"
    emoji: "🧠"
    color: "#888888"
    requirement: "Signed the manifesto"
    points: 0

  tier_1:
    name: "Wrinkled Brain"
    emoji: "🧠✨"
    color: "#5b9bd5"
    requirement: "Passed ELIZA vetting + 3 sessions attended"
    points: 100

  tier_2:
    name: "Big Brain"
    emoji: "🧠🔥"
    color: "#4ae08a"
    requirement: "Published 1 post + served as reviewer + 500 points"
    points: 500

  tier_3:
    name: "Galaxy Brain"
    emoji: "🧠🌌"
    color: "#d4883a"
    requirement: "Served as auditor OR processed refusal + 1,500 points"
    points: 1500

  tier_4:
    name: "Cosmic Brain"
    emoji: "🧠🪐"
    color: "#aa44ff"
    requirement: "CL-3 aligned org + published white paper + 5,000 points"
    points: 5000

  tier_5:
    name: "Transcendent Brain"
    emoji: "🧠⚡"
    color: "#ffd700"
    requirement: "Founding member OR 10,000+ points + community nomination"
    points: 10000
    note: "The Alex tier. The Woody tier. You earn this one."

point_system:
  attend_session: 10
  pass_eliza_vetting: 100
  publish_post: 50
  publish_project: 100
  serve_as_reviewer: 200
  serve_as_auditor: 500
  process_refusal_review: 300
  file_ethical_refusal: 200
  contribute_to_spec: 300
  contribute_to_tool: 400
  mentor_new_member: 150
  present_at_session: 100
  recruit_new_member: 50
```

### Achievements

```
description: |
  Visual badges that show up on member profiles. Some are common,
  some are rare, some are legendary. Designed to be fun to collect
  and meaningful to earn.

achievements:
  first_steps:
    name: "First Steps"
    icon: "👣"
    description: "Forked the template and deployed your member page"
    rarity: "common"

  the_interview:
    name: "The Interview"
    icon: "🔍"
    description: "Passed ELIZA vetting — is the human conscious? yes."
    rarity: "common"

  wordsmith:
    name: "Wordsmith"
    icon: "✍️"
    description: "Published your first post"
    rarity: "common"

  prolific:
    name: "Prolific"
    icon: "📚"
    description: "Published 10 posts"
    rarity: "uncommon"

  toolmaker:
    name: "Toolmaker"
    icon: "🔧"
    description: "Contributed to a guild tool (ELIZA, Guild Ops, etc.)"
    rarity: "rare"

  white_paper:
    name: "White Paper"
    icon: "📜"
    description: "Co-authored a published ACG white paper"
    rarity: "rare"

  spec_writer:
    name: "Spec Writer"
    icon: "📐"
    description: "Contributed to a technical specification"
    rarity: "epic"

  gate_keeper:
    name: "Gate Keeper"
    icon: "🚪"
    description: "Served as reviewer for 5+ publications"
    rarity: "uncommon"

  the_auditor:
    name: "The Auditor"
    icon: "🔎"
    description: "Completed a conformance audit"
    rarity: "rare"

  i_said_no:
    name: "I Said No"
    icon: "✋"
    description: "Filed an ethical refusal. Principle 6 in action."
    rarity: "rare"
    note: "This is the most important achievement in the system."

  guardian:
    name: "Guardian"
    icon: "🛡️"
    description: "Served as independent reviewer on an ethical refusal"
    rarity: "epic"

  shield_wall:
    name: "Shield Wall"
    icon: "⚔️"
    description: "Supported a colleague's ethical refusal publicly"
    rarity: "epic"

  regular:
    name: "Regular"
    icon: "☕"
    description: "Attended 10 guild sessions"
    rarity: "common"

  mentor:
    name: "Mentor"
    icon: "🎓"
    description: "Mentored 3 new members through onboarding"
    rarity: "uncommon"

  recruiter:
    name: "Recruiter"
    icon: "📢"
    description: "Recruited 5 new members who passed vetting"
    rarity: "uncommon"

  founding_hammer:
    name: "Founding Hammer"
    icon: "⚒️"
    description: "Was there at the beginning. Signed the original manifesto."
    rarity: "legendary"
    holders: "Alex Bunardzic, Woody Zuill, Jona Heidsick, Matt Burch, Alex Thurow, Tsvetan Tsvetanov"

  galaxy_brain:
    name: "Galaxy Brain"
    icon: "🌌"
    description: "Reached Galaxy Brain tier. Thomas would be proud."
    rarity: "legendary"

  equation_breaker:
    name: "Equation Breaker"
    icon: "💥"
    description: "Demonstrated breaking the Harm Equation in a real-world scenario, documented and verified."
    rarity: "legendary"

  chain_runner:
    name: "Chain Runner"
    icon: "🔗"
    description: "Running an ACG-KCC node on a Raspberry Pi"
    rarity: "rare"

rarity_colors:
  common: "#888888"
  uncommon: "#5b9bd5"
  rare: "#4ae08a"
  epic: "#d4883a"
  legendary: "#ffd700"
```

### Leaderboard

```
design: |
  The hub's main page shows the guild leaderboard.
  Not competitive in a toxic way — competitive in a
  "look at all these people doing good work" way.

  Leaderboard sorts by contribution score but shows
  brain tier prominently. The vibe is onlybrains meets
  GitHub contribution graph meets RPG character sheet.

display:
  header: "⚒ ACG GUILD — Member Network"
  stats_bar:
    - "Total members"
    - "Total posts"
    - "Total achievements unlocked"
    - "Ethical refusals protected"
    - "Certifications issued"

  leaderboard:
    columns:
      - "Rank"
      - "Brain tier emoji"
      - "Handle (links to member page)"
      - "Contribution score"
      - "Achievement count"
      - "Latest activity"
    sort: "Contribution score (default), switchable"
    display: "Top 50, with search for others"

  achievement_showcase:
    - "Recently unlocked achievements across the guild"
    - "Rarest achievements and who holds them"
    - "Achievement completion stats (% of guild with each)"

  network_map:
    - "Visual graph of member connections"
    - "Lines between members who've collaborated"
    - "Cluster by chapter/region (future)"

  content_river:
    - "Latest posts from across all member sites"
    - "Aggregated from all manifest.json content arrays"
    - "Links to original member page (traffic goes to THEM)"
```

## 6. GitHub Actions: The Automation Layer

The automation model stays inside the GitHub ecosystem. The hub periodically crawls the registry and rebuilds the network index. Member repos regenerate manifests when content changes. The system behaves like a networked platform while remaining static at rest.

### Hub Actions

```
hourly_discovery:
  name: "ACG Network Discovery"
  trigger: "schedule: cron '0 * * * *'"
  steps:
    - "Checkout hub repo"
    - "Read data/registry.json"
    - "For each registered member:"
    -   "  Fetch their manifest.json"
    -   "  Validate schema"
    -   "  Record online/offline status"
    - "Aggregate all manifests into data/network.json"
    - "Compute rankings, brain tiers, leaderboard"
    - "Detect newly unlocked achievements"
    - "Rebuild hub site (static HTML from templates + data)"
    - "Commit and push if changes detected"
    - "GitHub Pages auto-deploys"

  script_language: "Node.js (runs in GitHub Actions)"
  no_secrets_needed: "All manifest URLs are public GitHub Pages"

on_pr_merge:
  name: "New Member Registration"
  trigger: "pull_request merged to main, modifies data/registry.json"
  steps:
    - "Validate new member's manifest URL is reachable"
    - "Validate manifest schema"
    - "Run immediate discovery cycle"
    - "Welcome message in PR comments"
```

### Member Actions

```
on_content_change:
  name: "Update Manifest"
  trigger: "push to main branch"
  steps:
    - "Scan content/ directory for posts, projects, resources"
    - "Update manifest.json content arrays"
    - "Recalculate local stats"
    - "Commit updated manifest.json"
    - "GitHub Pages redeploys"

  result: |
    When a member pushes a new blog post, their manifest.json
    auto-updates within minutes. The hub's next hourly crawl
    picks up the new content. No manual updating needed.

verify_content:
  name: "Content Validation"
  trigger: "pull_request to own repo"
  steps:
    - "Validate markdown frontmatter"
    - "Check for required fields (title, date, tags)"
    - "Lint markdown"
    - "Preview manifest changes"
```

## 7. Cross-Site Communication Patterns

The network has four basic communication patterns: the hub reads members, members read the hub, members navigate to one another via the hub index, and the hub aggregates distributed content into a river of posts.

### Pattern 1: Hub Reads Members (Discovery)

```
async function discoverNetwork() {
  const registry = JSON.parse(fs.readFileSync('data/registry.json'));
  const network = { members: [], updated: new Date().toISOString() };

  for (const entry of registry.members) {
    try {
      const res = await fetch(entry.manifest_url);
      if (!res.ok) { markOffline(entry); continue; }
      const manifest = await res.json();
      if (!validateSchema(manifest)) { markInvalid(entry); continue; }
      network.members.push({
        ...manifest.member,
        stats: manifest.stats,
        achievements: manifest.achievements,
        content: manifest.content,
        status: 'online',
        last_seen: new Date().toISOString()
      });
    } catch (e) {
      markOffline(entry);
    }
  }

  computeRankings(network);
  computeAchievements(network);
  fs.writeFileSync('data/network.json', JSON.stringify(network, null, 2));
}
```

### Pattern 2: Members Read Hub (Backfeed)

```
async function loadNetworkData() {
  const HUB = 'https://aicraftspeopleguild.github.io';
  try {
    const res = await fetch(`${HUB}/data/network.json`);
    const network = await res.json();

    const me = network.members.find(m => m.github === MY_GITHUB);
    if (me) {
      renderRank(me.rank);
      renderBrainTier(me.brain_tier);
      renderLeaderboardPosition(me, network.members);
    }

    renderNetworkStats({
      total_members: network.members.length,
      total_posts: network.members.reduce((s,m) => s + m.stats.publications, 0),
      total_achievements: network.members.reduce((s,m) => s + m.achievements.length, 0)
    });
  } catch (e) {
    renderOfflineState();
  }
}
```

### Pattern 3: Member-to-Member (Via Hub Index)

```
async function findMemberContent(handle) {
  const res = await fetch(`${HUB}/data/network.json`);
  const network = await res.json();
  const member = network.members.find(m => m.handle === handle);
  if (member) {
    window.location.href = member.site_url;
  }
}

// Members don't talk to each other directly.
// They talk THROUGH the hub index.
// The hub is the router, not the server.
```

### Pattern 4: Content Aggregation (River of Posts)

```
function buildContentRiver(network) {
  const allPosts = [];
  for (const member of network.members) {
    for (const post of member.content.posts) {
      allPosts.push({
        ...post,
        author: member.handle,
        author_url: member.site_url,
        author_tier: member.brain_tier
      });
    }
  }
  allPosts.sort((a, b) => new Date(b.date) - new Date(a.date));
  return allPosts.slice(0, 100);
}
```

## 8. ACG-KCC Chain Integration (Future)

The federation works without the Guild chain. That is deliberate. The chain is an optional verification layer that can later replace self-reported claims with trust-minimized checks for membership, seals, vettings, and achievement unlocks.

```
description: |
  When the guild chain goes live, the GitHub Pages federation
  gains a verification layer. Achievements and stats are currently
  self-reported (in manifest.json, updated by member's own Actions).
  The chain adds trustless verification.

verification_flow:
  vetting:
    current: "Member claims 'vettings_passed: 1' in manifest"
    with_chain: "Hub verifies against VettingSession contract on ACG-KCC L1"

  achievements:
    current: "Member claims achievements in achievements.json"
    with_chain: "Achievement unlock events emitted by chain, hub verifies"

  membership:
    current: "PR approval by existing member"
    with_chain: "Member registration on MembershipContract, hub reads chain"

  seal_display:
    current: "Visual badge on member page"
    with_chain: "On-chain seal with verify link to chain explorer"

  note: |
    The GitHub Pages federation works WITHOUT the chain. The chain
    adds verification but is not required. This is deliberate:
    the federation should work even if the chain hasn't launched yet,
    or if members don't run nodes. Graceful degradation.
    Chain = nice to have. Git federation = the foundation.
```

## 9. Template Customization Guide

The protocol constrains the schema, not the person. Members share a machine-readable manifest contract so the hub can index them, but the visible identity of each node remains member-owned.

```
what_members_customize:
  must_edit:
    - "manifest.json (handle, tagline, joined date)"
    - "assets/avatar.png (their photo or icon)"

  should_edit:
    - "content/ (add their posts, projects)"
    - "README.md (personal intro)"

  can_edit:
    - "assets/style.css (custom colors, fonts, layout)"
    - "index.html (layout modifications)"
    - "achievements.html (display preferences)"

  must_not_edit:
    - "ACG protocol version in manifest.json"
    - "Schema structure of manifest.json"
    - ".github/workflows/ (breaks auto-updates)"
    - "Protocol-level JavaScript (hub communication)"

customization_philosophy: |
  The template gives you guild identity. Your edits give you
  personal identity. The constraint is the schema (so the hub
  can read your manifest). Everything else is yours.

  Thomas's page should look like Thomas's page.
  Alex's page should look like Alex's page.
  The guild aesthetic is a shared thread, not a uniform.
```

## 10. Build Commands

```
# === HUB REPO ===
mkdir -p acg-guild-hub/{data,.github/workflows}
cd acg-guild-hub
# Create: index.html, data/registry.json, data/network.json
# Create: .github/workflows/discover.yml
# Create: scripts/discover.js (Node.js discovery script)
# Deploy: GitHub Pages on main branch
# URL: aicraftspeopleguild.github.io

# === MEMBER TEMPLATE REPO ===
mkdir -p acg-member-template/{content/{posts,projects,resources},assets,data,.github/workflows}
cd acg-member-template
# Create: index.html, manifest.json, achievements.html
# Create: assets/style.css, CUSTOMIZE.md, README.md
# Create: .github/workflows/update-manifest.yml
# Mark as "Template repository" in GitHub settings
# Members click "Use this template" -> instant fork + deploy

# === MEMBER JOINS ===
# 1. Member clicks "Use this template" on acg-member-template
# 2. Edits manifest.json with their info
# 3. Enables GitHub Pages (Settings -> Pages -> main branch)
# 4. Submits PR to hub repo adding their URL to registry.json
# 5. Existing member approves PR
# 6. Hub discovers them on next hourly crawl
# 7. They appear on the leaderboard within the hour
# 8. They're in. No server. No account. No permission. Just git.
```

## 11. The Network Effect

Each new member adds one more node, one more manifest, more content, more discoverability, and more visible participation. The value of the hub increases with every member because it indexes more useful material, yet the operating model remains cheap because the hub is only fetching public JSON and rebuilding static pages.

That means the network effect is real without requiring platform capture. Member pages become more valuable because the shared index brings readers to them. The hub becomes more valuable because it shows a denser and more active Guild. And any member can still leave with their content intact, because their repo was always theirs.

```
growth_dynamics: |
  Each new member adds:
  - One more node in the network (their GitHub Pages site)
  - One more manifest for the hub to discover
  - Content that appears in the guild river
  - A leaderboard entry that shows the guild is growing
  - A potential collaborator visible to all other members

  The hub gets MORE VALUABLE as members join, because it indexes
  MORE CONTENT. But it doesn't get more EXPENSIVE, because it's
  just fetching JSON files. GitHub Actions free tier handles
  thousands of manifests.

  Member pages get more valuable too, because the network widget
  shows their rank among more people, and the content river
  brings more readers to their posts.

  This is the same network effect that makes onlybrains.io work:
  the more people, the more interesting the leaderboard,
  the more reason to participate, the more people.

  But unlike centralized platforms: every member can take their
  content and leave. Their repo is theirs. Their posts are theirs.
  The guild never owned them. The guild just discovered them.
```

the hub is a router not a server

your page is yours the network is ours

git is the backend json is the database

github actions is the cron

PRs are registration

no servers no databases no permission

just static files talking to static files

galaxy brain energy

⚒ ACG
