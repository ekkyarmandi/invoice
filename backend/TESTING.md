# Testing & Coverage Cheat Sheet

Quick reference for testing and coverage analysis commands.

## 🚀 Quick Commands

```bash
# Complete test run with coverage
uv run coverage run -m pytest tests/ -v && uv run coverage report -m

# Router coverage only
uv run coverage report -m --include="app/routers/*"

# HTML report (visual coverage)
uv run coverage html && open htmlcov/index.html

# Find missing lines in specific file
uv run coverage report -m --include="app/routers/invoices.py"
```

## 🔍 Debugging Missing Coverage

### 1. Identify Missing Lines

```bash
# Show missing lines for all files
uv run coverage report -m

# Show context around specific missing lines
sed -n '75p;120p;180p;210p' app/routers/invoices.py

# Get 5 lines of context around missing line
sed -n '$((LINE-2)),$((LINE+2))p' app/routers/filename.py
```

### 2. Find Coverage Patterns

```bash
# Find all error handling (common missing coverage)
grep -n "raise HTTPException" app/routers/*.py

# Find return statements (often missed)
grep -n "return" app/routers/*.py

# Find CRUD operations that might need failure tests
grep -n "crud\." app/routers/*.py

# Find permission checks
grep -n "current_user\." app/routers/*.py
```

### 3. Analyze Specific Components

```bash
# Test single router file
uv run coverage run -m pytest tests/test_invoices_router.py -v
uv run coverage report -m --include="app/routers/invoices.py"

# Test specific test method
uv run coverage run -m pytest tests/test_invoices_router.py::TestInvoicesRouter::test_create_invoice -v

# Combine coverage from multiple runs
uv run coverage run -m pytest tests/test_auth.py -v
uv run coverage run --append -m pytest tests/test_invoices_router.py -v
uv run coverage report -m
```

## 🎯 Common Missing Coverage Scenarios

### Error Handling Paths

```python
# This line might be missed if no test triggers the error
if not success:
    raise HTTPException(status_code=404, detail="Not found")  # ← Missing coverage
```

**Solution:** Create test that makes CRUD operation fail

```python
def test_delete_crud_failure(self, client, db):
    # Delete via CRUD first
    crud.delete_resource(db, resource.id)

    # Then try to delete via API (triggers the error path)
    response = client.delete(f"/api/v1/resources/{resource.id}")
    assert response.status_code == 404
```

### Permission Checks

```python
# Permission check that might not be tested
if not current_user.is_super_admin and resource.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Forbidden")  # ← Missing coverage
```

**Solution:** Test with different user trying to access resource

```python
def test_permission_denied(self, client, db):
    # Create resource for user1
    # Login as user2
    # Try to access user1's resource
```

### Return Statements

```python
def delete_resource():
    # ... validation and deletion logic ...
    return  # ← This return might not be covered
```

**Solution:** Ensure test reaches successful completion path

## 📊 Coverage Goals by File Type

| Component | Target Coverage | Priority |
| --------- | --------------- | -------- |
| Routers   | 95-100%         | High     |
| CRUD      | 100%            | High     |
| Models    | 80-90%          | Medium   |
| Auth      | 90-95%          | High     |
| Utils     | 70-80%          | Low      |

## 🛠️ Useful Coverage Commands

### Basic Reports

```bash
# Overall coverage
uv run coverage report

# With missing line numbers
uv run coverage report -m

# Sort by percentage (lowest first)
uv run coverage report --sort=cover

# Sort by missing lines (most missing first)
uv run coverage report --sort=miss
```

### Filtering

```bash
# Include only specific patterns
uv run coverage report --include="app/routers/*"
uv run coverage report --include="app/models/*"
uv run coverage report --include="app/crud.py"

# Exclude patterns
uv run coverage report --omit="tests/*"
uv run coverage report --omit="*/migrations/*"

# Multiple patterns
uv run coverage report --include="app/routers/*,app/crud.py"
```

### Output Formats

```bash
# HTML (visual, best for debugging)
uv run coverage html

# XML (for CI/CD)
uv run coverage xml

# JSON (for analysis tools)
uv run coverage json

# Text to file
uv run coverage report > coverage_report.txt
```

## 🔧 Advanced Debugging

### Find Uncovered Code Blocks

```bash
# Combine grep with coverage to find patterns
uv run coverage report -m | grep "invoices.py"
# Then examine those lines:
sed -n '75,80p' app/routers/invoices.py
```

### Test Individual Functions

```bash
# Run coverage on single test, then check specific file
uv run coverage erase
uv run coverage run -m pytest tests/test_invoices_router.py::TestInvoicesRouter::test_delete_invoice -v
uv run coverage report -m --include="app/routers/invoices.py"
```

### Coverage Data Management

```bash
# Start fresh
uv run coverage erase

# Combine multiple coverage files
uv run coverage combine

# Debug coverage data
uv run coverage debug data

# Show coverage configuration
uv run coverage debug config
```

## 📝 Test Writing Patterns

### Complete Router Endpoint Test Suite

```python
class TestResourceRouter:
    def test_create_success(self, client, db):
        """Happy path"""

    def test_create_validation_error(self, client, db):
        """Invalid input"""

    def test_create_permission_denied(self, client, db):
        """Access control"""

    def test_read_success(self, client, db):
        """Successful retrieval"""

    def test_read_not_found(self, client, db):
        """Non-existent resource"""

    def test_update_success(self, client, db):
        """Happy path update"""

    def test_update_not_found(self, client, db):
        """Update non-existent"""

    def test_delete_success(self, client, db):
        """Successful deletion"""

    def test_delete_crud_failure(self, client, db):
        """CRUD operation fails"""

    def test_unauthorized_access(self, client):
        """No authentication"""

    def test_invalid_token(self, client):
        """Bad token"""
```
