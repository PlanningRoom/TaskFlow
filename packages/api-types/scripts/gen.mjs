#!/usr/bin/env node
/**
 * Regenerate the OpenAPI artifacts for @taskflow/api-types (TDD §14.1):
 *
 *   1. Dump the FastAPI schema offline (no uvicorn/Postgres) to openapi.json.
 *   2. Run openapi-typescript to emit src/generated/schema.d.ts.
 *
 * Both artifacts are committed; the `openapi-drift` CI job reruns this and
 * fails if either differs from what's checked in.
 */
import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = resolve(here, '..');
const apiDir = resolve(pkgRoot, '../../apps/api');
const schemaJson = resolve(pkgRoot, 'openapi.json');
const schemaDts = resolve(pkgRoot, 'src/generated/schema.d.ts');

const run = (cmd, args, opts = {}) => execFileSync(cmd, args, { stdio: 'inherit', ...opts });

// 1. Offline schema dump via uv (the API workspace owns its Python env).
run('uv', ['run', 'python', '-m', 'taskflow.scripts.dump_openapi', schemaJson], {
  cwd: apiDir,
});

// 2. Generate TypeScript types from the dumped schema.
run('pnpm', ['exec', 'openapi-typescript', schemaJson, '-o', schemaDts], {
  cwd: pkgRoot,
});

console.log('api-types: regenerated openapi.json + src/generated/schema.d.ts');
