# Database Connection & Pool Management Skill

## 1. Universal Session Management
* All FastAPI database dependencies (e.g., `get_db()`) MUST use an asynchronous generator (`yield`).
* The database session MUST be explicitly closed in a `finally` block to guarantee connection release back to the pool, regardless of success or exception.
* **Never** leave a session open or rely on garbage collection to close it.

## 2. Environment-Aware Pooling
* **Production & Local Dev:** Use SQLAlchemy's default `QueuePool` in `database.py`. 
* Pool sizes and overflow limits must be dynamically read from environment variables (e.g., `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`). Never hardcode these values.
* **Testing:** The pytest test engine (`conftest.py`) MUST be instantiated using `poolclass=NullPool`. Tests must never hold open idle connections in a pool, as this causes deadlocks on remote databases like Supabase.

## 3. Asynchronous Teardown Hooks
* All pytest suites must include asynchronous teardown hooks for database connections.
* Explicitly call `await engine.dispose()` at the end of the test session to cleanly sever all connections and prevent hanging threads.

## 4. Error Handling & Rollbacks
* Wrap database execution logic in `try/except` blocks.
* Always explicitly call `await session.rollback()` inside the `except` block before raising an `HTTPException` to clear the transaction state.