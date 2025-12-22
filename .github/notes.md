# Developer notes

This document is for developer notes and SHOULD NOT be used by Copilot, AI or LLM

## Interest

- token counters - token counters -- match input (output?) prompts to tokens

  1.  HuggingFace Tokenizers (https://pypi.org/project/tokenizers/) - 4 pre-made tokenizers (Bert WordPiece and the 3 most common BPE versions)
  1.  tiktoken (https://pypi.org/project/tiktoken/) - BPE (byte pair encoding) tokeniser for OpenAI models

- give mcp ability to execute code ( https://www.anthropic.com/engineering/code-execution-with-mcp )

- [poor man's vector](https://karboosx.net/post/4eZxhBon/building-a-simple-search-engine-that-actually-works)

## Tech Debit

- otel: logs, metrics, traces (typescript, python)

  1. prometheus and grafana; elastic stack; jaeger; zipkin

- frontend e2e:
  1.  support retries
  2.  add html reporter
