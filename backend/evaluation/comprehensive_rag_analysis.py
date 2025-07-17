#!/usr/bin/env python3
"""
Comprehensive analysis of RAGAs evaluation results for music RAG system
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import json
import pandas as pd

# Import your components
from app.tools.vector_search_tool import search_music_by_vibe

load_dotenv()

def analyze_rag_performance():
    """Comprehensive analysis of RAG performance with detailed insights"""
    
    print("🎵 Music RAG Pipeline Analysis")
    print("=" * 60)
    
    # Test cases with more variety
    test_data = {
        "question": [
            "Give me upbeat electronic dance music",
            "Find chill acoustic songs for relaxation",
            "I want energetic rock music for working out",
            "Recommend sad ballads with piano",
            "Find happy pop songs with high danceability"
        ],
        "ground_truth": [
            "Electronic dance music with high energy (0.7+) and high danceability (0.7+), featuring synthesized beats and rhythmic elements suitable for dancing.",
            "Acoustic music with high acousticness (0.6+) and low energy (0.1-0.4), featuring organic instruments and peaceful melodies for relaxation.",
            "Rock music with high energy (0.7+) and medium to high tempo (120+ BPM), featuring guitar-driven melodies suitable for exercise motivation.",
            "Ballad music with low energy (0.1-0.4) and low valence (0.1-0.4), featuring piano prominently and emotional vocal delivery.",
            "Pop music with high valence (0.7+) and high danceability (0.7+), featuring upbeat tempo and catchy melodies."
        ]
    }
    
    # Generate contexts and answers
    contexts = []
    answers = []
    detailed_results = []
    
    for i, question in enumerate(test_data["question"]):
        print(f"\n📝 Processing Question {i+1}: {question}")
        
        try:
            # Get recommendations
            result = search_music_by_vibe.invoke({
                "query": question,
                "num_results": 5
            })
            
            parsed = json.loads(result)
            
            # Extract detailed context
            if "recommendations" in parsed and parsed["recommendations"]:
                context_parts = []
                rec_details = []
                
                for rec in parsed["recommendations"]:
                    # Basic info
                    context_part = f"{rec['track']} (similarity: {rec['similarity_score']:.3f}"
                    
                    # Add vibe profile if available
                    if "vibe_profile" in rec:
                        vibe = rec["vibe_profile"]
                        context_part += f", energy: {vibe.get('energy', 'N/A')}"
                        context_part += f", danceability: {vibe.get('danceability', 'N/A')}"
                        context_part += f", mood: {vibe.get('mood', 'N/A')}"
                    
                    context_part += ")"
                    context_parts.append(context_part)
                    rec_details.append(rec)
                
                context = " | ".join(context_parts)
                
                # Generate detailed answer
                answer = f"Based on your request for '{question}', I found {len(rec_details)} matching tracks:\n"
                for j, rec in enumerate(rec_details, 1):
                    answer += f"{j}. {rec['track']} (similarity: {rec['similarity_score']:.3f})"
                    if "vibe_profile" in rec:
                        vibe = rec["vibe_profile"]
                        answer += f" - This track has {vibe.get('energy', 'unknown')} energy"
                        answer += f" and {vibe.get('danceability', 'unknown')} danceability"
                        answer += f", giving it a {vibe.get('mood', 'neutral')} mood"
                    answer += "\n"
                
                # Store detailed results for analysis
                detailed_results.append({
                    'question': question,
                    'num_recommendations': len(rec_details),
                    'avg_similarity': sum(r['similarity_score'] for r in rec_details) / len(rec_details),
                    'recommendations': rec_details
                })
                
            else:
                context = "No recommendations found"
                answer = "I couldn't find suitable music for your request."
                detailed_results.append({
                    'question': question,
                    'num_recommendations': 0,
                    'avg_similarity': 0,
                    'recommendations': []
                })
            
            contexts.append(context)
            answers.append(answer)
            
            print(f"   ✅ Found {len(parsed.get('recommendations', []))} recommendations")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            contexts.append("Error retrieving context")
            answers.append("Error generating answer")
            detailed_results.append({
                'question': question,
                'num_recommendations': 0,
                'avg_similarity': 0,
                'recommendations': [],
                'error': str(e)
            })
    
    # Prepare dataset
    test_data["contexts"] = [[ctx] for ctx in contexts]
    test_data["answer"] = answers
    
    dataset = Dataset.from_dict(test_data)
    
    # Run RAGAs evaluation
    print(f"\n🔍 Running RAGAs Evaluation on {len(dataset)} questions...")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    embeddings = OpenAIEmbeddings()
    
    try:
        result = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=llm,
            embeddings=embeddings
        )
        
        # Analyze results
        df = result.to_pandas()
        
        print("\n" + "=" * 60)
        print("📊 RAGAs EVALUATION RESULTS")
        print("=" * 60)
        
        print("\n🎯 Overall Performance:")
        print("-" * 30)
        for metric in ['faithfulness', 'answer_relevancy', 'context_precision']:
            if metric in df.columns:
                mean_score = df[metric].mean()
                std_score = df[metric].std()
                print(f"{metric.replace('_', ' ').title():20}: {mean_score:.3f} (±{std_score:.3f})")
        
        print("\n📋 Individual Question Performance:")
        print("-" * 50)
        for i, row in df.iterrows():
            print(f"\nQuestion {i+1}: {test_data['question'][i]}")
            print(f"  Faithfulness:      {row.get('faithfulness', 'N/A'):.3f}")
            print(f"  Answer Relevancy:  {row.get('answer_relevancy', 'N/A'):.3f}")
            print(f"  Context Precision: {row.get('context_precision', 'N/A'):.3f}")
            
            # Add music-specific analysis
            detail = detailed_results[i]
            print(f"  Recommendations:   {detail['num_recommendations']}")
            if detail['num_recommendations'] > 0:
                print(f"  Avg Similarity:    {detail['avg_similarity']:.3f}")
        
        print("\n💡 Performance Analysis:")
        print("-" * 30)
        
        # Faithfulness analysis
        faithfulness_scores = df['faithfulness'].tolist()
        avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
        if avg_faithfulness > 0.8:
            print("✅ High Faithfulness: Answers are well-grounded in context")
        elif avg_faithfulness > 0.6:
            print("⚠️  Medium Faithfulness: Some answers may not be fully grounded")
        else:
            print("❌ Low Faithfulness: Answers often not grounded in context")
        
        # Answer relevancy analysis
        relevancy_scores = df['answer_relevancy'].tolist()
        avg_relevancy = sum(relevancy_scores) / len(relevancy_scores)
        if avg_relevancy > 0.8:
            print("✅ High Answer Relevancy: Responses directly address questions")
        elif avg_relevancy > 0.6:
            print("⚠️  Medium Answer Relevancy: Responses somewhat address questions")
        else:
            print("❌ Low Answer Relevancy: Responses don't address questions well")
        
        # Context precision analysis
        precision_scores = df['context_precision'].tolist()
        avg_precision = sum(precision_scores) / len(precision_scores)
        if avg_precision > 0.7:
            print("✅ High Context Precision: Retrieved context is highly relevant")
        elif avg_precision > 0.4:
            print("⚠️  Medium Context Precision: Some irrelevant context retrieved")
        else:
            print("❌ Low Context Precision: Much irrelevant context retrieved")
            print("   💡 Consider improving similarity thresholds or ranking algorithm")
        
        print("\n🎵 Music-Specific Insights:")
        print("-" * 30)
        
        total_recs = sum(d['num_recommendations'] for d in detailed_results)
        avg_recs_per_query = total_recs / len(detailed_results)
        print(f"Average recommendations per query: {avg_recs_per_query:.1f}")
        
        similarities = [d['avg_similarity'] for d in detailed_results if d['avg_similarity'] > 0]
        if similarities:
            avg_similarity = sum(similarities) / len(similarities)
            print(f"Average similarity score: {avg_similarity:.3f}")
            if avg_similarity > 0.8:
                print("✅ High similarity scores indicate good matching")
            elif avg_similarity > 0.6:
                print("⚠️  Medium similarity scores - room for improvement")
            else:
                print("❌ Low similarity scores - consider improving embeddings")
        
        # Save detailed results
        results_summary = {
            'overall_faithfulness': avg_faithfulness,
            'overall_answer_relevancy': avg_relevancy,
            'overall_context_precision': avg_precision,
            'avg_recommendations_per_query': avg_recs_per_query,
            'avg_similarity_score': avg_similarity if similarities else 0,
            'total_questions': len(test_data['question']),
            'successful_queries': sum(1 for d in detailed_results if d['num_recommendations'] > 0)
        }
        
        # Save to CSV
        df.to_csv("detailed_rag_results.csv", index=False)
        
        with open("rag_summary.json", "w") as f:
            json.dump(results_summary, f, indent=2)
        
        print(f"\n💾 Results saved:")
        print(f"   - Detailed results: detailed_rag_results.csv")
        print(f"   - Summary: rag_summary.json")
        
        return results_summary
        
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        return None

if __name__ == "__main__":
    analyze_rag_performance()
