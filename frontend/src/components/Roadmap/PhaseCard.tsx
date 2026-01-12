import { useState } from 'react';
import { phaseApi } from '../../services/api';
import TaskPlan from '../Tasks/TaskPlan';

interface PhaseCardProps {
  projectId: string;
  phase: {
    number: number;
    name: string;
    description: string;
  };
  isSelected: boolean;
  onSelect: () => void;
}

export default function PhaseCard({ projectId, phase, isSelected, onSelect }: PhaseCardProps) {
  const [planning, setPlanning] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [taskPlan, setTaskPlan] = useState<any>(null);

  const handlePlan = async () => {
    setPlanning(true);
    try {
      const plan = await phaseApi.plan(projectId, phase.number);
      setTaskPlan(plan);
    } catch (error) {
      console.error('Failed to plan phase:', error);
      alert('Failed to plan phase. Please try again.');
    } finally {
      setPlanning(false);
    }
  };

  const handleExecute = async () => {
    setExecuting(true);
    try {
      await phaseApi.execute(projectId, phase.number);
      alert('Phase execution started. Check progress in the task view.');
    } catch (error) {
      console.error('Failed to execute phase:', error);
      alert('Failed to execute phase. Please try again.');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h4 className="font-semibold">{phase.name}</h4>
          <p className="text-sm text-gray-600 mt-1">{phase.description.trim()}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePlan}
            disabled={planning}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {planning ? 'Planning...' : 'Plan'}
          </button>
          {taskPlan && (
            <button
              onClick={handleExecute}
              disabled={executing}
              className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {executing ? 'Executing...' : 'Execute'}
            </button>
          )}
        </div>
      </div>

      {taskPlan && (
        <div className="mt-4">
          <TaskPlan plan={taskPlan} />
        </div>
      )}
    </div>
  );
}
