import { test, expect } from '@playwright/test';
import { ProjectViewPage } from './page-objects/ProjectViewPage';
import { RoadmapPage } from './page-objects/RoadmapPage';

test.describe('Task Workflow', () => {
  const testProjectId = './projects/test-project';
  
  test.beforeEach(async ({ page }) => {
    // Mock project get
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}`, async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: testProjectId,
            name: 'Test Project',
            description: 'A test project',
            path: testProjectId,
            exists: true,
          }),
        });
      }
    });
    
    // Mock roadmap get
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/roadmap`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          roadmap: `# Roadmap

## Milestone v1.0

### Phase 1: Setup
Initialize project structure and development environment.`,
          project_id: testProjectId,
        }),
      });
    });
  });

  test('should plan a phase', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Mock phase planning
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/phases/1/plan`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          phase_number: 1,
          tasks: [
            {
              id: 'task-1-1-abc123',
              name: 'Initialize project structure',
              type: 'auto',
              action: 'Create project directory structure',
              status: 'pending',
            },
            {
              id: 'task-1-2-def456',
              name: 'Set up development environment',
              type: 'auto',
              action: 'Configure development tools',
              status: 'pending',
            },
          ],
        }),
      });
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    await projectView.waitForRoadmap();
    
    // Click Plan button for Phase 1
    await roadmapPage.clickPlanPhase(1);
    
    // Wait for tasks to appear
    await roadmapPage.waitForTasks();
    
    // Verify tasks are displayed
    await expect(page.getByText('Initialize project structure')).toBeVisible();
    await expect(page.getByText('Set up development environment')).toBeVisible();
  });

  test('should execute a phase', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Mock phase planning
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/phases/1/plan`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          phase_number: 1,
          tasks: [
            {
              id: 'task-1-1-abc123',
              name: 'Initialize project structure',
              type: 'auto',
              action: 'Create project directory structure',
              status: 'pending',
            },
          ],
        }),
      });
    });
    
    // Mock phase execution
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/phases/1/execute`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          results: [
            {
              task_id: 'task-1-1-abc123',
              task_name: 'Initialize project structure',
              status: 'complete',
              result: 'Project structure created successfully',
            },
          ],
          project_id: testProjectId,
          phase_number: 1,
        }),
      });
    });
    
    // Mock alert dialog
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('execution started');
      await dialog.accept();
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    await projectView.waitForRoadmap();
    
    // Plan phase first
    await roadmapPage.clickPlanPhase(1);
    await roadmapPage.waitForTasks();
    
    // Execute phase
    await roadmapPage.clickExecutePhase(1);
    
    // Alert should be shown (handled by dialog handler)
  });

  test('should handle planning error', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Mock phase planning failure
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/phases/1/plan`, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Failed to plan phase' }),
      });
    });
    
    // Mock alert dialog
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Failed');
      await dialog.accept();
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    await projectView.waitForRoadmap();
    
    await roadmapPage.clickPlanPhase(1);
    
    // Alert should be shown (handled by dialog handler)
  });

  test('should show loading state during planning', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Mock slow phase planning
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/phases/1/plan`, async (route) => {
      await page.waitForTimeout(500); // Simulate delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          phase_number: 1,
          tasks: [],
        }),
      });
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    await projectView.waitForRoadmap();
    
    // Click Plan button
    await roadmapPage.clickPlanPhase(1);
    
    // Should show "Planning..." text
    await expect(page.getByText('Planning...')).toBeVisible({ timeout: 1000 });
  });
});
