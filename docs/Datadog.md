To enable datadog:

## Option-1: 
- Containerized installation [link](https://github.com/DataDog/datadog-agent/tree/main/Dockerfiles/agent)
  - ```shell
    # For Linux
    docker run -d --name datadog-agent \
           -e DD_API_KEY=xxxxxxxxxxxxxxxxxxxxxx \
           -e DD_LOGS_ENABLED=true \
           -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
           -e DD_CONTAINER_EXCLUDE_LOGS="name:datadog-agent" \
           -e DD_APM_ENABLED=true \
           -e DD_SITE=xxxxxxxxxxxxxxxxxxxxxx \
           -v /var/run/docker.sock:/var/run/docker.sock:ro \
           -v /proc/:/host/proc/:ro \
           -v /opt/datadog-agent/run:/opt/datadog-agent/run:rw \
           -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
           datadog/agent:latest
    ```
- Autodiscovery and Log Integrations
  - Dockerfile:
    - `LABEL "com.datadoghq.ad.check_names"='["autobots"]'`
    - `LABEL "com.datadoghq.ad.init_configs"='[{}]'`
    - `LABEL "com.datadoghq.ad.instances"='[{"autobots_status_url": "https://%%host%%:%%port%%/v1/hello"}]'`
    - `LABEL "com.datadoghq.ad.logs"='[{"source": "autobots", "service": "autobots"}]'`


Containerized installation on macOS
```shell
# For MacOS
docker run -d --name datadog-agent \
           --cgroupns host \
           --pid host \
           -e DD_API_KEY=xxxxxxxxxxxxxxxxxxxxxx \
           -e DD_LOGS_ENABLED=true \
           -e DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL=true \
           -e DD_LOGS_CONFIG_DOCKER_CONTAINER_USE_FILE=true \
           -e DD_CONTAINER_EXCLUDE="name:datadog-agent" \
           -e DD_SITE=xxxxxxxxxxxxxxxxxxxxxx \
           -v /var/run/docker.sock:/var/run/docker.sock:ro \
           -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
           -v /opt/datadog-agent/run:/opt/datadog-agent/run:rw \
           gcr.io/datadoghq/agent:latest
```

