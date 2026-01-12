import { TaskPlan as TaskPlanType } from '../../services/api';

interface TaskPlanProps {
  plan: TaskPlanType;
}

export default function TaskPlan({ plan }: TaskPlanProps) {
  return (
    <div className="bg-gray-50 rounded p-4">
      <h5 className="font-semibold mb-2">Phase {plan.phase_number} Tasks</h5>
      <div className="space-y-2">
        {plan.tasks.map((task) => (
          <div key={task.id} className="bg-white rounded p-3 border border-gray-200">
            <div className="font-medium">{task.name}</div>
            <div className="text-sm text-gray-600 mt-1">{task.action}</div>
            {task.files && task.files.length > 0 && (
              <div className="text-xs text-gray-500 mt-1">
                Files: {task.files.join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
