# kcore hypervisor — site overview for agents

kcore is a NixOS-based hypervisor: declarative VMs, gRPC API, Terraform provider, and optional MCP integration.

## Canonical entry points

- Marketing and docs hub: https://kcorehypervisor.com/
- User documentation index: https://kcorehypervisor.com/docs/user/index.html
- Product source and technical docs: https://github.com/rtacconi/kcore

## API surface

- Management APIs are gRPC (not REST on this domain). Discover specifications and protobuf in the GitHub repository.
- This marketing host does not terminate gRPC; use a deployed controller for live API access.

## Machine-readable discovery on this host

- `/.well-known/api-catalog` — RFC 9727 linkset
- `/sitemap.xml` — URL list
- `/robots.txt` — crawl and content signals
- `/llms.txt` — concise summary for LLM crawlers
