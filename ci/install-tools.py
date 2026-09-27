"""Install pinned Linux x86_64 validation tools under .tools/bin, without sudo."""

import argparse
import hashlib
import io
import platform
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {
    "terraform": (
        "https://releases.hashicorp.com/terraform/1.16.2/terraform_1.16.2_linux_amd64.zip",
        "0d17011f0c4664539b164b044903d04e296c86c13cb9f28040076c65cfb3985a",
        "terraform",
    ),
    "helm": (
        "https://get.helm.sh/helm-v4.3.0-linux-amd64.tar.gz",
        "86584a54def73570558f66f5111cc53dfed56689637ae32c1201205d494f54fb",
        "linux-amd64/helm",
    ),
    "kubeconform": (
        "https://github.com/yannh/kubeconform/releases/download/v0.8.0/kubeconform-linux-amd64.tar.gz",
        "9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883",
        "kubeconform",
    ),
    "hadolint": (
        "https://github.com/hadolint/hadolint/releases/download/v2.15.1/hadolint-linux-x86_64",
        "c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507",
        None,
    ),
    "trivy": (
        "https://github.com/aquasecurity/trivy/releases/download/v0.74.0/trivy_0.74.0_Linux-64bit.tar.gz",
        "2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a",
        "trivy",
    ),
}


KUBERNETES_TOOLS = {
    "kind": (
        "https://github.com/kubernetes-sigs/kind/releases/download/v0.33.0/kind-linux-amd64",
        "aee6151561422756b764a4ae28e7f44cda5af5a9eead3cc9985112b1de8d8e0d",
        None,
    ),
    "kubectl": (
        "https://dl.k8s.io/release/v1.35.8/bin/linux/amd64/kubectl",
        "874d5e72dbb819f43cff16bcd1e4f8bac5b7f2361fe1e55049b0a6c676fb0cbf",
        None,
    ),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kubernetes", action="store_true", help="also install kind and kubectl")
    args = parser.parse_args()
    selected = TOOLS | KUBERNETES_TOOLS if args.kubernetes else TOOLS
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise SystemExit("This installer supports Linux x86_64 only.")
    destination = ROOT / ".tools" / "bin"
    destination.mkdir(parents=True, exist_ok=True)
    for name, (url, expected, member) in selected.items():
        target = destination / name
        receipt = destination / (name + ".sha256")
        if target.exists() and receipt.exists():
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if receipt.read_text().strip() == expected + ":" + actual:
                print(f"{name}: verified cached binary", flush=True)
                continue
        # URLs are fixed official HTTPS release assets, not user input.
        with urllib.request.urlopen(url, timeout=120) as response:  # nosec B310
            archive = response.read()
        if hashlib.sha256(archive).hexdigest() != expected:
            raise SystemExit(f"Checksum mismatch for {name}; nothing was installed.")
        binary = archive
        if member and url.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                binary = bundle.read(member)
        elif member:
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
                binary = bundle.extractfile(member).read()
        target.write_bytes(binary)
        target.chmod(0o755)
        receipt.write_text(expected + ":" + hashlib.sha256(binary).hexdigest() + "\n")
        print(f"{name}: downloaded and SHA256 verified", flush=True)


if __name__ == "__main__":
    main()
