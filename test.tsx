import { renderToString } from 'react-dom/server';
import React from 'react';
import App from './App';

// Mocks to allow it to run in Node
global.localStorage = {
    getItem: (key: string) => key === 'auth_token' ? 'yup' : null,
    setItem: () => { },
    removeItem: () => { },
    clear: () => { },
    length: 0,
    key: () => null
} as any;

global.fetch = async () => ({
    json: async () => ({ valid: true, user: { email: 'test@assetplan.cl' } }),
    ok: true
}) as any;

console.log("Rendering App...");
try {
    const html = renderToString(<App />);
    console.log("Success! Rendered HTML:", html.slice(0, 100) + "...");
} catch (e: any) {
    console.error("\n\n🔥 RENDER ERROR CAUGHT:\n", e.message);
    console.error("Stack trace:\n", e.stack);
}
