import { useState } from 'react';
import { Roadmap } from '../../services/api';
import PhaseCard from './PhaseCard';

interface RoadmapViewProps {
  projectId: string;
  roadmap: Roadmap;
}

export default function RoadmapView({ projectId, roadmap }: RoadmapViewProps) {
  const [selectedPhase, setSelectedPhase] = useState<number | null>(null);

  // Simple parsing of roadmap markdown to extract phases
  const parseRoadmap = (content: string) => {
    const lines = content.split('\n');
    const milestones: any[] = [];
    let currentMilestone: any = null;
    let currentPhase: any = null;

    for (const line of lines) {
      if (line.startsWith('## Milestone')) {
        if (currentMilestone) {
          milestones.push(currentMilestone);
        }
        currentMilestone = {
          name: line.replace('##', '').trim(),
          phases: [],
        };
      } else if (line.startsWith('### Phase')) {
        if (currentPhase && currentMilestone) {
          currentMilestone.phases.push(currentPhase);
        }
        const phaseMatch = line.match(/Phase (\d+)/);
        currentPhase = {
          number: phaseMatch ? parseInt(phaseMatch[1]) : 0,
          name: line.replace('###', '').trim(),
          description: '',
        };
      } else if (currentPhase && line.trim()) {
        currentPhase.description += line + '\n';
      }
    }

    if (currentPhase && currentMilestone) {
      currentMilestone.phases.push(currentPhase);
    }
    if (currentMilestone) {
      milestones.push(currentMilestone);
    }

    return milestones;
  };

  const milestones = parseRoadmap(roadmap.roadmap);

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Roadmap</h2>
        <div className="bg-white rounded-lg shadow p-4">
          <pre className="whitespace-pre-wrap text-sm">{roadmap.roadmap}</pre>
        </div>
      </div>

      {milestones.length > 0 && (
        <div className="space-y-6">
          {milestones.map((milestone, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">{milestone.name}</h3>
              <div className="space-y-4">
                {milestone.phases.map((phase: any) => (
                  <PhaseCard
                    key={phase.number}
                    projectId={projectId}
                    phase={phase}
                    isSelected={selectedPhase === phase.number}
                    onSelect={() => setSelectedPhase(phase.number)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
