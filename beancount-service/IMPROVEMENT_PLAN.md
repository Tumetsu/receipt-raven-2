# Beancount Service - Improvement Plan

**Created:** 2025-11-07
**Status:** Phase 2 Completed ✅ (3 more phases remaining)
**Estimated Timeline:** 5-6 weeks
**Progress:** 40% (2 of 5 phases complete)

## Overview

This document tracks architectural improvements and refactoring tasks for the beancount-service microservice. The plan addresses critical pain points in configuration management, error handling, testing, and code maintainability.

---

## Phase 1: Foundation (High Priority) ✅
**Timeline:** Weeks 1-2
**Status:** Completed (2025-11-07)

### 1.1 Configuration Management ✅
- [x] Create `config/settings.py` with Pydantic Settings
- [x] Define `Settings` class with type-safe configuration
- [x] Implement `get_settings()` singleton function
- [x] Replace global variables in `main.py` with settings injection
- [x] Add configuration validation on startup
- [ ] Update `.env.example` with all required variables *(deferred)*
- [ ] Update documentation with new configuration approach *(deferred)*

**Files Modified:**
- ✅ Created: `config/__init__.py`, `config/settings.py`
- ✅ Modified: `main.py` (removed global variables)
- ✅ Updated: `requirements.txt` (added pydantic-settings)

**Commit:** `cf5d2c4` - Implement type-safe configuration management with Pydantic Settings

---

### 1.2 Logging Infrastructure ✅
- [x] Add `structlog` to requirements.txt
- [x] Create `utils/logging.py` module
- [x] Implement `setup_logging()` function
- [x] Replace all `print()` statements with structured logging
- [ ] Add request ID middleware for request tracing *(deferred to Phase 2.3)*
- [x] Configure log levels per environment
- [x] Add logging to all service functions

**Files Modified:**
- ✅ Created: `utils/__init__.py`, `utils/logging.py`
- ✅ Modified: `main.py`, `services/accounts.py`, `services/payees.py`, `services/monthly_expenses.py`
- ✅ Updated: `requirements.txt` (added structlog)

**Commit:** `9384b81` - Add structured logging infrastructure with structlog

---

### 1.3 Repository Pattern & Abstraction ✅
- [x] Create `repositories/` directory
- [x] Define `ILedgerRepository` abstract interface
- [x] Implement `BeancountFileRepository` with caching
- [x] Add `load_entries()` method with error handling
- [x] Add `append_transaction()` method with atomic writes
- [ ] Implement file locking for concurrent access *(deferred to Phase 4.2)*
- [x] Add ledger entry caching with TTL (60 seconds)
- [x] Create repository factory function (`get_ledger_repository()`)
- [x] Update all service functions to use repository

**Files Modified:**
- ✅ Created: `repositories/__init__.py`, `repositories/ledger_repository.py`
- ✅ Modified: `services/accounts.py`, `services/payees.py`, `services/monthly_expenses.py`, `services/transactions.py`
- ✅ Updated: All service functions now accept `ILedgerRepository`

**Commit:** `2b18130` - Implement repository pattern and dependency injection

---

### 1.4 Dependency Injection ✅
- [x] Create `dependencies.py` module
- [x] Implement `get_ledger_repository()` dependency
- [x] Implement `get_settings()` dependency (already available from config)
- [x] Update all route handlers to use FastAPI dependency injection
- [x] Remove global variable usage from route handlers
- [x] Create dependency fixtures for testing

**Files Modified:**
- ✅ Created: `dependencies.py`
- ✅ Modified: `main.py` (all 6 route handlers updated with `Depends()`)
- ✅ Updated: `tests/test_transactions.py` (added repository fixtures)

**Test Status:** All 26 existing tests passing ✅

**Commit:** `2b18130` - Implement repository pattern and dependency injection

---

## Phase 2: Error Handling & Observability ✅
**Timeline:** Week 3
**Status:** Completed (2025-11-07)

### 2.1 Custom Exception Hierarchy ✅
- [x] Create `exceptions.py` module
- [x] Define `BeancountServiceError` base exception
- [x] Define `LedgerNotFoundError` exception
- [x] Define `LedgerParseError` exception
- [x] Define `TransactionValidationError` with error details
- [x] Define `AccountNotFoundError` exception
- [x] Define `RepositoryError` exception
- [x] Update all service functions to raise typed exceptions
- [x] Remove generic `Exception` catches

**Files Modified:**
- ✅ Created: `exceptions.py`
- ✅ Modified: `services/transactions.py`, `repositories/ledger_repository.py`

**Commit:** `677c4c5` - Implement custom exception hierarchy and error handling middleware

---

### 2.2 Error Handler Middleware ✅
- [x] Create `middleware/error_handler.py`
- [x] Implement exception handler for `LedgerNotFoundError`
- [x] Implement exception handler for `LedgerParseError`
- [x] Implement exception handler for `TransactionValidationError`
- [x] Implement exception handler for `AccountNotFoundError`
- [x] Implement exception handler for `RepositoryError`
- [x] Add structured error responses with error codes
- [x] Register all exception handlers in `main.py`
- [x] Remove try-except blocks from route handlers
- [x] Update all tests to work with exception-based validation
- [ ] Add error response examples to OpenAPI schema *(deferred)*

**Files Modified:**
- ✅ Created: `middleware/__init__.py`, `middleware/error_handler.py`
- ✅ Modified: `main.py` (registered exception handlers, removed route-level error handling)
- ✅ Updated: `tests/test_transactions.py` (all 26 tests passing with pytest.raises())

**Test Status:** All 26 tests passing ✅

**Commit:** `677c4c5` - Implement custom exception hierarchy and error handling middleware

---

### 2.3 Observability
- [ ] Add structured logging for all requests
- [ ] Log all errors with full context

**Files to Modify:**
- Create: `middleware/observability.py`
- Modify: `main.py`

---

## Phase 3: Testing & Validation
**Timeline:** Week 4
**Status:** Not Started

### 3.1 Expand Test Coverage
- [ ] Create `tests/unit/` directory structure
- [ ] Write unit tests for `services/accounts.py` (100% coverage)
- [ ] Write unit tests for `services/payees.py` (100% coverage)
- [ ] Write unit tests for `services/monthly_expenses.py` (100% coverage)
- [ ] Create `tests/integration/` directory
- [ ] Write integration tests for all API endpoints
- [ ] Write integration tests for repository with real files
- [ ] Add test for concurrent transaction writes

**Files to Create:**
- `tests/unit/test_accounts.py`
- `tests/unit/test_payees.py`
- `tests/unit/test_monthly_expenses.py`
- `tests/integration/test_api_endpoints.py`
- `tests/integration/test_ledger_repository.py`

---

### 3.2 Testing Infrastructure
- [ ] Add pytest fixtures for repository mocking
- [ ] Add fixtures for settings configuration
- [ ] Create factory functions for test data
- [ ] Add test helpers for API client

**Files to Modify:**
- Create: `tests/conftest.py` (shared fixtures)
- Update: `pytest.ini`, `requirements-dev.txt`

---

### 3.3 Validation Improvements
- [ ] Extract magic numbers to constants
- [ ] Create `constants.py` for business rules
- [ ] Add validation for transaction tolerance
- [ ] Add validation for date formats
- [ ] Centralize all validation logic

**Files to Modify:**
- Create: `constants.py`
- Modify: `services/transactions.py`

---

## Phase 4: Performance & Scalability
**Timeline:** Week 5
**Status:** Not Started

### 4.1 Caching Strategy
- [x] Add in-memory cache for ledger entries *(completed in Phase 1)*
- [x] Add cache for accounts list with TTL *(via ledger entries cache)*
- [x] Add cache for payees list with TTL *(via ledger entries cache)*
- [x] Implement cache invalidation on transaction write *(completed in Phase 1)*

**Files Modified:**
- ✅ Modified: `repositories/ledger_repository.py` (60-second TTL cache implemented)
- Update: `README.md` *(pending documentation)*

---

### 4.2 File Safety
- [ ] Implement file locking with `fcntl`
- [ ] Add atomic write operations
- [ ] Add transaction rollback on failure
- [ ] Add backup mechanism before writes
- [ ] Document file safety guarantees

**Files to Modify:**
- Modify: `repositories/ledger_repository.py`
- Add tests: `tests/integration/test_concurrent_writes.py`

---

## Code Quality Tasks (Ongoing)

### Type Safety
- [ ] Add return type hints to all functions
- [ ] Enable strict mypy checking
- [ ] Fix all type warnings
- [ ] Add `py.typed` marker file

### Code Style
- [ ] Add `ruff` for linting
- [ ] Add `black` for formatting
- [ ] Configure pre-commit hooks
- [ ] Add code style to CI/CD

---

## Critical Issues Summary

### High Priority (Phase 1-2)
1. ✅ **Configuration Management** - ~~No type safety, global variables~~ → **FIXED**: Pydantic Settings with validation
2. ✅ **Logging** - ~~Using `print()`~~ → **FIXED**: Structured logging with structlog
3. ✅ **File I/O Abstraction** - ~~No abstraction~~ → **FIXED**: Repository pattern with caching
4. ✅ **Dependency Injection** - ~~Hard to test, tight coupling~~ → **FIXED**: FastAPI Depends()
5. ✅ **Error Handling** - ~~Generic exceptions~~ → **FIXED**: Custom exception hierarchy with middleware handlers
6. ⚠️ **File Locking** - No concurrent access protection (Phase 4)

### Medium Priority (Phase 3-4) 📋
5. **Test Coverage** - Only 40-50% coverage
6. **Validation Logic** - Magic numbers, inconsistent patterns
7. **Performance** - No caching, loading ledger on every request

### Low Priority (Phase 5) 🔍
8. **API Design** - No versioning, basic documentation
9. **Async Operations** - Misleading async declarations

---

## Metrics & Success Criteria

### Test Coverage
- **Current:** ~40-50%
- **Target:** 80%+

### Code Quality
- **Current:** No linting enforcement
- **Target:** 100% type hints, zero linting errors

### Performance
- **Current:** Ledger loaded on every request
- **Target:** <50ms response time with caching

### Maintainability
- **Current:** Medium complexity
- **Target:** Well-documented, easy to onboard new developers

---

## Risk Assessment

### Before Improvements
- **Data Corruption Risk:** Medium-High (no file locking)
- **Debug Difficulty:** High (print statements, no structured logging)
- **Test Confidence:** Medium (incomplete coverage)
- **Maintainability:** Medium (lacks abstractions)

### After Improvements
- **Data Corruption Risk:** Low (file locking, atomic writes)
- **Debug Difficulty:** Low (structured logging, error tracking)
- **Test Confidence:** High (80%+ coverage)
- **Maintainability:** High (clean architecture, well-documented)

---

## Notes

- This plan can be executed incrementally without breaking existing functionality
- Each phase should be completed with tests and documentation
- Deployment should happen after each phase for gradual rollout
- Breaking changes should be communicated to frontend team

---

## Progress Tracking

**Last Updated:** 2025-11-07
**Completed Phases:** 2/5 (Phase 1: Foundation ✅, Phase 2: Error Handling ✅)
**Completed Tasks:** 42/100+ tasks
**Overall Progress:** ~40%

### Recent Completions
- ✅ **Phase 1.1**: Configuration Management with Pydantic Settings
- ✅ **Phase 1.2**: Structured Logging with structlog
- ✅ **Phase 1.3**: Repository Pattern with ILedgerRepository
- ✅ **Phase 1.4**: Dependency Injection with FastAPI Depends
- ✅ **Phase 2.1**: Custom Exception Hierarchy
- ✅ **Phase 2.2**: Error Handler Middleware

### Git Commits
- `cf5d2c4` - Configuration management
- `9384b81` - Logging infrastructure
- `2b18130` - Repository pattern and dependency injection
- `677c4c5` - Custom exception hierarchy and error handling middleware

### Next Steps
- **Phase 2.3**: Observability (request timing, correlation IDs) - Optional
- **Phase 3**: Testing & Validation (expand test coverage, testing infrastructure)
