import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Project {
  id: string;
  name: string;
  description?: string;
  path: string;
  exists: boolean;
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
  status?: string;
}

export interface TaskPlan {
  phase_number: number;
  tasks: Task[];
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
    const response = await api.post(`/api/projects/${projectId}/phases/${phaseNumber}/execute`, {
      project_id: projectId,
      phase_number: phaseNumber,
      task_id: taskId,
    });
    return response.data;
  },
  getProgress: async (projectId: string, phaseNumber: number): Promise<any> => {
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
