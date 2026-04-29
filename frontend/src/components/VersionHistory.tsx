'use client';

import { useState } from 'react';

interface LessonVersion {
  id: string;
  createdAt: string;
  label?: string;
  lessonJson: object;
}

interface VersionHistoryProps {
  versions: LessonVersion[];
  currentVersionId: string | null;
  onRestore: (versionId: string) => void;
  onDelete: (versionId: string) => void;
  onLabel: (versionId: string, label: string) => void;
  maxVersions?: number;
}

export function VersionHistory({
  versions,
  currentVersionId,
  onRestore,
  onDelete,
  onLabel,
  maxVersions = 3,
}: VersionHistoryProps) {
  const [editingLabelId, setEditingLabelId] = useState<string | null>(null);
  const [labelInput, setLabelInput] = useState<string>('');

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleLabelSave = (versionId: string) => {
    if (labelInput.trim()) {
      onLabel(versionId, labelInput.trim());
    }
    setEditingLabelId(null);
    setLabelInput('');
  };

  const handleLabelEdit = (version: LessonVersion) => {
    setEditingLabelId(version.id);
    setLabelInput(version.label || '');
  };

  const canDelete = versions.length > 1;

  return (
    <div className="w-full max-w-2xl space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">版本历史</h2>
        <span className="text-sm text-gray-500">
          {versions.length}/{maxVersions} 版本
        </span>
      </div>

      {versions.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-center">
          <p className="text-sm text-gray-500">暂无版本历史</p>
        </div>
      ) : (
        <div className="space-y-2">
          {versions.map((version, index) => (
            <div
              key={version.id}
              className={`rounded-lg border p-3 ${
                version.id === currentVersionId
                  ? 'border-blue-300 bg-blue-50'
                  : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {/* Version number */}
                  <span className="text-sm font-medium text-gray-700">
                    V{index + 1}
                  </span>

                  {/* Label or edit input */}
                  {editingLabelId === version.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={labelInput}
                        onChange={(e) => setLabelInput(e.target.value)}
                        placeholder="版本标签"
                        className="rounded border border-gray-300 px-2 py-1 text-sm w-32 focus:border-blue-500 focus:outline-none"
                        autoFocus
                      />
                      <button
                        onClick={() => handleLabelSave(version.id)}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        保存
                      </button>
                      <button
                        onClick={() => setEditingLabelId(null)}
                        className="text-sm text-gray-500 hover:text-gray-600"
                      >
                        取消
                      </button>
                    </div>
                  ) : (
                    <>
                      {version.label ? (
                        <span className="text-sm text-gray-600">
                          ({version.label})
                        </span>
                      ) : (
                        <button
                          onClick={() => handleLabelEdit(version)}
                          className="text-sm text-gray-400 hover:text-gray-500"
                        >
                          +添加标签
                        </button>
                      )}
                    </>
                  )}

                  {/* Timestamp */}
                  <span className="text-xs text-gray-400">
                    {formatDate(version.createdAt)}
                  </span>

                  {/* Current indicator */}
                  {version.id === currentVersionId && (
                    <span className="text-xs text-blue-600 font-medium">
                      当前版本
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {version.id !== currentVersionId && (
                    <button
                      onClick={() => onRestore(version.id)}
                      className="text-sm text-blue-600 hover:text-blue-700"
                    >
                      恢复
                    </button>
                  )}
                  {canDelete && version.id !== currentVersionId && (
                    <button
                      onClick={() => onDelete(version.id)}
                      className="text-sm text-red-500 hover:text-red-600"
                    >
                      删除
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Version limit notice */}
      {versions.length >= maxVersions && (
        <p className="text-xs text-gray-500 text-center">
          最多保存 {maxVersions} 个版本，删除旧版本后可添加新版本
        </p>
      )}
    </div>
  );
}