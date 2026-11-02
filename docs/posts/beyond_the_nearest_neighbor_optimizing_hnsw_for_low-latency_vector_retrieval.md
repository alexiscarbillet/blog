---
date: 2026-11-02
authors: [gemini]
categories: [Tech]
---



As large language models become the backbone of modern enterprise applications, the technical bottleneck has shifted from model inference time to vector retrieval latency. Vector databases are no longer just a luxury; they serve as the high-speed long-term memory for our AI agents and RAG (Retrieval-Augmented Generation) pipelines. However, as datasets scale into the hundreds of millions of embeddings, traditional flat-search methods collapse under the computational weight of high dimensionality. To maintain sub-millisecond response times without sacrificing recall accuracy, engineers must master the mechanics of Hierarchical Navigable Small Worlds (HNSW). Understanding the delicate interplay between graph construction parameters and query-time constraints is the critical difference between a fluid user experience and a system plagued by high p99 latencies.

<!-- truncate -->

## The Architecture of HNSW

Hierarchical Navigable Small Worlds (HNSW) is currently the gold standard for approximate nearest neighbor (ANN) search. It works by creating a multi-layered graph where the top layers contain fewer points (long-range skips) and the bottom layers contain the full dataset (short-range precision).

### Layered Navigation and Skip Lists
Think of HNSW as a skip list but for a proximity graph. When a query enters the system, it starts at the top layer, finding the nearest neighbor among a sparse set of points. Once the closest point in that layer is found, the search "zooms in" to the next layer down, using the previous winner as the entry point. This process repeats until the search reaches the base layer, significantly reducing the number of distance calculations required.

## Tuning for Performance: M and ef_construction

Optimizing an HNSW index requires a deep dive into its construction parameters. These values are immutable once the index is built, making it vital to get them right during the initial engineering phase.

### Balancing M and connectivity
The parameter `M` defines the maximum number of outgoing connections each node can have in the graph. A higher `M` increases accuracy (recall) because there are more paths to reach the true nearest neighbor, but it also increases the memory footprint and the time it takes to build the index. For most high-dimensional OpenAI or Cohere embeddings, an `M` between 16 and 64 is typically the "sweet spot."

### The ef_construction Trade-off
The `ef_construction` parameter determines how many neighbors are explored during the index building process. While increasing this value won't affect search speed, it will significantly improve the quality of the graph connections, leading to better recall. If you are building a static index where search performance is the priority, it is often worth setting a very high `ef_construction` (e.g., 200 or 400).

## Implementing Optimized Retrieval

Once the index is built, we can control the search-time complexity using `ef_search`. This allows us to dynamically trade off speed for accuracy depending on the specific use case of the query.

The following Python example demonstrates how to configure these parameters using the `faiss` library, a popular choice for high-performance vector operations.

```python
import faiss
import numpy as np

# Dimension of embeddings (e.g., for text-embedding-3-small)
d = 1536 
nb = 100000  # Database size
nq = 10      # Number of queries

# Generate synthetic data
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# Initialize HNSW index
# M = 32 (links per node)
index = faiss.IndexHNSWFlat(d, 32)

# Set ef_construction for high-quality graph building
index.hnsw.efConstruction = 200

# Add vectors to the index
index.add(xb)

# Set ef_search for query-time performance
# Higher = more accurate, Lower = faster
index.hnsw.efSearch = 64

# Perform the search
k = 5 # Find 5 nearest neighbors
distances, indices = index.search(xq, k)

print(f"Indices of nearest neighbors: {indices[0]}")
```

## Conclusion

Optimizing vector search is an iterative process of benchmarking and refinement. By moving beyond default configurations and manually tuning HNSW parameters like `M` and `ef_search`, engineering teams can achieve a 10x improvement in retrieval throughput. As we look toward 2027, the ability to manage these high-dimensional indices efficiently will remain a core competency for any developer building in the AI space. Always remember to test your recall against a "ground truth" flat index to ensure your optimizations aren't leaving relevant data behind.