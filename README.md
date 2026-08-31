# engrams.md

**ENGRAMS.md** is an open format for the fact memories an agent can mount.

`AGENTS.md` tells an agent how to behave. `ENGRAMS.md` declares what it can
*know*: the detachable fact memories — **cartridges** — it may mount, what
questions each answers, which exact model stack each is bound to, and how
well each has been measured to recall its own contents.

- **Specification** — [`SPEC.md`](SPEC.md) (v0.1 draft): the file format,
  the `engram-gguf/1` cartridge format with its normative hash function,
  stack binding, audits, provenance, security profiles, registry index.
- **Schema + validator** — [`schema/engrams.schema.json`](schema/engrams.schema.json),
  [`tools/validate.py`](tools/validate.py).
- **Example** — [`examples/ENGRAMS.md`](examples/ENGRAMS.md).
- **Registry** — [`registry/index.json`](registry/index.json): public
  cartridges with base-model fingerprints, audits and checksums. Add yours by
  pull request; CI validates the entry.
- **Site** — https://engrams.md (this repository, static).
- **Live demo** — https://engram.md: mount and unmount real cartridges in a
  browser tab, including a chat agent that writes the memory's key itself.
- **Reference toolchain** — [aoa-engram](https://github.com/AgentOrientedArchitecture/aoa-engram)
  (compile → train → audit → repair → stamp → export), runtimes:
  [llama.cpp fork](https://github.com/trunksio/llama.cpp/tree/engram),
  [wllama fork](https://github.com/trunksio/wllama/tree/engram).

## Adopt it in three steps

1. Compile your facts into canonical lines (`<key> | <value>`), train a
   cartridge against your frozen base, audit it whole, repair, stamp.
2. Write `ENGRAMS.md` at your project root declaring the cartridge, its
   query shapes, its stack fingerprints and its audit.
3. Have your agent read `ENGRAMS.md`, mount by fingerprint, and ask only in
   the declared query shapes.

## Contributing

Issues and pull requests welcome — spec clarifications, validator fixes,
registry entries (public data only; see §8 of the spec). Contact:
hello@engram.md.

MIT licensed.
