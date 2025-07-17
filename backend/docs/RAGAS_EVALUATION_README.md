# Music RAG Pipeline Evaluation with RAGAs

This directory contains evaluation scripts for assessing the performance of our music recommendation RAG pipeline using RAGAs (Retrieval-Augmented Generation Assessment).

## Setup

### 1. Install Dependencies

```bash
pip install -r evaluation_requirements.txt
```

### 2. Required Environment Variables

Make sure you have these in your `.env` file:

```
OPENAI_API_KEY=your_openai_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
```

## Evaluation Scripts

### 1. Full RAGAs Evaluation (`evaluate_rag_with_ragas.py`)

Comprehensive evaluation using all RAGAs metrics:

- **Faithfulness**: How faithful the answer is to the retrieved context
- **Answer Relevancy**: How relevant the answer is to the question
- **Context Precision**: Precision of retrieved context
- **Context Recall**: Recall of retrieved context
- **Context Relevancy**: Relevance of retrieved context

```bash
python evaluate_rag_with_ragas.py
```

### 2. Quick Evaluation (`quick_rag_eval.py`)

Simplified evaluation for rapid testing:

```bash
python quick_rag_eval.py
```

### 3. Music-Specific Metrics (`music_rag_metrics.py`)

Custom metrics tailored for music recommendation evaluation:

- **Audio Feature Relevance**: How well audio features match query intent
- **Genre Consistency**: Whether recommendations match requested genre
- **Similarity Coherence**: Whether similarity scores make sense
- **Diversity Score**: Diversity of recommendations
- **Response Completeness**: Whether the system provided recommendations

```bash
python music_rag_metrics.py
```

## Understanding RAGAs Metrics

### Core RAGAs Metrics Explained

1. **Faithfulness (0-1)**:

   - Measures if the generated answer is grounded in the retrieved context
   - Higher scores mean the answer doesn't hallucinate facts not in context
   - Target: > 0.8

2. **Answer Relevancy (0-1)**:

   - Measures how well the answer addresses the original question
   - Higher scores mean the answer directly addresses what was asked
   - Target: > 0.7

3. **Context Precision (0-1)**:

   - Measures the precision of the retrieval system
   - Higher scores mean less irrelevant context was retrieved
   - Target: > 0.7

4. **Context Recall (0-1)**:

   - Measures if all relevant information was retrieved
   - Higher scores mean no important context was missed
   - Target: > 0.6

5. **Context Relevancy (0-1)**:
   - Measures how relevant the retrieved context is to the question
   - Higher scores mean better retrieval quality
   - Target: > 0.7

### Music-Specific Metrics

1. **Audio Feature Relevance**:

   - Evaluates if recommended songs match audio characteristics mentioned in the query
   - Example: "upbeat" should return high-energy songs

2. **Genre Consistency**:

   - Checks if recommendations match the requested genre
   - Example: "jazz" query should return jazz songs

3. **Similarity Coherence**:

   - Verifies that similarity scores are meaningful and ordered correctly

4. **Diversity Score**:
   - Ensures recommendations aren't too repetitive (different artists, varied features)

## Interpreting Results

### Good Performance Indicators:

- Faithfulness > 0.8: Answers are well-grounded
- Answer Relevancy > 0.7: Responses address the questions
- Context Precision > 0.7: Retrieved context is relevant
- Audio Feature Relevance > 0.7: Music features match requests

### Areas for Improvement:

- Low Faithfulness: Model generates non-grounded answers
- Low Context Precision: Retrieval brings irrelevant songs
- Low Genre Consistency: Genre matching needs improvement
- Low Diversity: Recommendations too similar

## Customizing Evaluation

### Adding New Test Cases

Edit the evaluation scripts to add domain-specific test cases:

```python
evaluation_data = {
    "question": [
        "Your new test question",
        # Add more questions
    ],
    "ground_truth": [
        "Expected answer for the question",
        # Add corresponding ground truths
    ]
}
```

### Creating Custom Metrics

Extend the `MusicRAGMetrics` class to add your own evaluation criteria:

```python
def your_custom_metric(self, query: str, recommendations: List[Dict]) -> float:
    # Your evaluation logic here
    return score
```

## Continuous Evaluation

Set up regular evaluation runs to monitor your RAG pipeline performance:

1. **Development**: Run `quick_rag_eval.py` during development
2. **Testing**: Use `evaluate_rag_with_ragas.py` for comprehensive testing
3. **Production**: Monitor with `music_rag_metrics.py` for domain-specific insights

## Troubleshooting

### Common Issues:

1. **API Rate Limits**:

   - Reduce batch size or add delays between requests
   - Consider using different OpenAI models

2. **Context Too Long**:

   - Reduce the number of retrieved documents
   - Truncate context if necessary

3. **No Recommendations Found**:
   - Check if your vector database is properly loaded
   - Verify your embedding generation is working

### Performance Optimization:

1. **Improve Retrieval**:

   - Tune similarity thresholds
   - Experiment with different embedding models
   - Add metadata filtering

2. **Enhance Generation**:

   - Refine prompt templates
   - Adjust model parameters
   - Add response validation

3. **Better Evaluation**:
   - Expand test dataset
   - Add more diverse queries
   - Include edge cases
