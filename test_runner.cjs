const express = require('express');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

app.use(express.json());
app.get('/api/auth/verify', (req, res) => res.json({ valid: true, user: { email: 'carlos.echeverria@assetplan.cl', role: 'admin' } }));
app.get('/api/v4_goals', (req, res) => res.json([]));

app.use(express.static(path.join(__dirname, 'dist')));

const server = app.listen(PORT, async () => {
    if (fs.existsSync('browser_log.txt')) fs.unlinkSync('browser_log.txt');
    console.log(`Server running on http://localhost:${PORT}`);
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    page.on('console', msg => fs.appendFileSync('browser_log.txt', `[${msg.type()}] ${msg.text()}\n`));
    page.on('pageerror', err => fs.appendFileSync('browser_log.txt', `[PAGE EXCEPTION Caught!]\n${err.message}\n${err.stack}\n`));

    try {
        await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
        await page.evaluate(() => localStorage.setItem('auth_token', 'test_token'));
        await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle0' });
        console.log('Done.');
    } catch (e) {
        console.error(e);
    } finally {
        await browser.close();
        server.close();
        process.exit(0);
    }
});
