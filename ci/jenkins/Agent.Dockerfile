FROM docker:cli@sha256:eccaacfeed644c7de222ff047483568cb988dde95476fbaaf10ea2d04921bb66 AS docker_cli
FROM jenkins/inbound-agent:latest-jdk21@sha256:a2ee24c1dbd2080a9f03bb668f63a2c8d23c7b6e5bf20fe0033d4d28f4410048
USER 0:0
# Distro tools receive current security updates when this lab image is rebuilt.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv shellcheck \
    && rm -rf /var/lib/apt/lists/*
COPY --from=docker_cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker_cli /usr/local/libexec/docker/cli-plugins/docker-buildx /usr/local/libexec/docker/cli-plugins/docker-buildx
COPY --chmod=0755 agent-entrypoint.sh /usr/local/bin/course-agent
USER 1000:1000
ENTRYPOINT ["/usr/local/bin/course-agent"]
