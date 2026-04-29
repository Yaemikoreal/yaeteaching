// 任务状态类型
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

// 产物类型
export type ProductType = 'lesson' | 'tts' | 'ppt' | 'video';

// 单个任务进度
export interface TaskProgress {
  type: ProductType;
  status: TaskStatus;
  progress: number; // 0-100
  message?: string;
  error?: string;
  downloadUrl?: string;
}

// 任务整体状态
export interface JobStatus {
  jobId: string;
  status: TaskStatus;
  tasks: TaskProgress[];
  createdAt: string;
  updatedAt: string;
}

// WebSocket 进度推送消息
export interface ProgressMessage {
  jobId: string;
  taskType: ProductType;
  status: TaskStatus;
  progress: number;
  message?: string;
  error?: string;
  downloadUrl?: string;
}

// 生成请求参数
export interface GenerateRequest {
  subject: string;
  grade: string;
  duration: number;
  topic: string;
  style?: string;
}

// 生成响应
export interface GenerateResponse {
  jobId: string;
  message: string;
}