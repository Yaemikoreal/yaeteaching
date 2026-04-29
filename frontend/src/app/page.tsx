'use client';

import { useState, useCallback } from 'react';
import {
  GenerateForm,
  ProgressDisplay,
  ProductDownload,
  LessonPreview,
} from '@/components';
import { useWebSocket } from '@/hooks';
import { generateLessonPlan } from '@/lib/api';
import type { GenerateRequest, ProgressMessage } from '@/types';

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleProgress = useCallback((message: ProgressMessage) => {
    console.log('Progress update:', message);
  }, []);

  const { status, isConnected, error: wsError } = useWebSocket({
    jobId,
    onProgress: handleProgress,
  });

  const handleSubmit = async (params: GenerateRequest) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setJobId(null);

    try {
      const response = await generateLessonPlan(params);
      setJobId(response.jobId);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : '生成请求失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setJobId(null);
    setSubmitError(null);
  };

  return (
    <div className="min-h-full flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-900">
            AI教案生成工作站
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            输入提示词，自动生成教案、语音、PPT和视频
          </p>
        </div>
      </header>

      <main className="flex-1 px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Connection status */}
          {jobId && (
            <div className="flex items-center gap-2 text-sm">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-gray-500">
                {isConnected ? '已连接' : '连接断开'}
              </span>
            </div>
          )}

          {/* Error messages */}
          {submitError && (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
              {submitError}
            </div>
          )}
          {wsError && (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600">
              WebSocket 错误: {wsError}
            </div>
          )}

          {/* Form */}
          {!jobId && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">
                生成教案
              </h2>
              <GenerateForm onSubmit={handleSubmit} isLoading={isSubmitting} />
            </div>
          )}

          {/* Progress */}
          {status && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <ProgressDisplay tasks={status.tasks} />
            </div>
          )}

          {/* Product downloads */}
          {status && jobId && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <ProductDownload tasks={status.tasks} jobId={jobId} />
            </div>
          )}

          {/* Lesson preview */}
          {status && jobId && (
            <div className="rounded-lg bg-white p-6 shadow-sm">
              <LessonPreview
                jobId={jobId}
                downloadUrl={status.tasks.find((t) => t.type === 'lesson' && t.downloadUrl)?.downloadUrl}
              />
            </div>
          )}

          {/* Reset button */}
          {jobId && status?.tasks.every(t => t.status === 'completed' || t.status === 'failed') && (
            <div className="text-center">
              <button
                onClick={handleReset}
                className="rounded-lg bg-gray-100 px-6 py-2 text-gray-700 font-medium hover:bg-gray-200 transition-colors"
              >
                开始新的生成
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-7xl mx-auto text-center text-sm text-gray-500">
          AI教案生成工作站 — Multica Platform
        </div>
      </footer>
    </div>
  );
}