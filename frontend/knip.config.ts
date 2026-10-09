import type { KnipConfig } from 'knip';

/**
 * Knip finds files, exports and dependencies nothing references any more.
 *
 * Run it with `npm run knip`. The route tree has to be generated first (the
 * script does that), otherwise every route file looks unreachable. Entry points
 * come from knip's Vite and Vitest plugins.
 */
const config: KnipConfig = {
  // Registered by src/main.tsx at runtime, not imported.
  entry: ['public/sw.js'],
  // shadcn/ui primitives are vendored whole; their unused parts are fine.
  ignoreIssues: { 'src/components/ui/**': ['exports'] },
  ignore: [
    // Regenerated wholesale from the backend's OpenAPI schema. Orval emits a
    // hook for every endpoint whether or not the frontend calls it.
    'src/api/generated/**',
  ],
  ignoreDependencies: [
    // Loaded by the Vitest browser runner, never imported by our own code.
    '@vitest/browser',
    // The parser dependency-cruiser loads (`parser: 'swc'` in .dependency-cruiser.cjs).
    '@swc/core',
  ],
};

export default config;
