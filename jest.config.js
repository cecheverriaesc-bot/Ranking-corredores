/**
 * @type {import('jest').Config}
 */
export default {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  testMatch: [
    '**/__tests__/**/*.test.[jt]s?(x)',
    '**/src/__tests__/**/*.test.[jt]s?(x)'
  ],
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'src/components/**/*.{ts,tsx}',
    'stores/**/*.{ts,tsx}',
    'src/hooks/**/*.{ts,tsx}',
    '!**/node_modules/**',
    '!**/vendor/**',
  ],
  transform: {
    '^.+\\.(ts|tsx)$': ['babel-jest', { configFile: './babel.config.json' }],
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
};
