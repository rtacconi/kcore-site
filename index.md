---
title: kcore hypervisor — declarative virtualization on NixOS
canonical: https://kcorehypervisor.com/
---

# kcore hypervisor

Declarative virtualization for edge and datacenters. kcore runs on **NixOS**: VMs are defined in **Terraform** or **YAML**, applied through a **gRPC** API and **kctl**, with **atomic upgrades and rollback**.

## Start here

- [Documentation hub](https://kcorehypervisor.com/docs.html)
- [User guides](https://kcorehypervisor.com/docs/user/index.html)
- [Features](https://kcorehypervisor.com/features.html)
- [Pricing](https://kcorehypervisor.com/pricing.html)
- [Roadmap](https://kcorehypervisor.com/roadmap.html)
- [Blog](https://kcorehypervisor.com/blog.html)

## What you get (summary)

- **Atomic updates and rollback** — NixOS generations; immutable host baseline.
- **Declarative infrastructure** — commit infra, review in PRs, apply like other config.
- **gRPC API** — same interface for CLI, Terraform provider, and automation.
- **Terraform provider** — plan and apply VMs with the rest of your stack.
- **MCP** — an MCP server ships **with the product** for AI agents; it is not served as a public endpoint on this marketing host.

## First cluster demo

The HTML homepage embeds an asciinema of install, node approval, SSH key, Debian 12 VM, and `describe` / SSH. Full write-up: [First node to Debian 12 VM](https://kcorehypervisor.com/blog/first-node-debian12-quickstart.html).

## Source and APIs

- Product repo: [github.com/rtacconi/kcore](https://github.com/rtacconi/kcore)
- Management plane APIs are **gRPC** to **your** controller, not REST on `kcorehypervisor.com`. See the repository for `.proto` files and design documentation.

## Machine-readable discovery

- [Sitemap](https://kcorehypervisor.com/sitemap.xml)
- [API catalog (RFC 9727)](https://kcorehypervisor.com/.well-known/api-catalog)
- [Agent skills index](https://kcorehypervisor.com/.well-known/agent-skills/index.json)
- [MCP server card (distribution note)](https://kcorehypervisor.com/.well-known/mcp/server-card.json)
- [llms.txt](https://kcorehypervisor.com/llms.txt)

## Company

kcore is developed by **Tacconi Consulting Ltd** ([about](https://kcorehypervisor.com/about.html)).
