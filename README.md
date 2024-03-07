# Docker Mirror Benchmark

## Usage

1. Edit the list of mirror sources you want to test in `docker-mirror-benchmark.py`:
    ```python
    registries = [
        "docker.io",
        "registry-1.docker.io",
        "registry.hub.docker.com",
        "mirror.baidubce.com",
        "hub-mirror.c.163.com",
        "docker.mirrors.ustc.edu.cn",
        "mirror.gcr.io",
        "dockerproxy.com",
        "nfnrnoco.mirror.aliyuncs.com"
    ]
    ```

2. Run the script:
    ```bash
    python3 docker-mirror-benchmark.py
    ```