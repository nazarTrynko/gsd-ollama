import { Page, Locator } from '@playwright/test';

export class ProjectViewPage {
  readonly page: Page;
  readonly projectName: Locator;
  readonly projectDescription: Locator;
  readonly createRoadmapButton: Locator;
  readonly roadmapView: Locator;
  readonly noRoadmapMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.projectName = page.locator('h1').first();
    this.projectDescription = page.locator('p.text-gray-600').first();
    this.createRoadmapButton = page.getByRole('button', { name: /Create Roadmap/i });
    this.roadmapView = page.locator('[class*="roadmap"]');
    this.noRoadmapMessage = page.getByText('No roadmap yet');
  }

  async goto(projectId: string) {
    await this.page.goto(`/projects/${encodeURIComponent(projectId)}`);
  }

  async waitForProject() {
    await this.page.waitForSelector('h1', { state: 'visible' });
  }

  async clickCreateRoadmap() {
    await this.createRoadmapButton.click();
  }

  async waitForRoadmap() {
    await this.page.waitForSelector('text=Phase', { state: 'visible', timeout: 30000 });
  }

  async getProjectName(): Promise<string | null> {
    return await this.projectName.textContent();
  }
}
