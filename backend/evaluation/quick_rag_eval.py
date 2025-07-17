#!/usr/bin/env python3
"""
Simplified RAGAs Evaluation for Music Recommendation System
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import json

# Import your components
from src.tools.vector_search_tool import search_music_by_vibe

load_dotenv()

def quick_rag_evaluation():
    """Quick evaluation with minimal setup"""
    
    # Simple test cases
    test_data = {
        "question": [
            "Give me upbeat electronic dance music",
            "Find chill acoustic songs for relaxation",
            "I want energetic rock music for working out"
        ],
        "ground_truth": [
            "Electronic dance music with high energy and danceability",
            "Acoustic music with low energy and high acousticness for relaxation",
            "Rock music with high energy and tempo suitable for exercise"
        ]
    }
    
    # Generate contexts and answers
    contexts = []
    answers = []
    
    for question in test_data["question"]:
        try:
            # Get recommendations
            result = search_music_by_vibe.invoke({
                "query": question,
                "num_results": 3
            })
            
            parsed = json.loads(result)
            
            # Extract context
            if "recommendations" in parsed:
                context_parts = []
                for rec in parsed["recommendations"][:3]:
                    context_parts.append(f"{rec['track']} (similarity: {rec['similarity_score']})")
                context = " | ".join(context_parts)
            else:
                context = "No recommendations found"
            
            contexts.append(context)
            
            # Simple answer based on recommendations
            if "recommendations" in parsed and parsed["recommendations"]:
                answer = f"Based on your request for '{question}', I recommend these tracks: "
                track_names = [rec['track'] for rec in parsed["recommendations"][:3]]
                answer += ", ".join(track_names)
            else:
                answer = "No suitable music found for your request."
            
            answers.append(answer)
            
        except Exception as e:
            print(f"Error with question '{question}': {e}")
            contexts.append("Error retrieving context")
            answers.append("Error generating answer")
    
    # Prepare dataset
    test_data["contexts"] = [[ctx] for ctx in contexts]
    test_data["answer"] = answers
    
    dataset = Dataset.from_dict(test_data)
    
    # Evaluate with basic metrics
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    embeddings = OpenAIEmbeddings()
    
    print("🔍 Starting RAGAs evaluation...")
    print(f"Dataset size: {len(dataset)}")
    print("Sample data:")
    for i in range(min(2, len(dataset))):
        print(f"  Question {i+1}: {dataset[i]['question']}")
        print(f"  Context: {dataset[i]['contexts'][0][:100]}...")
        print(f"  Answer: {dataset[i]['answer'][:100]}...")
        print()
    
    try:
        result = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=llm,
            embeddings=embeddings
        )
        print("✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return None
    
    print("🎵 Quick RAG Evaluation Results:")
    print("=" * 40)
    
    # Handle RAGAs result format
    if hasattr(result, 'to_pandas'):
        # Convert to pandas DataFrame and get mean scores
        df = result.to_pandas()
        print("Individual scores per question:")
        for col in df.columns:
            if col in ['faithfulness', 'answer_relevancy', 'context_precision']:
                mean_score = df[col].mean()
                print(f"{col.replace('_', ' ').title()}: {mean_score:.3f}")
                print(f"  Individual scores: {df[col].tolist()}")
    else:
        # Fallback for direct dictionary access
        try:
            for metric, score in result.items():
                if isinstance(score, (int, float)):
                    print(f"{metric.replace('_', ' ').title()}: {score:.3f}")
        except:
            print("Result format:", type(result))
            print("Result content:", result)
    
    return result

if __name__ == "__main__":
    quick_rag_evaluation()
