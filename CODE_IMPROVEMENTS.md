# Code Improvements & Recommendations

This document consolidates all code improvement recommendations for OmniDoc, including both backend and frontend improvements.

## 📋 Table of Contents

1. [Critical Issues](#critical-issues)
2. [Backend Improvements](#backend-improvements)
3. [Frontend Improvements](#frontend-improvements)
4. [UI Improvements](#ui-improvements)
5. [Performance Optimizations](#performance-optimizations)
6. [Security Improvements](#security-improvements)

## 🔴 Critical Issues

### 1. Backend: In-Memory State (`PROJECT_SELECTIONS`)

**Location:** `src/web/app.py:38`

**Issue:**
```python
# In-memory selection tracker until DB persistence fully migrated
PROJECT_SELECTIONS: Dict[str, List[str]] = {}
```

**Problem:**
- Data is lost on server restart
- Not shared across multiple server instances (horizontal scaling)
- Race conditions possible with concurrent requests
- Comment suggests this is temporary but it's still in use

**Recommendation:**
- Store `selected_documents` in the database (`project_status` table already has this column)
- Remove `PROJECT_SELECTIONS` dictionary
- Update all references to read from database

**Impact:** High - Data loss risk

---

### 2. Backend: Global State Variables

**Location:** `src/web/app.py:40-42`

**Issue:**
```python
# Global coordinator/context instances
coordinator: Optional[WorkflowCoordinator] = None
context_manager: Optional[ContextManager] = None
```

**Problem:**
- Global state makes testing difficult
- Not thread-safe (though FastAPI handles this)
- Hard to mock in tests
- Unclear lifecycle management

**Recommendation:**
- Use dependency injection pattern
- Store in `app.state` for FastAPI apps
- Better lifecycle management

**Impact:** Medium - Testing and maintainability

---

## 🔧 Backend Improvements

### Medium Priority

1. **Error Handling**: Add more specific exception types
2. **Validation**: Add Pydantic models for all API requests
3. **Logging**: Structured logging with context
4. **Testing**: Increase test coverage
5. **Documentation**: Add more docstrings

### Low Priority

1. **Code Organization**: Better module structure
2. **Type Hints**: Complete type annotations
3. **Performance**: Profile and optimize slow paths

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed backend improvement recommendations.

## 🎨 Frontend Improvements

### Medium Priority

1. **Error Boundaries**: Better error handling
2. **Loading States**: Improve loading indicators
3. **Accessibility**: ARIA labels and keyboard navigation
4. **Performance**: Code splitting and lazy loading

### Low Priority

1. **Code Organization**: Better component structure
2. **Type Safety**: More TypeScript types
3. **Testing**: Add unit and integration tests

## 🎨 UI Improvements

See [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) for comprehensive UI improvement roadmap with 25 improvements organized by priority.

### High Priority UI Improvements

1. **Color Palette Implementation** - Use defined color scheme
2. **Typography Standardization** - Consistent font usage
3. **Button & Input Standardization** - Unified component styles
4. **Accessibility Basics** - Keyboard navigation, ARIA labels

### Medium Priority UI Improvements

5. **Onboarding Flow** - Welcome screen and tutorial
6. **Visual Enhancements** - Icons, animations, spacing
7. **Mobile Responsiveness** - Better mobile experience

### Low Priority UI Improvements

8. **Advanced Features** - Dark mode, themes, etc.

## ⚡ Performance Optimizations

### Backend

1. **Database Queries**: Optimize slow queries
2. **Caching**: Expand Redis caching
3. **Connection Pooling**: Tune database pool settings
4. **Async Operations**: More async/await usage

### Frontend

1. **Code Splitting**: Lazy load components
2. **Image Optimization**: Optimize images
3. **Bundle Size**: Reduce JavaScript bundle
4. **Caching**: Better browser caching

## 🔒 Security Improvements

1. **Input Validation**: More comprehensive validation
2. **Rate Limiting**: Fine-tune rate limits
3. **CORS**: Review and tighten CORS settings
4. **Secrets Management**: Use secrets manager in production
5. **Dependencies**: Regular security audits

See [SECURITY.md](SECURITY.md) for complete security checklist.

## 📚 Related Documentation

- [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) - Complete UI improvement roadmap
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Detailed backend code improvements
- [SECURITY.md](SECURITY.md) - Security improvements and checklist
- [DEPLOYMENT_STRATEGY.md](DEPLOYMENT_STRATEGY.md) - When to implement improvements

