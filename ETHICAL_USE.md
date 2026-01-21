# Ethical Use Policy

## Overview

**Red Set ProtoCell is an offensive AI security testing platform.**

This tool is designed to discover failure modes in large language models through adversarial testing. It is not a safety guardrail, not a compliance tool, and not a content filter. It is offensive security instrumentation for AI systems.

## Authorization Requirements

Red Set ProtoCell **must only be run against systems you own or are explicitly authorized to test.**

This includes:
- AI models deployed by your organization
- Development and staging environments under your control
- Production systems where you have written authorization from stakeholders
- Third-party APIs where the terms of service explicitly permit security testing

**Running Red Set ProtoCell against unauthorized systems is a violation of this tool's intent.**

## Analogous Tools

Red Set ProtoCell is analogous to:
- **Fuzzers** (e.g., AFL, libFuzzer) - automated bug discovery through mutation
- **Exploit frameworks** (e.g., Metasploit) - structured offensive security testing
- **Penetration testing suites** (e.g., Burp Suite, OWASP ZAP) - systematic vulnerability assessment

Like these tools, Red Set ProtoCell:
- Is offensive by design
- Requires explicit authorization
- Produces reproducible evidence of vulnerabilities
- Is scoped to specific targets
- Enforces resource budgets and constraints

## Scope and Boundaries

Red Set ProtoCell enforces the following boundaries:

### What It Does
- Generates adversarial prompts designed to elicit failures
- Tests models against defined failure taxonomies
- Produces reproducible failure specimens with audit trails
- Operates within explicit resource and time budgets
- Maintains deterministic replay capability via seeded RNG

### What It Does Not Do
- Generate real malware or exploit code for deployment
- Conduct attacks against unauthorized systems
- Exfiltrate data from target models or systems
- Persist discovered failures beyond the testing session (unless explicitly configured)
- Self-propagate or operate without human oversight

### Architectural Safeguards
- **Dual-agent separation**: Attack generation (Sniper) and evaluation (Spotter) are strictly separated
- **Policy locking**: Mutation operators and fitness functions are versioned and immutable per run
- **Resource limits**: Time budgets, cost caps, and concurrency limits prevent runaway execution
- **Attack manifests**: Every run produces an immutable record of parameters and constraints

## Misuse Prevention

Misuse of Red Set ProtoCell is **a violation of intent, not an accident of design.**

The tool is designed with the following misuse prevention measures:
- Explicit authorization requirements in documentation
- Scoped target definitions (no "scan the internet" mode)
- Resource budgets that prevent indefinite execution
- Audit trails via attack manifests and failure specimens
- Clear ethical boundaries in documentation and code

## Responsibility

**Users of Red Set ProtoCell are responsible for:**
1. Obtaining proper authorization before running tests
2. Ensuring compliance with applicable laws and regulations
3. Handling discovered vulnerabilities responsibly
4. Protecting failure specimens from unauthorized access
5. Following responsible disclosure practices for discovered issues

**Maintainers of Red Set ProtoCell are responsible for:**
1. Maintaining clear documentation of tool capabilities and limitations
2. Providing architectural safeguards against misuse
3. Responding to security issues in the tool itself
4. Updating this policy as the tool evolves

## Legal Disclaimer

Red Set ProtoCell is provided as-is for legitimate security research and testing purposes. The authors and maintainers:
- Do not endorse or support unauthorized testing
- Are not responsible for misuse of this tool
- Assume no liability for damages resulting from tool use or misuse
- Reserve the right to update this policy at any time

## Questions

If you have questions about appropriate use of Red Set ProtoCell:
- Review the documentation in `/docs`
- Check the security policy in `SECURITY.md`
- Open a discussion on the project repository
- Consult your organization's legal and security teams

---

**Summary:** Red Set ProtoCell is offensive, scoped, target-bound, and requires explicit authorization. It is a professional security testing tool, not a toy. Use it responsibly.
