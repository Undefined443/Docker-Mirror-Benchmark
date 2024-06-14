#!/usr/bin/env python3

import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 要测试的镜像源
registries = [
    "docker.io",
    "registry-1.docker.io",
    "registry.hub.docker.com",
    "mirror.baidubce.com",
    "hub-mirror.c.163.com",
    "docker.mirrors.ustc.edu.cn",
    "mirror.gcr.io",
    "dockerproxy.com",
    "docker.nju.edu.cn",
    "docker.mirrors.sjtug.sjtu.edu.cn",
    "docker.m.daocloud.io"
]

# 要测试的镜像
image = "library/nginx:1.25.1-alpine"
timeout_seconds = 60  # 设置超时时间为 60 秒


# 当信号被捕获时这个函数将会被调用
def signal_handler(sig, frame):
    for registry in registries:
        cleanup_image(registry, timeout_seconds)
    sys.exit(0)


# 告诉程序使用 signal_handler 函数来响应 SIGINT 信号（Ctrl + C）
signal.signal(signal.SIGINT, signal_handler)


# 下载一个镜像
def run_command(registry, timeout):
    command = ["docker", "pull", f"{registry}/{image}"]
    try:
        # 记录命令执行之前的时间
        start_time = time.time()
        # 运行命令，并设置超时时间
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            timeout=timeout,
        )
        # 计算执行时间
        elapsed_time = time.time() - start_time
        return registry, True, elapsed_time
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        # 计算执行时间
        elapsed_time = time.time() - start_time
        return registry, False, elapsed_time


# 删除一个镜像
def cleanup_image(registry, timeout):
    command = ["docker", "rmi", f"{registry}/{image}"]
    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"Warning: 'docker rmi' command timed out for {registry}")
    except subprocess.CalledProcessError:
        print(f"Warning: 'docker rmi' command failed for {registry}")
        pass


# 创建线程池
with ThreadPoolExecutor() as executor:
    # 提交所有测试到线程池并行执行
    future_to_registry = {
        executor.submit(run_command, registry, timeout_seconds): registry
        for registry in registries
    }
    for future in as_completed(future_to_registry):
        registry = future_to_registry[future]
        try:
            registry, success, elapsed_time = future.result()
            if success:
                print(
                    f"\033[32m{registry} is good (took {elapsed_time:.2f} seconds)\033[0m"
                )
            else:
                if elapsed_time >= timeout_seconds: # 因为超时导致失败
                    print(
                        f"\033[33m{registry} test timed out after {elapsed_time:.2f} seconds\033[0m"
                    )
                else: # 其他原因导致失败（镜像失效）
                    print(
                        f"\033[31m{registry} unable to connect (took {elapsed_time:.2f} seconds)\033[0m"
                    )
        except Exception as exc:
            print(f"{registry} generated an exception: {exc}")
        finally:
            # 清理镜像
            cleanup_image(registry, timeout_seconds)
