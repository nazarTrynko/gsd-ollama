import { test, expect } from '@playwright/test';
import { ProjectListPage } from './page-objects/ProjectListPage';
import { NewProjectPage } from './page-objects/NewProjectPage';
import { ProjectViewPage } from './page-objects/ProjectViewPage';

test.describe('Project Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/projects', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ projects: [], total: 0 }),
        });
      }
    });
  });

  test('should display empty state when no projects', async ({ page }) => {
    const projectList = new ProjectListPage(page);
    await projectList.goto();
    
    await expect(projectList.heading).toBeVisible();
    await expect(projectList.emptyState).toBeVisible();
    await expect(projectList.newProjectButton).toBeVisible();
  });

  test('should navigate to new project page', async ({ page }) => {
    const projectList = new ProjectListPage(page);
    const newProject = new NewProjectPage(page);
    
    await projectList.goto();
    await projectList.clickNewProject();
    
    await expect(newProject.heading).toBeVisible();
    await expect(newProject.nameInput).toBeVisible();
    await expect(newProject.descriptionTextarea).toBeVisible();
  });

  test('should create a new project', async ({ page }) => {
    const projectList = new ProjectListPage(page);
    const newProject = new NewProjectPage(page);
    const projectView = new ProjectViewPage(page);
    
    // Mock project creation
    await page.route('**/api/projects/new', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: './projects/test-project',
          name: 'Test Project',
          description: 'A test project',
          path: './projects/test-project',
          exists: true,
        }),
      });
    });
    
    // Mock project get
    await page.route('**/api/projects/**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: './projects/test-project',
            name: 'Test Project',
            description: 'A test project',
            path: './projects/test-project',
            exists: true,
          }),
        });
      }
    });
    
    await projectList.goto();
    await projectList.clickNewProject();
    
    await newProject.fillForm({
      name: 'Test Project',
      description: 'A test project',
      initialTask: 'Set up testing',
    });
    
    await newProject.submit();
    await newProject.waitForRedirect();
    
    // Should redirect to project view
    await expect(page).toHaveURL(/\/projects\/.*/);
    await expect(projectView.projectName).toContainText('Test Project');
  });

  test('should validate required fields', async ({ page }) => {
    const newProject = new NewProjectPage(page);
    
    await newProject.goto();
    
    // Try to submit without filling required fields
    await newProject.submit();
    
    // HTML5 validation should prevent submission
    const nameInput = newProject.nameInput;
    const descriptionInput = newProject.descriptionTextarea;
    
    await expect(nameInput).toHaveAttribute('required');
    await expect(descriptionInput).toHaveAttribute('required');
  });

  test('should display project list with projects', async ({ page }) => {
    // Mock projects list
    await page.route('**/api/projects', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          projects: [
            {
              id: './projects/project1',
              name: 'Project 1',
              description: 'First project',
              path: './projects/project1',
              exists: true,
            },
            {
              id: './projects/project2',
              name: 'Project 2',
              description: 'Second project',
              path: './projects/project2',
              exists: true,
            },
          ],
          total: 2,
        }),
      });
    });
    
    const projectList = new ProjectListPage(page);
    await projectList.goto();
    
    await projectList.waitForProjects();
    const count = await projectList.getProjectCount();
    expect(count).toBeGreaterThan(0);
  });

  test('should navigate to project view from list', async ({ page }) => {
    // Mock projects list
    await page.route('**/api/projects', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          projects: [
            {
              id: './projects/test-project',
              name: 'Test Project',
              description: 'Test description',
              path: './projects/test-project',
              exists: true,
            },
          ],
          total: 1,
        }),
      });
    });
    
    // Mock project get
    await page.route('**/api/projects/**', async (route) => {
      if (route.request().method() === 'GET' && !route.request().url().includes('/roadmap')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: './projects/test-project',
            name: 'Test Project',
            description: 'Test description',
            path: './projects/test-project',
            exists: true,
          }),
        });
      }
    });
    
    const projectList = new ProjectListPage(page);
    const projectView = new ProjectViewPage(page);
    
    await projectList.goto();
    await projectList.clickProject('Test Project');
    
    await expect(page).toHaveURL(/\/projects\/.*/);
    await expect(projectView.projectName).toContainText('Test Project');
  });
});
