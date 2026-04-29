'use client';

import { useState, useCallback, useMemo } from 'react';

interface LessonVersion {
  id: string;
  createdAt: string;
  label?: string;
  lessonJson: object;
}

interface UseLessonVersionsOptions {
  maxVersions?: number;
  initialVersions?: LessonVersion[];
  initialCurrentVersionId?: string | null;
}

interface UseLessonVersionsReturn {
  versions: LessonVersion[];
  currentVersionId: string | null;
  currentVersion: LessonVersion | null;
  saveVersion: (lessonJson: object, label?: string) => void;
  restoreVersion: (versionId: string) => void;
  deleteVersion: (versionId: string) => void;
  labelVersion: (versionId: string, label: string) => void;
  canSaveNewVersion: boolean;
}

const DEFAULT_MAX_VERSIONS = 3;

function generateId(): string {
  return `v_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

export function useLessonVersions({
  maxVersions = DEFAULT_MAX_VERSIONS,
  initialVersions = [],
  initialCurrentVersionId = null,
}: UseLessonVersionsOptions): UseLessonVersionsReturn {
  const [versions, setVersions] = useState<LessonVersion[]>(initialVersions);
  const [currentVersionId, setCurrentVersionId] = useState<string | null>(
    initialCurrentVersionId || initialVersions[initialVersions.length - 1]?.id || null
  );

  const currentVersion = useMemo(() => {
    return versions.find(v => v.id === currentVersionId) || null;
  }, [versions, currentVersionId]);

  const canSaveNewVersion = versions.length < maxVersions;

  const saveVersion = useCallback((lessonJson: object, label?: string) => {
    const newVersion: LessonVersion = {
      id: generateId(),
      createdAt: new Date().toISOString(),
      label,
      lessonJson,
    };

    setVersions(prev => {
      // If at max, remove the oldest version (not current)
      let newVersions = [...prev];
      if (newVersions.length >= maxVersions) {
        // Find oldest version that is not current
        const oldestNonCurrent = newVersions.find(
          v => v.id !== currentVersionId && !newVersions.some(
            (nv, idx) => idx === 0 && nv.id === v.id && nv.id !== currentVersionId
          )
        );
        if (oldestNonCurrent) {
          newVersions = newVersions.filter(v => v.id !== oldestNonCurrent.id);
        } else {
          // Remove oldest regardless
          newVersions = newVersions.slice(1);
        }
      }

      return [...newVersions, newVersion];
    });

    setCurrentVersionId(newVersion.id);
  }, [maxVersions, currentVersionId]);

  const restoreVersion = useCallback((versionId: string) => {
    const version = versions.find(v => v.id === versionId);
    if (version) {
      setCurrentVersionId(versionId);
    }
  }, [versions]);

  const deleteVersion = useCallback((versionId: string) => {
    if (versionId === currentVersionId) {
      return; // Cannot delete current version
    }

    setVersions(prev => prev.filter(v => v.id !== versionId));
  }, [currentVersionId]);

  const labelVersion = useCallback((versionId: string, label: string) => {
    setVersions(prev =>
      prev.map(v =>
        v.id === versionId ? { ...v, label } : v
      )
    );
  }, []);

  return {
    versions,
    currentVersionId,
    currentVersion,
    saveVersion,
    restoreVersion,
    deleteVersion,
    labelVersion,
    canSaveNewVersion,
  };
}