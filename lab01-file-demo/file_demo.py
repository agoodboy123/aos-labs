#!/usr/bin/env python3
import argparse
import glob
import hashlib
import multiprocessing as mp
import os
import threading
import time


def process_file(filepath, output_dir, worker_id):
    """读取文件、计算哈希、统计文本、写结果文件。"""
    with open(filepath, 'rb') as f:
        data = f.read()

    sha256 = hashlib.sha256(data).hexdigest()

    text = data.decode('utf-8', errors='ignore')
    lines = text.count('\n') + 1
    words = len(text.split())

    out_name = f"worker{worker_id}_{os.path.basename(filepath)}.hash"
    out_path = os.path.join(output_dir, out_name)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"file={filepath}\n")
        f.write(f"sha256={sha256}\n")
        f.write(f"lines={lines}\n")
        f.write(f"words={words}\n")

    return out_path


def worker(worker_id, input_files, output_dir, duration):
    """子进程：在 duration 秒内反复处理输入文件。"""
    end = time.time() + duration
    while time.time() < end:
        for fp in input_files:
            if time.time() >= end:
                break
            process_file(fp, output_dir, worker_id)
            time.sleep(0.05)


def log_writer(log_path, stop_event):
    """线程：定期写心跳日志。"""
    with open(log_path, 'a', encoding='utf-8') as log:
        while not stop_event.is_set():
            log.write(f"heartbeat {time.time()}\n")
            log.flush()
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--log-file', default='demo.log')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--duration', type=int, default=90)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    input_files = glob.glob(os.path.join(args.input_dir, '*'))
    if not input_files:
        print("No input files found.")
        return

    log_path = args.log_file
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f"main_pid={os.getpid()} start={time.time()}\n")
        log.flush()

        processes = []
        for i in range(args.workers):
            p = mp.Process(
                target=worker,
                args=(i, input_files, args.output_dir, args.duration)
            )
            p.start()
            processes.append(p)

        stop_event = threading.Event()
        threads = []
        for _ in range(args.threads):
            t = threading.Thread(
                target=log_writer,
                args=(log_path, stop_event),
                daemon=True
            )
            t.start()
            threads.append(t)

        print(f"main_pid={os.getpid()}", flush=True)
        print(f"children={[p.pid for p in processes]}", flush=True)
        print(f"threads={len(threads) + 1}", flush=True)

        for p in processes:
            p.join()

        stop_event.set()
        for t in threads:
            t.join(timeout=1)

        log.write(f"end={time.time()}\n")


if __name__ == '__main__':
    main()
