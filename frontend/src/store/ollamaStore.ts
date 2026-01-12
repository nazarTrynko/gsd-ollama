import { create } from 'zustand';

interface OllamaState {
  connected: boolean;
  models: string[];
  defaultModel: string;
  serverUrl: string;
  setStatus: (status: { connected: boolean; models: string[]; defaultModel: string; serverUrl: string }) => void;
}

export const useOllamaStore = create<OllamaState>((set) => ({
  connected: false,
  models: [],
  defaultModel: 'llama3.2',
  serverUrl: 'http://localhost:11434',
  setStatus: (status) => set(status),
}));
