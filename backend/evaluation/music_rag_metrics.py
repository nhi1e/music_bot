#!/usr/bin/env python3
"""
Custom Music-Specific RAG Evaluation Metrics
"""

import numpy as np
import json
from typing import List, Dict, Any
from app.tools.vector_search_tool import search_music_by_vibe

class MusicRAGMetrics:
    """Custom evaluation metrics specific to music recommendation"""
    
    def __init__(self):
        pass
    
    def audio_feature_relevance(self, query: str, recommendations: List[Dict]) -> float:
        """
        Evaluate how well the audio features of recommended songs match the query intent
        """
        # Extract audio characteristics from query
        query_lower = query.lower()
        
        # Define characteristic mappings
        characteristics = {
            'energy': {
                'high': ['energetic', 'upbeat', 'intense', 'powerful', 'workout', 'gym'],
                'low': ['chill', 'calm', 'relaxed', 'mellow', 'peaceful', 'ambient']
            },
            'danceability': {
                'high': ['danceable', 'groovy', 'rhythmic', 'dance', 'party'],
                'low': ['slow', 'ballad', 'contemplative']
            },
            'valence': {
                'high': ['happy', 'upbeat', 'joyful', 'positive', 'cheerful'],
                'low': ['sad', 'melancholy', 'depressing', 'emotional']
            },
            'acousticness': {
                'high': ['acoustic', 'unplugged', 'organic', 'natural'],
                'low': ['electronic', 'synthesized', 'digital', 'produced']
            }
        }
        
        # Score each recommendation
        scores = []
        for rec in recommendations:
            if 'vibe_profile' not in rec:
                continue
                
            vibe = rec['vibe_profile']
            rec_score = 0
            feature_count = 0
            
            for feature, ranges in characteristics.items():
                if feature in vibe:
                    feature_value = float(vibe[feature])
                    feature_count += 1
                    
                    # Check if query mentions this feature
                    for level, keywords in ranges.items():
                        if any(keyword in query_lower for keyword in keywords):
                            if level == 'high' and feature_value > 0.6:
                                rec_score += 1
                            elif level == 'low' and feature_value < 0.4:
                                rec_score += 1
            
            if feature_count > 0:
                scores.append(rec_score / feature_count)
        
        return np.mean(scores) if scores else 0.0
    
    def genre_consistency(self, query: str, recommendations: List[Dict]) -> float:
        """
        Evaluate if recommended songs match the requested genre
        """
        query_lower = query.lower()
        
        # Extract genre from query
        genres = ['pop', 'rock', 'jazz', 'electronic', 'hip-hop', 'country', 'classical', 
                 'k-pop', 'indie', 'folk', 'blues', 'metal', 'reggae', 'r&b']
        
        requested_genre = None
        for genre in genres:
            if genre in query_lower or genre.replace('-', ' ') in query_lower:
                requested_genre = genre
                break
        
        if not requested_genre:
            return 1.0  # No specific genre requested
        
        # Check if recommendations mention or contain the genre
        matching_count = 0
        for rec in recommendations:
            track_info = rec.get('track', '').lower()
            if 'genre' in rec:
                rec_genre = rec['genre'].lower()
                if requested_genre in rec_genre or rec_genre in requested_genre:
                    matching_count += 1
            # Also check in track name/artist for genre indicators
            elif requested_genre in track_info:
                matching_count += 0.5
        
        return matching_count / len(recommendations) if recommendations else 0.0
    
    def similarity_coherence(self, recommendations: List[Dict]) -> float:
        """
        Evaluate if the similarity scores make sense (higher scores should be more relevant)
        """
        similarities = [rec.get('similarity_score', 0) for rec in recommendations]
        
        if len(similarities) < 2:
            return 1.0
        
        # Check if similarities are in descending order (more relevant first)
        sorted_similarities = sorted(similarities, reverse=True)
        
        # Calculate how close the actual order is to the ideal sorted order
        correlation = np.corrcoef(similarities, sorted_similarities)[0, 1]
        return max(0, correlation) if not np.isnan(correlation) else 0.0
    
    def diversity_score(self, recommendations: List[Dict]) -> float:
        """
        Evaluate the diversity of recommendations (avoid too similar songs)
        """
        if len(recommendations) < 2:
            return 1.0
        
        # Extract unique artists
        artists = set()
        for rec in recommendations:
            track = rec.get('track', '')
            if ' by ' in track:
                artist = track.split(' by ')[1]
                artists.add(artist)
        
        # Diversity = unique artists / total recommendations
        artist_diversity = len(artists) / len(recommendations)
        
        # Also check audio feature diversity
        if all('vibe_profile' in rec for rec in recommendations):
            feature_values = []
            for rec in recommendations:
                vibe = rec['vibe_profile']
                features = [vibe.get('danceability', 0), vibe.get('energy', 0)]
                feature_values.append(features)
            
            if len(feature_values) > 1:
                feature_array = np.array(feature_values)
                feature_diversity = np.std(feature_array, axis=0).mean()
            else:
                feature_diversity = 0
        else:
            feature_diversity = 0
        
        # Combine artist and feature diversity
        return (artist_diversity + min(feature_diversity, 1.0)) / 2
    
    def evaluate_music_rag_response(self, query: str, response: str) -> Dict[str, float]:
        """
        Comprehensive evaluation of a music RAG response
        """
        try:
            # Parse the response if it's JSON
            if response.startswith('{'):
                parsed_response = json.loads(response)
                recommendations = parsed_response.get('recommendations', [])
            else:
                # If response is text, try to extract recommendations
                recommendations = []
                # This would need more sophisticated parsing for text responses
        
            metrics = {
                'audio_feature_relevance': self.audio_feature_relevance(query, recommendations),
                'genre_consistency': self.genre_consistency(query, recommendations),
                'similarity_coherence': self.similarity_coherence(recommendations),
                'diversity_score': self.diversity_score(recommendations),
                'response_completeness': 1.0 if recommendations else 0.0
            }
            
            # Overall score
            metrics['overall_music_score'] = np.mean(list(metrics.values()))
            
            return metrics
            
        except Exception as e:
            print(f"Error evaluating response: {e}")
            return {
                'audio_feature_relevance': 0.0,
                'genre_consistency': 0.0,
                'similarity_coherence': 0.0,
                'diversity_score': 0.0,
                'response_completeness': 0.0,
                'overall_music_score': 0.0
            }

def test_music_metrics():
    """Test the custom music metrics"""
    evaluator = MusicRAGMetrics()
    
    # Test query
    test_query = "Give me upbeat electronic dance music"
    
    # Get response from your system
    result = search_music_by_vibe.invoke({
        "query": test_query,
        "num_results": 5
    })
    
    # Evaluate
    metrics = evaluator.evaluate_music_rag_response(test_query, result)
    
    print("🎵 Music-Specific RAG Metrics:")
    print("=" * 40)
    for metric, score in metrics.items():
        print(f"{metric.replace('_', ' ').title()}: {score:.3f}")

if __name__ == "__main__":
    test_music_metrics()
