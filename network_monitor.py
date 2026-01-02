#!/usr/bin/env python3
"""
Network Traffic Monitor
A continuous monitoring tool to measure network upload and download speeds.
Usage: python network_monitor.py [--interval N]
Press Ctrl+C to stop.
"""

import argparse
import time
from typing import Dict
import psutil
import sys
from datetime import datetime

def get_network_usage(interval: int = 1) -> Dict[str, float]:
    """
    Measure network upload and download speeds.
    
    Args:
        interval (int): Time interval in seconds. Default 1.
    
    Returns:
        Dict with 'upload' and 'download' speeds in KB/s.
    
    Raises:
        ValueError: If interval <= 0.
    """
    if interval <= 0:
        raise ValueError("interval must be greater than 0")
    
    try:
        # Get initial counters
        start = psutil.net_io_counters()
        
        # Wait for the interval
        time.sleep(interval)
        
        # Get final counters
        end = psutil.net_io_counters()
        
        # Calculate differences
        sent_bytes = end.bytes_sent - start.bytes_sent
        recv_bytes = end.bytes_recv - start.bytes_recv
        
        # Convert to KB/s
        upload_kbps = sent_bytes / 1024 / interval
        download_kbps = recv_bytes / 1024 / interval
        
        return {
            "upload": round(upload_kbps, 2),
            "download": round(download_kbps, 2)
        }
    
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve network stats: {e}")

def main():
    parser = argparse.ArgumentParser(description="Monitor network upload/download usage continuously.")
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Time interval in seconds (default: 1)"
    )
    args = parser.parse_args()
    
    print(f"Starting network monitor (interval: {args.interval}s). Press Ctrl+C to stop.")
    print("---" * 10)  # Separator for readability
    
    try:
        while True:
            usage = get_network_usage(args.interval)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Network Usage:")
            print(f"  Upload: {usage['upload']} KB/s")
            print(f"  Download: {usage['download']} KB/s")
            print(f"  Overall: {{'upload': {usage['upload']} KB/s, 'download': {usage['download']} KB/s}}")
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