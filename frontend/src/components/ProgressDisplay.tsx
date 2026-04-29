'use client';

import type { TaskProgress, ProductType } from '@/types';

interface ProgressItemProps {
  task: TaskProgress;
}

const TASK_LABELS: Record<ProductType, string> = {
  lesson: '教案生成',
  tts: '语音合成',
  ppt: 'PPT生成',
  video: '视频生成',
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-200',
  in_progress: 'bg-blue-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
};

function ProgressItem({ task }: ProgressItemProps) {
  const label = TASK_LABELS[task.type];
  const barColor = STATUS_COLORS[task.status];
  const progressText = task.status === 'pending' ? '等待中' : `${task.progress}%`;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm text-gray-500">{progressText}</span>
      </div>
      <div className="h-3 w-full rounded-full bg-gray-200 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${barColor}`}
          style={{ width: `${task.progress}%` }}
        />
      </div>
      {task.message && (
        <p className="text-xs text-gray-500">{task.message}</p>
      )}
      {task.error && (
        <p className="text-xs text-red-500">{task.error}</p>
      )}
    </div>
  );
}

interface ProgressDisplayProps {
  tasks: TaskProgress[];
}

export function ProgressDisplay({ tasks }: ProgressDisplayProps) {
  if (!tasks.length) return null;

  const allCompleted = tasks.every(
    (t) => t.status === 'completed' || t.status === 'failed'
  );

  return (
    <div className="w-full max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">生成进度</h2>
        {allCompleted && (
          <span className="text-sm text-green-600 font-medium">
            已完成
          </span>
        )}
      </div>
      <div className="space-y-4">
        {tasks.map((task) => (
          <ProgressItem key={task.type} task={task} />
        ))}
      </div>
    </div>
  );
}