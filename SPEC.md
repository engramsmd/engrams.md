# ENGRAMS.md — specification, version 0.1 (draft)

*An open format for the fact memories an agent can mount.*

## 0. Status

Draft 0.1, 2026-08-31. Everything here is implemented by the reference
toolchain (aoa-engram) and runtimes (llama.cpp and wllama forks) and has
been exercised on public cartridges. Field names may still change before
1.0; the cartridge binary format (`engram-gguf/1`) is frozen for the
reference implementation and will only be extended, not altered.

## 1. Purpose

`AGENTS.md` tells an agent how to behave. `ENGRAMS.md` declares what an
agent can *know*: the detachable fact memories — **cartridges** — it may
mount, what questions each one answers, which exact model stack each is
bound to, and how well each has been measured to recall its own contents.

It is a text file at the root of a project (or an agent directory), readable
by humans, checkable by tools.

## 2. Terms

- **Engram** — a hash-keyed lookup memory injected into a frozen language
  model's residual stream at one decoder layer (after DeepSeek's *Conditional
  Memory via Scalable Lookup*). Keys are hashed suffix windows of the token
  stream; values are learned vectors.
- **Cartridge** — a detachable engram trained *after the fact* against a
  frozen base model: a single file that mounts in milliseconds and unmounts
  leaving the base byte-identical.
- **Canonical fact** — one training line of the form `<key> | <value>`, e.g.
  `Paris, FR | population | 2138551`. A cartridge's store is the set of its
  canonical facts; it is enumerable.
- **Query shape** — a key format the cartridge was compiled to answer, e.g.
  `{city}, {CC} | population |`. A cartridge answers only its query shapes.
- **Stack** — the exact base model (and any behaviour adapters such as LoRA)
  a cartridge was trained against. Cartridges are **stack-bound**.
- **Audit** — regenerating every canonical fact from its key with the
  deployed decoding and comparing exactly against the store.

## 3. The ENGRAMS.md file

### 3.1 Location and structure

`ENGRAMS.md` lives at the project root, next to `AGENTS.md` if present.
It is Markdown. Prose is free-form. Each cartridge is declared in a fenced
code block whose info string is `engram`, containing a YAML mapping.
Tools MUST parse only those blocks and MUST ignore everything else.

```markdown
# Memories for this project

Mount the season cartridge for match questions; the cities cartridge for
population questions. Nothing else is known offline.

## Premier League 2025-26

```engram
name: premier-league-2025-26
version: 2026.08.31
description: Every result of the 2025-26 Premier League season (380 matches).
base_model:
  id: Qwen/Qwen3-0.6B-Base
  fingerprint: c8018233286f
stack:
  - type: lora
    name: format-lora-2324
    sha256: 52d3de3b53114a11560bae3fdfb34d398b997369e5891c08f6155059ae1047ee
query_shapes:
  - format: "{home} v {away} | result |"
    example: "Newcastle v Liverpool | result |"
    value: "2-3 (Liverpool)"
facts: 380
audit:
  method: full-store greedy generation, exact match, deployment-exact prompts
  accuracy: 1.0
  correct: 380
  total: 380
files:
  - url: https://huggingface.co/lewisdog/engram-md-demo/resolve/main/cartridge-premier-league-2526.gguf
    sha256: 68f79d2a15b500811a63dcedb3c3515f670138218c18a3aa272e288fb3971a1e
    format: engram-gguf/1
security:
  profile: public
```
```

### 3.2 Fields

Required:

| field | meaning |
| --- | --- |
| `name` | stable identifier, `[a-z0-9-]+` |
| `version` | publisher-defined; a rebuild from changed source data is a new version |
| `base_model.id` | the frozen base, by public identifier |
| `base_model.fingerprint` | fingerprint of the base model configuration the cartridge was trained against (reference: first 12 hex of the SHA-256 of the model config) |
| `query_shapes[]` | the key formats this cartridge answers; `format` uses `{placeholders}`, `example` is a concrete key |
| `facts` | number of canonical facts in the store |
| `files[]` | where the cartridge bytes are: `url` or `path`, `sha256`, `format` |

Recommended:

| field | meaning |
| --- | --- |
| `description`, `publisher`, `license`, `source` | provenance of the *data* |
| `base_model.tokenizer_fingerprint` | the tokenizer is part of the key contract |
| `stack[]` | behaviour adapters merged into the training target, in order; each with `type`, `name`, `sha256` |
| `injection_layer` | decoder layer index the memory injects at |
| `keys` | `orders`, `heads`, `buckets`, `dim` — the memory's geometry |
| `audit` | see §6; without it a consumer should treat recall as unmeasured |
| `security.profile` | `public` or `pseudonymous` (§8) |
| `adapter_fingerprint` | first 16 hex of the SHA-256 over the cartridge's tensors |

### 3.3 Semantics for consumers

- An agent MAY mount a cartridge only on a stack whose fingerprints match
  `base_model` (and `stack`, if present). Mounting elsewhere is undefined and
  measured to mis-recall.
- An agent SHOULD only ask a cartridge questions in its declared query
  shapes. Recall is bound to the exact key tokens; paraphrase is not
  supported by the memory (it is the model's job).
- `audit.accuracy` is a statement about the *whole store* under the declared
  method, not a sample. A cartridge without an audit block is unverified.

## 4. Cartridge file format: `engram-gguf/1`

A cartridge is a GGUF file (general.architecture may be omitted; consumers
identify it by the `engram.*` keys).

Metadata keys:

| key | type | meaning |
| --- | --- | --- |
| `engram.hidden_size` | u32 | base model hidden size |
| `engram.heads_per_order` | u32 | hash heads per n-gram order |
| `engram.buckets` | u32 | rows per table (row 0 reserved for invalid windows) |
| `engram.head_dim` | u32 | table row width |
| `engram.injection_layer` | u32 | decoder layer whose output receives the residual |
| `engram.use_gate` | u32 | 1 if the learned gate is applied |
| `engram.residual_scale` | f32 | scalar applied to the summed contribution |
| `engram.orders` | int32[] | n-gram orders, e.g. `[6, 8, 10, 12]` |
| `engram.gate_biases` | f32[] | one per order |
| `engram.hash_seeds` | int64[] | `orders × heads`, order-major |
| `engram.ignored_tokens` | int32[] | token ids that invalidate any window containing them (special tokens) |
| `engram.base_model` | string | base model identifier |
| `engram.adapter_sha256` | string | tensor fingerprint |

Tensors (F32), one set per order `o` and head `h`:

| tensor | role |
| --- | --- |
| `engram.table.{o}.{h}` | lookup table, `buckets` rows of `head_dim` |
| `engram.hidden_key.{o}` | projects the hidden state to the candidate space |
| `engram.memory_key.{o}` | projects the gathered candidate for gating |
| `engram.value.{o}` | projects the gathered candidate into the residual stream |

Shapes follow the reference exporter (`scripts/export_engram_gguf.py` in
aoa-engram); `candidate_dim = heads_per_order × head_dim`.

### 4.1 Hashing (normative)

At token position `p`, for each order `N` and head `h`:

1. The window is the `N` tokens ending at `p`. If fewer than `N` tokens
   precede-and-include `p`, or any token in the window is in
   `ignored_tokens`, the window is **invalid** and indexes row 0.
2. Otherwise, with 64-bit wrapping arithmetic and `t_k` the token id at
   offset `k` back from `p` (`k = 0 … N-1`):

```
state = seed[o, h]
for k in 0 .. N-1:
    mixed = (t_k + 1 + k) * 2862933555777941757
    state = state XOR mixed
    state = state * (3935559000370003845 + (h + 1) * 2 + k)
    state = state XOR (state >> 29)          # arithmetic shift
index = 1 + (state mod (buckets - 1))         # non-negative remainder
```

Reference implementations agree to the bit (Python `hashing.py`; C++
`llama-engram.cpp`).

### 4.2 Application (normative)

For each order: gather the head rows at their indices and concatenate into
a candidate vector `c`; `gate = sigmoid((W_hk·h · W_mk·c) / sqrt(candidate_dim) + bias_o) × valid`;
`contribution_o = (W_v·c) × gate`. Sum over orders, multiply by
`residual_scale`, add to the hidden state at the output of `injection_layer`.
Unmounting removes the addition; base weights are never modified.

## 5. Stack binding and fingerprints

A cartridge is trained against one exact stack and must be mounted on it.
`base_model.fingerprint` and `base_model.tokenizer_fingerprint` identify the
frozen base; `stack[]` lists behaviour adapters merged into the training
target. Runtimes SHOULD refuse to mount on a mismatch. Measured: a cartridge
built on a bare base drops from 100% to 71% recall under a format LoRA it
was not trained with.

## 6. Audits

`audit.method` MUST name the decoding used. The reference method is
*full-store greedy generation, exact match, deployment-exact prompts*:

- every canonical fact's key is prompted exactly as a consumer would send it
  (the same token sequence, including whether a trailing space is present);
- the value is generated greedily and compared exactly to the stored value;
- `accuracy = correct / total` over the **whole** store.

Publishers SHOULD make the miss list available (e.g. alongside the key list
for public cartridges) so consumers can flag stored-but-mis-recalled keys.
Candidate-scoring accuracies (value tokens in context) are not audits under
this specification and MUST be labelled as such if reported.

## 7. Provenance signal (optional runtime capability)

A runtime MAY expose the per-token norm of the injected residual (the
"memory signal"). It separates a silent memory (out-of-domain key) from an
active one, but cannot by itself distinguish a stored fact from a blend of
look-alike keys; consumers SHOULD combine it with an exact membership check
against the published key list where available.

## 8. Security profiles

`security.profile: public` — the facts are public. The key list and miss
list may be published. **A cartridge file is a compiled extract of its
facts**: with the hash seeds in the file, an attacker who can guess keys can
reconstruct values offline (measured: 42% of sampled facts recovered exactly
from a public cities cartridge with no model loaded). Publish only what may
be public.

`security.profile: pseudonymous` (draft) — for protected data. Keys (and
optionally values) are keyed-hash tags (`HMAC(secret, normalised key)`) so
that an attacker without the secret cannot form a candidate window; the
secret is supplied to the runtime at mount time from a secret store. Key
lists, example keys and schema metadata MUST NOT be shipped with the file.
A future revision defines `engram.seeds_external` for seeds held outside the
file.

## 9. Registry index

A registry is a JSON document `{"version": 1, "bases": [...], "cartridges":
[...]}` whose `cartridges` entries carry the same fields as an `engram`
block plus `publisher` and `published`. `bases` lists the frozen base models
(`id`, `fingerprint`, optional `files`). Consumers select cartridges by
`base_model.fingerprint`. The reference registry lives in this repository
under `registry/index.json`; entries are added by pull request and validated
in CI.

## 10. Conformance

A **conforming ENGRAMS.md** parses under `schema/engrams.schema.json` for
every `engram` block. A **conforming cartridge** is an `engram-gguf/1` file
whose hashing and application match §4 (the reference parity test:
identical greedy generations across the Python and llama.cpp
implementations). A **conforming runtime** refuses stack mismatches, applies
§4.2, and leaves the base byte-identical after unmount.

## 11. References

- DeepSeek, *Conditional Memory via Scalable Lookup: A New Axis of Sparsity
  for Large Language Models* — arXiv:2601.07372.
- Reference toolchain and results: aoa-engram (`docs/audit-and-repair.md`).
- Runtimes: llama.cpp fork (`engram` branch) and wllama fork.
- Live demo: https://engram.md
