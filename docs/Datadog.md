To enable datadog:

## Option-1: 
- Containerized installation [link](https://github.com/DataDog/datadog-agent/tree/main/Dockerfiles/agent)
  - `docker run -d --name datadog-agent \
           -e DD_API_KEY=xxxxxxxxxxxxxxxxxxxxxx \
           -e DD_LOGS_ENABLED=true \
           -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
           -e DD_CONTAINER_EXCLUDE_LOGS="name:datadog-agent" \
           -e DD_APM_ENABLED=true \
           -v /var/run/docker.sock:/var/run/docker.sock:ro \
           -v /proc/:/host/proc/:ro \
           -v /opt/datadog-agent/run:/opt/datadog-agent/run:rw \
           -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
           datadog/agent:latest`
- Autodiscovery and Log Integrations
  - Dockerfile:
    - `LABEL "com.datadoghq.ad.check_names"='["autobots"]'`
    - `LABEL "com.datadoghq.ad.init_configs"='[{}]'`
    - `LABEL "com.datadoghq.ad.instances"='[{"autobots_status_url": "https://%%host%%:%%port%%/v1/hello"}]'`
    - `LABEL "com.datadoghq.ad.logs"='[{"source": "autobots", "service": "autobots"}]'`
