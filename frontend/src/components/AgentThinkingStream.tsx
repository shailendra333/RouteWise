import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Terminal, Eye, Brain, Zap, Sparkles, MessageSquare, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import API_BASE_URL from '../config/api';

export interface TraceEvent {
  phase: string;
  message: string;
  data?: string | null;
  ts: number;
}

export interface TraceRun {
  run_id: string;
  agent_id: string;
  agent_name: string;
  task_label: string;
  status: 'running' | 'completed' | 'error';
  events: TraceEvent[];
  result: any;
  error?: string | null;
}

interface AgentThinkingStreamProps {
  /** The run_id returned when starting a traced agent execution */
  runId: string | null;
  /** Optional accent theme: 'blue' for traditional agents, 'purple' for GenAI */
  theme?: 'blue' | 'purple';
  /** Called once when the run reaches a terminal state (completed/error) */
  onComplete?: (run: TraceRun) => void;
  /** Poll interval in ms (default 450ms) */
  pollIntervalMs?: number;
}

const PHASE_ICONS: Record<string, React.ReactNode> = {
  perceive: <Eye className="h-3.5 w-3.5" />,
  decide: <Brain className="h-3.5 w-3.5" />,
  act: <Zap className="h-3.5 w-3.5" />,
  learn: <Sparkles className="h-3.5 w-3.5" />,
  explain: <MessageSquare className="h-3.5 w-3.5" />,
};

const PHASE_LABELS: Record<string, string> = {
  perceive: 'PERCEIVE',
  decide: 'DECIDE',
  act: 'ACT',
  learn: 'LEARN',
  explain: 'EXPLAIN',
};

const PHASE_COLORS: Record<string, string> = {
  perceive: 'text-sky-400',
  decide: 'text-amber-400',
  act: 'text-emerald-400',
  learn: 'text-fuchsia-400',
  explain: 'text-violet-400',
};

/**
 * Live "Agent Thinking" console.
 * Polls /api/trace/<run_id> and renders each Perceive/Decide/Act/Learn
 * lifecycle event as it happens, terminal-style, with auto-scroll.
 */
const AgentThinkingStream: React.FC<AgentThinkingStreamProps> = ({
  runId,
  theme = 'blue',
  onComplete,
  pollIntervalMs = 450,
}) => {
  const [run, setRun] = useState<TraceRun | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const completedRef = useRef(false);

  useEffect(() => {
    if (!runId) {
      setRun(null);
      return;
    }

    completedRef.current = false;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const poll = async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/trace/${runId}`);
        if (cancelled) return;

        if (res.data?.success) {
          const data: TraceRun = res.data;
          setRun(data);

          if (data.status !== 'running') {
            if (!completedRef.current) {
              completedRef.current = true;
              onComplete?.(data);
            }
            return; // stop polling
          }
        }
      } catch (err) {
        // Swallow transient errors (run may not be registered yet); keep polling briefly
      }

      if (!cancelled) {
        timer = setTimeout(poll, pollIntervalMs);
      }
    };

    poll();

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [run?.events?.length]);

  if (!runId) return null;

  const accent = theme === 'purple' ? 'border-purple-500/40' : 'border-blue-500/40';
  const headerAccent = theme === 'purple' ? 'text-purple-300' : 'text-blue-300';

  return (
    <div className={`bg-gray-950 rounded-lg border ${accent} shadow-inner overflow-hidden`}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800 bg-gray-900/60">
        <div className={`flex items-center gap-2 text-sm font-mono ${headerAccent}`}>
          <Terminal className="h-4 w-4" />
          <span>{run?.agent_name || 'Agent'} — live reasoning</span>
        </div>
        <div className="flex items-center gap-1 text-xs font-mono">
          {!run || run.status === 'running' ? (
            <>
              <Loader2 className="h-3.5 w-3.5 text-yellow-400 animate-spin" />
              <span className="text-yellow-400">running</span>
            </>
          ) : run.status === 'completed' ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
              <span className="text-green-400">completed</span>
            </>
          ) : (
            <>
              <XCircle className="h-3.5 w-3.5 text-red-400" />
              <span className="text-red-400">error</span>
            </>
          )}
        </div>
      </div>

      <div ref={scrollRef} className="p-4 max-h-72 overflow-y-auto font-mono text-xs space-y-2">
        {!run || run.events.length === 0 ? (
          <p className="text-gray-500 italic">Waiting for agent to start…</p>
        ) : (
          run.events.map((ev, idx) => (
            <div key={idx} className="animate-[fadeIn_0.25s_ease-out] leading-relaxed">
              <span className={`inline-flex items-center gap-1 font-bold ${PHASE_COLORS[ev.phase] || 'text-gray-300'}`}>
                {PHASE_ICONS[ev.phase]}
                [{PHASE_LABELS[ev.phase] || ev.phase.toUpperCase()}]
              </span>{' '}
              <span className="text-gray-200">{ev.message}</span>
              {ev.data && (
                <div className="pl-5 mt-0.5 text-gray-500 whitespace-pre-wrap break-words">{'> ' + ev.data}</div>
              )}
            </div>
          ))
        )}
        {run?.status === 'running' && (
          <span className="inline-block w-2 h-3.5 bg-green-400 animate-pulse align-middle" />
        )}
        {run?.status === 'error' && run.error && (
          <div className="text-red-400">✖ {run.error}</div>
        )}
      </div>
    </div>
  );
};

export default AgentThinkingStream;
