# Vercel Configuration Files - Complete Repository List

**Generated:** 2026-01-19  
**Repository:** Arnoldlarry15/red-set-protocell  
**Purpose:** Comprehensive list of all Vercel-related files after cleanup

---

## 📋 Complete List of Vercel-Related Files

### ✅ ACTIVE CONFIGURATION FILES (Authoritative)

#### 1. `/vercel.json`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/vercel.json`  
**Status:** ✅ **AUTHORITATIVE - SINGLE SOURCE OF TRUTH**  
**Type:** Vercel deployment configuration  
**Size:** 332 bytes  

**Description:**
Root-level Vercel configuration that defines the deployment strategy for the entire repository. This is the single authoritative configuration file for Vercel deployments.

**Contains:**
- Build configuration for frontend using `@vercel/static-build`
- Build configuration for serverless API functions using `@vercel/python`
- Rewrite rules routing `/api/*` to serverless functions
- Rewrite rules routing all other requests to frontend SPA

**Configuration Keys:**
- `builds` - Defines build steps for frontend and API
- `rewrites` - Defines URL routing rules

**Critical:** This file must never be deleted or duplicated. All Vercel deployments use this configuration.

---

#### 2. `/.vercelignore`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/.vercelignore`  
**Status:** ✅ **AUTHORITATIVE**  
**Type:** Deployment exclusion configuration  
**Size:** 998 bytes  
**Lines:** 92  

**Description:**
Root-level file that specifies which files and directories should be excluded from Vercel deployment. Reduces deployment size and build time.

**Key Exclusions:**
- Backend development files (legacy FastAPI server: `backend/`)
- Database files (`*.db`, `*.db-journal`)
- Python artifacts (`__pycache__/`, `*.pyc`, `build/`, `dist/`)
- Virtual environments (`venv/`, `env/`, `.venv`)
- Testing files (`.pytest_cache/`, `tests/`)
- Documentation (`docs/`, `*.md` except README.md)
- IDE files (`.vscode/`, `.idea/`)
- Git metadata (`.git/`, `.github/`)
- Demo/export directories
- Docker files
- Large images (`*.png`, `*.jpg`, `*.jpeg`)

**Critical:** This file reduces deployment bundle size from ~500MB to ~10MB by excluding unnecessary files.

---

### 📝 DOCUMENTATION FILES (Containing Configuration Examples)

#### 3. `/docs/deployment/VERCEL_SERVERLESS_GUIDE.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/docs/deployment/VERCEL_SERVERLESS_GUIDE.md`  
**Status:** ✅ **CURRENT & AUTHORITATIVE GUIDE**  
**Type:** Comprehensive deployment documentation  
**Lines:** 326  

**Description:**
The primary, up-to-date guide for deploying Red Set ProtoCell to Vercel using the serverless architecture. This is the official documentation that all developers should follow.

**Contents:**
- Explanation of serverless architecture with `/api` directory
- Handler pattern for Python serverless functions
- Environment variable configuration guide
- Security best practices and guardrails
- Deployment methods (automatic, CLI, dashboard)
- Testing instructions for local and production
- Migration path from legacy FastAPI architecture
- Troubleshooting common issues

**Configuration Examples:** Contains example `vercel.json` configurations that match the current architecture (though uses `"routes"` instead of `"rewrites"` in examples).

---

#### 4. `/docs/archive/VERCEL_SETUP.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/docs/archive/VERCEL_SETUP.md`  
**Status:** ⚠️ **ARCHIVED - OUTDATED**  
**Type:** Legacy deployment guide  
**Lines:** 174  

**Description:**
**[NOW CONTAINS WARNING BANNER]** Archived guide that documents the old FastAPI monolith deployment pattern. Routes API requests to `/backend/main.py` instead of serverless functions. Kept for historical reference only.

**Issues:**
- References old architecture (FastAPI monolith vs. serverless functions)
- Routes to `/backend/main.py` which is not used in production
- Uses deprecated Vercel function pattern
- Conflicts with current `/vercel.json`

**Warning Banner Added:** Clearly marks document as outdated and directs users to current guide.

---

#### 5. `/docs/archive/VERCEL_DEPLOYMENT_CONFIG.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/docs/archive/VERCEL_DEPLOYMENT_CONFIG.md`  
**Status:** ⚠️ **ARCHIVED - OUTDATED**  
**Type:** Legacy configuration guide  
**Lines:** 201  

**Description:**
**[NOW CONTAINS WARNING BANNER]** Archived configuration documentation that references outdated directory names (`rsp-ui` instead of `frontend`). Frontend-only configuration missing serverless API setup.

**Issues:**
- References `rsp-ui` directory (renamed to `frontend`)
- Missing `/api` serverless function configuration
- Would fail if followed literally (directory doesn't exist)
- Focuses on SPA routing issues now resolved

**Warning Banner Added:** Clearly marks document as outdated and directs users to current guide.

---

#### 6. `/docs/archive/VERCEL_DEPLOYMENT.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/docs/archive/VERCEL_DEPLOYMENT.md`  
**Status:** ⚠️ **ARCHIVED - OUTDATED**  
**Type:** Legacy deployment walkthrough  
**Lines:** 261  

**Description:**
**[NOW CONTAINS WARNING BANNER]** Archived deployment guide with outdated directory references and frontend-only configuration.

**Issues:**
- References `rsp-ui` directory (renamed to `frontend`)
- Frontend-only configuration (no API/backend)
- Simplified routing that doesn't handle API requests
- Would fail if followed literally

**Warning Banner Added:** Clearly marks document as outdated and directs users to current guide.

---

#### 7. `/docs/archive/SERVERLESS_IMPLEMENTATION_SUMMARY.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/docs/archive/SERVERLESS_IMPLEMENTATION_SUMMARY.md`  
**Status:** 📋 **ARCHIVED - HISTORICAL RECORD**  
**Type:** Migration summary documentation  
**Lines:** 275  

**Description:**
**[NOW CONTAINS HISTORICAL NOTE]** Documents the completed migration from FastAPI monolith to serverless architecture. Mostly accurate but uses `"routes"` instead of `"rewrites"` in examples.

**Contents:**
- Summary of serverless migration
- API endpoints created
- Configuration changes made
- Security improvements implemented
- Architecture comparison (before/after)

**Note:** This is a historical record of the migration process, not an active deployment guide. Configuration examples differ slightly from current implementation but architecture is correct.

---

### 🔧 SUPPORTING CONFIGURATION FILES

#### 8. `/frontend/package.json`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/frontend/package.json`  
**Status:** ✅ **ACTIVE**  
**Type:** NPM package configuration  

**Vercel-Related Content:**
```json
"scripts": {
  "vercel-build": "npm run build"
}
```

**Description:**
The `vercel-build` script is automatically detected and executed by Vercel when using `@vercel/static-build` builder specified in root `vercel.json`.

---

#### 9. `/frontend/vite.config.ts`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/frontend/vite.config.ts`  
**Status:** ✅ **ACTIVE (Local Development Only)**  
**Type:** Vite build configuration  

**Vercel-Related Content:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Description:**
Contains proxy configuration for local development only. Routes `/api` requests to local FastAPI backend running on port 8000. **Not used in Vercel deployment** (Vercel's rewrites handle routing instead).

---

#### 10. `/api/README.md`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/api/README.md`  
**Status:** ✅ **ACTIVE**  
**Type:** API documentation  
**Lines:** 228  

**Description:**
Documents the serverless API functions deployed to Vercel. Describes endpoints, request/response formats, environment variables, and architecture considerations for serverless deployment.

**Contents:**
- API endpoint documentation
- Handler pattern explanation
- Environment variable requirements
- Serverless architecture notes
- Security considerations
- Development and testing instructions

---

#### 11. `/requirements.txt` (Root)
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/requirements.txt`  
**Status:** ✅ **ACTIVE**  
**Type:** Python dependencies  

**Description:**
Minimal Python dependencies for serverless API functions in `/api` directory. Installed by Vercel Python runtime during deployment.

**Dependencies:**
- `pydantic>=2.0.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variables
- `requests>=2.31.0` - HTTP client

---

### 🔒 GIT CONFIGURATION

#### 12. `/.gitignore`
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/.gitignore`  
**Status:** ✅ **ACTIVE (Updated)**  
**Type:** Git exclusion configuration  

**Vercel-Related Content:**
```gitignore
# Vercel local metadata (do not commit)
.vercel/
```

**Description:**
**[RECENTLY UPDATED]** Now includes `.vercel/` directory exclusion to prevent local Vercel metadata and authentication tokens from being committed to the repository.

**Why Important:**
- `.vercel/` contains local deployment metadata
- May contain authentication tokens
- Should never be committed to version control
- Not required for deployment (Vercel uses repository configuration)

---

## ❌ REMOVED FILES

### 13. `/frontend/.vercelignore` (DELETED)
**Full Path:** `/home/runner/work/red-set-protocell/red-set-protocell/frontend/.vercelignore`  
**Status:** ❌ **REMOVED (Redundant)**  
**Type:** Frontend deployment exclusion  
**Size:** ~34 lines (before removal)  

**Why Removed:**
1. Duplicated patterns from root `.vercelignore`
2. Created potential for configuration conflicts
3. Not standard practice for monorepo with root-level `vercel.json`
4. Root-level `.vercelignore` is authoritative when building from repository root
5. Build configuration in root `vercel.json` processes entire project from root

**Impact of Removal:**
- ✅ No deployment impact (root `.vercelignore` handles all exclusions)
- ✅ Eliminates configuration ambiguity
- ✅ Follows Vercel best practices

---

## 📊 Summary Statistics

### Current Configuration Files
- **Active Config Files:** 2 (vercel.json, .vercelignore)
- **Active Documentation:** 1 (VERCEL_SERVERLESS_GUIDE.md)
- **Archived Documentation:** 4 (all with warning banners)
- **Supporting Files:** 4 (package.json, vite.config.ts, api/README.md, requirements.txt)
- **Git Configuration:** 1 (.gitignore with .vercel/ exclusion)

### Files Removed
- **Redundant Config Files:** 1 (frontend/.vercelignore)
- **.vercel/ Directories:** 0 (none found, now excluded by .gitignore)

---

## 🎯 Single Source of Truth

### Deployment Configuration
**File:** `/vercel.json` (root level)  
**Purpose:** Defines build steps, routing, and deployment strategy  
**Status:** Authoritative, must not be duplicated

### Deployment Exclusions
**File:** `/.vercelignore` (root level)  
**Purpose:** Specifies files to exclude from deployment  
**Status:** Authoritative, must not be duplicated

### Deployment Documentation
**File:** `/docs/deployment/VERCEL_SERVERLESS_GUIDE.md`  
**Purpose:** Official deployment guide  
**Status:** Current and authoritative

---

## 🚀 For Developers

**To deploy to Vercel:**
1. Read: `/docs/deployment/VERCEL_SERVERLESS_GUIDE.md`
2. Use: `/vercel.json` (root) as the configuration reference
3. Ignore: All files in `/docs/archive/` (historical reference only)

**Configuration files to modify:**
- `/vercel.json` - For deployment configuration changes
- `/.vercelignore` - To exclude additional files from deployment
- `/frontend/package.json` - For frontend build script changes
- `/requirements.txt` (root) - For API dependencies

**Configuration files to NEVER modify:**
- Archived documentation (read-only historical reference)

---

## 📝 File Inventory Summary

| Category | Count | Files |
|----------|-------|-------|
| Active Config | 2 | vercel.json, .vercelignore |
| Current Docs | 1 | VERCEL_SERVERLESS_GUIDE.md |
| Archived Docs | 4 | VERCEL_SETUP.md, VERCEL_DEPLOYMENT_CONFIG.md, VERCEL_DEPLOYMENT.md, SERVERLESS_IMPLEMENTATION_SUMMARY.md |
| Supporting Files | 4 | frontend/package.json, frontend/vite.config.ts, api/README.md, requirements.txt |
| Git Config | 1 | .gitignore (with .vercel/ exclusion) |
| Analysis Docs | 2 | VERCEL_CONFIG_ANALYSIS.md, VERCEL_CLEANUP_SUMMARY.md |
| **TOTAL** | **14** | **All files accounted for** |

---

**Document Status:** ✅ Complete and Current  
**Last Updated:** 2026-01-19  
**Maintenance:** Update when Vercel configuration changes
