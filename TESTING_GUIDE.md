# Study Companion API - Testing Guide

## 📋 Overview

This guide covers comprehensive testing for the Study Companion API, including unit tests, integration tests, and end-to-end workflows.

## 🧪 Test Structure

```
base/
├── test_models.py      # Model validation and relationships
├── test_views.py       # API endpoint functionality
├── test_serializers.py # Data serialization/validation
└── test_integration.py # End-to-end workflows
```

## 🚀 Quick Start

### Basic Test Commands

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test base.test_models

# Run with verbose output
python manage.py test --verbosity=2

# Keep database between test runs (faster)
python manage.py test --keepdb
```

### Using the Test Runner Script

```bash
# Run all tests
python test_runner.py all

# Run specific test categories
python test_runner.py models
python test_runner.py views
python test_runner.py serializers
python test_runner.py integration

# Generate coverage report
python test_runner.py coverage

# Fast tests (keep database)
python test_runner.py fast
```

## 📊 Test Categories

### 1. Model Tests (`test_models.py`)
Tests data models, validation, and relationships:

```bash
python manage.py test base.test_models
```

**What it tests:**
- User model creation and validation
- Room-Topic-Message relationships
- Model string representations
- Data constraints and uniqueness

### 2. View Tests (`test_views.py`)
Tests API endpoints and business logic:

```bash
python manage.py test base.test_views
```

**What it tests:**
- Authentication (register, login, logout)
- CRUD operations for all models
- Permission-based access control
- Search functionality
- Error handling

### 3. Serializer Tests (`test_serializers.py`)
Tests data transformation and validation:

```bash
python manage.py test base.test_serializers
```

**What it tests:**
- Data serialization/deserialization
- Validation rules
- Custom field handling
- Error messages

### 4. Integration Tests (`test_integration.py`)
Tests complete user workflows:

```bash
python manage.py test base.test_integration
```

**What it tests:**
- End-to-end user journeys
- Multi-user interactions
- Authentication flows
- Data integrity

## 🔧 Advanced Testing

### Coverage Analysis

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test base

# Generate report
coverage report

# Generate HTML report
coverage html
```

View HTML report: `htmlcov/index.html`

### Testing with Different Databases

```bash
# Test with SQLite (default)
python manage.py test

# Test with PostgreSQL (if configured)
DATABASE_URL=postgresql://user:pass@localhost/testdb python manage.py test
```

### Parallel Testing

```bash
# Run tests in parallel (faster)
python manage.py test --parallel

# Specify number of processes
python manage.py test --parallel 4
```

## 🎯 Test Examples

### Testing Authentication

```python
def test_user_registration(self):
    response = self.client.post('/api/register/', {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'securepass123',
        'password2': 'securepass123'
    })
    self.assertEqual(response.status_code, 201)
    self.assertIn('access', response.data)
```

### Testing Permissions

```python
def test_room_update_permission(self):
    # Only host can update room
    response = self.client.put(f'/api/rooms/{self.room.id}/update/', {
        'name': 'Updated Room'
    })
    if self.user == self.room.host:
        self.assertEqual(response.status_code, 200)
    else:
        self.assertEqual(response.status_code, 403)
```

### Testing Workflows

```python
def test_complete_user_journey(self):
    # 1. Register user
    # 2. Create room
    # 3. Send message
    # 4. Search content
    # 5. Update profile
    # Each step builds on the previous
```

## 🐛 Debugging Tests

### Verbose Output

```bash
# See detailed test output
python manage.py test --verbosity=3

# See SQL queries
python manage.py test --debug-mode
```

### Running Single Tests

```bash
# Run specific test class
python manage.py test base.test_views.AuthenticationTestCase

# Run specific test method
python manage.py test base.test_views.AuthenticationTestCase.test_user_registration
```

### Using pdb for Debugging

```python
def test_something(self):
    import pdb; pdb.set_trace()  # Breakpoint
    # Your test code here
```

## 📈 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python manage.py test
```

## 🔍 Test Data Management

### Using Fixtures

```python
# Create test data
def setUp(self):
    self.user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
```

### Factory Pattern

```python
class UserFactory:
    @staticmethod
    def create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
```

## 📋 Testing Checklist

### Before Committing Code

- [ ] All tests pass: `python test_runner.py all`
- [ ] Coverage > 80%: `python test_runner.py coverage`
- [ ] No test warnings
- [ ] New features have tests
- [ ] Edge cases covered

### Test Quality Checklist

- [ ] Tests are independent (can run in any order)
- [ ] Tests clean up after themselves
- [ ] Tests have descriptive names
- [ ] Tests cover both success and failure cases
- [ ] Tests are fast (< 1 second each)

## 🚨 Common Issues

### Database Issues

```bash
# Reset test database
python manage.py flush --settings=test_settings

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Permission Errors

```python
# Always authenticate before testing protected endpoints
self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
```

### Async Issues

```python
# Use TransactionTestCase for complex workflows
class IntegrationTest(TransactionTestCase):
    pass
```

## 📚 Best Practices

### Test Organization

1. **One test file per app component**
2. **Group related tests in classes**
3. **Use descriptive test names**
4. **Keep tests simple and focused**

### Test Data

1. **Create minimal test data**
2. **Use factories for complex objects**
3. **Clean up after tests**
4. **Don't rely on external services**

### Assertions

1. **Use specific assertions**
2. **Test both positive and negative cases**
3. **Verify side effects**
4. **Check error messages**

## 🎓 Learning Resources

### Django Testing

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [DRF Testing Guide](https://www.django-rest-framework.org/api-guide/testing/)

### Testing Patterns

- Test-Driven Development (TDD)
- Behavior-Driven Development (BDD)
- Integration vs Unit Testing

### Tools

- `coverage.py` - Code coverage analysis
- `pytest-django` - Alternative test runner
- `factory_boy` - Test data factories
- `mock` - Mocking external dependencies

## 🔄 Maintenance

### Regular Tasks

```bash
# Weekly: Run full test suite
python test_runner.py all

# Monthly: Check coverage
python test_runner.py coverage

# Before releases: Integration tests
python test_runner.py integration
```

### Updating Tests

1. **Add tests for new features**
2. **Update tests when changing APIs**
3. **Remove obsolete tests**
4. **Refactor duplicate test code**

This comprehensive testing setup ensures your Study Companion API remains reliable, maintainable, and bug-free throughout development and production.