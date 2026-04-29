'use client';

import { useState, useCallback } from 'react';

interface LessonPreviewProps {
  jobId: string;
  downloadUrl?: string;
}

interface LessonPlan {
  meta: {
    title: string;
    subject: string;
    grade: string;
    duration_minutes: number;
  };
  outline: Array<{
    section_id: number;
    title: string;
    content: string;
    teaching_points: string[];
    examples: string[];
  }>;
  summary: {
    key_points: string[];
    homework: string;
    next_preview: string;
  };
}

export function LessonPreview({ downloadUrl }: LessonPreviewProps) {
  const [lesson, setLesson] = useState<LessonPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLesson = useCallback(async () => {
    if (!downloadUrl) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(downloadUrl);
      if (!response.ok) {
        throw new Error('Failed to fetch lesson plan');
      }
      const data = await response.json();
      setLesson(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [downloadUrl]);

  // Fetch lesson when downloadUrl becomes available
  if (downloadUrl && !lesson && !loading && !error) {
    // Trigger fetch on next render
    setLoading(true);
    fetch(downloadUrl)
      .then((response) => {
        if (!response.ok) throw new Error('Failed to fetch lesson plan');
        return response.json();
      })
      .then((data) => {
        setLesson(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      });
  }

  if (!downloadUrl) return null;

  if (loading) {
    return (
      <div className="w-full max-w-2xl p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-500">加载教案...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full max-w-2xl p-4 bg-red-50 rounded-lg">
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (!lesson) return null;

  return (
    <div className="w-full max-w-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">教案预览</h2>
        <button
          onClick={fetchLesson}
          className="text-sm text-blue-600 hover:text-blue-700"
        >
          刷新
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-4">
        {/* Meta info */}
        <div className="border-b border-gray-100 pb-3">
          <h3 className="text-xl font-bold text-gray-900">{lesson.meta.title}</h3>
          <div className="mt-2 flex gap-3 text-sm text-gray-500">
            <span>{lesson.meta.subject}</span>
            <span>{lesson.meta.grade}</span>
            <span>{lesson.meta.duration_minutes}分钟</span>
          </div>
        </div>

        {/* Outline */}
        <div className="space-y-3">
          <h4 className="text-md font-semibold text-gray-800">课程大纲</h4>
          {lesson.outline.map((section) => (
            <div key={section.section_id} className="space-y-2">
              <div className="font-medium text-gray-700">
                {section.section_id}. {section.title}
              </div>
              <p className="text-sm text-gray-600 pl-4">{section.content}</p>
              {section.teaching_points.length > 0 && (
                <div className="pl-4">
                  <span className="text-xs font-medium text-gray-500">
                    教学要点：
                  </span>
                  <ul className="text-xs text-gray-600 list-disc pl-4">
                    {section.teaching_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
              )}
              {section.examples.length > 0 && (
                <div className="pl-4">
                  <span className="text-xs font-medium text-gray-500">
                    例子：
                  </span>
                  <ul className="text-xs text-gray-600 list-disc pl-4">
                    {section.examples.map((example, i) => (
                      <li key={i}>{example}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        {lesson.summary && (
          <div className="border-t border-gray-100 pt-3 space-y-2">
            <h4 className="text-md font-semibold text-gray-800">总结</h4>
            <div className="space-y-1">
              <p className="text-sm text-gray-600">
                <span className="font-medium">核心要点：</span>
                {lesson.summary.key_points.join('、')}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">作业：</span>
                {lesson.summary.homework}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">下节预告：</span>
                {lesson.summary.next_preview}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}