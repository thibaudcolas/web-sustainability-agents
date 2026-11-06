module.exports = async (page) => {
  await page.setViewportSize({width: 1280, height: 800});
  const response = await page.goto('', {waitUntil: 'load', timeout: 45000});
  if (!response || !response.ok()) throw new Error('Initial document did not return a successful response');
  await page.waitForTimeout(3000);
  await page.addMilestone('initial: no interaction');
};
