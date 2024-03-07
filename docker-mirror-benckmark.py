#!/usr/bin/env python3

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

registries = [
    "docker.io",
    "registry-1.docker.io",
    "registry.hub.docker.com",
    "mirror.baidubce.com",
    "hub-mirror.c.163.com",
    "docker.mirrors.ustc.edu.cn",
    "mirror.gcr.io",
    "dockerproxy.com"
]

image = "library/nginx:1.25.1-alpine"
timeout_seconds = 60  # 设置超时时间为 60 秒

def run_command(registry, timeout):
    command = ["docker", "pull", f"{registry}/{image}"]
    try:
        # 记录命令执行之前的时间
        start_time = time.time()
        # 运行命令，并设置超时时间
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True, timeout=timeout)
        # 计算执行时间
        elapsed_time = time.time() - start_time
        return registry, True, elapsed_time
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        # 计算执行时间
        elapsed_time = time.time() - start_time
        return registry, False, elapsed_time

def cleanup_image(registry, timeout):
    command = ["docker", "rmi", f"{registry}/{image}"]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Warning: 'docker rmi' command timed out for {registry}")
    except subprocess.CalledProcessError:
        # print(f"Warning: 'docker rmi' command failed for {registry}")
        pass

# 创建线程池
with ThreadPoolExecutor() as executor:
    # 提交所有测试到线程池并行执行
    future_to_registry = {executor.submit(run_command, registry, timeout_seconds): registry for registry in registries}
    for future in as_completed(future_to_registry):
        registry = future_to_registry[future]
        try:
            registry, success, elapsed_time = future.result()
            if success:
                print(f"\033[32m{registry} is good (took {elapsed_time:.2f} seconds)\033[0m")
            else:
                if elapsed_time >= timeout_seconds:
                    print(f"\033[33m{registry} test timed out after {elapsed_time:.2f} seconds\033[0m")
                else:
                    print(f"\033[31m{registry} is outdated (took {elapsed_time:.2f} seconds)\033[0m")
        except Exception as exc:
            print(f"{registry} generated an exception: {exc}")
        finally:
            # 清理镜像，也可以并行操作，但为了简单起见这里逐个执行
            cleanup_image(registry, timeout_seconds)