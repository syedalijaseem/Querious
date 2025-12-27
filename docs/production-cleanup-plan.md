# Production Cleanup & Quality Assurance Plan

> **Branch:** `refactor/production-cleanup`  
> **Goal:** Prepare Querious for production deployment with clean code, proper security, and complete documentation.

---

## Initial Analysis Summary

### ✅ Already Good

- No `console.log` statements in frontend code
- No `debugger` statements anywhere
- `.gitignore` properly configured for most cases
- Frontend uses relative `/api` URL (proxied correctly)

### ⚠️ Issues Found

| Issue                           | Location                                     | Action                    |
| ------------------------------- | -------------------------------------------- | ------------------------- |
| Hardcoded Inngest URL           | `frontend/src/api.ts:239`                    | ✅ Fixed → use env var    |
| Hardcoded API fallback          | `frontend/src/hooks/useStreamingQuery.ts:24` | Replace with env var      |
| Debug print statements          | `main.py`, `debug_rag.py`, `list_chats.py`   | Convert to logging        |
| Incomplete `.env.example`       | Root                                         | ✅ Fixed → added all vars |
| Missing frontend `.env.example` | `frontend/`                                  | Create new file           |
| Debug scripts in root           | `debug_rag.py`, `list_chats.py`              | Move to `scripts/` folder |

---

## Phase 1: Code Cleanup

### 1.1 Debug Code

| File                | Action                                |
| ------------------- | ------------------------------------- |
| `main.py`           | Convert `print()` to `logging.info()` |
| `debug_rag.py`      | Move to `scripts/debug_rag.py`        |
| `list_chats.py`     | Move to `scripts/list_chats.py`       |
| `reset_database.py` | Move to `scripts/`                    |
| `migrate_db.py`     | Move to `scripts/`                    |

### 1.2 Unused Code

- [ ] Run `npm run build` to check for unused imports
- [ ] Check for unused components in `frontend/src/components/`
- [ ] Check for unused hooks in `frontend/src/hooks/`
- [ ] Remove unused CSS classes

### 1.3 Unused Files

- [x] Delete `frontend/src/assets/react.svg` (already deleted)
- [ ] Check for any `.bak` files
- [ ] Verify no duplicate files exist

---

## Phase 2: Refactoring

### 2.1 Environment URLs

#### Frontend (`frontend/.env.example`)

```env
# API URL (leave empty in production if same-origin)
VITE_API_URL=

# Inngest dev server URL (local development only)
VITE_INNGEST_URL=http://localhost:8288/v1
```

#### Files to Update

| File                                         | Current                       | New                                        |
| -------------------------------------------- | ----------------------------- | ------------------------------------------ |
| `frontend/src/hooks/useStreamingQuery.ts:24` | `"http://localhost:8000/api"` | `import.meta.env.VITE_API_URL \|\| "/api"` |

### 2.2 Type Safety

- [ ] Search for `any` types and replace with proper types
- [ ] Ensure all function parameters are typed

### 2.3 Constants

- [ ] Verify all magic numbers are in constants
- [ ] Check for hardcoded strings that should be constants

### 2.4 Error Handling

- [ ] Add `ErrorBoundary` component wrapping main app
- [ ] Ensure all async functions have try-catch
- [ ] Verify API calls show user-friendly errors on failure
- [ ] Check that failed uploads don't crash the app
- [ ] Ensure network errors are handled gracefully

---

## Phase 3: Security Audit

### 3.1 Frontend Security

| Check                                           | Status | Notes                              |
| ----------------------------------------------- | ------ | ---------------------------------- |
| Tokens in httpOnly cookies                      | ✅     | Auth uses `credentials: "include"` |
| External links have `rel="noopener noreferrer"` | ✅     | Verified in footer                 |
| No sensitive data in localStorage               | ⚠️     | Verify manually                    |
| XSS protection                                  | ⚠️     | Check user-rendered content        |

### 3.2 Backend Security

| Check                    | Status | Notes                           |
| ------------------------ | ------ | ------------------------------- |
| Auth on protected routes | ⚠️     | Audit all routes                |
| Password hashing         | ✅     | Uses bcrypt                     |
| JWT expiration           | ⚠️     | Verify token TTL                |
| Rate limiting            | ⚠️     | Verify exists, defer if missing |
| File upload validation   | ⚠️     | Verify type/size checks         |

### 3.3 Secrets Check

- [ ] Verify no API keys in git history
- [x] Verify `.env` is in `.gitignore`
- [ ] Create `.env.local` for local development

---

## Phase 4: Testing

### 4.1 Functionality Testing

- [ ] User registration works
- [ ] User login/logout works
- [ ] Create new chat works
- [ ] Upload document works
- [ ] Send message and receive AI response
- [ ] View chat history
- [ ] Create project
- [ ] Add documents to project
- [ ] Delete chat/project/document
- [ ] Settings page functionality
- [ ] Upgrade page displays correctly
- [ ] Landing page renders correctly
- [ ] Auth redirects work (`/` → `/home` when logged in)

### 4.2 UI Testing

- [ ] All pages render without errors
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Dark/light mode toggle works
- [ ] All buttons have hover/active states
- [ ] Skeleton loaders display during loading
- [ ] Empty states show when no chats/projects
- [ ] Markdown renders correctly in messages (no raw `**text**`)
- [ ] Sources accordion expands/collapses
- [ ] Modals open/close properly
- [ ] Navigation works correctly
- [ ] Footer displays with social links

### 4.3 Performance Testing

- [ ] Run: `npm run build` (check for errors)
- [ ] Check bundle size is reasonable
- [ ] Verify no large dependencies bloating bundle
- [ ] Check for duplicate API calls in Network tab
- [ ] No unnecessary re-renders (React DevTools)
- [ ] Images are optimized

### 4.4 Edge Cases

- [ ] Token limit reached → shows upgrade modal
- [ ] Empty message submission blocked
- [ ] Very long message handling
- [ ] Upload non-PDF file → proper error
- [ ] Upload file > 50MB → proper error
- [ ] Rapid clicking/submitting
- [ ] Back/forward navigation
- [ ] Multiple browser tabs
- [ ] Token expiration handling

---

## Phase 5: File Organization

### Move Debug Scripts

```
scripts/
├── debug_rag.py
├── list_chats.py
├── reset_database.py
├── migrate_db.py
├── setup_auth_db.py
└── setup_document_db.py
```

### Update `.gitignore`

Add:

```
.env.local
frontend/.env.local
```

---

## Phase 6: Documentation & Pre-Deployment

### README.md Updates

- [ ] Project description
- [ ] Tech stack list
- [ ] Features list
- [ ] Setup instructions (with env vars reference)
- [ ] Local development guide
- [ ] Deployment guide
- [ ] Author credits with links

### New Files

- [ ] `frontend/.env.example`
- [ ] `LICENSE` (MIT)

### Pre-Deployment Checklist

| Item                                              | Status |
| ------------------------------------------------- | ------ |
| All console.logs removed                          | ✅     |
| No TypeScript errors (`npm run build` passes)     | ⚠️     |
| No ESLint errors                                  | ⚠️     |
| No `any` types remaining                          | ⚠️     |
| No commented-out code                             | ⚠️     |
| No hardcoded URLs in codebase                     | ⚠️     |
| `.env.example` exists with all required variables | ✅     |
| `.env` files are in `.gitignore`                  | ✅     |
| No secrets in git history                         | ⚠️     |
| Authentication working correctly                  | ⚠️     |
| Protected routes are protected                    | ⚠️     |
| API keys are server-side only                     | ⚠️     |
| Input validation in place                         | ⚠️     |
| **404 page exists**                               | ⚠️     |
| **Favicon set (not default Vite)**                | ⚠️     |
| **Meta tags set (title, description, og:image)**  | ⚠️     |
| **ErrorBoundary in place**                        | ⚠️     |
| **PublicOnlyRoute has loading check**             | ✅     |
| Mobile responsive                                 | ⚠️     |
| Bundle size optimized                             | ⚠️     |

---

## Execution Order

1. **Phase 2.4:** Create ErrorBoundary component
2. **Phase 2.1:** Fix remaining hardcoded URL in `useStreamingQuery.ts`
3. **Phase 2.1:** Create frontend `.env.example`
4. **Phase 1.1:** Move scripts to `scripts/` folder
5. **Phase 1.1:** Convert `main.py` prints to logging
6. **Phase 5:** Update `.gitignore`
7. **Phase 4:** Run build and lint checks
8. **Phase 4:** Run existing tests, fix or delete as needed
9. **Phase 6:** Verify/add 404 page
10. **Phase 6:** Verify favicon set
11. **Phase 6:** Verify meta tags
12. **Phase 6:** Update README.md
13. **Phase 6:** Create LICENSE file
14. **Phase 4:** Manual testing
15. **Commit and push**

---

## Decisions Made

| Question                  | Decision                               |
| ------------------------- | -------------------------------------- |
| Debug prints in `main.py` | Convert to `logging.info()`            |
| Debug scripts             | Keep in `scripts/` folder              |
| Rate limiting             | Verify exists, defer adding if missing |
| Tests                     | Run them, fix or delete as needed      |
