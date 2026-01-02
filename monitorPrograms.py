#!/usr/bin/env python3
"""
Network Process Monitor
Monitor network traffic per process and optionally shut down high-usage programs.
Usage: python network_process_monitor.py [--interval N]
Press Ctrl+C to stop, or enter process ID to terminate.
"""

import argparse
import time
from typing import Dict, List, Optional
import psutil
import os
import sys
from datetime import datetime

def get_process_network_usage(interval: int = 1) -> Dict[int, Dict[str, float]]:
    """
    Measure network usage per process.
    
    Args:
        interval (int): Time interval in seconds. Default 1.
    
    Returns:
        Dict mapping PID to {'upload': float, 'download': float, 'name': str} in KB/s.
    """
    if interval <= 0:
        raise ValueError("interval must be greater than 0")
    
    usage = {}
    try:
        # Initial counters
        proc_io = {}
        for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
            try:
                pid = proc.info['pid']
                proc_io[pid] = proc.io_counters()
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError) as e:
                print(f"Warning: Could not access PID {pid}: {e}", file=sys.stderr)
                continue
        
        if not proc_io:
            print("Warning: No processes with accessible I/O counters.", file=sys.stderr)
            return usage
        
        time.sleep(interval)
        
        # Final counters
        for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
            pid = proc.info['pid']
            if pid in proc_io:
                try:
                    initial = proc_io[pid]
                    current = proc.io_counters()
                    sent_bytes = max(0, current.bytes_sent - initial.bytes_sent)
                    recv_bytes = max(0, current.bytes_recv - initial.bytes_recv)
                    usage[pid] = {
                        "upload": round(sent_bytes / 1024 / interval, 2),
                        "download": round(recv_bytes / 1024 / interval, 2),
                        "name": proc.info['name']
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError) as e:
                    print(f"Warning: Error updating PID {pid}: {e}", file=sys.stderr)
                    continue
    
    except Exception as e:
        print(f"Error in network usage collection: {e}", file=sys.stderr)
    
    return usage

def get_top_processes(usage: Dict[int, Dict[str, float]], limit: int = 5) -> List[Dict]:
    """Return top processes by total network usage, including zero-usage if none active."""
    if not usage:
        return [{"pid": 0, "name": "No Active Network Processes", "upload": 0, "download": 0, "total": 0}]
    return sorted(
        [{"pid": pid, "name": data["name"], "upload": data["upload"], "download": data["download"],
          "total": data["upload"] + data["download"]} for pid, data in usage.items()],
        key=lambda x: x["total"],
        reverse=True
    )[:limit]

def terminate_process(pid: int) -> bool:
    """Attempt to terminate a process by PID, avoiding system processes."""
    try:
        proc = psutil.Process(pid)
        # Avoid terminating critical system processes
        critical_processes = ['system', 'svchost.exe', 'explorer.exe', 'csrss.exe']
        if proc.name().lower() in critical_processes:
            print(f"Cannot terminate {proc.name()} (critical system process).")
            return False
        proc.terminate()
        print(f"Terminated process {proc.name()} (PID: {pid}).")
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"Failed to terminate PID {pid}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Monitor network traffic per process and shut down programs.")
    parser.add_argument(
        "--interval",
        type=int,
        default=2,  # Increased to 2s to capture more activity
        help="Time interval in seconds (default: 2)"
    )
    args = parser.parse_args()
    
    print(f"Starting network process monitor (interval: {args.interval}s). Press Ctrl+C to stop.")
    print("Enter PID to terminate a process, or leave blank to continue. Avoid system PIDs.")
    print("---" * 10)
    
    try:
        while True:
            usage = get_process_network_usage(args.interval)
            top_processes = get_top_processes(usage)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Top Network Users:")
            for i, proc in enumerate(top_processes, 1):
                print(f"  {i}. PID: {proc['pid']}, Name: {proc['name']}, "
                      f"Upload: {proc['upload']} KB/s, Download: {proc['download']} KB/s, "
                      f"Total: {proc['total']} KB/s")
            print("---" * 10)
            
            # Interactive termination
            pid_input = input("Enter PID to terminate (or press Enter to skip): ").strip()
            if pid_input:
                try:
                    pid = int(pid_input)
                    if pid in [p['pid'] for p in top_processes if p['pid'] != 0]:
                        terminate_process(pid)
                    else:
                        print(f"PID {pid} not in top processes or invalid.")
                except ValueError:
                    print("Invalid PID. Please enter a number.")
            sys.stdout.flush()
    
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()