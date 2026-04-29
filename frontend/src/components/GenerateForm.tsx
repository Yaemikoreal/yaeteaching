'use client';

import { useState } from 'react';
import type { GenerateRequest } from '@/types';

interface GenerateFormProps {
  onSubmit: (params: GenerateRequest) => void;
  isLoading: boolean;
}

const SUBJECTS = [
  '物理',
  '数学',
  '语文',
  '英语',
  '化学',
  '历史',
  '地理',
  '生物',
];

const GRADES = ['小学一年级', '小学二年级', '小学三年级', '小学四年级', '小学五年级', '小学六年级', '七年级', '八年级', '九年级', '高一', '高二', '高三'];

const STYLES = ['讲授式', '探究式', '互动式', '案例式'];

export function GenerateForm({ onSubmit, isLoading }: GenerateFormProps) {
  const [subject, setSubject] = useState('物理');
  const [grade, setGrade] = useState('七年级');
  const [duration, setDuration] = useState(45);
  const [topic, setTopic] = useState('');
  const [style, setStyle] = useState('讲授式');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;
    onSubmit({ subject, grade, duration, topic, style });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label
            htmlFor="subject"
            className="block text-sm font-medium text-gray-700"
          >
            学科
          </label>
          <select
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {SUBJECTS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="grade"
            className="block text-sm font-medium text-gray-700"
          >
            年级
          </label>
          <select
            id="grade"
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {GRADES.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label
            htmlFor="duration"
            className="block text-sm font-medium text-gray-700"
          >
            课时（分钟）
          </label>
          <input
            id="duration"
            type="number"
            min={10}
            max={120}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-2">
          <label
            htmlFor="style"
            className="block text-sm font-medium text-gray-700"
          >
            教学风格
          </label>
          <select
            id="style"
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {STYLES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <label
          htmlFor="topic"
          className="block text-sm font-medium text-gray-700"
        >
          课题/主题
        </label>
        <input
          id="topic"
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="例如：力学入门、牛顿第一定律"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || !topic.trim()}
        className="w-full rounded-lg bg-blue-600 px-4 py-3 text-white font-medium transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {isLoading ? '生成中...' : '开始生成'}
      </button>
    </form>
  );
}