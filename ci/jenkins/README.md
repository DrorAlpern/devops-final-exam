# Local Jenkins

The controller runs without build executors. A separate Docker agent runs
one job at a time. The UI is bound to localhost port 18080.

## Start

Requirements: Linux amd64, Python 3, Docker with Compose, and sudo access.
Run `docker login` as the normal lab user first. From the repository root:

```bash
bash ci/jenkins/start.sh
```

The script builds the containers, creates a local administrator password if
needed, starts the controller, and connects the agent. The username is `dror`.
Read the password privately from `~/.config/devops-jenkins/admin_password`.
To connect from another computer:

```bash
ssh -N -L 18080:127.0.0.1:18080 user@linux-host
```

Open `http://127.0.0.1:18080`, sign in, and run **devops-monitor**. The job reads
`dev` and executes the root Jenkinsfile. Reports are archived with each build.

## Registry access and stopping

Startup imports the user's existing Docker login as Jenkins credential
`dockerhub-config`. Credentials and generated passwords stay outside Git.
The agent mounts the Docker socket, so use this stack only for trusted jobs.

Stop the containers while testing Kubernetes on a small host:

```bash
sudo docker stop devops-jenkins-agent-1 devops-jenkins-controller-1
```

Named volumes keep jobs and build history. Run the start script again to resume.
This environment was tested on the Linux VM, not on an AWS builder.
