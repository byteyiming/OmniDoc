# Development Guide

## Getting Started

1. **Setup**: See [README.md](../../README.md#-quick-start)
2. **Testing**: See [Testing Guide](./testing.md)
3. **Phase 1**: See [Phase 1 Guide](./phase1.md)

## Documentation

### Testing
- **[Testing Guide](./testing.md)** - Test framework and best practices
- **[Test Summary](./TEST_SUMMARY.md)** - Test coverage and results

### Implementation Guides
- **[Phase 1 Guide](./phase1.md)** - Phase 1 complete implementation guide
- **[Phase 1 Visual Flow](./PHASE1_VISUAL_FLOW.md)** - Visual diagrams
- **[Phase 2 Summary](./PHASE2_SUMMARY.md)** - Multi-agent system

### Setup
- **[Phase 1 Setup](./PHASE1_SETUP.md)** - Detailed setup instructions

### Maintenance
- **[Cleanup Summary](./CLEANUP_SUMMARY.md)** - Project cleanup notes

## Development Workflow

1. Write code following architecture patterns
2. Write tests (unit → integration → e2e)
3. Run test suite: `pytest`
4. Check coverage: `pytest --cov=src`
5. Update documentation if needed

## Adding New Features

1. Create feature branch
2. Implement with tests
3. Ensure all tests pass
4. Update documentation
5. Submit for review

