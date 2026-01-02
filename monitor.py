#!/usr/bin/env python3
"""
Resource Monitor
A continuous monitoring tool to track CPU, memory, disk, and network usage on your PC.
Usage: python resource_monitor.py [--interval N]
Press Ctrl+C to stop.
"""

import argparse
import time
from typing import Dict
import psutil
import sys
from datetime import datetime

def get_system_resources(interval: int = 1) -> Dict[str, Dict]:
    """
    Measure system resources including CPU, memory, disk, and network usage.
    
    Args:
        interval (int): Time interval in seconds. Default 1.
    
    Returns:
        Dict with nested metrics for CPU, memory, disk, and network in KB/s.
    
    Raises:
        ValueError: If interval <= 0.
    """
    if interval <= 0:
        raise ValueError("interval must be greater than 0")
    
    try:
        # CPU Usage
        cpu_usage = psutil.cpu_percent(interval=interval)
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total / 1024 / 1024,  # MB
            "available": memory.available / 1024 / 1024,  # MB
            "percent": memory.percent
        }
        
        # Disk Usage (root filesystem)
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total": disk.total / 1024 / 1024 / 1024,  # GB
            "used": disk.used / 1024 / 1024 / 1024,  # GB
            "free": disk.free / 1024 / 1024 / 1024,  # GB
            "percent": disk.percent
        }
        
        # Network Usage
        start = psutil.net_io_counters()
        time.sleep(interval)  # Align with CPU interval
        end = psutil.net_io_counters()
        sent_bytes = end.bytes_sent - start.bytes_sent
        recv_bytes = end.bytes_recv - start.bytes_recv
        network_usage = {
            "upload": round(sent_bytes / 1024 / interval, 2),  # KB/s
            "download": round(recv_bytes / 1024 / interval, 2)  # KB/s
        }
        
        return {
            "cpu": {"usage": cpu_usage},
            "memory": memory_usage,
            "disk": disk_usage,
            "network": network_usage
        }
    
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve system stats: {e}")

def main():
    parser = argparse.ArgumentParser(description="Monitor system resources continuously.")
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Time interval in seconds (default: 1)"
    )
    args = parser.parse_args()
    
    print(f"Starting resource monitor (interval: {args.interval}s). Press Ctrl+C to stop.")
    print("---" * 10)  # Separator for readability
    
    try:
        while True:
            resources = get_system_resources(args.interval)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Resource Usage:")
            print(f"  CPU: {resources['cpu']['usage']}%")
            print(f"  Memory: {resources['memory']['percent']}% used "
                  f"({resources['memory']['available']:.1f} MB available of {resources['memory']['total']:.1f} MB)")
            print(f"  Disk: {resources['disk']['percent']}% used "
                  f"({resources['disk']['used']:.1f} GB used of {resources['disk']['total']:.1f} GB)")
            print(f"  Network: Upload: {resources['network']['upload']} KB/s, "
                  f"Download: {resources['network']['download']} KB/s")
            print("---" * 10)  # Separator between readings
            sys.stdout.flush()  # Ensure output is displayed immediately
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()