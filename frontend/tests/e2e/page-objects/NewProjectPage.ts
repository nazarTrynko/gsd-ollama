import { Page, Locator } from '@playwright/test';

export class NewProjectPage {
  readonly page: Page;
  readonly nameInput: Locator;
  readonly descriptionTextarea: Locator;
  readonly initialTaskInput: Locator;
  readonly createButton: Locator;
  readonly cancelButton: Locator;
  readonly heading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: 'New Project' });
    this.nameInput = page.getByLabel('Project Name *');
    this.descriptionTextarea = page.getByLabel('Description *');
    this.initialTaskInput = page.getByLabel('Initial Task (Optional)');
    this.createButton = page.getByRole('button', { name: /Create Project/i });
    this.cancelButton = page.getByRole('button', { name: 'Cancel' });
  }

  async goto() {
    await this.page.goto('/projects/new');
  }

  async fillForm(data: { name: string; description: string; initialTask?: string }) {
    await this.nameInput.fill(data.name);
    await this.descriptionTextarea.fill(data.description);
    if (data.initialTask) {
      await this.initialTaskInput.fill(data.initialTask);
    }
  }

  async submit() {
    await this.createButton.click();
  }

  async cancel() {
    await this.cancelButton.click();
  }

  async waitForLoading() {
    await this.page.waitForSelector('text=Creating...', { state: 'visible' });
  }

  async waitForRedirect() {
    await this.page.waitForURL(/\/projects\/.*/, { timeout: 10000 });
  }
}
