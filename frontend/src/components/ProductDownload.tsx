'use client';

import type { TaskProgress, ProductType } from '@/types';
import { getDownloadUrl } from '@/lib/api';

interface ProductDownloadProps {
  tasks: TaskProgress[];
  jobId: string;
}

const PRODUCT_LABELS: Record<ProductType, string> = {
  lesson: '教案',
  tts: '语音',
  ppt: 'PPT',
  video: '视频',
};

const PRODUCT_EXTENSIONS: Record<ProductType, string> = {
  lesson: '.json',
  tts: '.mp3',
  ppt: '.pptx',
  video: '.mp4',
};

export function ProductDownload({ tasks, jobId }: ProductDownloadProps) {
  const completedTasks = tasks.filter(
    (t) => t.status === 'completed' && t.downloadUrl
  );

  if (!completedTasks.length) return null;

  return (
    <div className="w-full max-w-2xl space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">产物下载</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {completedTasks.map((task) => {
          const label = PRODUCT_LABELS[task.type];
          const ext = PRODUCT_EXTENSIONS[task.type];
          const url = task.downloadUrl || getDownloadUrl(task.type, jobId);

          return (
            <div
              key={task.type}
              className="flex items-center justify-between rounded-lg border border-gray-200 p-3 bg-white"
            >
              <span className="text-sm font-medium text-gray-700">
                {label}
              </span>
              <a
                href={url}
                download
                className="inline-flex items-center rounded-md bg-blue-100 px-2.5 py-1.5 text-sm font-medium text-blue-700 hover:bg-blue-200 transition-colors"
              >
                <svg
                  className="w-4 h-4 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
                下载{ext}
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}