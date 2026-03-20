# Customer Installation (Automator API)

This guide documents the customer installation flow using the node Automator API.

## Scope

- Target node booted from kcore ISO/iPXE
- Discovery API available on `:9091`
- Remote OS install triggered by `kctl`

## Prerequisites

- Latest `kctl` binary (from Releases or local build)
- Network reachability to the target node
- Node in pre-install discovery mode

If macOS blocks the binary after download:

```bash
xattr -d com.apple.quarantine ./kctl
chmod +x ./kctl
```

## 1) Discover disks and NICs

```bash
./kctl --insecure node disks --node 192.168.40.135:9091
./kctl --insecure node nics --node 192.168.40.135:9091
```

## 2) Example installation manifest

```yaml
apiVersion: kcore.io/v1alpha1
kind: NodeInstall
metadata:
  name: install-192-168-40-135
spec:
  node: 192.168.40.135:9091
  osDisk: /dev/sda
  dataDisks:
    - /dev/nvme0n1
  joinController: 192.168.40.135
  insecure: true
```

## 3) Install command

```bash
./kctl --insecure node install --node 192.168.40.135:9091 --os-disk /dev/sda --data-disk /dev/nvme0n1 --join-controller 192.168.40.135
```

Expected output:

```text
install-to-disk launched in background (forced wipe + reboot enabled)
```

## 4) Validate after reboot

```bash
./kctl --insecure node disks --node 192.168.40.135:9091
./kctl --insecure node nics --node 192.168.40.135:9091
```

## Notes

- Discovery mode uses `--insecure` before certificates exist.
- After certificate provisioning, use mTLS-authenticated APIs for production operations.
