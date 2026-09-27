#!/usr/bin/env sh
set -eu
JENKINS_SECRET=$(cat /run/secrets/agent_secret)
export JENKINS_SECRET
exec /usr/local/bin/jenkins-agent
