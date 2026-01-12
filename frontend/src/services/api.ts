import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes timeout for long-running operations like project creation
});

export interface Project {
  id: string;
  name: string;
  description?: string;
  path: string;
  exists: boolean;
  created_at?: string; // ISO datetime string from backend
  updated_at?: string; // ISO datetime string from backend
}

export interface ProjectCreate {
  name: string;
  description: string;
  initial_task?: string;
  project_path?: string;
}

export interface Roadmap {
  roadmap: string;
  project_id: string;
}

export interface Task {
  id: string;
  name: string;
  type: string;
  files?: string[];
  action: string;
  verify?: string;
  done?: string;
  status: string; // Required, defaults to "pending" in backend
  result?: string;
}

export interface TaskPlan {
  phase_number: number;
  tasks: Task[];
  created_at?: string; // ISO datetime string from backend
}

export interface TaskProgress {
  project_id: string;
  phase_number: number;
  current_task?: string;
  completed_tasks: number;
  total_tasks: number;
  status: string;
  logs: string[];
}

export interface TaskExecute {
  project_id: string;
  phase_number: number;
  task_id?: string;
}

export const projectApi = {
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post('/api/projects/new', data);
    return response.data;
  },
  list: async (): Promise<Project[]> => {
    const response = await api.get('/api/projects');
    return response.data.projects;
  },
  get: async (id: string): Promise<Project> => {
    const response = await api.get(`/api/projects/${id}`);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/projects/${id}`);
  },
};

export const roadmapApi = {
  create: async (projectId: string): Promise<Roadmap> => {
    const response = await api.post(`/api/projects/${projectId}/roadmap`, {});
    return response.data;
  },
  get: async (projectId: string): Promise<Roadmap> => {
    const response = await api.get(`/api/projects/${projectId}/roadmap`);
    return response.data;
  },
};

export const phaseApi = {
  plan: async (projectId: string, phaseNumber: number): Promise<TaskPlan> => {
    const response = await api.post(`/api/projects/${projectId}/phases/${phaseNumber}/plan`);
    return response.data;
  },
  execute: async (projectId: string, phaseNumber: number, taskId?: string): Promise<any> => {
    const executeData: TaskExecute = {
      project_id: projectId,
      phase_number: phaseNumber,
      task_id: taskId,
    };
    const response = await api.post(`/api/projects/${projectId}/phases/${phaseNumber}/execute`, executeData);
    return response.data;
  },
  getProgress: async (projectId: string, phaseNumber: number): Promise<TaskProgress> => {
    const response = await api.get(`/api/projects/${projectId}/phases/${phaseNumber}/progress`);
    return response.data;
  },
};

export const ollamaApi = {
  getStatus: async (): Promise<any> => {
    const response = await api.get('/api/ollama/status');
    return response.data;
  },
  listModels: async (): Promise<string[]> => {
    const response = await api.get('/api/ollama/models');
    return response.data.models;
  },
};

export default api;
