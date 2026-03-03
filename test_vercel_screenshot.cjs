const puppeteer = require('puppeteer');

(async () => {
    console.log('Lanzando Puppeteer screenshot...');
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    await page.goto('https://ranking-2026.vercel.app');
    await page.waitForSelector('input', { timeout: 10000 });

    const inputs = await page.$$('input');
    await inputs[0].type('carlos.echeverria');
    await inputs[1].type('1234');

    const btn = await page.$('button[type="submit"]');
    if (btn) await btn.click();

    await new Promise(r => setTimeout(r, 6000));
    await page.screenshot({ path: 'C:/Users/assetplan/.gemini/antigravity/brain/7a57ba6f-40b8-40d8-9715-c420888963be/media_success_vercel.png' });

    await browser.close();
    console.log('Captura tomada');
})();
