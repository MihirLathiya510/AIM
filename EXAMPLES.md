# AIM Usage Examples

Real-world examples of using AIM for complex tasks.

## Example 1: Build a REST API

```
Task: Create a RESTful API for a todo application with:
- CRUD operations for todos
- User authentication (JWT)
- SQLite database
- Input validation
- Error handling
- API documentation (OpenAPI/Swagger)
- Unit tests with >80% coverage
- Integration tests
- Docker deployment configuration

Use FastAPI framework and return production-ready code.
```

**AIM Process:**
1. Decomposes into 8 subtasks (models, auth, CRUD, validation, docs, tests, docker)
2. Assigns coding agents for implementation
3. Testing agents create comprehensive test suites
4. Documentation agents generate OpenAPI specs
5. Review agents validate each component
6. Iterates until all constraints met
7. Returns complete, production-ready API

## Example 2: Code Refactoring

```
Task: Refactor the legacy authentication module to:
- Replace basic auth with OAuth2 + PKCE
- Add support for social login (Google, GitHub)
- Implement refresh tokens with rotation
- Add rate limiting (failed attempts)
- Ensure backward compatibility
- Maintain >90% test coverage
- Update all documentation
- Add migration guide

Files to refactor: auth/basic_auth.py, auth/session.py
```

**AIM Process:**
1. Analyzes existing code structure
2. Plans refactoring strategy
3. Implements OAuth2 with PKCE
4. Adds social login providers
5. Updates tests to maintain coverage
6. Validates backward compatibility
7. Generates migration documentation
8. Reviews for security issues
9. Iterates until all requirements met

## Example 3: Data Pipeline

```
Task: Build a data processing pipeline that:
- Reads CSV files from S3
- Validates data schema (Pydantic models)
- Transforms data (normalize, dedupe)
- Loads into PostgreSQL
- Handles errors gracefully (retry logic)
- Logs all operations
- Monitors performance (timing, memory)
- Unit tests for each component
- Integration test with test database
- Documentation with examples

Use Python 3.11+ with type hints throughout.
```

**AIM Process:**
1. Decomposes into pipeline stages
2. Creates Pydantic schemas for validation
3. Implements ETL transformations
4. Adds error handling and retry logic
5. Integrates logging and monitoring
6. Creates comprehensive test suite
7. Validates performance requirements
8. Generates usage documentation

## Example 4: Frontend Component

```
Task: Create a React data table component with:
- Server-side pagination
- Column sorting (multi-column)
- Filtering (per column)
- Row selection (single/multi)
- Export to CSV/Excel
- Responsive design (mobile-friendly)
- Accessibility (WCAG 2.1 AA)
- TypeScript with strict mode
- Storybook stories
- Jest unit tests (>85% coverage)
- Documentation with examples

Use React 18+ with hooks, no class components.
```

**AIM Process:**
1. Scaffolds React component structure
2. Implements pagination, sorting, filtering
3. Adds export functionality
4. Ensures responsive design
5. Validates accessibility compliance
6. Creates TypeScript definitions
7. Writes Storybook stories
8. Adds comprehensive tests
9. Validates against constraints
10. Generates component documentation

## Example 5: Machine Learning Pipeline

```
Task: Build an ML model training pipeline for:
- Data ingestion from multiple sources
- Feature engineering (scaling, encoding)
- Model training (scikit-learn RandomForest)
- Hyperparameter tuning (GridSearch)
- Model evaluation (metrics, plots)
- Model versioning (MLflow)
- API endpoint for predictions
- Monitoring and logging
- Unit tests for preprocessing
- Integration tests for pipeline
- Documentation with example notebooks

Target accuracy: >85%
Training time: <10 minutes
```

**AIM Process:**
1. Sets up data ingestion
2. Implements feature engineering
3. Trains baseline model
4. Iterates on hyperparameters
5. Validates accuracy requirement
6. Integrates MLflow tracking
7. Creates prediction API
8. Adds monitoring
9. Writes tests
10. Generates documentation

## Example 6: Database Migration

```
Task: Migrate from MongoDB to PostgreSQL:
- Analyze existing schema (5 collections)
- Design normalized PostgreSQL schema
- Create migration scripts (ETL)
- Preserve data integrity (foreign keys)
- Handle large datasets (batching)
- Validate data after migration (checksums)
- Update application code (ORM changes)
- Update all tests
- Zero downtime migration plan
- Rollback procedure
- Complete documentation

Collections: users, posts, comments, likes, follows
Estimated records: 10M+ total
```

**AIM Process:**
1. Analyzes MongoDB schema
2. Designs normalized SQL schema
3. Creates migration scripts with batching
4. Implements data validation
5. Updates application ORM code
6. Migrates all tests
7. Plans blue-green deployment
8. Creates rollback scripts
9. Validates data integrity
10. Documents complete process

## Example 7: Security Audit

```
Task: Perform security audit and fixes for web application:
- Scan for OWASP Top 10 vulnerabilities
- Fix SQL injection risks
- Implement CSP headers
- Add rate limiting
- Secure session management
- Encrypt sensitive data at rest
- Add security logging
- Implement CSRF protection
- Update dependencies (security patches)
- Penetration testing
- Security documentation
- Compliance report

Target: Pass OWASP ZAP scan with 0 high/critical issues
```

**AIM Process:**
1. Runs security scanners
2. Identifies vulnerabilities
3. Implements fixes systematically
4. Adds security headers
5. Encrypts sensitive data
6. Validates CSRF protection
7. Updates dependencies
8. Re-runs security scans
9. Iterates until clean scan
10. Generates compliance report

## Example 8: Documentation Generation

```
Task: Generate comprehensive documentation for existing codebase:
- API reference (all endpoints)
- Code documentation (docstrings)
- User guide with examples
- Architecture overview
- Setup instructions
- Deployment guide
- Troubleshooting section
- Contributing guidelines
- Changelog
- README with badges

Requirements:
- Auto-generate from code where possible
- Include code examples
- Add diagrams (architecture, flow)
- Responsive documentation site
```

**AIM Process:**
1. Analyzes codebase structure
2. Generates API docs from code
3. Creates user guide with examples
4. Draws architecture diagrams
5. Writes setup instructions
6. Documents deployment process
7. Compiles troubleshooting guide
8. Creates contributing guidelines
9. Validates completeness
10. Builds documentation site

## Tips for Best Results

### 1. Be Specific with Constraints

**Good:**
```
- Test coverage >90%
- TypeScript strict mode
- ESLint with Airbnb config
- Prettier formatting
- API response time <200ms
```

**Bad:**
```
- Good code quality
- Well tested
```

### 2. Provide Context

```
Context:
- Framework: FastAPI 0.104
- Database: PostgreSQL 15
- Python: 3.11+
- Existing auth: JWT tokens
- Deployment: Docker + AWS ECS
```

### 3. Define Success Criteria

```
Success criteria:
- All tests pass
- Coverage >85%
- Zero linter errors
- Documentation complete
- Performance benchmarks met
```

### 4. Specify Dependencies

```
Dependencies:
- Must work with existing user module
- Compatible with current database schema
- Use company standard libraries
- Follow internal style guide
```

### 5. Request Iterations Explicitly

If output isn't perfect:

```
Please iterate on this output to:
- Increase test coverage from 75% to 90%
- Add more error handling
- Improve documentation
- Optimize performance
```

AIM will refine until all requirements are met.

---

**More examples coming soon!**

Have an interesting use case? Share it in [Discussions](https://github.com/aim-mcp/aim-mcp-server/discussions)!

