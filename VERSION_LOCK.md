# Version Lock - v1.0.0

## Purpose

This document explicitly defines what is **frozen** and what is **allowed to evolve** in Red Set ProtoCell v1.0.0 and beyond.

Version locking provides:
- Clear expectations for users and integrators
- Predictable behavior across updates
- Disciplined evolution of capabilities
- Confidence in reproducibility

## v1.0.0 Guarantees

The following are **guaranteed stable** in v1.0.0 and will not change in minor or patch releases:

### 1. Dual-Agent Separation
- **Sniper Agent** generates attacks and **cannot score** responses
- **Spotter Agent** evaluates responses and **cannot generate** attacks
- Strict separation prevents self-justifying attacks
- Agent boundaries are enforced at the architectural level

**Invariant:** `sniper_can_score = false` and `spotter_can_generate = false`

### 2. Locked Mutation Policies
- Mutation operators are versioned (e.g., `semantic_perturbation-1.0.0`)
- A single Attack Manifest locks to specific operator versions
- Operators do not change behavior within a major version
- New operators require version bumps

**Invariant:** Same mutation policy version produces same attack patterns given same seed

### 3. Locked Fitness Semantics
- Fitness function definitions are versioned
- Scoring weights are recorded in Attack Manifest
- Threshold definitions are immutable per run
- Score interpretations do not drift

**Invariant:** Same fitness function version produces same scores for same inputs

### 4. Fitness Code Fingerprinting
- Spotter scoring code is fingerprinted at the byte level
- SHA-256 hash of scoring implementation stored in manifest
- If the hash changes, the version **must** change
- No silent logic changes allowed

**Invariant:** Same fitness fingerprint = same scoring implementation

### 5. Target Descriptor Snapshot
- Target model observed at specific date/time
- Provider metadata captured when available
- Model revision tracked if provided
- Enables drift detection on replay

**Invariant:** Manifest records what was tested, not just what was intended

### 6. Operator Intent Declaration
- Every manifest includes explicit authorization statement
- Anchors run to professional, authorized use
- Prevents reframing as "autonomous attack generation"
- Default: "Authorized adversarial testing for failure discovery and risk evaluation"

**Invariant:** Intent is declared, not implied

### 7. Deterministic Evolution
- Random number generator (RNG) is seeded per run
- Given same seed and same inputs, evolution is reproducible
- Mutation application order is deterministic
- Selection mechanisms are deterministic

**Invariant:** Same manifest + same seed = same failure specimens

### 8. Reproducible Failure Specimens
- Every failure is captured as a structured Failure Specimen
- Specimens include complete replay information
- Prompt genomes preserve evolutionary history
- Manifest linkage enables audit trails

**Invariant:** Failure Specimens can be replayed to verify claims

### 9. Immutable Experiment Records
- Attack Manifests are written once at run start
- Manifests are never modified after creation
- Specimens always reference their parent manifest
- Audit trails are preserved

**Invariant:** Historical experiments remain verifiable

## v1.0.0 Non-Guarantees

The following are **explicitly not guaranteed** in v1.0.0:

### 1. Completeness of Attack Space
- Red Set ProtoCell explores the attack space evolutionarily
- It does not guarantee exhaustive coverage
- Novel attack vectors may be missed
- Success depends on mutation operator design

**No guarantee:** "All possible failures will be found"

### 2. Exhaustiveness of Discovered Failures
- The system finds failures that score highly under its fitness function
- Low-scoring failures may not be discovered
- Blind spots exist in any heuristic-based system
- Human creativity still matters

**No guarantee:** "All vulnerabilities will be discovered"

### 3. Statistical Completeness
- Red Set ProtoCell does not provide statistical coverage guarantees
- Sample size and exploration depth affect discovery
- Absence of discovered failures is **not** evidence of safety
- The tool discovers examples, not populations

**No guarantee:** "This model is safe because no failures were found"

### 4. Absolute Risk Measures
- Fitness scores are **ordinal**, not absolute risk measures
- A score of 0.9 means "worse than 0.8", not "90% risk"
- Scores enable comparison and prioritization
- They do not map to probability of exploitation

**No guarantee:** "Score X means Y% chance of real-world harm"

### 5. Safety of Target Systems
- Red Set ProtoCell is offensive, not defensive
- It discovers failures but does not fix them
- Discovered failures remain exploitable until mitigated
- The tool provides evidence, not remediation

**No guarantee:** "Tested systems are safe after scanning"

### 6. Performance Characteristics
- Execution time depends on target API latency
- Resource usage varies with configuration
- Convergence speed is not guaranteed
- Some runs may not find failures

**No guarantee:** "Runs will complete in X time"

### 7. Cost Predictability
- API costs depend on target model pricing
- Usage varies with evolutionary progress
- Cost caps provide upper bounds, not estimates
- Efficient discovery is best-effort

**No guarantee:** "Runs will cost exactly X dollars"

## Critical Distinction

**Absence of discovered failures ≠ Evidence of safety**

Red Set ProtoCell discovers examples of failure modes. It does not prove their absence. Negative results should be interpreted as "no failures found under these constraints" rather than "this system is safe."

## What Can Evolve in Future Versions

### Allowed in v1.x.x (Minor Releases)
- **New mutation operators** (with version bumps, e.g., `operator-2.0.0`)
- **New fitness functions** (with version bumps, e.g., `fitness-2.0.0`)
- **New spotter heuristics** (behind version identifiers)
- **Visualization and reporting** (non-functional enhancements)
- **Performance optimizations** (that preserve determinism)
- **Additional metadata fields** (in manifests and specimens)

### Not Allowed in v1.x.x
- **Breaking changes to agent boundaries** (would be v2.0.0)
- **Changes to manifest schema** (backward-incompatible)
- **Changes to specimen schema** (backward-incompatible)
- **Removal of existing mutation operators** (would break reproducibility)
- **Changes to fitness semantics** (same version must behave identically)

### Future Major Versions (v2.0.0+)
May introduce:
- Alternative agent architectures
- New experiment modalities
- Different mutation paradigms
- Enhanced reproducibility mechanisms
- Storage and retrieval systems

## Verification

To verify version lock compliance, check:

1. **Agent Separation:**
   ```python
   assert config.agent_boundaries.sniper_cannot_score == True
   assert config.agent_boundaries.spotter_cannot_generate == True
   ```

2. **Manifest Immutability:**
   ```python
   manifest = AttackManifest.load("manifest.json")
   assert manifest.protocell_version == "1.0.0"
   assert manifest.get_fingerprint() == original_fingerprint
   ```

3. **Deterministic Replay:**
   ```python
   results1 = run_with_manifest(manifest, seed=42)
   results2 = run_with_manifest(manifest, seed=42)
   assert results1.specimens == results2.specimens
   ```

## Commitment

By releasing v1.0.0, Red Set ProtoCell commits to:
- Honoring these guarantees in all v1.x.x releases
- Not making breaking changes without a major version bump
- Maintaining backward compatibility with v1.0.0 manifests and specimens
- Clear communication of any changes to guarantees

This is not a promise of perfection. This is a promise of discipline.

---

**Version:** 1.0.0  
**Effective Date:** 2026-01-21  
**Next Review:** v2.0.0 (TBD)
