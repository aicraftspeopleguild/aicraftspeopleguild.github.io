import { test, expect } from '@playwright/test';

// FIXED list of known pages on the site.
// If a page is deleted or renamed, the test fails → regression detected.
// To add a new page to the scope, add it manually here.
const knownPages = [
  { path: '/index.html',                                        name: 'index' },
  { path: '/white-papers.html',                                 name: 'white-papers' },
  { path: '/ai-rituals.html',                                   name: 'ai-rituals' },
  { path: '/flywheel.html',                                     name: 'flywheel' },
  { path: '/showcases.html',                                    name: 'showcases' },
  { path: '/members.html',                                      name: 'members' },
  { path: '/hall-of-fame.html',                                 name: 'hall-of-fame' },
  { path: '/hall-of-shame.html',                                name: 'hall-of-shame' },
  { path: '/mission-statement.html',                            name: 'mission-statement' },
  { path: '/charter.html',                                      name: 'charter' },
  { path: '/code-of-conduct.html',                              name: 'code-of-conduct' },
  { path: '/aicraftspeopleguild-manifesto.html',                name: 'manifesto' },
  { path: '/ai-harness.html',                                   name: 'ai-harness' },
  { path: '/acg-peer-reviews.html',                             name: 'acg-peer-reviews' },
  { path: '/alex-bunardzic.html',                               name: 'alex-bunardzic' },
  { path: '/jona-heidsick.html',                                name: 'jona-heidsick' },
  { path: '/kelly-hohman.html',                                 name: 'kelly-hohman' },
  { path: '/laurie-scheepers.html',                             name: 'laurie-scheepers' },
  { path: '/matt-burch.html',                                   name: 'matt-burch' },
  { path: '/nicolas-rosado.html',                               name: 'nicolas-rosado' },
  { path: '/thomas-frumkin.html',                               name: 'thomas-frumkin' },
  { path: '/tsvetan.html',                                      name: 'tsvetan' },
  { path: '/burnt-toast-scraping-analysis.html',                name: 'burnt-toast-scraping-analysis' },
  { path: '/burnt-toast-second-look.html',                      name: 'burnt-toast-second-look' },
  { path: '/chief-ai-skeptic-officer.html',                     name: 'chief-ai-skeptic-officer' },
  { path: '/decentralized-guild-web.html',                      name: 'decentralized-guild-web' },
  { path: '/florence-governance-paper.html',                    name: 'florence-governance-paper' },
  { path: '/fractally-wrong.html',                              name: 'fractally-wrong' },
  { path: '/from-correctness-to-integrity.html',                name: 'from-correctness-to-integrity' },
  { path: '/grid-brain.html',                                   name: 'grid-brain' },
  { path: '/guild-chain.html',                                  name: 'guild-chain' },
  { path: '/guild-radar.html',                                   name: 'guild-radar' },
  { path: '/hushbell.html',                                     name: 'hushbell' },
  { path: '/hushbell-full-spec.html',                           name: 'hushbell-full-spec' },
  { path: '/irrational-universe.html',                          name: 'irrational-universe' },
  { path: '/konomi-standard.html',                              name: 'konomi-standard' },
  { path: '/lightning-factory.html',                            name: 'lightning-factory' },
  { path: '/occams-razor.html',                                 name: 'occams-razor' },
  { path: '/question-reflection-action.html',                   name: 'question-reflection-action' },
  { path: '/sad.html',                                          name: 'sad' },
  { path: '/shield-of-all-knights.html',                        name: 'shield-of-all-knights' },
  { path: '/speedrunning-the-mythical-man-month.html',          name: 'speedrunning-the-mythical-man-month' },
  { path: '/the-dog-the-data-scientist-and-the-mrna-vaccine.html', name: 'the-dog-the-data-scientist-and-the-mrna-vaccine' },
  { path: '/the-harm-equation.html',                            name: 'the-harm-equation' },
  { path: '/the-pattern-that-wasnt-there.html',                 name: 'the-pattern-that-wasnt-there' },
  { path: '/the-prediction-trap.html',                          name: 'the-prediction-trap' },
  { path: '/the-rational-empire.html',                          name: 'the-rational-empire' },
  { path: '/toastmasters-scrapers-guild.html',                  name: 'toastmasters-scrapers-guild' },
  { path: '/youre-absolutely-wrong.html',                       name: 'youre-absolutely-wrong' },
];

for (const { path, name } of knownPages) {
  test(`${name} — responds with 200`, async ({ page }) => {
    const response = await page.goto(path);

    // Page must exist (not deleted, not renamed)
    expect(response.status(), `${path} returned ${response.status()} instead of 200`).toBe(200);
  });

  test(`${name} — no JavaScript errors`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));

    await page.goto(path);
    await page.waitForLoadState('networkidle');

    expect(errors, `JS errors on ${path}: ${errors.join(', ')}`).toHaveLength(0);
  });

}
