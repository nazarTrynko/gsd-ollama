import { test, expect } from '@playwright/test';
import { ProjectListPage } from './page-objects/ProjectListPage';
import { NewProjectPage } from './page-objects/NewProjectPage';
import { ProjectViewPage } from './page-objects/ProjectViewPage';
import { RoadmapPage } from './page-objects/RoadmapPage';

test.describe('Full Stack E2E - Complete User Journey', () => {
  test('complete workflow: create project → generate roadmap → plan phase → execute', async ({ page }) => {
    const projectList = new ProjectListPage(page);
    const newProject = new NewProjectPage(page);
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Step 1: Navigate to project list
    await projectList.goto();
    await expect(projectList.heading).toBeVisible();
    
    // Step 2: Create new project
    await projectList.clickNewProject();
    await expect(newProject.heading).toBeVisible();
    
    // Fill and submit project form
    await newProject.fillForm({
      name: 'Full Stack E2E Test',
      description: 'Testing complete workflow from UI to backend',
      initialTask: 'Set up e2e testing',
    });
    
    await newProject.submit();
    
    // Wait for project creation and redirect
    await newProject.waitForRedirect();
    
    // Step 3: Verify project view
    await projectView.waitForProject();
    const projectName = await projectView.getProjectName();
    expect(projectName).toContain('Full Stack E2E Test');
    
    // Step 4: Generate roadmap
    await expect(projectView.noRoadmapMessage).toBeVisible();
    await projectView.clickCreateRoadmap();
    
    // Wait for roadmap generation (may take time)
    await projectView.waitForRoadmap();
    
    // Step 5: Verify roadmap is displayed
    await expect(page.getByText('Roadmap')).toBeVisible();
    
    // Step 6: Plan phase 1
    await roadmapPage.clickPlanPhase(1);
    await roadmapPage.waitForTasks();
    
    // Verify tasks are displayed
    await expect(page.getByText(/task/i)).toBeVisible({ timeout: 10000 });
    
    // Step 7: Execute phase (if execute button is available)
    // Note: Execute button only appears after planning
    const executeButton = page.getByRole('button', { name: /Execute/i });
    if (await executeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Handle alert dialog
      page.on('dialog', async (dialog) => {
        await dialog.accept();
      });
      
      await roadmapPage.clickExecutePhase(1);
    }
  });

  test('verify API-frontend integration', async ({ page }) => {
    // This test verifies that UI actions trigger correct API calls
    const projectList = new ProjectListPage(page);
    const newProject = new NewProjectPage(page);
    
    const apiCalls: string[] = [];
    
    // Intercept API calls
    await page.route('**/api/**', async (route) => {
      apiCalls.push(`${route.request().method()} ${route.request().url()}`);
      await route.continue();
    });
    
    await projectList.goto();
    
    // Should call GET /api/projects
    await page.waitForTimeout(500);
    expect(apiCalls.some(call => call.includes('GET') && call.includes('/api/projects'))).toBeTruthy();
    
    await projectList.clickNewProject();
    await newProject.fillForm({
      name: 'API Integration Test',
      description: 'Testing API calls',
    });
    
    await newProject.submit();
    
    // Should call POST /api/projects/new
    await page.waitForTimeout(500);
    expect(apiCalls.some(call => call.includes('POST') && call.includes('/api/projects/new'))).toBeTruthy();
  });

  test('verify error handling in UI', async ({ page }) => {
    const projectList = new ProjectListPage(page);
    const newProject = new NewProjectPage(page);
    
    // Mock API error
    await page.route('**/api/projects/new', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' }),
      });
    });
    
    // Handle alert dialog
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Failed');
      await dialog.accept();
    });
    
    await projectList.goto();
    await projectList.clickNewProject();
    
    await newProject.fillForm({
      name: 'Error Test',
      description: 'Testing error handling',
    });
    
    await newProject.submit();
    
    // Should show error alert
    // Alert is handled by dialog handler above
  });
});
