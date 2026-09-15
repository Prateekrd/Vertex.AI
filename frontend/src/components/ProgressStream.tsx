import React, { useState, useEffect, useRef } from 'react';

interface ProgressStep {
  stage: string;
  progress: number;
  details?: string;
  timestamp: string;
}

interface ProgressStreamProps {
  ws: WebSocket | null;
  onDone?: (data: any) => void;
}

export default function ProgressStream({ ws, onDone }: ProgressStreamProps) {
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [current, setCurrent] = useState<ProgressStep | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ws) return;

    const handleOpen = () => {
      addStep('connected', 0, 'WebSocket connected');
    };

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'progress') {
          addStep(data.stage, data.progress, data.details);
          setCurrent({ stage: data.stage, progress: data.progress, details: data.details, timestamp: new Date().toISOString() });
          if (data.stage === 'done' && onDone) {
            onDone(data);
          }
        }
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    const handleError = (event: Event) => {
      addStep('error', 0, 'WebSocket error');
    };

    const handleClose = () => {
      addStep('closed', 0, 'WebSocket closed');
    };

    ws.onopen = handleOpen;
    ws.onmessage = handleMessage;
    ws.onerror = handleError;
    ws.onclose = handleClose;

    return () => {
      ws.onopen = null;
      ws.onmessage = null;
      ws.onerror = null;
      ws.onclose = null;
    };
  }, [ws, onDone]);

  const addStep = (stage: string, progress: number, details?: string) => {
    setSteps((prev) => [
      ...prev,
      { stage, progress, details, timestamp: new Date().toISOString() },
    ]);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);

  return (
    <div className="bg-secondary-800 rounded-lg border border-secondary-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Processing Pipeline</h3>

      {/* Progress bar */}
      {current && (
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-secondary-300 capitalize">{current.stage}</span>
            <span className="text-primary-400">{current.progress}%</span>
          </div>
          <div className="w-full bg-secondary-700 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${current.progress}%` }}
            />
          </div>
          {current.details && (
            <p className="text-xs text-secondary-400 mt-2">{current.details}</p>
          )}
        </div>
      )}

      {/* Live log */}
      <div
        ref={scrollRef}
        className="bg-secondary-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs space-y-1"
      >
        {steps.map((step, i) => (
          <div key={i} className="flex gap-2">
            <span className="text-secondary-500">
              {new Date(step.timestamp).toLocaleTimeString()}
            </span>
            <span
              className={`capitalize ${
                step.stage === 'done'
                  ? 'text-success-500'
                  : step.stage === 'error'
                  ? 'text-danger-500'
                  : 'text-primary-400'
              }`}
            >
              [{step.stage}]
            </span>
            <span className="text-secondary-300">
              {step.details || `${step.progress}%`}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}