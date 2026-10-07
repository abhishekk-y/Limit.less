import { expect, Page, test } from '@playwright/test';

async function register(page: Page, tenant = 'individual') {
  await page.goto('/register');
  await page.evaluate(() => localStorage.removeItem('skillsetu.navigation.v1'));
  await page.getByLabel('Your name').fill('Journey Tester');
  await page.getByRole('combobox', { name: 'Workspace' }).selectOption(tenant);
  await page.getByLabel('Email address').fill(`journey-${tenant}-${Date.now()}@example.com`);
  await page.getByRole('textbox', { name: /^Password/ }).fill('Journey-Test-Password-2026');
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Create workspace' }).click();
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Journey');
}

async function expandSidebar(page: Page) {
  await page.getByRole('complementary', { name: 'Workspace sidebar' }).hover();
}

test('resume to mission to evidence to approved demo application', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await register(page);
  await page.screenshot({ path: 'test-results/overview-desktop.png', fullPage: true, animations: 'disabled' });
  await page.getByRole('link', { name: 'Document Vault', exact: true }).click();
  await page.getByLabel('Choose résumé').setInputFiles({ name: 'resume.txt', mimeType: 'text/plain', buffer: Buffer.from('I studied Python, SQL, Git and Linux during college and built a small project to practice these skills.') });
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Upload and build my Twin' }).click();
  await expect(page.getByRole('status')).toContainText('Résumé saved');
  await expect(page.getByRole('heading', { name: 'Résumé uploaded: resume.txt' })).toBeVisible();
  await expect(page.getByRole('link', {name:'Match live jobs', exact:true})).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'test-results/resume-upload.png', fullPage: true, animations: 'disabled' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'test-results/resume-upload-readme.png', animations: 'disabled' });
  await page.getByRole('link', { name: 'Talent Twin', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Python', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Career GPS', exact: true }).click();
  await page.getByRole('button', { name: 'Build my roadmap' }).click();
  await page.getByRole('button', { name: 'Start project mission' }).first().click();
  await expect(page.getByRole('status')).toContainText('mission is ready');
  await page.getByRole('link', { name: 'Skill Missions', exact: true }).click();
  await page.getByLabel('Original project link').fill('https://github.com/demo-user/original-project');
  await page.getByLabel('What did you build?').fill('Created an original demonstration project with documented changes and a repeatable test workflow.');
  await page.getByLabel('Hours spent').fill('6');
  await page.getByRole('button', { name: 'Complete mission', exact: true }).click();
  await expect(page.getByText('Evidence added to your Talent Twin.')).toBeVisible();
  await page.getByRole('link', { name: 'Opportunities', exact: true }).click();
  await page.getByRole('button', { name: 'Prepare application' }).first().click();
  await expect(page).toHaveURL('/application-tracker');
  await expect(page.getByText('Evidence guard: PASS')).toBeVisible();
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Approve demo application' }).click();
  await expect(page.getByText('Submitted · demo')).toBeVisible();
  await page.reload();
  await expect(page.getByText('Submitted · demo')).toBeVisible();
  await page.screenshot({ path: 'test-results/application-desktop.png', fullPage: true, animations: 'disabled' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'test-results/application-desktop-readme.png', animations: 'disabled' });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('aside')).not.toBeInViewport();
  await page.screenshot({ path: 'test-results/application-mobile.png', fullPage: true, animations: 'disabled' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
  await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
  await page.getByRole('link', { name: 'Overview', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Journey');
  expect(errors).toEqual([]);
});

test('organization imports workforce and composes a team', async ({ page }) => {
  await register(page, 'organization');
  await page.getByRole('link', { name: 'Workforce', exact: true }).click();
  await page.getByLabel('Employee CSV').fill('employee_id,name,role,skills\nE1,Asha,Engineer,python:80;sql:70\nE2,Meera,Analyst,sql:85');
  await page.getByRole('button', { name: 'Save workforce' }).click();
  await expect(page.getByRole('status')).toContainText('2 employees saved');
  await page.getByRole('button', { name: 'Compose a team of up to 3' }).click();
  await expect(page.getByText('Suggested team: Asha')).toBeVisible();
  await page.screenshot({ path: 'test-results/workforce-desktop.png', fullPage: true, animations: 'disabled' });
});

test('institution saves a curriculum and computes its gaps', async ({ page }) => {
  await register(page, 'institution');
  await page.getByRole('link', { name: 'Curriculum', exact: true }).click();
  await page.getByLabel('Program or course name').fill('Computer Science Demo');
  await page.getByRole('checkbox', { name: 'Python', exact: true }).check();
  await page.getByRole('checkbox', { name: 'SQL', exact: true }).check();
  await page.getByRole('button', { name: 'Analyze curriculum' }).click();
  await expect(page.getByRole('heading', { name: 'Computer Science Demo' })).toBeVisible();
  await expect(page.getByText('Skills to consider:')).toContainText('git');
  await page.screenshot({ path: 'test-results/curriculum-desktop.png', fullPage: true, animations: 'disabled' });
});


test('assessment evidence and revocable public passport', async ({ page, browser }) => {
  await register(page);
  await page.getByRole('link', { name: 'Assessments', exact: true }).click();
  await page.getByRole('heading', { name: 'Python foundations', exact: true }).locator('..').getByRole('button', { name: 'Skill sprint' }).click();
  await page.getByRole('button', { name: /^practice Accessible/ }).click();
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Begin practice' }).click();
  const correct = ['set', 'Resource cleanup', 'KeyError', 'value is None'];
  for (let i = 0; i < 4; i++) {
    for (const choice of correct) {
      const option = page.getByRole('radio', { name: choice, exact: true });
      if (await option.count()) { await option.check(); break; }
    }
    if (i < 3) await page.getByRole('button', { name: 'Next question' }).click();
  }
  await page.getByRole('button', { name: 'Submit assessment' }).click();
  await expect(page.getByText('4 of 4 correct')).toBeVisible();
  await page.getByRole('button', { name: 'Back to assessments' }).click();
  await page.getByRole('link', { name: 'Skill Passport', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Create share link' })).toBeDisabled();
  await page.getByLabel('I consent to sharing this snapshot with anyone who has the link.').check();
  await page.getByRole('button', { name: 'Create share link' }).click();
  const link = page.getByLabel('Your private share link');
  await expect(link).toBeVisible();
  const publicContext = await browser.newContext();
  const publicPage = await publicContext.newPage();
  await publicPage.goto(await link.inputValue());
  await expect(publicPage.getByRole('heading', { level: 1 })).toContainText('Journey Tester');
  await expect(publicPage.getByRole('heading', { name: 'Python', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Revoke access' }).click();
  await expect(page.getByRole('button', { name: 'Revoke access' })).toHaveCount(0);
  await publicPage.reload();
  await expect(publicPage.getByRole('heading', { name: 'Python', exact: true })).toHaveCount(0);
  await expect(publicPage.getByRole('alert')).toBeVisible();
  await publicContext.close();
});



test('categorized navigation remembers preferences and supports tool search', async ({ page }) => {
  await register(page);
  await expandSidebar(page);
  await page.getByRole('button', { name: 'Learn & grow', exact: true }).click();
  await expect(page.getByRole('link', { name: 'Assessments', exact: true })).toBeHidden();
  await page.reload();
  await expandSidebar(page);
  await expect(page.getByRole('button', { name: 'Learn & grow', exact: true })).toHaveAttribute('aria-expanded', 'false');
  await page.getByRole('button', { name: 'Collapse sidebar', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Expand sidebar', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Assessments', exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('button', { name: 'Expand sidebar', exact: true })).toBeVisible();
  await page.screenshot({ path: 'test-results/navigation-compact.png', fullPage: true, animations: 'disabled' });
  await page.keyboard.press('Control+k');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Find a workspace tool' })).toBeFocused();
  await page.getByRole('textbox', { name: 'Find a workspace tool' }).fill('privacy');
  await page.getByRole('dialog').getByRole('link', { name: /Settings & privacy/ }).click();
  await expect(page).toHaveURL('/settings');
  await expect(page.getByRole('dialog')).toBeHidden();
  await expandSidebar(page);
  await page.getByRole('button', { name: 'Learn & grow', exact: true }).click();
  await page.screenshot({ path: 'test-results/navigation-expanded.png', fullPage: true, animations: 'disabled' });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('aside')).not.toBeInViewport();
  await page.getByRole('button', { name: 'Open navigation', exact: true }).click();
  await expect(page.getByRole('link', { name: 'Limit.less home', exact: true })).toBeFocused();
  await page.screenshot({ path: 'test-results/navigation-mobile.png', fullPage: true, animations: 'disabled' });
  await page.keyboard.press('Escape');
  await expect(page.getByRole('button', { name: 'Open navigation', exact: true })).toBeFocused();
  await expect(page.locator('aside')).not.toBeInViewport();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});



test('assessment studio stays readable in dark system mode and records fullscreen exit', async ({ page, context }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await context.grantPermissions(['camera', 'microphone']);
  await register(page);
  await expect(page.getByText('Your job hunt progress', { exact: true })).toBeVisible();
  await expect(page.getByText('Saved roles', { exact: true })).toBeVisible();
  await expect(page.getByText('Applications & saved roles', { exact: true })).toBeVisible();
  await expandSidebar(page);
  await page.getByRole('link', { name: 'Assessments', exact: true }).click();
  const heading = page.getByRole('heading', { name: 'Python foundations', exact: true });
  await expect(heading).toHaveCSS('color', 'rgb(2, 6, 23)');
  await expect(heading.locator('..')).toHaveCSS('background-color', 'rgb(255, 255, 255)');
  await page.screenshot({ path: 'test-results/assessment-studio.png', fullPage: true, animations: 'disabled' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'test-results/assessment-studio-readme.png', animations: 'disabled' });
  await heading.locator('..').getByRole('button', { name: 'Monitored check' }).click();
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Check camera & microphone' }).click();
  await expect(page.getByText('Devices connected', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Enter fullscreen & begin' }).click();
  await expect(page.getByRole('dialog', { name: 'Assessment attempt' })).toBeVisible();
  await page.screenshot({ path: 'test-results/assessment-attempt.png', fullPage: true, animations: 'disabled' });
  await page.evaluate(() => document.exitFullscreen());
  await expect(page.getByText('A session interruption was recorded.', { exact: false })).toBeVisible();
  await page.getByRole('button', { name: 'End attempt and save current answers' }).click();
  await expect(page.getByText('0 of 4 correct · review required')).toBeVisible();
  await expect(page.getByText('This attempt was saved without adding skill evidence.', { exact: false })).toBeVisible();
});

test('social studio saves private drafts and live-job pages expose connector limits', async ({ page }) => {
  await register(page);
  await expandSidebar(page);
  await page.getByRole('link', { name: 'Social Studio', exact: true }).click();
  await page.getByLabel('Draft title').fill('What I built this week');
  await page.getByLabel('Your reviewed text', { exact: true }).fill('I built a small Python project and documented what I learned. Here are the changes I would make next time.');
  await page.getByLabel('Related LinkedIn post').fill('https://www.linkedin.com/posts/test-activity-7448808898326654978-abcd');
  await page.getByRole('button', { name: 'Save draft' }).click();
  await expect(page.getByRole('heading', { name: 'What I built this week' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'What I built this week' })).toBeVisible();
  await page.getByRole('link', { name: 'Live Jobs', exact: true }).click();
  await expect(page.getByLabel('Company board name')).toBeVisible();
  await page.getByRole('link', { name: 'Open Apply Queue' }).click();
  await expect(page.getByRole('heading', { name: 'Auto-Apply with Gemini' })).toBeVisible();
});

test('Limit.less landing supports reduced motion and mobile layout', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark', reducedMotion: 'reduce' });
  await page.goto('/');
  await expect(page).toHaveTitle('Limit.less');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('BIG PLANS.');
  await expect(page.locator('.limit-sculpture')).toHaveCSS('animation-name', 'none');
  await page.screenshot({ path: 'test-results/landing-limitless-desktop.png', fullPage: true, animations: 'disabled' });
  await page.setViewportSize({ width: 390, height: 844 });
  const overflow = await page.evaluate(() => ({
    viewport: window.innerWidth,
    document: document.documentElement.scrollWidth,
    elements: Array.from(document.querySelectorAll<HTMLElement>('body *'))
      .map(element => ({ tag: element.tagName, text: (element.innerText || '').slice(0, 32), left: Math.round(element.getBoundingClientRect().left), right: Math.round(element.getBoundingClientRect().right), width: Math.round(element.getBoundingClientRect().width) }))
      .filter(item => item.right > window.innerWidth + 1 || item.left < -1)
      .slice(0, 10),
  }));
  expect(overflow.document <= overflow.viewport, JSON.stringify(overflow)).toBeTruthy();
  await page.screenshot({ path: 'test-results/landing-limitless-mobile.png', fullPage: true, animations: 'disabled' });
  await page.getByRole('link', { name: 'Make your next move' }).click();
  await expect(page).toHaveURL('/register');
});

test('Limit.less sign-in and registration share the Y2K brand and remain accessible', async ({ page }) => {
  await page.goto('/login');
  await expect(page.getByRole('heading', { level: 1 })).toContainText('starts with proof');
  await expect(page.getByRole('heading', { name: 'Good to have you back.' })).toBeVisible();
  await page.getByRole('link', { name: 'Create an account' }).click();
  await expect(page).toHaveURL('/register');
  await expect(page.getByRole('heading', { name: 'Make room for what’s next.' })).toBeVisible();
  const password = page.getByRole('textbox', { name: 'Password' });
  await password.fill('Y2K-career-demo-2026!');
  await expect(password).toHaveValue('Y2K-career-demo-2026!');
  await page.getByRole('button', { name: 'Show password' }).click();
  await expect(page.getByRole('textbox', { name: 'Password' })).toHaveValue('Y2K-career-demo-2026!');
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy();
});

test('automatic sidebar expands on hover and becomes a dark rail when leaving', async ({ page }) => {
  await register(page);
  const sidebar = page.getByRole('complementary', { name: 'Workspace sidebar' });
  await expect(sidebar).toHaveAttribute('data-collapsed', 'true');
  await expect(sidebar).toHaveCSS('background-color', 'rgb(41, 37, 48)');
  await page.screenshot({ path: 'test-results/sidebar-dark-rail.png', fullPage: true, animations: 'disabled' });
  await sidebar.hover();
  await expect(sidebar).toHaveAttribute('data-collapsed', 'false');
  await expect(sidebar).toHaveCSS('background-color', 'rgb(255, 255, 255)');
  await page.getByRole('heading', { level: 1 }).hover();
  await page.reload();
  await expect(sidebar).toHaveAttribute('data-auto-collapse', 'true');
  await page.getByRole('link', { name: 'Limit.less home' }).focus();
  await expect(sidebar).toHaveAttribute('data-collapsed', 'false');
});

test('hackathon dashboard exposes demo applications and SAS workspace without live submission', async ({ page }) => {
  await register(page);
  await page.goto('/settings');
  await page.getByRole('button', { name: 'Hybrid · live + hackathon', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Hybrid · live + hackathon', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', {name:'From source data to skill insights'})).toBeVisible();
  await expect(page.getByRole('heading', {name:'Your skills in today’s job listings'})).toBeVisible();
  await page.goto('/settings');
  await page.getByRole('button', { name: 'Hackathon dataset view', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Hackathon dataset view', exact: true })).toHaveAttribute('aria-pressed', 'true');
  await expect(page.getByRole('link', { name: 'Open SAS Viya for Learners', exact: true })).toHaveAttribute('href', 'https://vle.sas.com/vfl');
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', {name:'From source data to skill insights'})).toBeVisible();
  await expect(page.getByRole('link', { name: 'Try the demo application flow · no employer contact' })).toBeVisible();
  await page.screenshot({ path: 'test-results/hackathon-dashboard.png', fullPage: true, animations: 'disabled' });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: 'test-results/hackathon-dashboard-readme.png', animations: 'disabled' });
  await page.getByRole('link', { name: 'Try the demo application flow · no employer contact' }).click();
  await expect(page.getByText('Approval records a demo submission; nothing is sent to an employer.', {exact:false})).toBeVisible();
});

test('resume skills show demand and missing skills use the current document', async ({ page }) => {
  await register(page);
  await page.route('**/api/v1/market/live', route => route.fulfill({json:{active_postings:10,source_refreshed_at:'2026-10-07T20:00:00Z',skills:[{id:'python',name:'Python',postings:4,share_percent:40,change:2},{id:'sql',name:'SQL',postings:6,share_percent:60,change:null}]}}));
  await page.goto('/vault');
  await page.getByLabel('Choose résumé').setInputFiles({name:'demand-resume.txt',mimeType:'text/plain',buffer:Buffer.from('I built Python applications and documented my project experience.')});
  await page.getByRole('checkbox').check();
  await page.getByRole('button',{name:'Upload and build my Twin'}).click();
  await expect(page.getByRole('heading',{name:'Résumé uploaded: demand-resume.txt'})).toBeVisible();
  await expect(page.getByText('40% demand',{exact:true}).first()).toBeVisible();
  await expect(page.getByText('4 of 10 job listings',{exact:true}).first()).toBeVisible();
  await expect(page.getByText('Change: +2 listings',{exact:true}).first()).toBeVisible();
  const missing=page.getByRole('textbox',{name:'In-demand skills missing from this résumé'}).first();
  await expect(missing).toHaveValue('SQL: 60% demand · 6 of 10 listings');
  await expect(missing).toHaveAttribute('readonly','');
  await page.getByRole('heading', {name:'Extracted skills & job demand'}).first().locator('..').screenshot({path:'test-results/resume-skill-demand.png',animations:'disabled'});
});

