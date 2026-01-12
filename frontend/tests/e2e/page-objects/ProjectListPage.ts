import { Page, Locator } from '@playwright/test';

export class ProjectListPage {
  readonly page: Page;
  readonly newProjectButton: Locator;
  readonly projectCards: Locator;
  readonly emptyState: Locator;
  readonly heading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.newProjectButton = page.getByRole('link', { name: 'New Project' });
    this.projectCards = page.locator('[class*="grid"] a');
    this.emptyState = page.getByText('No projects yet');
    this.heading = page.getByRole('heading', { name: 'Projects' });
  }

  async goto() {
    await this.page.goto('/');
  }

  async clickNewProject() {
    await this.newProjectButton.click();
  }

  async getProjectCount(): Promise<number> {
    return await this.projectCards.count();
  }

  async clickProject(name: string) {
    await this.page.getByRole('heading', { name }).click();
  }

  async waitForProjects() {
    await this.page.waitForSelector('[class*="grid"]', { state: 'visible' });
  }
}
