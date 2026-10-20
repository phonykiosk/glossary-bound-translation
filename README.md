# GlossaryBoundTranslation

AI-assisted, unaudited GenLayer prototype for a bounded bilingual excerpt signal. An integration can lock source clauses, proposed translations, terminology and critical tokens, then obtain a scope-bound receipt only when every declared clause passes independently re-evaluated consensus. This is an independent IC, not a Project extraction, certified translation service, factual truth oracle or complete-document coverage claim.

## Interface and state

Deploy only `glossary_bound_translation.py`, constructor `[]`. Deployer is the owner. The exact runner is `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.

| Method | Purpose |
|---|---|
| `register(bundle_id,spec_json) -> scope_sha256` | Owner locks two source descriptors, language tags and 1..8 clauses, with exact excerpt, token and glossary inputs. See `fixtures/demo-spec.json`. |
| `assess_clause(bundle_id,clause_id)` | Anyone evaluates a PENDING clause in an OPEN bundle once. Terminal MATCH, MISMATCH or UNCERTAIN, with source-grounded assessment and deterministic timestamp. |
| `seal(bundle_id)` | Anyone may seal only an OPEN bundle with every declared clause MATCH. Independently re-fetches both pinned sources before making SEALED. |
| `withdraw(bundle_id)` | Owner may invalidate OPEN or SEALED authority permanently, preserving assessment/sealing history. |
| `get_bundle`, `get_receipt` | Inspect scope, state, per-clause evidence and current `valid` flag. Only SEALED is valid. |

Source document is UTF-8 plain text; target is a deliberately restricted GNU PO parser. It only accepts nonempty singular, non-fuzzy `msgstr` entries associated with nonempty `msgid`. Header, English `msgid`, obsolete comments, fuzzy and plural translations cannot provide target evidence. A target clause must fit within one eligible translation entry. JSON-style PO quoted string escapes are supported; unsupported escaping/structure fails closed by excluding the entry. This is a bounded subset, not a general PO tooling replacement.

Both selected excerpts are 12..1500 characters. Every declared code token (up to eight) must occur literally in both selections; every glossary pair (up to eight) must occur on the respective sides. Numeric literals must match as a multiset. English number words zero through nine are normalized to digits; all other numeric notation must match exactly, including signs and decimals. No number conversion, locale inference, unit conversion or Unicode digit normalization is claimed. These conservative checks can reject correct translations. A deterministic invariant failure produces MISMATCH with TOKEN, NUMBER or GLOSSARY reason even if a model would approve.

Bundle ID, clause IDs and list ordering cannot reroll an identical scope: fingerprinting excludes cosmetic clause IDs and canonicalizes clauses, tokens and glossary order. Terminal semantic outcomes cannot be reassessed or overridden. A transport/invalid-model failure reverts without inventing an outcome. Changing real scope content, omitting clauses, or using another deployment can request another result; consumers must bind their expected scope hash rather than accepting any SEALED receipt.

## Consensus, security and integration

For each clause, leader and validator independently fetch both URLs, check exact SHA256, parse eligible translations and locate both declared selections. They independently enforce deterministic invariants and, if those pass, evaluate meaning, negation, qualifiers, quantities, obligations and contextual terminology. Candidate decision and reason must equal the validator's own result. Candidate quotations must occur inside the locked selected clauses, which the validator has independently located in its fetched bytes. The validator does not merely check JSON shape or follow a leader decision. Sources, clauses and glossary values are explicitly untrusted prompt data.

Seal rechecks byte evidence through consensus without repeating the already terminal semantic judgments. Fixed hashes make previous source versions explicit; it does not silently certify later changes. State uses deterministic transaction time, and the assessment context binds contract, chain, scope, clause and transaction time. No TTL or continuous monitoring is claimed for immutable pinned excerpts. Owner withdrawal is a revocation power; downstream systems must check finalized current state, expected scope and chain/contract before relying on a receipt.

URLs are restricted to public raw.githubusercontent.com paths containing an exact 40-hex commit. Responses must be HTTP 200, UTF-8, nonempty, <=64000 bytes and match the locked SHA256. Requested paths disallow queries/fragments/credentials/ports/dot segments. The pinned SDK cannot check redirect final URLs or stop downloads before receipt; transport/DNS/TLS and GitHub availability remain trusted. Independent models may share errors or follow injection despite the instruction boundary. Quotes/invariants constrain but do not prove semantic correctness. Use public non-sensitive documents; scope and selected clauses are public state. No funds or legal/medical translation suitability is represented.

## Real demonstration fixture

The two recorded snapshots are the Python 3.14 interpreter tutorial: English CPython commit `46a54e5e6978d07f3396b48bf2bcbd1bf193e44f` and official Chinese documentation repository commit `9a92529a807deeab37c0fd4db5b68a33ea227e36`. Actual unchanged bytes, source URLs, SHA256 and byte lengths are in `fixtures/` and `fixtures/sources.json`. The selected exit clause preserves `Control-D`, `Control-Z` and `quit()`, maps interpreter to 解释器, and matches English zero to Chinese 0. It proves only the selected exit paragraph, not the tutorial or language as a whole.

`fixtures/demo-spec.json` contains this public scope. Register it as `python`, assess clause `exit`, inspect MATCH, seal, then inspect the receipt. A live model is allowed to return UNCERTAIN. Local direct tests mock HTTP transport and model outputs with the real bytes; no live successful model judgment is claimed. Adversarial token/number/glossary mutations are labeled synthetic in tests and are not presented as upstream content. Fixture copyright/PSF licensing is retained in original headers, `UPSTREAM-CPYTHON-LICENSE.txt` and the upstream translated `UPSTREAM-TRANSLATED-LICENSE.po`; no Python documentation text was modified in the preserved fixtures.

## Verification

Python 3.12+, dedicated environment:

```text
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe tools/verify.py
```

Linux/macOS use `.venv/bin/python`. Official exact GenVM v0.2.12 SDK direct tests execute the deployable file. The verifier records full SDK lint/semantic validation, ABI schema, source hash and dependency versions in `evidence/verification.json`. Test-only upstream compatibility in `tests/conftest.py` repairs Windows stdin cleanup and warp metadata refresh without replacing contract algorithms or validator execution.

**The initial suite had 15 passing tests; the current complete suite has 22.** `evidence/tdd-red.log` retains 13 initial behavioral failures against the minimal contract. Subsequent logs retain the fuzzy-detection bug and SDK single-contract-per-test fixture limitation before fixes. Coverage includes independent source/model/citation rejection, msgid/fuzzy/plural exclusion, deterministic critical invariants, scope reroll prevention, terminal assessment, sealing order, seal re-fetch, owner access and withdrawal. No host-side translation or state-machine substitute is used.

The constructor is FINALIZED/SUCCESS at `0xF5C3337CcE38332b6Ff73471DE0a22087bC697ac` on Studio61999, with normal majority consensus, zero value and on-chain bytes matching tested source; see evidence/deployment.json. Full live translation assessment/sealing, model quality, GenVM HTTP and downstream integration remain unverified. No audit, production users or upstream endorsement is claimed.

References checked: [official boilerplate](https://github.com/genlayerlabs/genlayer-project-boilerplate), [official direct tests](https://github.com/genlayerlabs/genlayer-testing-suite/blob/main/docs/direct-runner.md), [exact release](https://github.com/genlayerlabs/genvm/releases/tag/v0.2.12). Original source/tests MIT; fixture licenses are separate.


## Commit locator namespace repair (2026-10-21)

The prior local source SHA256 `b4f9b496eae67707cbb9006a40cdc70152005b585c5f2983880dc8d0584a430e` is superseded by `aba6166f764bf6fe6eeadaf23b025ebb17d62c076128de903b0eceb60cba0e7c`. Literal repository `.` and `..` segments are now rejected before registration or fetching, alongside the existing path restrictions. Legitimate `.github`, `repo.name` and `_repo` names remain accepted. The previous defect concerned the declared repository/commit locator under dot-segment URL normalization; exact expected SHA256 byte checks remained effective. No arbitrary-byte bypass is claimed.

The actual public SDK API regression first produced 4 failures and 3 valid-name passes. The repaired full suite has 22 passing tests, full semantic validation and schema extraction succeed on GenVM v0.2.12, and the extracted public schema is byte-identical. See `evidence/namespace-fix.json`, `namespace-red.log` and the current `verification-*.log`. Previous counts/reviews describe their frozen historical candidates; Root independently reviewed this narrow correction and closed it after the fix; see `evidence/namespace-final-review.json`. The constructor deployment is recorded separately in evidence/deployment.json; full live source assessment remains unverified.
