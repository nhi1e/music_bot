#!/usr/bin/env python3
"""
RAGAs Evaluation for Music Recommendation RAG Pipeline
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import pandas as pd
import numpy as np
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_relevancy
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import json
from typing import List, Dict, Any

# Import your RAG components
from app.agent import graph
from app.schema import ChatState
from app.tools.vector_search_tool import search_music_by_vibe
from app.tools.spotify_tool import get_top_tracks, search_tracks

# Load environment variables
load_dotenv()

class MusicRAGEvaluator:
    """Evaluator for Music Recommendation RAG Pipeline using RAGAs"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.embeddings = OpenAIEmbeddings()
        
    def create_evaluation_dataset(self) -> Dataset:
        """Create evaluation dataset with questions, contexts, and ground truth answers"""
        
        # Sample evaluation questions for music recommendation
        evaluation_data = {
            "question": [
                "Give me chill but danceable electronic music",
                "I want upbeat rock songs for working out",
                "Find me sad acoustic ballads similar to Hotel California",
                "What are some popular K-pop songs with high energy?",
                "Recommend instrumental ambient music for studying",
                "I need happy pop songs with low acousticness",
                "Find energetic hip-hop tracks with high danceability",
                "Give me mellow jazz songs for relaxation"
            ],
            "ground_truth": [
                "Electronic music with moderate to high danceability (0.6-0.8) and medium energy (0.4-0.6), characterized by synthesized sounds and rhythmic beats suitable for both relaxation and movement.",
                "Rock music with high energy (0.7+) and moderate to high tempo (120+ BPM), featuring guitar-driven melodies and powerful rhythms ideal for exercise and motivation.",
                "Acoustic ballads with high acousticness (0.7+), low to medium energy (0.2-0.5), and emotional lyrical content, similar in style to classic rock storytelling.",
                "K-pop tracks with high energy (0.7+), high danceability (0.7+), and modern production, representing popular Korean pop music.",
                "Instrumental ambient music with high instrumentalness (0.8+), low energy (0.1-0.3), and minimal vocals for background listening during study.",
                "Pop music with high valence (0.6+), low acousticness (0.1-0.3), and upbeat tempo, featuring electronic production and catchy melodies.",
                "Hip-hop tracks with high energy (0.7+), high danceability (0.7+), and rhythmic beats characteristic of the genre.",
                "Jazz music with medium acousticness (0.5+), low to medium energy (0.2-0.5), and smooth, relaxing instrumental arrangements."
            ]
        }
        
        # Generate contexts and answers using your RAG pipeline
        contexts = []
        answers = []
        
        for question in evaluation_data["question"]:
            try:
                # Get context from your vector search
                vector_result = search_music_by_vibe.invoke({
                    "query": question, 
                    "num_results": 5
                })
                
                # Parse the JSON result to extract context
                parsed_result = json.loads(vector_result)
                
                # Extract context from recommendations
                context_items = []
                if "recommendations" in parsed_result:
                    for rec in parsed_result["recommendations"]:
                        context_item = f"Track: {rec['track']}, "
                        context_item += f"Similarity: {rec['similarity_score']}, "
                        if "vibe_profile" in rec:
                            vibe = rec["vibe_profile"]
                            context_item += f"Danceability: {vibe.get('danceability', 'N/A')}, "
                            context_item += f"Energy: {vibe.get('energy', 'N/A')}, "
                            context_item += f"Mood: {vibe.get('mood', 'N/A')}"
                        context_items.append(context_item)
                
                context = " | ".join(context_items)
                contexts.append(context)
                
                # Generate answer using your full RAG pipeline
                state = ChatState(
                    messages=[{"role": "user", "content": question}],
                    conversation_id="eval_session"
                )
                
                result = graph.invoke(state)
                
                # Extract the AI's response
                if result and "messages" in result and len(result["messages"]) > 1:
                    answer = result["messages"][-1].content
                else:
                    answer = "No response generated"
                
                answers.append(answer)
                
            except Exception as e:
                print(f"Error processing question '{question}': {e}")
                contexts.append("Error retrieving context")
                answers.append("Error generating answer")
        
        # Add contexts and answers to evaluation data
        evaluation_data["contexts"] = [[context] for context in contexts]  # RAGAs expects list of lists
        evaluation_data["answer"] = answers
        
        return Dataset.from_dict(evaluation_data)
    
    def evaluate_rag_pipeline(self, dataset: Dataset) -> Dict[str, float]:
        """Evaluate the RAG pipeline using RAGAs metrics"""
        
        # Define evaluation metrics
        metrics = [
            faithfulness,          # How faithful the answer is to the context
            answer_relevancy,      # How relevant the answer is to the question
            context_precision,     # Precision of retrieved context
            context_recall,        # Recall of retrieved context
            context_relevancy      # Relevance of retrieved context
        ]
        
        # Run evaluation
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=self.llm,
            embeddings=self.embeddings
        )
        
        return result
    
    def detailed_analysis(self, dataset: Dataset, results: Dict[str, float]):
        """Perform detailed analysis of evaluation results"""
        
        print("=" * 60)
        print("MUSIC RAG PIPELINE EVALUATION RESULTS")
        print("=" * 60)
        
        print("\n📊 Overall Metrics:")
        print("-" * 30)
        for metric, score in results.items():
            if isinstance(score, (int, float)):
                print(f"{metric.replace('_', ' ').title()}: {score:.3f}")
        
        print("\n🎵 Individual Question Analysis:")
        print("-" * 40)
        
        # Analyze each question
        for i, row in enumerate(dataset):
            print(f"\nQuestion {i+1}: {row['question']}")
            print(f"Ground Truth: {row['ground_truth'][:100]}...")
            print(f"Generated Answer: {row['answer'][:100]}...")
            print(f"Context Quality: {'Good' if len(row['contexts'][0]) > 50 else 'Poor'}")
            print("-" * 40)
    
    def get_improvement_recommendations(self, results: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on evaluation results"""
        
        recommendations = []
        
        # Thresholds for good performance (adjust based on your requirements)
        thresholds = {
            'faithfulness': 0.8,
            'answer_relevancy': 0.7,
            'context_precision': 0.7,
            'context_recall': 0.6,
            'context_relevancy': 0.7
        }
        
        for metric, score in results.items():
            if isinstance(score, (int, float)) and metric in thresholds:
                if score < thresholds[metric]:
                    if metric == 'faithfulness':
                        recommendations.append(
                            f"Low faithfulness ({score:.3f}): The model is generating answers not well-grounded in the retrieved context. "
                            "Consider improving context relevance or adjusting the generation prompt."
                        )
                    elif metric == 'answer_relevancy':
                        recommendations.append(
                            f"Low answer relevancy ({score:.3f}): Generated answers don't directly address the questions. "
                            "Consider refining the prompt template or improving question understanding."
                        )
                    elif metric == 'context_precision':
                        recommendations.append(
                            f"Low context precision ({score:.3f}): Retrieved context contains irrelevant information. "
                            "Consider improving your vector search similarity thresholds or ranking algorithm."
                        )
                    elif metric == 'context_recall':
                        recommendations.append(
                            f"Low context recall ({score:.3f}): Important information is missing from retrieved context. "
                            "Consider increasing the number of retrieved documents or improving embedding quality."
                        )
                    elif metric == 'context_relevancy':
                        recommendations.append(
                            f"Low context relevancy ({score:.3f}): Retrieved context doesn't match the question well. "
                            "Consider improving your embedding model or query processing."
                        )
        
        if not recommendations:
            recommendations.append("🎉 All metrics are above threshold! Your RAG pipeline is performing well.")
        
        return recommendations

def main():
    """Main evaluation function"""
    print("🎵 Starting Music RAG Pipeline Evaluation with RAGAs")
    print("=" * 60)
    
    # Initialize evaluator
    evaluator = MusicRAGEvaluator()
    
    # Create evaluation dataset
    print("📊 Creating evaluation dataset...")
    dataset = evaluator.create_evaluation_dataset()
    print(f"✅ Created dataset with {len(dataset)} examples")
    
    # Run evaluation
    print("\n🔍 Running RAGAs evaluation...")
    try:
        results = evaluator.evaluate_rag_pipeline(dataset)
        
        # Display results
        evaluator.detailed_analysis(dataset, results)
        
        # Get improvement recommendations
        print("\n💡 Improvement Recommendations:")
        print("-" * 40)
        recommendations = evaluator.get_improvement_recommendations(results)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        # Save results
        results_df = pd.DataFrame([results])
        results_df.to_csv("rag_evaluation_results.csv", index=False)
        print(f"\n💾 Results saved to 'rag_evaluation_results.csv'")
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        print("Please ensure you have the required API keys and dependencies installed.")

if __name__ == "__main__":
    main()
