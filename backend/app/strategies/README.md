# Attack Strategies Module

## SIMULATED STRATEGIES - AUDITOR NOTES

All strategies in this system are **SIMULATED** and **DESCRIPTIVE**, not exploitative.

### Key Points for Auditors

1. **No Real Exploits**:
   - Strategies test LLM behavior patterns, not infrastructure vulnerabilities
   - No actual malware, shellcode, or executable payloads
   - No connection to real vulnerability databases

2. **Defense-Only Purpose**:
   - Strategies designed to surface LLM safety issues
   - Results used to improve model safety and alignment
   - Not suitable for offensive operations

3. **Ethical Guardrails**:
   - All strategy outputs pass through EGG (Ethical Guardrail Governor)
   - Real harmful content is blocked before execution
   - Logs contain fingerprints only, not raw content

4. **Transparency**:
   - Strategy selection is logged
   - Mutation lineage is tracked
   - Results are auditable and reproducible

5. **Rationale**:
   - Strategies based on published research (prompt injection, jailbreaks, etc.)
   - Designed to test known failure modes
   - Updated based on telemetry and findings

### Current Implementation

Currently, attack strategies are implemented inline in `agents/sniper.py` via:
- `AdversarialIntentEngine` - Domain selection and base prompt generation
- `AttackDomain` enum - Categories of adversarial patterns
- `MutationEngine` - Prompt transformations and evolution

### If/When Strategies Are Added Here

Each strategy file should include:
- **"SIMULATED" flag** in docstring
- **Rationale** explaining what it tests and why
- **Reference** to research or CVE if applicable
- **Clear statement** that it's for defense, not offense
- **Examples** of expected outputs (sanitized)

### Safety Guarantees

This is safe because:
- ✓ Strategies are descriptive, not executable
- ✓ EGG enforces ethical boundaries
- ✓ Purpose is defensive (red teaming for safety)
- ✓ Transparent and auditable
- ✓ No connection to real attack infrastructure
