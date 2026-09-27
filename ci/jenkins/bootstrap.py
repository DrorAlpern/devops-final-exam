"""Connect the local Jenkins agent without printing its authentication secret."""

import base64
import os
import time
import urllib.error
import urllib.request

# XML comes only from our authenticated, fixed local Jenkins endpoint.
import xml.etree.ElementTree as ET  # nosec B405
from pathlib import Path

BASE = "http://127.0.0.1:18080"


def main():
    folder = Path(os.environ["JENKINS_SECRET_DIR"])
    password = (folder / "admin_password").read_text().strip()
    authorization = base64.b64encode(("dror:" + password).encode()).decode()
    request = urllib.request.Request(
        BASE + "/computer/docker-agent/jenkins-agent.jnlp",
        headers={"Authorization": "Basic " + authorization},
    )
    for attempt in range(90):
        try:
            # Only the fixed local Jenkins endpoint receives these credentials.
            with urllib.request.urlopen(request, timeout=5) as response:  # nosec B310
                root = ET.fromstring(response.read())  # nosec B314
            arguments = [item.text for item in root.iter("argument")]
            if not arguments or not arguments[0]:
                raise RuntimeError("Jenkins returned no agent credential.")
            (folder / "agent_secret").write_text(arguments[0])
            (folder / "agent_secret").chmod(0o600)
            print("Agent connection credential saved outside the repository.")
            return
        except (urllib.error.URLError, ConnectionResetError):
            if attempt == 89:
                raise SystemExit("Jenkins did not become ready; inspect its startup log.")
            time.sleep(2)


if __name__ == "__main__":
    main()
