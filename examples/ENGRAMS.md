# Memories for this project

Mount the season cartridge for match questions and the cities cartridge for
population questions. Each answers only the query shapes declared below; the
model is expected to write those keys itself. Nothing else is known offline.

## Premier League 2025-26

```engram
name: premier-league-2025-26
version: 2026.08.31
description: Every result of the 2025-26 Premier League season (380 matches).
base_model:
  id: Qwen/Qwen3-0.6B-Base
  fingerprint: c8018233286f
  tokenizer_fingerprint: 41e00eccf531
stack:
- type: lora
  name: format-lora-2324
  sha256: 52d3de3b53114a11560bae3fdfb34d398b997369e5891c08f6155059ae1047ee
query_shapes:
- format: '{home} v {away} | result |'
  example: Newcastle v Liverpool | result |
  value: 2-3 (Liverpool)
facts: 380
audit:
  method: full-store greedy generation, exact match, deployment-exact prompts
  accuracy: 1.0
  correct: 380
  total: 380
  misses: https://huggingface.co/lewisdog/engram-md-demo/resolve/main/stored-keys.json
files:
- url: https://huggingface.co/lewisdog/engram-md-demo/resolve/main/cartridge-premier-league-2526.gguf
  sha256: 68f79d2a15b500811a63dcedb3c3515f670138218c18a3aa272e288fb3971a1e
  bytes: 10553248
  format: engram-gguf/1
security:
  profile: public
```

## GeoNames cities (16,000)

```engram
name: geonames-cities-16k
version: 2026.08.31
description: Populations of the world's 16,000 largest cities.
base_model:
  id: Qwen/Qwen3-0.6B-Base
  fingerprint: c8018233286f
  tokenizer_fingerprint: 41e00eccf531
query_shapes:
- format: '{city}, {CC} | population |'
  example: Paris, FR | population |
  value: '2138551'
facts: 16000
audit:
  method: full-store greedy generation, exact match, deployment-exact prompts
  accuracy: 0.99494
  correct: 15919
  total: 16000
  misses: https://huggingface.co/lewisdog/engram-md-demo/resolve/main/stored-keys.json
files:
- url: https://huggingface.co/lewisdog/engram-md-demo/resolve/main/cartridge-cities-16k.gguf
  sha256: 4d1ba05592ee85ea55d2f8cbe4d45e86feee9cb5210e0643d6afc2cb3a1d9c36
  bytes: 270600096
  format: engram-gguf/1
security:
  profile: public
```
