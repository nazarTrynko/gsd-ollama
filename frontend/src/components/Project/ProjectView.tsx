import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { projectApi, roadmapApi, Project, Roadmap } from '../../services/api';
import RoadmapView from '../Roadmap/RoadmapView';

export default function ProjectView() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingRoadmap, setCreatingRoadmap] = useState(false);

  useEffect(() => {
    if (id) {
      loadProject();
    }
  }, [id]);

  const loadProject = async () => {
    if (!id) return;
    try {
      const projectData = await projectApi.get(decodeURIComponent(id));
      setProject(projectData);
      await loadRoadmap();
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRoadmap = async () => {
    if (!id) return;
    try {
      const roadmapData = await roadmapApi.get(decodeURIComponent(id));
      setRoadmap(roadmapData);
    } catch (error: any) {
      if (error.response?.status !== 404) {
        console.error('Failed to load roadmap:', error);
      }
    }
  };

  const handleCreateRoadmap = async () => {
    if (!id) return;
    setCreatingRoadmap(true);
    try {
      const roadmapData = await roadmapApi.create(decodeURIComponent(id));
      setRoadmap(roadmapData);
    } catch (error) {
      console.error('Failed to create roadmap:', error);
      alert('Failed to create roadmap. Please try again.');
    } finally {
      setCreatingRoadmap(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading project...</div>;
  }

  if (!project) {
    return <div className="text-center py-8">Project not found</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">{project.name}</h1>
        {project.description && (
          <p className="text-gray-600">{project.description}</p>
        )}
      </div>

      {!roadmap ? (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-500 mb-4">No roadmap yet</p>
          <button
            onClick={handleCreateRoadmap}
            disabled={creatingRoadmap}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {creatingRoadmap ? 'Creating...' : 'Create Roadmap'}
          </button>
        </div>
      ) : (
        <RoadmapView projectId={id!} roadmap={roadmap} />
      )}
    </div>
  );
}
