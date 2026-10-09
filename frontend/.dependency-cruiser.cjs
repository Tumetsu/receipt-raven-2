/**
 * Frontend module boundaries, checked by `npm run deps:check` (CI and the
 * Claude Code stop hook). `npm run deps:graph` prints the src/ dependency graph
 * as a Mermaid diagram.
 *
 * Layers, from top to bottom: routes -> components -> hooks/lib -> api.
 * A lower layer never imports a higher one.
 *
 * @type {import('dependency-cruiser').IConfiguration}
 */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      comment: 'Circular imports make module initialisation order-dependent. Extract the shared part.',
      from: {},
      to: { circular: true },
    },
    {
      name: 'components-not-to-routes',
      severity: 'error',
      comment:
        'Routes compose components. A component importing a route ties it to one URL ' +
        'and creates a cycle through the generated route tree.',
      from: { path: '^src/components' },
      to: { path: '^src/(routes|routeTree\\.gen)' },
    },
    {
      name: 'shared-code-is-ui-agnostic',
      severity: 'error',
      comment: 'src/api, src/lib and src/hooks serve every component; they never import UI.',
      from: { path: '^src/(api|lib|hooks)' },
      to: { path: '^src/(components|routes)' },
    },
    {
      name: 'http-only-through-api',
      severity: 'error',
      comment:
        'Only src/api talks HTTP. Everything else calls the generated client in ' +
        'src/api/generated, which `make api-client` builds from the backend contract.',
      from: { path: '^src', pathNot: '^src/api' },
      to: { path: 'node_modules/axios' },
    },
    {
      name: 'ui-primitives-are-leaves',
      severity: 'error',
      comment:
        'src/components/ui holds shadcn/ui primitives. They know nothing about features, ' +
        'so they import only each other and src/lib.',
      from: { path: '^src/components/ui' },
      to: { path: '^src/(?!components/ui|lib)' },
    },
    {
      name: 'no-test-code-in-app',
      severity: 'error',
      comment: 'Application code must not depend on test helpers.',
      from: { path: '^src', pathNot: '\\.test\\.tsx?$' },
      to: { path: '^tests/' },
    },
    {
      name: 'not-to-dev-dep',
      severity: 'error',
      comment:
        'Application code ships to the browser, so it may only import runtime dependencies. ' +
        'Move the package to "dependencies" in package.json.',
      from: { path: '^src', pathNot: ['\\.test\\.tsx?$', '\\.d\\.ts$'] },
      to: {
        dependencyTypes: ['npm-dev'],
        dependencyTypesNot: ['type-only'],
        pathNot: ['node_modules/@types/'],
      },
    },
    {
      name: 'not-to-unresolvable',
      severity: 'error',
      comment: 'The import does not resolve: a typo, or a package missing from package.json.',
      from: {},
      to: { couldNotResolve: true },
    },
  ],
  options: {
    doNotFollow: { path: 'node_modules' },
    tsPreCompilationDeps: true,
    // swc, not the TypeScript compiler: dependency-cruiser cannot load
    // TypeScript 7 yet. It still prints a "missing-typescript-transpiler"
    // warning, but parses every .ts/.tsx file through swc.
    parser: 'swc',
    tsConfig: { fileName: 'tsconfig.json' },
    enhancedResolveOptions: {
      exportsFields: ['exports'],
      conditionNames: ['import', 'require', 'node', 'default', 'types'],
      mainFields: ['module', 'main', 'types', 'typings'],
    },
    reporterOptions: {
      text: { highlightFocused: true },
    },
  },
};
