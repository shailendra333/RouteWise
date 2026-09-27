"""
Agent Trace Bus
Lightweight in-memory pub/sub-style store for streaming an agent's
Perceive -> Decide -> Act -> Learn lifecycle to the frontend in near
real time via polling.

Design:
- A background thread executes the agent lifecycle and calls `emit()`
  after each meaningful step.
- The frontend polls GET /api/trace/<run_id> every ~400ms and renders
  the accumulated `events` list as a live "agent thinking" console.
- Runs are kept in memory for a bounded time (TTL) and pruned lazily.
"""

import threading
import time
import uuid
from typing import Any, Dict, List, Optional

_lock = threading.Lock()
_traces: Dict[str, Dict[str, Any]] = {}

_RUN_TTL_SECONDS = 60 * 30  # keep completed runs around for 30 minutes


def start_run(agent_id: str, agent_name: str, task_label: str = '') -> str:
    """Create a new trace run and return its run_id"""
    run_id = uuid.uuid4().hex[:12]
    with _lock:
        _traces[run_id] = {
            'run_id': run_id,
            'agent_id': agent_id,
            'agent_name': agent_name,
            'task_label': task_label,
            'status': 'running',
            'events': [],
            'result': None,
            'error': None,
            'started_at': time.time(),
            'updated_at': time.time(),
        }
    _prune_old_runs()
    return run_id


def emit(run_id: str, phase: str, message: str, data: Optional[Any] = None) -> None:
    """Append a lifecycle event to a run's trace"""
    with _lock:
        run = _traces.get(run_id)
        if run is None:
            return
        run['events'].append({
            'phase': phase,
            'message': message,
            'data': data,
            'ts': time.time(),
        })
        run['updated_at'] = time.time()


def complete(run_id: str, result: Optional[Any] = None) -> None:
    """Mark a run as successfully completed with a final result payload"""
    with _lock:
        run = _traces.get(run_id)
        if run is None:
            return
        run['status'] = 'completed'
        run['result'] = result
        run['updated_at'] = time.time()


def fail(run_id: str, error: str) -> None:
    """Mark a run as failed"""
    with _lock:
        run = _traces.get(run_id)
        if run is None:
            return
        run['status'] = 'error'
        run['error'] = error
        run['updated_at'] = time.time()


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Return a snapshot of a run's current state, or None if unknown"""
    with _lock:
        run = _traces.get(run_id)
        if run is None:
            return None
        # Shallow copy is sufficient; events list contents are immutable dicts
        return {**run, 'events': list(run['events'])}


def _prune_old_runs() -> None:
    """Remove runs older than the TTL to keep memory bounded"""
    cutoff = time.time() - _RUN_TTL_SECONDS
    with _lock:
        stale = [rid for rid, run in _traces.items() if run['updated_at'] < cutoff]
        for rid in stale:
            del _traces[rid]
