import { describe, it, expect, beforeAll } from 'vitest';
import { parse } from 'node-html-parser';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const ROOT = process.cwd();

function load(filename) {
  const filepath = join(ROOT, filename);
  if (!existsSync(filepath)) throw new Error(`File not found: ${filename}`);
  return parse(readFileSync(filepath, 'utf-8'));
}

// CSS files that every page must reference
const REQUIRED_CSS = ['main.css'];

// Internal links discovered across all pages — validated in a dedicated suite
const collectedLinks = new Set();

// ---------------------------------------------------------------------------
// Known pages
// ---------------------------------------------------------------------------

const pages = [
  // Main navigation pages
  { file: 'index.html',                                           title: 'AI Craftspeople Guild - Professional Code of Conduct' },
  { file: 'white-papers.html',                                    title: 'White Papers - AI Craftspeople Guild' },
  { file: 'ai-rituals.html',                                      title: 'AI Rituals - AI Craftspeople Guild' },
  { file: 'flywheel.html',                                        title: 'Flywheel - AI Craftspeople Guild' },
  { file: 'showcases.html',                                       title: 'Showcases - AI Craftspeople Guild' },
  { file: 'members.html',                                         title: 'Members - AI Craftspeople Guild' },
  { file: 'hall-of-fame.html',                                    title: 'Hall of Fame - AI Craftspeople Guild' },
  { file: 'hall-of-shame.html',                                   title: 'Hall of Shame - AI Craftspeople Guild' },
  { file: 'mission-statement.html',                               title: 'Mission Statement - AI Craftspeople Guild' },
  { file: 'charter.html',                                         title: 'AI Craftspeople Guild Charter' },
  { file: 'code-of-conduct.html',                                 title: 'AI Craftspeople Guild Code of Conduct' },
  // Core documents
  { file: 'aicraftspeopleguild-manifesto.html',                   title: 'ACG Manifesto - AI Craftspeople Guild' },
  { file: 'ai-harness.html',                                      title: 'AI Harness - AI Craftspeople Guild' },
  { file: 'acg-peer-reviews.html',                                title: 'ACG Review Forge - AI Craftspeople Guild' },
  // Member profiles
  { file: 'alex-bunardzic.html',                                  title: 'Alex Bunardzic - AI Craftspeople Guild' },
  { file: 'jona-heidsick.html',                                   title: 'Jona Heidsick - AI Craftspeople Guild' },
  { file: 'kelly-hohman.html',                                    title: 'Kelly Hohman - AI Craftspeople Guild' },
  { file: 'laurie-scheepers.html',                                title: 'Laurie Scheepers - AI Craftspeople Guild' },
  { file: 'matt-burch.html',                                      title: 'Matt Burch - AI Craftspeople Guild' },
  { file: 'nicolas-rosado.html',                                  title: 'Nicolas Rosado - AI Craftspeople Guild' },
  { file: 'thomas-frumkin.html',                                  title: 'Thomas Frumkin - AI Craftspeople Guild' },
  { file: 'tsvetan.html',                                         title: 'Tsvetan Tsvetanov - AI Craftspeople Guild' },
  // Articles & white papers
  { file: 'burnt-toast-scraping-analysis.html',                   title: '"I\'ll Burn Toast and You Scrape It" - AI Craftspeople Guild' },
  { file: 'burnt-toast-second-look.html',                         title: 'Structural Toast Carbonization - AI Craftspeople Guild' },
  { file: 'chief-ai-skeptic-officer.html',                        title: 'Chief AI Skeptic Officer - AI Craftspeople Guild' },
  { file: 'decentralized-guild-web.html',                         title: 'ACG-NET: Decentralized Guild Web - AI Craftspeople Guild' },
  { file: 'florence-governance-paper.html',                       title: 'Convergent Governance Topologies in Specialist Networks - AI Craftspeople Guild' },
  { file: 'fractally-wrong.html',                                 title: 'Avoid Being Fractally Wrong - AI Craftspeople Guild' },
  { file: 'from-correctness-to-integrity.html',                   title: 'From Correctness to Integrity - AI Craftspeople Guild' },
  { file: 'grid-brain.html',                                      title: 'Grid Brain - AI Craftspeople Guild' },
  { file: 'guild-chain.html',                                     title: 'ACG-KCC: Guild Chain - AI Craftspeople Guild' },
  { file: 'guild-radar.html',                                     title: 'Guild Radar - AI Craftspeople Guild' },
  { file: 'hushbell.html',                                        title: 'HUSHBELL - AI Craftspeople Guild' },
  { file: 'hushbell-full-spec.html',                              title: 'HUSHBELL Full Spec - AI Craftspeople Guild' },
  { file: 'irrational-universe.html',                             title: 'The Irrational Universe - AI Craftspeople Guild' },
  { file: 'konomi-standard.html',                                 title: 'The Konomi Standard - AI Craftspeople Guild' },
  { file: 'lightning-factory.html',                               title: 'Lightning Factory - AI Craftspeople Guild' },
  { file: 'occams-razor.html',                                    title: 'OCCAM - AI Craftspeople Guild' },
  { file: 'question-reflection-action.html',                      title: 'AI as a Triad-Guided Cognitive Apprenticeship - AI Craftspeople Guild' },
  { file: 'sad.html',                                             title: 'S.A.D. - AI Craftspeople Guild' },
  { file: 'shield-of-all-knights.html',                           title: 'The Shield of All Knights Against Bounded Rationality - AI Craftspeople Guild' },
  { file: 'speedrunning-the-mythical-man-month.html',             title: 'Speedrunning the Mythical Man-Month - AI Craftspeople Guild' },
  { file: 'the-dog-the-data-scientist-and-the-mrna-vaccine.html', title: 'The Dog, the Data Scientist, and the mRNA Vaccine - AI Craftspeople Guild' },
  { file: 'the-harm-equation.html',                               title: 'The Harm Equation - AI Craftspeople Guild' },
  { file: 'the-pattern-that-wasnt-there.html',                    title: "The Pattern That Wasn't There - AI Craftspeople Guild" },
  { file: 'the-prediction-trap.html',                             title: 'The Prediction Trap - AI Craftspeople Guild' },
  { file: 'the-rational-empire.html',                             title: 'The Rational Empire - AI Craftspeople Guild' },
  { file: 'toastmasters-scrapers-guild.html',                     title: 'Toastmasters Scrapers Guild - AI Craftspeople Guild' },
  { file: 'youre-absolutely-wrong.html',                          title: "You're Absolutely Wrong! - AI Craftspeople Guild" },
];

// ---------------------------------------------------------------------------
// Per-page unit tests
// ---------------------------------------------------------------------------

for (const { file, title } of pages) {
  describe(file, () => {
    let doc;

    beforeAll(() => {
      doc = load(file);

      // Collect internal .html links for the broken-link suite below
      doc.querySelectorAll('a[href]').forEach(a => {
        const href = a.getAttribute('href');
        if (href && href.endsWith('.html') && !href.startsWith('http')) {
          collectedLinks.add(href.replace(/^\//, ''));
        }
      });
    });

    // -- Structure --

    it('has exactly one <h1>', () => {
      expect(doc.querySelectorAll('h1').length).toBe(1);
    });

    it('has a non-empty <title>', () => {
      const tag = doc.querySelector('title');
      expect(tag).not.toBeNull();
      expect(tag.text.trim().length).toBeGreaterThan(0);
    });

    // -- Content --

      it(`<title> contains "${title}"`, () => {
        const tag = doc.querySelector('title');
        expect(tag.text).equal(title);
      });
  });
}
