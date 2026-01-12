import { Page, Locator } from '@playwright/test';

export class RoadmapPage {
  readonly page: Page;
  readonly phaseCards: Locator;
  readonly planButtons: Locator;
  readonly executeButtons: Locator;

  constructor(page: Page) {
    this.page = page;
    this.phaseCards = page.locator('[class*="phase"]');
    this.planButtons = page.getByRole('button', { name: /Plan/i });
    this.executeButtons = page.getByRole('button', { name: /Execute/i });
  }

  async getPhaseCount(): Promise<number> {
    return await this.phaseCards.count();
  }

  async clickPlanPhase(phaseNumber: number) {
    const planButton = this.page.getByRole('button', { name: new RegExp(`Plan.*Phase ${phaseNumber}`, 'i') });
    await planButton.click();
  }

  async clickExecutePhase(phaseNumber: number) {
    const executeButton = this.page.getByRole('button', { name: new RegExp(`Execute.*Phase ${phaseNumber}`, 'i') });
    await executeButton.click();
  }

  async waitForTasks() {
    await this.page.waitForSelector('text=Task', { state: 'visible', timeout: 10000 });
  }
}
