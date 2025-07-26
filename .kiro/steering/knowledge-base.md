---
inclusion: fileMatch
fileMatchPattern: '*knowledge*|*kb*|*chroma*|*vector*'
---

# Knowledge Base Management Guidelines

## ChromaDB Integration

### Collection Management
- Use descriptive collection names
- Implement proper metadata structure
- Handle collection creation and updates safely

```python
collection = self.client.get_or_create_collection(
    name="mogine_knowledge",
    metadata={"description": "Mogine Technology knowledge base"}
)
```

### Document Structure
- Include comprehensive metadata for filtering
- Use consistent document ID format
- Store source information for traceability

```python
metadata = {
    "title": document_title,
    "category": category,
    "source": source_file,
    "timestamp": datetime.now().isoformat(),
    "relevance_score": score
}
```

### Search Implementation
- Use semantic search with embeddings
- Implement relevance score thresholds
- Support multiple search strategies (semantic + keyword)

### Media File Handling
- Store media file paths in metadata
- Validate file existence before serving
- Support multiple media types (images, videos)
- Implement proper CORS for media serving

## Data Loading and Processing

### XML Knowledge Base Processing
- Parse structured XML knowledge files
- Extract text content and metadata
- Handle nested structures appropriately
- Validate data integrity during loading

### Incremental Updates
- Support adding new documents without full reload
- Implement document versioning
- Handle duplicate detection and merging

## Search Optimization

### Query Processing
- Preprocess user queries for better matching
- Handle multi-language queries if needed
- Implement query expansion techniques

### Result Ranking
- Combine semantic similarity with metadata relevance
- Implement custom scoring algorithms
- Support result filtering by category/type

### Performance Considerations
- Implement result caching for common queries
- Optimize embedding generation
- Monitor search latency and accuracy