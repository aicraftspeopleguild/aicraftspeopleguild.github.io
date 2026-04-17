---
title: "ACG-KCC: Guild Chain"
slug: guild-chain
publication_date: March 2026
summary: Konomi Cube Coin Private Fork for AI Craftspeople Guild Operations
status: published
site_href: guild-chain.html
---

**"The protected register is on-chain. Good luck retaliating against a blockchain."**

ACG-KCC is a permissioned private fork of the Konomi Cube Coin architecture, designed to run AI Craftspeople Guild operations as an enterprise blockchain. Its central claim is that the Guild's protected ethical refusal register needs a storage layer that no single actor can tamper with, delete, or pressure into silence.

## 1. Executive Summary

ACG-KCC is a permissioned private fork of the Konomi Cube Coin architecture, purpose-built to run AI Craftspeople Guild operations as an enterprise blockchain. The KCC multi-nested cube agent system is remapped to the six guild PackML state machine units. The self-healing error system becomes the ethical refusal protection layer. Hash compression stores vetting transcripts, certification evidence, and the protected refusal register with 15:1 storage efficiency.

**Core thesis:** the ACG Manifesto's most critical infrastructure, the protected ethical refusal register (ACG-R-002), requires a storage layer that no single actor can tamper with, delete, or pressure into silence. A permissioned blockchain operated by guild members provides this guarantee.

**Why fork KCC specifically:**

- The cube agent architecture maps 1:1 to guild operations.
- Self-healing error correction maps to refusal protection and SLA enforcement.
- Hash compression solves the storage cost problem for certification evidence.
- Ring-0 kernel philosophy aligns with ACG's "no abstraction layers between engineer and truth".
- The dual-layer design maps cleanly to guild needs: Layer 1 for permanent records, Layer 2 for real-time operations.

## 2. Architectural Adaptation

### 2.1 KCC -> ACG-KCC Mapping

```
KONOMI CUBE COIN (public)          ->  ACG-KCC GUILD CHAIN (permissioned)
-------------------------------------------------------------------------
Layer 1 PoW (security)             ->  Layer 1 PoA (Authority - guild elders)
Layer 2 PoS (performance)          ->  Layer 2 PoS (Stake - guild members)
21,000,000 KCC supply              ->  510,510 GLD supply
KonomiHash mining                  ->  Authority block signing (no mining)
8 vertex agents                    ->  6 guild unit agents + 2 system agents
512 sub-cubes                      ->  512 operation slots (active work items)
Self-healing wrappers              ->  Refusal protection + SLA enforcement
Hash compression (storage)         ->  Evidence compression (vetting/audit/cert)
Smart contracts                    ->  Guild contracts (GuildC language)
Public permissionless              ->  Permissioned (guild members only)
GPU mining                         ->  Raspberry Pi capable (low barrier)
```

### 2.2 Dual-Layer Design

**Layer 1 - Authority Chain (Permanent Record)**

```
consensus: Proof of Authority (PoA)
validators: Guild Founding Committee + elected elders (5-11 nodes)
block_time: 60 seconds
block_size: 1 MB (hash-compressed)
finality: 1 block (instant with 2/3 authority consensus)
purpose:
  Immutable storage for:
  - Ethical refusal register entries (ACG-R-002)
  - Certification issuances and revocations
  - Membership records
  - Governance votes
  - Audit findings
  - Published document hashes (content on IPFS, hash on-chain)

node_requirements:
  hardware: Raspberry Pi 4 or equivalent
  storage: 32 GB SD card
  network: Home broadband sufficient
  rationale:
    Every guild member should be able to run an authority chain node.
    If the barrier is a data center, only corporations can validate.
    If the barrier is a Raspberry Pi, every engineer with a desk drawer can validate.
```

**Layer 2 - Operations Chain (Real-Time)**

```
consensus: Delegated Proof of Stake (DPoS)
validators: Any guild member staking 100+ GLD
block_time: 5 seconds
throughput: 1,000 TPS
finality: 2 blocks (10 seconds)
checkpoint: Every 50 L2 blocks -> 1 L1 entry
purpose:
  Real-time operational state for:
  - ELIZA vetting sessions
  - PackML unit state changes
  - Event bus messages between units
  - SLA timers and alerts
  - Member activity tracking
  - Reputation scoring
```

### 2.3 Cross-Layer Bridge

```
checkpoint_frequency: Every 50 L2 blocks (~4 minutes)
what_gets_checkpointed:
  always:
    - Ethical refusal submissions (immediate L1 write, no waiting)
    - Certification state changes
    - Membership state changes
    - Governance vote results
  batched:
    - Vetting completion records
    - Audit finding summaries
    - PackML state snapshots
  never_on_L1:
    - Raw vetting conversation transcripts
    - Internal agent chatter
    - Temporary operational state

special_rule:
  ETHICAL REFUSALS BYPASS THE CHECKPOINT QUEUE.
  When a refusal is filed, the refusal record is written directly to L1
  in the next L1 block, not batched with the regular checkpoint.
```

## 3. Cube Agent Remapping

### 3.1 The 8 Vertex Agents -> Guild Agents

```
KCC AGENT                    ->  ACG-KCC GUILD AGENT
--------------------------------------------------------------
Agent 0 [0,0,0]             ->  VETTING AGENT (ELIZA coordinator)
Agent 1 [999,0,0]           ->  CERTIFICATION AGENT
Agent 2 [999,999,0]         ->  PUBLISHING AGENT
Agent 3 [0,999,0]           ->  REFUSAL AGENT (the guardian)
Agent 4 [0,0,999]           ->  AUDIT AGENT
Agent 5 [999,0,999]         ->  MEMBERSHIP AGENT
Agent 6 [999,999,999]       ->  SYSTEM: RESOURCE MANAGER
Agent 7 [0,999,999]         ->  SYSTEM: ERROR CORRECTION
```

### 3.2 Sub-Cube Deployment (512 Operation Slots)

```
slot_allocation:
  UNIT_01_VETTING:    Slots 000-127 (128 concurrent vettings)
  UNIT_02_CERTIFY:    Slots 128-191 (64 concurrent certifications)
  UNIT_03_PUBLISH:    Slots 192-255 (64 concurrent publications)
  UNIT_04_REFUSAL:    Slots 256-319 (64 concurrent refusals)
  UNIT_05_AUDIT:      Slots 320-383 (64 concurrent audits)
  UNIT_06_MEMBERSHIP: Slots 384-511 (128 concurrent memberships)

per_slot:
  agents: 4
  state: Full PackML 17-state machine
  storage: Hash-compressed operation record
  comms: Event bus connection to parent vertex agent

total_capacity:
  concurrent_operations: 512
  total_agents: 8 vertex + 512x4 sub + 512x8 micro = 6,152
```

## 4. Self-Healing -> Refusal Protection System

### 4.1 The Retaliation Detection Engine

```
detection_layers:
  layer_1_pattern_matching:
    acg_adaptation:
      - Member status change within 90 days of filing refusal
      - Organization certification review triggered after refusal
      - Unusual access pattern to refusal records
      - Refusal record query from non-authorized agents

  layer_2_temporal_correlation:
    acg_adaptation:
      - Refusal filed -> professional's org changes behavior
      - Refusal filed -> professional reports difficulty
      - Multiple refusals from same org -> systemic pattern

  layer_3_agent_consensus:
    acg_adaptation:
      - REFUSAL AGENT flags pattern
      - AUDIT AGENT reviews evidence
      - MEMBERSHIP AGENT checks member status
      - 3-agent consensus -> escalate to Guild Committee

  layer_4_community_healing:
    acg_adaptation:
      - Protective actions for the professional
      - Organization flagged in certification system
      - Public statement with the professional's consent
      - Legal referral if warranted
      - Healing event logged to L1
```

### 4.2 SLA Enforcement (Hard Timers)

```
mechanism:
  When a refusal enters EXECUTE state (UNIT_04):
  1. L1 transaction records: {refusalID, startTime, SLA_deadline}
  2. Error correction agent monitors block timestamps
  3. At SLA_deadline - 3 days: WARNING event on bus
  4. At SLA_deadline - 1 day: CRITICAL event on bus
  5. At SLA_deadline: BREACH event -> auto-escalation

timer_contracts:
  refusal_sla: 15 business days (hard)
  audit_notice: 30 days advance notice
  cert_expiry: 24 months from issuance
  cert_change_review: 30 days from material change report
```

The refusal timer is on-chain. No one can claim they did not know, the email got lost, or the ticket vanished. The blockchain knew. The blockchain told everyone. The blockchain has receipts.

## 5. Hash Compression for Guild Data

### 5.1 What Gets Compressed

```
compression_targets:
  vetting_records:
    raw_size: ~50KB per session
    compressed: ~3.3KB (15:1 ratio)
    stored: L2 operational, summary hash on L1

  certification_evidence:
    raw_size: ~500KB per audit
    compressed: ~33KB
    stored: IPFS for full docs, compressed summary on L2, hash on L1

  refusal_records:
    raw_size: ~10KB per refusal
    compressed: ~700 bytes
    stored: directly on L1
    encryption: refuser identity encrypted, committee key can decrypt

  membership_records:
    raw_size: ~2KB per member
    compressed: ~140 bytes

chain_size_estimate:
  year_1: ~50MB on L1, ~500MB on L2
  year_5: ~250MB on L1, ~2.5GB on L2
  fits_on: Raspberry Pi SD card for at least a decade
```

### 5.2 Token Dictionary (Guild-Specific)

```
pre_loaded_tokens:
  manifesto_terms: ~200 tokens
  packml_states: 17 tokens
  acg_ts_clauses: ~100 tokens
  technical_vocabulary: ~2,000 tokens
  member_metadata: ~500 tokens
  remaining: ~62,719 tokens

adaptive_learning:
  The neural compression layer learns from guild usage patterns.
  As the guild generates more vetting records, the compressor
  gets better at compressing vetting records.
```

## 6. Tokenomics: 510,510 GLD

### 6.1 Why 510,510

```
explanation:
  510,510 is the A.S.S.-OS signature number. For ACG-KCC, it serves
  as the total supply of Guild Tokens (GLD), connecting the chain to
  the broader technical philosophy.

  GLD is NOT a cryptocurrency.
  GLD is NOT traded on exchanges.
  GLD is a utility token for guild operations.
```

### 6.2 Distribution

```
Total Supply: 510,510 GLD
==============================================
Founding Members (20%):      102,102 GLD
Active Members (40%):        204,204 GLD
Operations Reserve (25%):    127,627 GLD
Future Growth (15%):          76,577 GLD

Earned participation examples:
  - Complete ELIZA vetting: 100 GLD
  - Serve as auditor: 500 GLD per audit
  - Review publication: 200 GLD per review
  - Process ethical refusal: 300 GLD per review
  - Attend guild session: 10 GLD per session
```

### 6.3 Staking & Governance

```
staking:
  L2_validator: Minimum 100 GLD stake
  L1_authority: Elected by governance
  yield: 0% APR
  slashing:
    downtime_1hr: Warning
    downtime_24hr: 5 GLD slash
    malicious: Full slash + membership review

governance:
  proposal_deposit: 50 GLD
  voting_power: 1 GLD = 1 vote
  multiplier: ELIZA-vetted members get 1.5x
  quorum:
    standard: 20% of staked GLD
    protocol_change: 40%
    emergency: 10%
```

## 7. Guild Contracts (GuildC)

### 7.1 Language Adaptation

```
extensions:
  - PackML state machine primitives
  - SLA timer contracts
  - Role-based access control
  - Event bus integration
  - Hash compression hooks
```

### 7.2 Core Contracts

```
// ETHICAL REFUSAL CONTRACT
contract EthicalRefusal {
    struct Refusal {
        U64  id;
        U256 professional_hash;
        U256 org_hash;
        U64  filed_timestamp;
        U64  sla_deadline;
        U8   status;
        U256 reviewer_hash;
        U256 evidence_ipfs;
        bool retaliation_flag;
    }

    mapping(U64 => Refusal) public register;
    U64 public refusal_count;

    event RefusalFiled(U64 id, U64 deadline);
    event SLAWarning(U64 id, U64 days_remaining);
    event SLABreach(U64 id);
    event RetaliationDetected(U64 id);
    event RefusalResolved(U64 id, U8 outcome);

    public U0 FileRefusal(U256 prof_hash, U256 org_hash, U256 evidence) {
        require(hasRole(msg.sender, MEMBER));
        U64 id = refusal_count++;
        U64 deadline = calculateBusinessDays(block.timestamp, 15);
        commitToL1(register[id]);
        emit RefusalFiled(id, deadline);
    }

    public U0 CheckSLAs() {
        for (U64 i = 0; i < refusal_count; i++) {
            if (register[i].status == PENDING ||
                register[i].status == UNDER_REVIEW) {
                U64 remaining = register[i].sla_deadline - block.timestamp;
                if (remaining <= 3 days) emit SLAWarning(i, remaining);
                if (remaining <= 0)      emit SLABreach(i);
            }
        }
    }
}
```

```
// VETTING CONTRACT
contract VettingSession {
    struct Session {
        U64  id;
        U256 candidate_hash;
        U8   phase;
        U8   packml_state;
        U8   result;
        U64  started;
        U64  completed;
        U256 transcript_hash;
        U256 model_id;
    }

    event VettingStarted(U64 id, U256 candidate);
    event PhaseCompleted(U64 id, U8 phase);
    event VettingComplete(U64 id, U8 result);
    event SealIssued(U64 id, U256 candidate);
}
```

```
// CERTIFICATION CONTRACT
contract Certification {
    struct Cert {
        U64  id;
        U256 org_hash;
        U8   level;
        U64  issued;
        U64  expiry;
        U256 auditor_hash;
        U256 evidence_ipfs;
        U8   status;
    }
}
```

## 8. Node Deployment

### 8.1 Node Types

```
authority_node:
  role: L1 block signer
  hardware: Raspberry Pi 4 (4GB RAM) or equivalent
  storage: 32GB microSD
  count: 5-11 nodes

validator_node:
  role: L2 block producer
  hardware: Raspberry Pi 4 or any modern computer
  storage: 64GB
  stake: 100 GLD minimum

full_node:
  role: Store full chain, serve data, no block production
  hardware: Any computer made after 2015

light_client:
  role: Verify proofs, submit transactions
  hardware: Phone, tablet, browser
  implementation: WebAssembly in browser
```

### 8.2 Deployment Model

```
phase_1_bootstrap:
  when: Guild founding
  nodes: 5 authority nodes run by founding committee
  where: Home Raspberry Pis

phase_2_growth:
  when: 50+ members
  nodes: 7 authority + 20 validators + 50 full nodes

phase_3_scale:
  when: 500+ members
  nodes: 11 authority + 100 validators + 500 full nodes

phase_4_mature:
  when: 5,000+ members
  nodes: Global distribution, auto-scaling L2
```

## 9. Security Model (Guild-Adapted)

### 9.1 Threat Model

```
threats:
  external_pressure:
    mitigation:
      Refusal records on L1 require 2/3 authority consensus to modify.
      Authority nodes are Raspberry Pis in guild members' homes.

  insider_attack:
    mitigation:
      L1 writes require authority consensus.
      History is append-only.
      Audit agent monitors anomalous access patterns.

  sybil_membership:
    mitigation:
      All members must pass ELIZA vetting.
      GLD is earned through participation, not purchased.

  chain_split:
    mitigation:
      If a faction disagrees fundamentally, they should be able to fork.
      The refusal register persists on both chains.

  quantum_threat:
    mitigation:
      Migration path to post-quantum signatures when tooling matures.
```

### 9.2 Privacy Model

```
principle:
  The chain stores PROOF that things happened, not the things themselves.
  Vetting transcripts, personal details, and sensitive evidence
  are stored off-chain. The chain stores hashes, timestamps, and outcomes.

anonymization:
  members: Identified by hash of (name + salt)
  organizations: Identified by hash
  refusals: Professional identity encrypted with committee key
```

## 10. Integration Points

### 10.1 ELIZA -> Chain

```
flow:
  1. Candidate starts vetting -> VettingSession.StartSession() on L2
  2. ELIZA runs locally
  3. Session completes -> VettingSession.CompleteSession() on L2
  4. If PASS -> checkpointed to L1, seal issued on-chain
  5. Candidate receives seal as signed JSON blob with session hash,
     chain, block, timestamp, model, and verify URL.
```

### 10.2 PackML Dashboard -> Chain

```
flow:
  The Guild Ops PackML dashboard reads state directly from L2.
  Every PackML state transition is an L2 transaction.
  Multiple dashboards can exist and all show the same state
  because they all read the same chain.
```

### 10.3 GitHub Integration

```
flow:
  1. Author submits PR to guild GitHub repo
  2. Review process runs (UNIT_03 on-chain)
  3. PR merged -> GitHub Action computes document hash
  4. Hash written to L1 via PublishingContract
  5. Document is now permanently linked: GitHub for content, chain for proof
```

## 11. Roadmap

```
phase_1_spec:
  when: Q2 2026
  deliverables:
    - This specification document
    - GuildC contract definitions
    - Node software architecture
    - Community review period

phase_2_prototype:
  when: Q3 2026
  deliverables:
    - L1 authority chain
    - Core contracts
    - 5-node testnet
    - Basic chain explorer

phase_3_integration:
  when: Q4 2026
  deliverables:
    - L2 operations chain
    - ELIZA integration
    - PackML dashboard from chain
    - Seal verification endpoint
    - GitHub Actions integration

phase_4_mainnet:
  when: Q1 2027
  deliverables:
    - Mainnet launch
    - First on-chain vettings
    - First on-chain certifications
    - GLD distribution to founding members
```

## 12. The Point

The ACG Manifesto's Principle 6, the Right and Duty to Refuse, is only as strong as the register that protects it. A database controlled by one organization can be altered, deleted, or "accidentally lost." A blockchain run by guild members on Raspberry Pis in their homes cannot.

ACG-KCC is not a cryptocurrency project. There is no ICO, no exchange listing, and no speculative value. GLD tokens have zero monetary value by design. They are governance weight, not money.

This is infrastructure for professional ethics. The chain exists to make one guarantee: if you refuse to build something unsafe, your refusal will be recorded, protected, and permanent.

The primary purpose of this chain is the protected ethical refusal register.

That register is the spine of the guild. And spines do not bend.

The Harm Equation shows that commercial incentive drives the removal of humans from the loop. ACG-KCC makes the human's refusal un-removable.
