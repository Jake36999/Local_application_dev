# RAG Integration System

## Overview

The Retrieval-Augmented Generation (RAG) integration system enhances the Canonical Code Platform with semantic understanding and AI-augmented analysis capabilities.

### Key Features

1. **Semantic Vector Search** - Find related components using natural language queries
2. **Component Indexing** - Automatically index code components with embeddings
3. **Relationship Tracking** - Maintain component dependency graphs
4. **Context-Aware Analysis** - Generate recommendations based on code patterns
5. **Augmented Reports** - Produce enhanced analysis with AI insights

## Architecture

### Core Components

#### 1. `rag_engine.py` - RAG Core System

**RAGVectorDB Class**
- Manages vector database (SQLite-based with embeddings)
- Provides semantic search capabilities
- Tracks component relationships
- Caches augmentation results

**RAGAnalyzer Class**
- High-level analysis operations
- Builds indexes from canonical database
- Generates component analyses
- Produces semantic recommendations

#### 2. `rag_orchestrator.py` - RAG Command Orchestrator

**RAGOrchestrator Class**
- Bridges message bus and RAG engine
- Processes RAG commands asynchronously
- Publishes RAG events to bus
- Manages RAG feature flag

#### 3. UI Integration (`ui_app.py`)

**New "🤖 RAG Analysis" Tab**
- Semantic search interface
- Component analysis viewer
- Report generation
- Recommendations display

## Database Schema

### rag_vectors.db Tables

#### indexed_components
```
component_id (PRIMARY KEY)
component_name
component_type
file_id
repo_path
source_snippet
documentation
semantic_tags (JSON)
indexed_at
indexed_model
```

#### component_relationships
```
rel_id (PRIMARY KEY)
source_component_id
target_component_id
relationship_type (calls, inherits, uses, etc.)
strength (0.0-1.0)
created_at
```

#### search_queries
```
query_id (PRIMARY KEY)
query_text
embedding_model
top_k
execution_time_ms
results_count
executed_at
```

#### rag_augmentations
```
augmentation_id (PRIMARY KEY)
source_component_id
augmentation_type (context_analysis, recommendation, etc.)
augmented_content
confidence_score
generated_at
```

## Usage Examples

### Indexing Components

```python
from rag_engine import get_rag_analyzer

analyzer = get_rag_analyzer()

# Build index from canonical database
indexed_count = analyzer.build_index_from_canon_db()
print(f"Indexed {indexed_count} components")
```

### Semantic Search

```python
from rag_engine import get_rag_db

db = get_rag_db()

# Search for components
results = db.search("database connection", top_k=5)

for result in results:
    print(f"{result.component_name}: {result.similarity_score:.2f}")
    print(f"  Context: {result.context}")
    print(f"  Related: {result.relationships}")
```

### Component Analysis

```python
from rag_orchestrator import get_rag_orchestrator

orch = get_rag_orchestrator()

# Analyze a component
analysis = orch.analyze_component(component_id)

print(f"Component: {analysis['component_name']}")
print(f"Relationships: {analysis['direct_relationships']}")
print("Recommendations:")
for rec in analysis['recommendations']:
    print(f"  - {rec}")
```

### Augmented Reports

```python
# Generate file-level report
report = orch.get_augmented_report(file_id)

print(f"Total components: {report['total_components']}")
print(f"Analyzed: {report['analyzed_components']}")

for comp_analysis in report['component_analyses']:
    print(f"\n{comp_analysis['component_name']}")
    for rec in comp_analysis.get('recommendations', []):
        print(f"  → {rec}")
```

## Message Bus Integration

### Events Published

#### rag_indexing_completed
```json
{
  "file_id": "...",
  "repo_path": "...",
  "components_indexed": 42,
  "timestamp": "2026-02-02T..."
}
```

#### rag_component_analysis
```json
{
  "component_id": "...",
  "analysis": {...},
  "timestamp": "2026-02-02T..."
}
```

#### rag_semantic_search
```json
{
  "query": "database",
  "results_count": 12,
  "top_k": 5,
  "timestamp": "2026-02-02T..."
}
```

#### rag_augmented_report
```json
{
  "file_id": "...",
  "components_analyzed": 42,
  "timestamp": "2026-02-02T..."
}
```

### Commands Supported

#### rag_index
Trigger indexing for a file
```python
bus.send_command(
    'rag_index',
    'rag_orchestrator',
    {'file_id': '...', 'repo_path': '...'}
)
```

#### rag_analyze
Analyze a component
```python
bus.send_command(
    'rag_analyze',
    'rag_orchestrator',
    {'component_id': '...'}
)
```

#### rag_search
Semantic search
```python
bus.send_command(
    'rag_search',
    'rag_orchestrator',
    {'query': 'error handling', 'top_k': 10}
)
```

#### rag_report
Generate report
```python
bus.send_command(
    'rag_report',
    'rag_orchestrator',
    {'file_id': '...'}
)
```

## Settings & Configuration

### Feature Flag

Enable RAG in the Settings tab:
- Setting: `rag_integration_enabled`
- Default: `false`
- Description: "Enable Retrieval-Augmented Generation for semantic analysis"

### Workflow Integration

RAG can be triggered automatically:

1. **On File Ingestion**: Index new components
2. **On Demand**: Via UI or message bus
3. **Scheduled**: Via orchestrator background tasks

## Embedding Models

### Current: SIMPLE_TF_IDF

Lightweight keyword-based search:
- No external dependencies
- Fast indexing and search
- Works with Python built-ins
- Suitable for code components

### Future: DENSE (Planned)

Neural embeddings:
- Use transformers or sentence-transformers
- Better semantic understanding
- Slower but more accurate
- Requires GPU support optional

### Future: HYBRID (Planned)

Combined approach:
- TF-IDF for keyword matching
- Neural embeddings for semantics
- Best of both worlds
- Configurable weighting

## Performance Considerations

### Indexing
- Time: O(n) where n = number of components
- Storage: ~1KB per component metadata
- Full database re-index on first run

### Search
- Time: O(m) where m = indexed components
- Results returned in relevance order
- Top-k search limits results efficiently

### Memory
- In-memory caching of embeddings (future)
- SQLite database for persistence
- Configurable retention policies

## Best Practices

1. **Index Regularly**
   - Index after each major ingestion
   - Set up background indexing task
   - Monitor indexing time

2. **Query Optimization**
   - Use specific, meaningful queries
   - Limit top_k results appropriately
   - Cache common searches

3. **Feature Management**
   - Enable RAG only when needed
   - Consider performance impact
   - Disable for lightweight deployments

4. **Monitoring**
   - Check `rag_augmentations` table for coverage
   - Monitor search latency
   - Track indexing completeness

## Troubleshooting

### RAG Tab Shows "Module Not Available"

**Solution:** Ensure `rag_orchestrator.py` exists and imports correctly
```bash
python -c "from rag_orchestrator import get_rag_orchestrator; print('OK')"
```

### No Components Found After Indexing

**Solution:** Trigger indexing from UI or manually:
```python
from rag_orchestrator import get_rag_orchestrator
orch = get_rag_orchestrator()
orch.trigger_indexing(file_id, repo_path)
```

### Search Returns Empty Results

**Solution:** Verify components are indexed:
```python
from rag_engine import get_rag_db
db = get_rag_db()
components = db.get_indexed_components(limit=5)
print(f"Indexed: {len(components)}")
```

### Feature Flag Not Showing in Settings

**Solution:** Ensure `rag_integration_enabled` is set in settings.db:
```python
from bus.settings_db import SettingsDB
sdb = SettingsDB()
sdb.set_feature_flag('rag_integration_enabled', True, 'Enable RAG')
```

## Future Enhancements

1. **LLM Integration** - Use GPT-4 or open source LLMs for smarter recommendations
2. **Fine-tuning** - Train embeddings on project-specific code patterns
3. **Real-time Updates** - Stream indexing as files are processed
4. **Batch Operations** - Bulk analysis and report generation
5. **Export** - Save augmented reports in multiple formats
6. **Metrics** - Dashboard showing RAG system health and performance
7. **Caching** - Multi-tier caching for faster searches
8. **Distributed** - Horizontal scaling for large codebases

## References

- **RAG Pattern**: https://arxiv.org/abs/2005.11401
- **Semantic Search**: https://en.wikipedia.org/wiki/Semantic_search
- **Vector Databases**: https://en.wikipedia.org/wiki/Vector_database
