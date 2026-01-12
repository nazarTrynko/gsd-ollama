import { test, expect } from '@playwright/test';
import { ProjectViewPage } from './page-objects/ProjectViewPage';
import { RoadmapPage } from './page-objects/RoadmapPage';

test.describe('Roadmap Workflow', () => {
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
  });

  test('should display no roadmap message initially', async ({ page }) => {
    // Mock roadmap 404
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/roadmap`, async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Roadmap not found' }),
      });
    });
    
    const projectView = new ProjectViewPage(page);
    await projectView.goto(testProjectId);
    
    await projectView.waitForProject();
    await expect(projectView.noRoadmapMessage).toBeVisible();
    await expect(projectView.createRoadmapButton).toBeVisible();
  });

  test('should create roadmap', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    // Mock roadmap creation
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/roadmap`, async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            roadmap: `# Roadmap

## Milestone v1.0

### Phase 1: Setup
Initialize project structure and development environment.

### Phase 2: Core Features
Implement main functionality.`,
            project_id: testProjectId,
          }),
        });
      } else {
        // GET request
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            roadmap: `# Roadmap

## Milestone v1.0

### Phase 1: Setup
Initialize project structure and development environment.

### Phase 2: Core Features
Implement main functionality.`,
            project_id: testProjectId,
          }),
        });
      }
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    
    // Click create roadmap button
    await projectView.clickCreateRoadmap();
    
    // Wait for roadmap to appear
    await projectView.waitForRoadmap();
    
    // Verify roadmap is displayed
    await expect(page.getByText('Roadmap')).toBeVisible();
    await expect(page.getByText('Phase 1')).toBeVisible();
  });

  test('should display roadmap with phases', async ({ page }) => {
    // Mock roadmap get
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/roadmap`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          roadmap: `# Roadmap

## Milestone v1.0

### Phase 1: Setup
Initialize project structure.

### Phase 2: Development
Implement core features.

### Phase 3: Testing
Add tests and polish.`,
          project_id: testProjectId,
        }),
      });
    });
    
    const projectView = new ProjectViewPage(page);
    const roadmapPage = new RoadmapPage(page);
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    
    // Wait for roadmap to load
    await projectView.waitForRoadmap();
    
    // Verify phases are displayed
    const phaseCount = await roadmapPage.getPhaseCount();
    expect(phaseCount).toBeGreaterThan(0);
    
    // Verify phase names are visible
    await expect(page.getByText('Phase 1: Setup')).toBeVisible();
  });

  test('should handle roadmap creation error', async ({ page }) => {
    const projectView = new ProjectViewPage(page);
    
    // Mock roadmap creation failure
    await page.route(`**/api/projects/${encodeURIComponent(testProjectId)}/roadmap`, async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Failed to create roadmap' }),
        });
      }
    });
    
    // Mock alert dialog
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Failed');
      await dialog.accept();
    });
    
    await projectView.goto(testProjectId);
    await projectView.waitForProject();
    
    await projectView.clickCreateRoadmap();
    
    // Should show error (alert in this case)
    // The alert is handled by the dialog handler above
  });
});
