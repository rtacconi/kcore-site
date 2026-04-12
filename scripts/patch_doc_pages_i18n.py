#!/usr/bin/env python3
"""Add data-i18n to shared navbar and sidebar on all doc HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NAVBAR = """
        <ul class="nav-menu">
            <li><a href="../../features.html" data-i18n="nav.features">Features</a></li>
            <li><a href="../../pricing.html" data-i18n="nav.pricing">Pricing</a></li>
            <li><a href="../../docs.html" data-i18n="nav.docs">Docs</a></li>
            <li><a href="../../roadmap.html" data-i18n="nav.roadmap">Roadmap</a></li>
            <li><a href="../../blog.html" data-i18n="footer.blog">Blog</a></li>
            <li><a href="../../index.html#get-started" class="btn-primary" data-i18n="nav.getStarted">Get Started</a></li>
        </ul>
""".strip()

# docs.html uses href without ../../
NAVBAR_HUB = """
            <ul class="nav-menu">
                <li><a href="features.html" data-i18n="nav.features">Features</a></li>
                <li><a href="pricing.html" data-i18n="nav.pricing">Pricing</a></li>
                <li><a href="docs.html" data-i18n="nav.docs">Docs</a></li>
                <li><a href="roadmap.html" data-i18n="nav.roadmap">Roadmap</a></li>
                <li><a href="blog.html" data-i18n="footer.blog">Blog</a></li>
                <li><a href="index.html#get-started" class="btn-primary" data-i18n="nav.getStarted">Get Started</a></li>
            </ul>
""".strip()

SIDEBAR_USER = r"""        <aside class="docs-sidebar"><nav class="docs-nav">
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.gettingstarted">Getting started</h4><ul>
                <li><a href="installation.html" data-i18n="docs.nav.installation">Installation</a></li>
                <li><a href="first-cluster.html" data-i18n="docs.nav.firstcluster">First cluster</a></li>
                <li><a href="add-node.html" data-i18n="docs.nav.addnode">Add a node</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.virtualmachines">Virtual machines</h4><ul>
                <li><a href="vm-creation.html" data-i18n="docs.nav.vmcreation">VM creation</a></li>
                <li><a href="images.html" data-i18n="docs.nav.vmimages">VM images</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.containers">Containers</h4><ul>
                <li><a href="containers.html" data-i18n="docs.nav.containerlifecycle">Container lifecycle</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.networking">Networking</h4><ul>
                <li><a href="networks.html" data-i18n="docs.nav.networks">Networks</a></li>
                <li><a href="overlay-vxlan.html" data-i18n="docs.nav.vxlanoverlay">VXLAN overlay</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.storage">Storage</h4><ul>
                <li><a href="storage.html" data-i18n="docs.nav.storagebackends">Storage backends</a></li>
                <li><a href="storage-day2.html" data-i18n="docs.nav.day2">Day-2 operations</a></li>
                <li><a href="storage-vsan.html" data-i18n="docs.nav.vsan">vSAN (Ceph)</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.security">Security</h4><ul>
                <li><a href="security-groups.html" data-i18n="docs.nav.securitygroups">Security groups</a></li>
                <li><a href="compliance.html" data-i18n="docs.nav.compliance">Compliance</a></li>
                <li><a href="certificates.html" data-i18n-html="docs.nav.certificates">Certificates &amp; encryption</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.reference">Reference</h4><ul>
                <li><a href="kctl-reference.html" data-i18n="docs.nav.kctl">kctl CLI</a></li>
                <li><a href="yaml-manifests.html" data-i18n="docs.nav.yamlmanifests">YAML manifests</a></li>
            </ul></div>
            <div class="docs-nav-section"><h4 data-i18n="docs.nav.licensing">Licensing</h4><ul>
                <li><a href="licensing.html" data-i18n="docs.nav.editions">Editions &amp; pricing</a></li>
            </ul></div>
        </nav></aside>"""

ACTIVE_MAP = {
    "installation.html": "installation",
    "first-cluster.html": "firstcluster",
    "add-node.html": "addnode",
    "vm-creation.html": "vmcreation",
    "images.html": "vmimages",
    "containers.html": "containerlifecycle",
    "networks.html": "networks",
    "overlay-vxlan.html": "vxlanoverlay",
    "storage.html": "storagebackends",
    "storage-day2.html": "day2",
    "storage-vsan.html": "vsan",
    "security-groups.html": "securitygroups",
    "compliance.html": "compliance",
    "certificates.html": "certificates",
    "kctl-reference.html": "kctl",
    "yaml-manifests.html": "yamlmanifests",
    "licensing.html": "editions",
}


def apply_active(sidebar: str, filename: str) -> str:
    key = ACTIVE_MAP.get(filename)
    if not key:
        return sidebar
    # Remove all class="active" first
    s = re.sub(r' class="active"', "", sidebar)
    needle = f'data-i18n="docs.nav.{key}"'
    s = s.replace(f'<a href="{filename}" {needle}', f'<a href="{filename}" class="active" {needle}', 1)
    return s


def patch_user_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fn = path.name
    # Navbar: match ul.nav-menu block (user pages use ../../)
    text = re.sub(
        r"<ul class=\"nav-menu\">.*?</ul>",
        NAVBAR,
        text,
        count=1,
        flags=re.DOTALL,
    )
    # Sidebar
    sidebar = apply_active(SIDEBAR_USER, fn)
    text = re.sub(
        r'<aside class="docs-sidebar"><nav class="docs-nav">.*?</nav></aside>',
        sidebar,
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text, encoding="utf-8")


def patch_docs_html() -> None:
    path = ROOT / "docs.html"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"<ul class=\"nav-menu\">.*?</ul>",
        NAVBAR_HUB,
        text,
        count=1,
        flags=re.DOTALL,
    )
    # Hub sidebar: add data-i18n to section h4 and links + technical section
    hub_sidebar = r"""            <aside class="docs-sidebar">
                <nav class="docs-nav">
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.gettingstarted">Getting started</h4>
                        <ul>
                            <li><a href="docs/user/installation.html" data-i18n="docs.nav.installation">Installation</a></li>
                            <li><a href="docs/user/first-cluster.html" data-i18n="docs.nav.firstcluster">First cluster</a></li>
                            <li><a href="docs/user/add-node.html" data-i18n="docs.nav.addnode">Add a node</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.virtualmachines">Virtual machines</h4>
                        <ul>
                            <li><a href="docs/user/vm-creation.html" data-i18n="docs.nav.vmcreation">VM creation</a></li>
                            <li><a href="docs/user/images.html" data-i18n="docs.nav.vmimages">VM images</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.containers">Containers</h4>
                        <ul>
                            <li><a href="docs/user/containers.html" data-i18n="docs.nav.containerlifecycle">Container lifecycle</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.networking">Networking</h4>
                        <ul>
                            <li><a href="docs/user/networks.html" data-i18n="docs.nav.networks">Networks</a></li>
                            <li><a href="docs/user/overlay-vxlan.html" data-i18n="docs.nav.vxlanoverlay">VXLAN overlay</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.storage">Storage</h4>
                        <ul>
                            <li><a href="docs/user/storage.html" data-i18n="docs.nav.storagebackends">Storage backends</a></li>
                            <li><a href="docs/user/storage-day2.html" data-i18n="docs.nav.day2">Day-2 operations</a></li>
                            <li><a href="docs/user/storage-vsan.html" data-i18n="docs.nav.vsan">vSAN (Ceph)</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.security">Security</h4>
                        <ul>
                            <li><a href="docs/user/security-groups.html" data-i18n="docs.nav.securitygroups">Security groups</a></li>
                            <li><a href="docs/user/compliance.html" data-i18n="docs.nav.compliance">Compliance</a></li>
                            <li><a href="docs/user/certificates.html" data-i18n-html="docs.nav.certificates">Certificates &amp; encryption</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.reference">Reference</h4>
                        <ul>
                            <li><a href="docs/user/kctl-reference.html" data-i18n="docs.nav.kctl">kctl CLI</a></li>
                            <li><a href="docs/user/yaml-manifests.html" data-i18n="docs.nav.yamlmanifests">YAML manifests</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.nav.licensing">Licensing</h4>
                        <ul>
                            <li><a href="docs/user/licensing.html" data-i18n="docs.nav.editions">Editions &amp; pricing</a></li>
                        </ul>
                    </div>
                    <div class="docs-nav-section">
                        <h4 data-i18n="docs.hub.nav.technical">Technical docs</h4>
                        <ul>
                            <li><a href="https://github.com/rtacconi/kcore/tree/main/docs" data-i18n="docs.hub.link.architecture">Architecture &amp; internals</a></li>
                        </ul>
                    </div>
                </nav>
            </aside>"""
    text = re.sub(
        r'<aside class="docs-sidebar">\s*<nav class="docs-nav">.*?</nav>\s*</aside>',
        hub_sidebar,
        text,
        count=1,
        flags=re.DOTALL,
    )
    # Main hub title and sections — replace h1 and first p and h2s and card inner divs
    text = text.replace(
        '<h1 id="user-guides">Documentation</h1>',
        '<h1 id="user-guides" data-i18n="docs.hub.pageTitle">Documentation</h1>',
    )
    text = text.replace(
        '<p>Operator-focused guides for installing kcore, managing clusters, creating VMs and containers, configuring networking and storage, and securing your infrastructure. Technical architecture and contributor docs live in the <a href="https://github.com/rtacconi/kcore/tree/main/docs" style="color: var(--accent-primary);">kcore repository</a>.</p>',
        '<p data-i18n-html="docs.hub.lead">Operator-focused guides for installing kcore, managing clusters, creating VMs and containers, configuring networking and storage, and securing your infrastructure. Technical architecture and contributor docs live in the <a href="https://github.com/rtacconi/kcore/tree/main/docs" style="color: var(--accent-primary);">kcore repository</a>.</p>',
    )
    text = text.replace("<h2>Getting started</h2>", '<h2 data-i18n="docs.hub.h2.gettingstarted">Getting started</h2>')
    text = text.replace("<h2>Virtual machines</h2>", '<h2 data-i18n="docs.hub.h2.virtualmachines">Virtual machines</h2>')
    text = text.replace("<h2>Containers</h2>", '<h2 data-i18n="docs.hub.h2.containers">Containers</h2>')
    text = text.replace("<h2>Networking</h2>", '<h2 data-i18n="docs.hub.h2.networking">Networking</h2>')
    text = text.replace("<h2>Storage</h2>", '<h2 data-i18n="docs.hub.h2.storage">Storage</h2>')
    text = text.replace("<h2>Security</h2>", '<h2 data-i18n="docs.hub.h2.security">Security</h2>')
    text = text.replace("<h2>Reference</h2>", '<h2 data-i18n="docs.hub.h2.reference">Reference</h2>')
    # Card grids: add data-i18n to title and desc divs (first line of each card)
    card_repls = [
        ('docs.hub.card.install.title', "Installation", "docs.hub.card.install.desc", "System requirements, create cluster PKI, and connect kctl."),
        ('docs.hub.card.firstcluster.title', "First cluster", "docs.hub.card.firstcluster.desc", "Boot ISO, install to disk, approve the node, create your first VM."),
        ('docs.hub.card.addnode.title', "Add a node", "docs.hub.card.addnode.desc", "Agent nodes, HA controllers, and cross-DC expansion."),
        ('docs.hub.card.vmcreate.title', "VM creation", "docs.hub.card.vmcreate.desc", "CLI and YAML creation, images, SSH keys, cloud-init, scheduling."),
        ('docs.hub.card.images.title', "VM images", "docs.hub.card.images.desc", "Controller downloads, node upload, formats, and readiness checks."),
        ('docs.hub.card.containers.title', "Container lifecycle", "docs.hub.card.containers.desc", "Create, start, stop, and delete OCI containers alongside VMs."),
        ('docs.hub.card.networks.title', "Networks", "docs.hub.card.networks.desc", "NAT, bridge, and VXLAN types, VLAN tagging, and network CRUD."),
        ('docs.hub.card.vxlan.title', "VXLAN overlay", "docs.hub.card.vxlan.desc", "Deep dive: VNI derivation, FDB entries, peer discovery, outbound NAT."),
        ('docs.hub.card.storage.title', "Storage backends", "docs.hub.card.storage.desc", "Filesystem, LVM, and ZFS backends, day-0 configuration."),
        ('docs.hub.card.day2.title', "Day-2 operations", "docs.hub.card.day2.desc", "Add disks, apply disko layouts, management modes."),
        ('docs.hub.card.vsan.title', "vSAN (Ceph)", "docs.hub.card.vsan.desc", "Upcoming distributed shared storage using Ceph."),
        ('docs.hub.card.sg.title', "Security groups", "docs.hub.card.sg.desc", "YAML manifests, ingress rules, DNAT, VM and network attachment."),
        ('docs.hub.card.compliance.title', "Compliance", "docs.hub.card.compliance.desc", "Report categories, framework mappings, implemented and planned features."),
        ('docs.hub.card.certs.title', "Certificates &amp; encryption", "docs.hub.card.certs.desc", "mTLS, PKI hierarchy, auto-renewal, LUKS disk encryption."),
        ('docs.hub.card.kctl.title', "kctl CLI", "docs.hub.card.kctl.desc", "Complete command reference: every command, subcommand, and flag."),
        ('docs.hub.card.yaml.title', "YAML manifests", "docs.hub.card.yaml.desc", "VM and SecurityGroup manifest field reference with examples."),
        ('docs.hub.card.licensing.title', "Licensing &amp; editions", "docs.hub.card.licensing.desc", "Open-core model, Community vs Standard vs Premium."),
    ]
    for tk, tv, dk, dv in card_repls:
        text = text.replace(
            f'<div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.4rem;">{tv}</div>',
            f'<div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.4rem;" data-i18n="{tk}">{tv}</div>',
        )
        text = text.replace(
            f'<div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">{dv}</div>',
            f'<div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;" data-i18n="{dk}">{dv}</div>',
        )
    text = text.replace(
        '<p style="border-left: 3px solid var(--accent-primary); padding-left: 1rem; color: var(--text-secondary); font-size: 0.95rem;"><strong>Related:</strong>',
        '<p style="border-left: 3px solid var(--accent-primary); padding-left: 1rem; color: var(--text-secondary); font-size: 0.95rem;" data-i18n-html="docs.hub.related"><strong>Related:</strong>',
    )
    text = text.replace(
        '<p style="color: var(--text-secondary); margin-top: 2rem;">Technical architecture, networking, replication, and contributor documentation lives in the <a href="https://github.com/rtacconi/kcore/tree/main/docs" style="color: var(--accent-primary);">docs/ directory</a> of the kcore repository.</p>',
        '<p style="color: var(--text-secondary); margin-top: 2rem;" data-i18n-html="docs.hub.technical">Technical architecture, networking, replication, and contributor documentation lives in the <a href="https://github.com/rtacconi/kcore/tree/main/docs" style="color: var(--accent-primary);">docs/ directory</a> of the kcore repository.</p>',
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for p in sorted((ROOT / "docs" / "user").glob("*.html")):
        if p.name == "index.html":
            continue
        patch_user_page(p)
    patch_docs_html()
    print("Patched doc pages and docs.html")


if __name__ == "__main__":
    main()
