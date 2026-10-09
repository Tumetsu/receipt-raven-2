import { defineConfig } from 'orval';

// Generates TanStack Query hooks and models from the backend's committed
// OpenAPI contract (backend/openapi.json). Run `make api-client` from the repo
// root after any backend API change; it re-exports the schema and runs this.
export default defineConfig({
  api: {
    input: {
      target: '../backend/openapi.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/api/generated',
      schemas: './src/api/generated/model',
      client: 'react-query',
      httpClient: 'axios',
      mock: false,
      clean: true,
      tsconfig: './tsconfig.json',
      override: {
        mutator: {
          path: './src/api/axios-instance.ts',
          name: 'axiosInstance',
        },
        query: {
          signal: true,
        },
      },
    },
  },
});
