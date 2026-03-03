const express = require('express');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const app = express();

const PORT = 3000;

// Mocks for API
app.use(express.json());
app.get('/api/auth/verify', (req, res) => {
    res.json({ valid: true, user: { email: 'carlos.echeverria@assetplan.cl', role: 'admin' } });
});
app.get('/api/v4_goals', (req, res) => {
    res.json([]);
});

// Serve the production build
app.use(express.static(path.join(__dirname, 'dist')));

// Fallback removed

const server = app.listen(PORT, async () => {
    console.log(`Server running on http://localhost:${PORT}`);

    console.log('Launching Puppeteer...');
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    // Capture console output
    page.on('console', msg => {
        const text = msg.text();
        fs.appendFileSync('browser_log.txt', `[${msg.type()}] ${text}\n`);
    });

    // Capture uncaught exceptions
    page.on('pageerror', err => {
        fs.appendFileSync('browser_log.txt', `[PAGE EXCEPTION Caught!]\n${err.message}\n${err.stack}\n`);
    });

    try {
        // Go once to set storage
        await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'domcontentloaded' });
        await page.evaluate(() => {
            localStorage.setItem('auth_token', 'test_token');
        });

        console.log('Setted auth_token, reloading to force dashboard load...');
        await page.goto(`http://localhost:${PORT}/`, { waitUntil: 'networkidle0' });

        console.log('Page loaded completely. Check above for errors.');
    } catch (e) {
        console.error("Puppeteer Script Error:", e);
    } finally {
        await browser.close();
        server.close();
        process.exit(0);
    }
});
