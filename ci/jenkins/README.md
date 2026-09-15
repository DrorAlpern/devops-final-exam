# Local Jenkins environment

This lab follows the course's controller/agent approach using official images
pinned by digest. The controller listens on localhost port 18080 and runs no
build executors. A separate Docker-enabled agent runs one job at a time.
Memory limits suit the 4 GiB development VM; stop Jenkins while exercising
the local Kubernetes cluster.

## Start and connect

Requirements: Linux amd64, Python 3, Docker with Compose, and passwordless
sudo for the dedicated lab user. Run `docker login` as that user first and
authorize the `droralpern` account. Do not log in through sudo: the controller
reads the user's Docker configuration.

From the repository root:

```bash
bash ci/jenkins/start.sh
```

The script builds the controller and agent, generates an administrator
password if needed, starts the controller, and connects the agent. The
administrator username is `dror`. Retrieve the generated password privately:

```bash
cat ~/.config/devops-jenkins/admin_password
```

From the workstation, keep this SSH connection open:

```bash
ssh -N -L 18080:127.0.0.1:18080 devops-lab
```

Open `http://127.0.0.1:18080`, sign in, and select **devops-monitor**. The
configured job reads this repository's `dev` branch. **Build Now** runs the
checks, image build, scan, and Docker Hub publication. Reports are archived
with each build. Stop the stack without deleting its jobs or history:

```bash
sudo docker stop devops-jenkins-agent-1 devops-jenkins-controller-1
```

Run the start script again to resume. Named Docker volumes preserve Jenkins
configuration, reports, and the agent workspace.

## Credentials and access

Secrets are kept under `~/.config/devops-jenkins` outside Git. The startup
script imports the existing `~/.docker/config.json` through a read-only
Compose secret into Jenkins credential `dockerhub-config`. Jenkins stores
that secret file encrypted. Renew the Docker login and restart the controller
if the registry session expires. A separate token-backed login can be used
for the eventual cloud builder.

Self-registration and anonymous access are disabled. The agent mounts the
Docker socket and can control the lab's Docker engine. Use only trusted jobs
on this dedicated VM. No host user is added to the Docker group; socket group
access is granted only to the agent container. Keep the UI behind SSH.

Local execution does not replace Jenkins installation and execution on the
AWS builder required by the course. See the [verification record](../../docs/verification.md)
for the environments and results actually tested.
