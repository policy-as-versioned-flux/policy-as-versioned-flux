# Minimal offline smart-HTTP git server for the touring demo.
# Debian's git ships git-http-backend (Alpine does not); lighttpd runs it as CGI.
# Only build-time network (apt); zero network at run — the image is kind-loaded.
FROM debian:stable-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends git lighttpd ca-certificates \
 && rm -rf /var/lib/apt/lists/*
# The seeded bare repos are prepared by scripts/up.sh into this build context.
# GIT_HTTP_EXPORT_ALL (lighttpd.conf) serves any *.git dropped under /srv/git,
# so tuppence's own source and its pinned nist dependency share one server.
COPY tuppence.git /srv/git/tuppence.git
COPY nist.git /srv/git/nist.git
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf
# safe.directory '*' so git-http-backend serves a root-owned repo as the non-root
# service user (dubious-ownership guard would otherwise 500).
RUN useradd -u 10001 git && git config --system --add safe.directory '*'
USER 10001
EXPOSE 8080
ENTRYPOINT ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
