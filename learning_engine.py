"""
Learning Engine for Sovereign Guard
Analyzes observed processes during LEARN mode and builds personalized whitelist
"""

import os
import json
from datetime import datetime, timedelta
from collections import Counter

LEARNING_LOG = os.path.join(os.path.dirname(__file__), '.learning_log.json')
LEARNING_SUMMARY = os.path.join(os.path.dirname(__file__), '.learning_summary.json')

def log_process(name, exe_path, cmdline):
    """Log a process observation during LEARN mode"""
    try:
        # Load existing log
        if os.path.exists(LEARNING_LOG):
            with open(LEARNING_LOG, 'r') as f:
                log = json.load(f)
        else:
            log = {"observations": [], "start_date": datetime.now().isoformat()}
        
        # Add observation
        log["observations"].append({
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "exe_path": exe_path,
            "cmdline": cmdline
        })
        
        # Write back
        with open(LEARNING_LOG, 'w') as f:
            json.dump(log, f, indent=2)
            
    except Exception as e:
        print(f"Error logging process: {e}")

def analyze_learnings():
    """
    Analyze learning log and generate whitelist recommendations
    Returns: dict with top processes and auto-whitelist suggestions
    """
    if not os.path.exists(LEARNING_LOG):
        return {
            "status": "no_data",
            "days_elapsed": 0,
            "total_observations": 0,
            "top_processes": [],
            "auto_whitelist": []
        }
    
    try:
        with open(LEARNING_LOG, 'r') as f:
            log = json.load(f)
        
        start_date = datetime.fromisoformat(log.get("start_date", datetime.now().isoformat()))
        days_elapsed = (datetime.now() - start_date).days
        
        # Count process occurrences
        process_counter = Counter()
        for obs in log["observations"]:
            process_counter[obs["name"]] += 1
        
        # Get top processes
        top_processes = [
            {"name": name, "count": count}
            for name, count in process_counter.most_common(20)
        ]
        
        # Auto-whitelist: processes run > 10 times
        auto_whitelist = [
            name for name, count in process_counter.items()
            if count > 10
        ]
        
        summary = {
            "status": "learning",
            "days_elapsed": days_elapsed,
            "total_observations": len(log["observations"]),
            "unique_processes": len(process_counter),
            "top_processes": top_processes,
            "auto_whitelist": auto_whitelist
        }
        
        # Save summary
        with open(LEARNING_SUMMARY, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
        
    except Exception as e:
        print(f"Error analyzing learnings: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

def get_protection_mode():
    """
    Determine current protection mode based on elapsed time
    Returns: 'learn' | 'warn' | 'protect'
    """
    mode = os.getenv('PROTECTION_MODE', 'learn')
    
    # If manually set, respect it
    if mode in ['warn', 'protect']:
        return mode
    
    # Auto-transition based on time
    if not os.path.exists(LEARNING_LOG):
        return 'learn'
    
    try:
        with open(LEARNING_LOG, 'r') as f:
            log = json.load(f)
        
        start_date = datetime.fromisoformat(log.get("start_date", datetime.now().isoformat()))
        days_elapsed = (datetime.now() - start_date).days
        
        if days_elapsed < 7:
            return 'learn'
        elif days_elapsed < 14:
            return 'warn'
        else:
            return 'protect'
            
    except:
        return 'learn'

def apply_learned_whitelist():
    """
    Apply auto-whitelist to sovereign_core.py
    Called when transitioning from LEARN to WARN mode
    """
    summary = analyze_learnings()
    
    if not summary.get('auto_whitelist'):
        return {"success": False, "message": "No processes to whitelist"}
    
    try:
        core_path = os.path.join(os.path.dirname(__file__), 'sovereign_core.py')
        
        with open(core_path, 'r') as f:
            lines = f.readlines()
        
        # Find SAFE_LIST_PROCESSES closing bracket
        insert_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('SAFE_LIST_PROCESSES = ['):
                for j in range(i, len(lines)):
                    if ']' in lines[j]:
                        insert_idx = j
                        break
                break
        
        if insert_idx != -1:
            # Insert learned processes
            new_processes = summary['auto_whitelist']
            new_line = f"    # Learned from user behavior\n"
            for proc in new_processes:
                new_line += f"    '{proc.lower()}',\n"
            
            lines.insert(insert_idx, new_line)
            
            with open(core_path, 'w') as f:
                f.writelines(lines)
            
            return {
                "success": True,
                "message": f"Added {len(new_processes)} learned processes to whitelist",
                "processes": new_processes
            }
        else:
            return {"success": False, "message": "Could not find SAFE_LIST in core"}
            
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
