import { useEffect } from 'react';
import { ollamaApi } from '../../services/api';
import { useOllamaStore } from '../../store/ollamaStore';

export default function StatusBar() {
  const { connected, serverUrl, defaultModel, setStatus } = useOllamaStore();

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await ollamaApi.getStatus();
        setStatus({
          connected: status.connected,
          models: status.models,
          defaultModel: status.default_model,
          serverUrl: status.server_url,
        });
      } catch (error) {
        setStatus({
          connected: false,
          models: [],
          defaultModel: 'llama3.2',
          serverUrl: 'http://localhost:11434',
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, [setStatus]);

  return (
    <div className="bg-gray-800 text-white px-4 py-2 flex items-center justify-between text-sm">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span>Ollama: {connected ? 'Connected' : 'Disconnected'}</span>
        </div>
        {connected && (
          <>
            <span className="text-gray-400">Model: {defaultModel}</span>
            <span className="text-gray-400">Server: {serverUrl}</span>
          </>
        )}
      </div>
    </div>
  );
}
