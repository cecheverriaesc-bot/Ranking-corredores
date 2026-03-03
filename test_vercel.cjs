const puppeteer = require('puppeteer');

(async () => {
    console.log('Lanzando Puppeteer...');
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    page.on('console', msg => console.log('[Console]', msg.type(), msg.text()));
    page.on('pageerror', error => console.error('[Error]', error.message));

    console.log('Navegando a Vercel...');
    await page.goto('https://ranking-2026.vercel.app');

    await page.waitForSelector('input', { timeout: 10000 });

    console.log('Ingresando credentials...');
    const inputs = await page.$$('input');
    await inputs[0].type('carlos.echeverria');
    await inputs[1].type('1234');

    // click login by finding the button inside the form
    const btn = await page.$('button[type="submit"]');
    if (btn) await btn.click();
    else console.log('Boton no encontrado');

    console.log('Esperando redirect...');
    await new Promise(r => setTimeout(r, 6000));

    const html = await page.evaluate(() => document.body.innerHTML);
    if (!html.includes('Total') && html.length < 500) {
        console.log('PANTALLA BLANCA:', html);
    } else {
        console.log('Exito, body length:', html.length);
    }
    await browser.close();
})();
