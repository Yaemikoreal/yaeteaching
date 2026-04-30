'use client';

import { useState, useCallback, useMemo } from 'react';

interface Section {
  section_id: number;
  title: string;
  content: string;
  teaching_points?: string[];
  examples?: string[];
  media_hint?: {
    slide_type?: string;
  };
}

interface LessonMeta {
  title: string;
  subject: string;
  grade: string;
  duration_minutes: number;
}

interface LessonPlan {
  meta: LessonMeta;
  outline: Section[];
  summary?: {
    key_points: string[];
    homework: string;
    next_preview: string;
  };
}

interface LessonPlanEditorProps {
  lesson: LessonPlan;
  onSave: (lesson: LessonPlan) => void;
  onRegenerateSections: (modifiedSectionIds: number[]) => void;
  disabled?: boolean;
}

const SLIDE_TYPES = ['title', 'knowledge', 'example', 'summary'];

export function LessonPlanEditor({
  lesson,
  onSave,
  onRegenerateSections,
  disabled = false,
}: LessonPlanEditorProps) {
  const [editMode, setEditMode] = useState<'structured' | 'json'>('structured');
  const [editedLesson, setEditedLesson] = useState<LessonPlan>(lesson);
  const [jsonText, setJsonText] = useState<string>(() => JSON.stringify(lesson, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Track which sections have been modified
  const modifiedSections = useMemo(() => {
    const modified: Set<number> = new Set();

    // Compare outline sections
    lesson.outline.forEach((originalSection, idx) => {
      const editedSection = editedLesson.outline[idx];
      if (!editedSection) return;

      if (
        originalSection.title !== editedSection.title ||
        originalSection.content !== editedSection.content ||
        JSON.stringify(originalSection.teaching_points) !== JSON.stringify(editedSection.teaching_points) ||
        JSON.stringify(originalSection.examples) !== JSON.stringify(editedSection.examples) ||
        originalSection.media_hint?.slide_type !== editedSection.media_hint?.slide_type
      ) {
        modified.add(originalSection.section_id);
      }
    });

    // Compare meta
    if (
      lesson.meta.title !== editedLesson.meta.title ||
      lesson.meta.subject !== editedLesson.meta.subject ||
      lesson.meta.grade !== editedLesson.meta.grade ||
      lesson.meta.duration_minutes !== editedLesson.meta.duration_minutes
    ) {
      // Meta changes affect all sections, but we mark as meta modification
    }

    return modified;
  }, [lesson, editedLesson]);

  const handleSectionChange = useCallback((
    sectionId: number,
    field: keyof Section,
    value: string | string[]
  ) => {
    setEditedLesson(prev => {
      const newOutline = prev.outline.map(section => {
        if (section.section_id === sectionId) {
          return { ...section, [field]: value };
        }
        return section;
      });
      return { ...prev, outline: newOutline };
    });
  }, []);

  const handleMetaChange = useCallback((
    field: keyof LessonMeta,
    value: string | number
  ) => {
    setEditedLesson(prev => ({
      ...prev,
      meta: { ...prev.meta, [field]: value },
    }));
  }, []);

  const handleSlideTypeChange = useCallback((
    sectionId: number,
    slideType: string
  ) => {
    setEditedLesson(prev => {
      const newOutline = prev.outline.map(section => {
        if (section.section_id === sectionId) {
          return {
            ...section,
            media_hint: { ...section.media_hint, slide_type: slideType },
          };
        }
        return section;
      });
      return { ...prev, outline: newOutline };
    });
  }, []);

  const handleJsonChange = useCallback((text: string) => {
    setJsonText(text);
    try {
      const parsed = JSON.parse(text) as LessonPlan;
      // Validate structure
      if (!parsed.meta || !parsed.outline) {
        throw new Error('缺少必要字段: meta 或 outline');
      }
      setEditedLesson(parsed);
      setJsonError(null);
    } catch (e) {
      setJsonError(e instanceof Error ? e.message : 'JSON 格式错误');
    }
  }, []);

  const handleSave = useCallback(() => {
    if (editMode === 'json' && jsonError) {
      return;
    }
    onSave(editMode === 'json' ? JSON.parse(jsonText) : editedLesson);
  }, [editMode, jsonError, jsonText, editedLesson, onSave]);

  const handleRegenerate = useCallback(() => {
    if (modifiedSections.size > 0) {
      onRegenerateSections(Array.from(modifiedSections));
    }
  }, [modifiedSections, onRegenerateSections]);

  const isModified = modifiedSections.size > 0;

  return (
    <div className="w-full max-w-2xl space-y-4">
      {/* Mode toggle */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">教案编辑</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEditMode('structured')}
            disabled={disabled}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              editMode === 'structured'
                ? 'bg-blue-100 text-blue-700 font-medium'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            结构化
          </button>
          <button
            onClick={() => setEditMode('json')}
            disabled={disabled}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              editMode === 'json'
                ? 'bg-blue-100 text-blue-700 font-medium'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            JSON
          </button>
        </div>
      </div>

      {/* Modified indicator */}
      {isModified && (
        <div className="flex items-center gap-2 px-3 py-2 bg-yellow-50 rounded-lg">
          <span className="text-sm text-yellow-700">
            已修改 {modifiedSections.size} 个章节
          </span>
          <span className="text-xs text-yellow-600">
            (ID: {Array.from(modifiedSections).join(', ')})
          </span>
        </div>
      )}

      {/* Editor content */}
      {editMode === 'structured' ? (
        <div className="space-y-4">
          {/* Meta section */}
          <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
            <h3 className="text-md font-semibold text-gray-700">基本信息</h3>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="text-sm text-gray-600">课程标题</label>
                <input
                  type="text"
                  value={editedLesson.meta.title}
                  onChange={(e) => handleMetaChange('title', e.target.value)}
                  disabled={disabled}
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm text-gray-600">学科</label>
                <input
                  type="text"
                  value={editedLesson.meta.subject}
                  onChange={(e) => handleMetaChange('subject', e.target.value)}
                  disabled={disabled}
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm text-gray-600">年级</label>
                <input
                  type="text"
                  value={editedLesson.meta.grade}
                  onChange={(e) => handleMetaChange('grade', e.target.value)}
                  disabled={disabled}
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm text-gray-600">时长(分钟)</label>
                <input
                  type="number"
                  value={editedLesson.meta.duration_minutes}
                  onChange={(e) => handleMetaChange('duration_minutes', Number(e.target.value))}
                  disabled={disabled}
                  className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                />
              </div>
            </div>
          </div>

          {/* Outline sections */}
          {editedLesson.outline.map((section) => (
            <div
              key={section.section_id}
              className={`rounded-lg border p-4 space-y-3 ${
                modifiedSections.has(section.section_id)
                  ? 'border-yellow-300 bg-yellow-50'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <h3 className="text-md font-semibold text-gray-700">
                  章节 {section.section_id}
                </h3>
                {modifiedSections.has(section.section_id) && (
                  <span className="text-xs text-yellow-600 font-medium">
                    已修改
                  </span>
                )}
              </div>

              <div className="space-y-2">
                <div className="space-y-1">
                  <label className="text-sm text-gray-600">标题</label>
                  <input
                    type="text"
                    value={section.title}
                    onChange={(e) => handleSectionChange(section.section_id, 'title', e.target.value)}
                    disabled={disabled}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-sm text-gray-600">内容</label>
                  <textarea
                    value={section.content}
                    onChange={(e) => handleSectionChange(section.section_id, 'content', e.target.value)}
                    disabled={disabled}
                    rows={3}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                  />
                </div>

                {section.teaching_points && section.teaching_points.length > 0 && (
                  <div className="space-y-1">
                    <label className="text-sm text-gray-600">教学要点</label>
                    {section.teaching_points.map((point, i) => (
                      <input
                        key={i}
                        type="text"
                        value={point}
                        onChange={(e) => {
                          const newPoints = [...(section.teaching_points || [])];
                          newPoints[i] = e.target.value;
                          handleSectionChange(section.section_id, 'teaching_points', newPoints);
                        }}
                        disabled={disabled}
                        className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                      />
                    ))}
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-sm text-gray-600">幻灯片类型</label>
                  <select
                    value={section.media_hint?.slide_type || 'knowledge'}
                    onChange={(e) => handleSlideTypeChange(section.section_id, e.target.value)}
                    disabled={disabled}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                  >
                    {SLIDE_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type === 'title' ? '标题页' :
                         type === 'knowledge' ? '知识点页' :
                         type === 'example' ? '例题页' : '总结页'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          ))}

          {/* Summary section */}
          {editedLesson.summary && (
            <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
              <h3 className="text-md font-semibold text-gray-700">总结</h3>
              <div className="space-y-2">
                <div className="space-y-1">
                  <label className="text-sm text-gray-600">核心要点</label>
                  <textarea
                    value={editedLesson.summary.key_points.join('\n')}
                    onChange={(e) => {
                      const points = e.target.value.split('\n').filter(p => p.trim());
                      setEditedLesson(prev => ({
                        ...prev,
                        summary: { ...prev.summary!, key_points: points },
                      }));
                    }}
                    disabled={disabled}
                    rows={3}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm text-gray-600">作业</label>
                  <input
                    type="text"
                    value={editedLesson.summary.homework}
                    onChange={(e) => {
                      setEditedLesson(prev => ({
                        ...prev,
                        summary: { ...prev.summary!, homework: e.target.value },
                      }));
                    }}
                    disabled={disabled}
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          <textarea
            value={jsonText}
            onChange={(e) => handleJsonChange(e.target.value)}
            disabled={disabled}
            rows={20}
            className={`w-full rounded border font-mono text-sm px-3 py-2 focus:outline-none ${
              jsonError
                ? 'border-red-300 bg-red-50'
                : 'border-gray-300 focus:border-blue-500'
            } disabled:bg-gray-100`}
          />
          {jsonError && (
            <p className="text-sm text-red-600">{jsonError}</p>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center justify-between gap-3 pt-4">
        <button
          onClick={handleSave}
          disabled={disabled || (editMode === 'json' && !!jsonError)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white font-medium transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          保存修改
        </button>

        {isModified && (
          <button
            onClick={handleRegenerate}
            disabled={disabled}
            className="rounded-lg bg-green-600 px-4 py-2 text-white font-medium transition-colors hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            重新生成修改的章节
          </button>
        )}
      </div>
    </div>
  );
}