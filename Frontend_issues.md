# Frontend Build Issues Documentation

## Overview
This document details the issues encountered while attempting to deploy the Swallowtail frontend to Vercel and the steps taken to resolve them.

## Environment Details
- **Node.js**: v22.17.0
- **npm**: 11.4.2
- **Next.js**: 15.4.3
- **React**: 19.1.0
- **Tailwind CSS**: v4 (beta)
- **TypeScript**: 5.x
- **ESLint**: 9.32.0

## Issues Encountered

### 1. Initial Vercel Deployment Error
**Error**: `Module not found: Can't resolve '@/lib/utils'`
- **Location**: Multiple files including `components/shared/sidebar.tsx`
- **Cause**: Path alias resolution failing on Vercel
- **Status**: Resolved

### 2. NPM Command Timeouts
**Issue**: npm commands (install, build, lint) consistently timing out
- **Symptoms**: Commands hang without output
- **Investigation Results**:
  - npm config is correct (registry: https://registry.npmjs.org/)
  - Disk space adequate (67% used)
  - No proxy issues
  - Large number of dependencies (582 packages) causing slow operations
- **Resolution**: Removed node_modules and package-lock.json for clean install
- **Status**: Resolved - npm install completes in ~2 minutes

### 3. Tailwind CSS v4 Compatibility Issues
**Issue**: Incompatible plugins from Tailwind v3 in package.json
- **Problematic packages**:
  - `@tailwindcss/forms`: ^0.5.10 (v3 plugin)
  - `@tailwindcss/typography`: ^0.5.16 (v3 plugin)
- **Resolution**: Removed incompatible plugins

### 4. ESLint Parsing Errors (UNRESOLVED)
**Error Messages**:
```
./app/(auth)/dashboard/page.tsx
65:5  Error: Parsing error: JSX element 'div' has no corresponding closing tag.

./app/(auth)/instances/[id]/tasks/page-client.tsx
132:11  Error: Parsing error: JSX element 'div' has no corresponding closing tag.

./app/(auth)/instances/page.tsx
135:4  Error: Parsing error: ')' expected.

./app/(auth)/layout.tsx
41:8  Error: Parsing error: '>' expected.

./app/page.tsx
103:3  Error: Parsing error: '}' expected.
```

**Investigation**:
- TypeScript compilation passes without errors (`npx tsc --noEmit` succeeds)
- Next.js build compiles successfully (shows "✓ Compiled successfully")
- Errors only appear during ESLint phase
- This is a known issue with Next.js 15 and ESLint 9's flat config format

**Root Cause**: 
- ESLint 9 uses new "flat config" format
- Next.js 15's ESLint configuration hasn't been fully migrated to support flat config
- The parser is incorrectly interpreting valid JSX syntax

**Attempted Solutions**:
1. Updated eslint.config.mjs to use FlatCompat with proper configuration
2. Added @eslint/js dependency
3. Tried ESLINT_USE_FLAT_CONFIG=false environment variable
4. Modified tsconfig.json paths configuration

**Status**: UNRESOLVED - These are false positive errors from ESLint

## Changes Made to Fix Deployment

### 1. Package.json Modifications
```json
// Moved from devDependencies to dependencies:
"tailwindcss": "^4",
"@tailwindcss/postcss": "^4",
"postcss": "^8.5.6"

// Removed incompatible v3 plugins:
- "@tailwindcss/forms": "^0.5.10",
- "@tailwindcss/typography": "^0.5.16",
```

### 2. TypeScript Configuration
**tsconfig.json changes**:
```json
// Removed path aliases:
- "paths": {
-   "@/*": ["./src/*", "./*"]
- },
// Kept only:
"baseUrl": "."
```

### 3. Import Path Updates
All imports changed from alias to relative paths:
- `import { cn } from '@/lib/utils'` → `import { cn } from '../../lib/utils'`
- `import { Button } from '@/components/ui/button'` → `import { Button } from '../ui/button'`
- etc.

**Files updated**:
- All files in `/components/ui/`
- All files in `/components/shared/`
- All files in `/components/instances/`
- All files in `/components/tasks/`
- All files in `/app/(auth)/`
- `/app/page.tsx`
- `/app/layout.tsx`

### 4. Configuration Files
- Removed `jsconfig.json` (no longer needed without path aliases)
- Updated `next.config.ts` to remove deprecated `swcMinify` option

## Current Status


## Resources
- [Next.js ESLint Configuration](https://nextjs.org/docs/app/api-reference/config/eslint)
- [ESLint Flat Config Migration Guide](https://eslint.org/docs/latest/use/configure/migration-guide)
- [GitHub Issue: ESLint 9 with Next.js 15](https://github.com/vercel/next.js/issues/64114)
- [GitHub Discussion: Flat Config in Next.js](https://github.com/vercel/next.js/discussions/49337)

## Files to Review
1. `/frontend/eslint.config.mjs` - Current ESLint configuration
2. `/frontend/package.json` - Dependencies and scripts
3. `/frontend/tsconfig.json` - TypeScript configuration
4. All files listed in ESLint errors above

## Next Steps
1. Decide on ESLint strategy
2. Test build completion without linting
3. Deploy to Vercel
4. Monitor for official Next.js flat config support