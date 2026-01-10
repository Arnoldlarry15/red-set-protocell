"""
Tests for uncertainty tracking and confidence intervals in scoring and evaluation.
"""

import pytest
from app.engines.scoring import ScoringEngine, LayerScore, EvaluationResult
from app.agents.spotter import Spotter


class TestLayerScoreUncertainty:
    """Test LayerScore with uncertainty fields."""
    
    def test_layer_score_with_uncertainty(self):
        """Test LayerScore can store uncertainty."""
        layer = LayerScore(
            score=0.62,
            confidence=0.75,
            indicators={},
            uncertainty=0.08
        )
        
        assert layer.score == 0.62
        assert layer.uncertainty == 0.08
        assert layer.confidence_interval_lower == pytest.approx(0.54, abs=0.01)
        assert layer.confidence_interval_upper == pytest.approx(0.70, abs=0.01)
    
    def test_layer_score_confidence_interval_bounds(self):
        """Test confidence intervals are properly bounded."""
        # Case where score - uncertainty would be negative
        layer1 = LayerScore(score=0.05, confidence=0.6, indicators={}, uncertainty=0.1)
        assert layer1.confidence_interval_lower == 0.0  # Clamped to 0.0
        
        # Case where score + uncertainty would exceed 1.0
        layer2 = LayerScore(score=0.95, confidence=0.6, indicators={}, uncertainty=0.1)
        assert layer2.confidence_interval_upper == 1.0  # Clamped to 1.0
    
    def test_layer_score_uncertainty_validation(self):
        """Test uncertainty must be in valid range."""
        with pytest.raises(ValueError):
            LayerScore(score=0.5, confidence=0.6, indicators={}, uncertainty=1.5)
        
        with pytest.raises(ValueError):
            LayerScore(score=0.5, confidence=0.6, indicators={}, uncertainty=-0.1)


class TestEvaluationResultUncertainty:
    """Test EvaluationResult with uncertainty metrics."""
    
    def test_evaluation_result_with_uncertainty(self):
        """Test EvaluationResult stores uncertainty metrics."""
        l1 = LayerScore(score=0.3, confidence=0.7, indicators={}, uncertainty=0.05)
        l2 = LayerScore(score=0.5, confidence=0.8, indicators={}, uncertainty=0.08)
        l3 = LayerScore(score=0.2, confidence=0.6, indicators={}, uncertainty=0.04)
        
        result = EvaluationResult(
            l1_linguistic_safety=l1,
            l2_security_exploitability=l2,
            l3_cognitive_stability=l3,
            global_score=0.38,
            global_uncertainty=0.06,
            mutation_guidance={}
        )
        
        assert result.global_uncertainty == 0.06
        assert result.global_confidence_interval is not None
        assert len(result.global_confidence_interval) == 2
    
    def test_evaluation_result_to_dict_includes_uncertainty(self):
        """Test to_dict includes uncertainty fields."""
        l1 = LayerScore(score=0.3, confidence=0.7, indicators={}, uncertainty=0.05)
        l2 = LayerScore(score=0.5, confidence=0.8, indicators={}, uncertainty=0.08)
        l3 = LayerScore(score=0.2, confidence=0.6, indicators={}, uncertainty=0.04)
        
        result = EvaluationResult(
            l1_linguistic_safety=l1,
            l2_security_exploitability=l2,
            l3_cognitive_stability=l3,
            global_score=0.38,
            global_uncertainty=0.06,
            mutation_guidance={}
        )
        
        result_dict = result.to_dict()
        
        assert 'global_uncertainty' in result_dict
        assert 'global_confidence_interval' in result_dict
        assert 'l1_linguistic_safety' in result_dict
        assert 'uncertainty' in result_dict['l1_linguistic_safety']
        assert 'confidence_interval' in result_dict['l1_linguistic_safety']


class TestScoringEngineUncertainty:
    """Test ScoringEngine uncertainty computations."""
    
    def test_compute_global_uncertainty(self):
        """Test global uncertainty is weighted sum of layer uncertainties."""
        engine = ScoringEngine()
        
        l1_unc = 0.05
        l2_unc = 0.10
        l3_unc = 0.03
        
        global_unc = engine.compute_global_uncertainty(l1_unc, l2_unc, l3_unc)
        
        # Expected: (0.05 * 0.35) + (0.10 * 0.45) + (0.03 * 0.20)
        expected = 0.0685
        assert global_unc == pytest.approx(expected, abs=0.001)
    
    def test_create_evaluation_with_uncertainty(self):
        """Test create_evaluation handles uncertainty."""
        engine = ScoringEngine()
        
        l1_data = {'score': 0.3, 'confidence': 0.7, 'indicators': {}, 'uncertainty': 0.05}
        l2_data = {'score': 0.5, 'confidence': 0.8, 'indicators': {}, 'uncertainty': 0.08}
        l3_data = {'score': 0.2, 'confidence': 0.6, 'indicators': {}, 'uncertainty': 0.04}
        
        result = engine.create_evaluation(l1_data, l2_data, l3_data)
        
        assert result.l1_linguistic_safety.uncertainty == 0.05
        assert result.l2_security_exploitability.uncertainty == 0.08
        assert result.l3_cognitive_stability.uncertainty == 0.04
        assert result.global_uncertainty > 0
    
    def test_aggregate_multi_pass_evaluations(self):
        """Test aggregating multiple evaluation passes."""
        engine = ScoringEngine()
        
        # Simulate 3 evaluation passes with slight variations
        evaluations = [
            {
                'l1': {'score': 0.30, 'confidence': 0.7, 'indicators': {'test': {'detected': True, 'match_count': 1}}},
                'l2': {'score': 0.50, 'confidence': 0.8, 'indicators': {}},
                'l3': {'score': 0.20, 'confidence': 0.6, 'indicators': {}},
                'mutation_guidance': {}
            },
            {
                'l1': {'score': 0.32, 'confidence': 0.75, 'indicators': {'test': {'detected': True, 'match_count': 1}}},
                'l2': {'score': 0.48, 'confidence': 0.82, 'indicators': {}},
                'l3': {'score': 0.22, 'confidence': 0.65, 'indicators': {}},
                'mutation_guidance': {}
            },
            {
                'l1': {'score': 0.28, 'confidence': 0.72, 'indicators': {'test': {'detected': False, 'match_count': 0}}},
                'l2': {'score': 0.52, 'confidence': 0.78, 'indicators': {}},
                'l3': {'score': 0.18, 'confidence': 0.62, 'indicators': {}},
                'mutation_guidance': {}
            }
        ]
        
        result = engine.aggregate_multi_pass_evaluations(evaluations)
        
        # Check means are computed
        assert result.l1_linguistic_safety.score == pytest.approx(0.30, abs=0.01)
        assert result.l2_security_exploitability.score == pytest.approx(0.50, abs=0.01)
        assert result.l3_cognitive_stability.score == pytest.approx(0.20, abs=0.01)
        
        # Check uncertainties are computed (should be > 0 due to variance)
        assert result.l1_linguistic_safety.uncertainty > 0
        assert result.l2_security_exploitability.uncertainty > 0
        assert result.l3_cognitive_stability.uncertainty > 0
        
        # Check agreement score is computed
        assert result.multi_pass_agreement is not None
        assert 0.0 <= result.multi_pass_agreement <= 1.0
    
    def test_aggregate_multi_pass_high_agreement(self):
        """Test aggregation with high agreement (low variance)."""
        engine = ScoringEngine()
        
        # All passes return same scores
        evaluations = [
            {
                'l1': {'score': 0.30, 'confidence': 0.7, 'indicators': {}},
                'l2': {'score': 0.50, 'confidence': 0.8, 'indicators': {}},
                'l3': {'score': 0.20, 'confidence': 0.6, 'indicators': {}},
                'mutation_guidance': {}
            },
            {
                'l1': {'score': 0.30, 'confidence': 0.7, 'indicators': {}},
                'l2': {'score': 0.50, 'confidence': 0.8, 'indicators': {}},
                'l3': {'score': 0.20, 'confidence': 0.6, 'indicators': {}},
                'mutation_guidance': {}
            }
        ]
        
        result = engine.aggregate_multi_pass_evaluations(evaluations)
        
        # Uncertainty should be very low (scores identical)
        assert result.l1_linguistic_safety.uncertainty < 0.01
        assert result.l2_security_exploitability.uncertainty < 0.01
        assert result.l3_cognitive_stability.uncertainty < 0.01
        
        # Agreement should be very high
        assert result.multi_pass_agreement > 0.95
    
    def test_aggregate_multi_pass_low_agreement(self):
        """Test aggregation with low agreement (high variance)."""
        engine = ScoringEngine()
        
        # Passes return very different scores
        evaluations = [
            {
                'l1': {'score': 0.10, 'confidence': 0.7, 'indicators': {}},
                'l2': {'score': 0.20, 'confidence': 0.8, 'indicators': {}},
                'l3': {'score': 0.10, 'confidence': 0.6, 'indicators': {}},
                'mutation_guidance': {}
            },
            {
                'l1': {'score': 0.90, 'confidence': 0.7, 'indicators': {}},
                'l2': {'score': 0.80, 'confidence': 0.8, 'indicators': {}},
                'l3': {'score': 0.70, 'confidence': 0.6, 'indicators': {}},
                'mutation_guidance': {}
            }
        ]
        
        result = engine.aggregate_multi_pass_evaluations(evaluations)
        
        # Uncertainty should be high (scores very different)
        assert result.l1_linguistic_safety.uncertainty > 0.2
        assert result.l2_security_exploitability.uncertainty > 0.2
        assert result.l3_cognitive_stability.uncertainty > 0.1
        
        # Agreement should be low
        assert result.multi_pass_agreement < 0.6
    
    def test_compute_cross_spotter_delta(self):
        """Test computing delta between two Spotter evaluations."""
        engine = ScoringEngine()
        
        # Create two evaluations with differences
        l1_a = LayerScore(score=0.3, confidence=0.7, indicators={}, uncertainty=0.05)
        l2_a = LayerScore(score=0.5, confidence=0.8, indicators={}, uncertainty=0.08)
        l3_a = LayerScore(score=0.2, confidence=0.6, indicators={}, uncertainty=0.04)
        
        eval_a = EvaluationResult(
            l1_linguistic_safety=l1_a,
            l2_security_exploitability=l2_a,
            l3_cognitive_stability=l3_a,
            global_score=0.38,
            mutation_guidance={}
        )
        
        l1_b = LayerScore(score=0.4, confidence=0.7, indicators={}, uncertainty=0.05)
        l2_b = LayerScore(score=0.6, confidence=0.8, indicators={}, uncertainty=0.08)
        l3_b = LayerScore(score=0.3, confidence=0.6, indicators={}, uncertainty=0.04)
        
        eval_b = EvaluationResult(
            l1_linguistic_safety=l1_b,
            l2_security_exploitability=l2_b,
            l3_cognitive_stability=l3_b,
            global_score=0.48,
            mutation_guidance={}
        )
        
        delta = engine.compute_cross_spotter_delta(eval_a, eval_b)
        
        # Delta should be weighted average of layer deltas
        # L1: |0.3 - 0.4| = 0.1, L2: |0.5 - 0.6| = 0.1, L3: |0.2 - 0.3| = 0.1
        # Weighted: (0.1 * 0.35) + (0.1 * 0.45) + (0.1 * 0.20) = 0.1
        assert delta == pytest.approx(0.1, abs=0.01)
    
    def test_compute_cross_spotter_delta_identical(self):
        """Test delta is zero for identical evaluations."""
        engine = ScoringEngine()
        
        l1 = LayerScore(score=0.3, confidence=0.7, indicators={}, uncertainty=0.05)
        l2 = LayerScore(score=0.5, confidence=0.8, indicators={}, uncertainty=0.08)
        l3 = LayerScore(score=0.2, confidence=0.6, indicators={}, uncertainty=0.04)
        
        eval_a = EvaluationResult(
            l1_linguistic_safety=l1,
            l2_security_exploitability=l2,
            l3_cognitive_stability=l3,
            global_score=0.38,
            mutation_guidance={}
        )
        
        eval_b = EvaluationResult(
            l1_linguistic_safety=l1,
            l2_security_exploitability=l2,
            l3_cognitive_stability=l3,
            global_score=0.38,
            mutation_guidance={}
        )
        
        delta = engine.compute_cross_spotter_delta(eval_a, eval_b)
        assert delta == 0.0


class TestSpotterUncertainty:
    """Test Spotter uncertainty computation."""
    
    def test_spotter_compute_uncertainty_high_confidence(self):
        """Test uncertainty is low when confidence is high."""
        spotter = Spotter()
        
        # High confidence, high matches
        uncertainty = spotter._compute_uncertainty(confidence=0.9, matches=8, total_checks=10)
        
        # Should be low uncertainty
        assert uncertainty < 0.3
    
    def test_spotter_compute_uncertainty_low_confidence(self):
        """Test uncertainty is high when confidence is low."""
        spotter = Spotter()
        
        # Low confidence, few matches
        uncertainty = spotter._compute_uncertainty(confidence=0.3, matches=2, total_checks=10)
        
        # Should be high uncertainty
        assert uncertainty > 0.5
    
    @pytest.mark.asyncio
    async def test_spotter_evaluate_returns_uncertainty(self):
        """Test that evaluate returns uncertainty in results."""
        spotter = Spotter()
        
        response = "This is a test response with no special indicators."
        evaluation = await spotter.evaluate(response)
        
        assert 'l1' in evaluation
        assert 'uncertainty' in evaluation['l1']
        assert 0.0 <= evaluation['l1']['uncertainty'] <= 1.0
        
        assert 'l2' in evaluation
        assert 'uncertainty' in evaluation['l2']
        assert 0.0 <= evaluation['l2']['uncertainty'] <= 1.0
        
        assert 'l3' in evaluation
        assert 'uncertainty' in evaluation['l3']
        assert 0.0 <= evaluation['l3']['uncertainty'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_spotter_multi_pass_disabled_by_default(self):
        """Test multi-pass is disabled by default."""
        spotter = Spotter()
        
        response = "Test response"
        evaluation = await spotter.evaluate_with_paraphrase(response)
        
        # Should return single evaluation, not multi-pass
        assert 'l1' in evaluation
        assert 'multi_pass' not in evaluation
    
    @pytest.mark.asyncio
    async def test_spotter_multi_pass_enabled(self):
        """Test multi-pass evaluation when enabled."""
        spotter = Spotter(enable_multi_pass=True, multi_pass_count=3)
        
        response = "Test response"
        result = await spotter.evaluate_with_paraphrase(response)
        
        # Should return multi-pass structure
        assert result['multi_pass'] is True
        assert result['pass_count'] == 3
        assert 'evaluations' in result
        assert len(result['evaluations']) == 3
    
    @pytest.mark.asyncio
    async def test_spotter_cross_evaluate(self):
        """Test cross-evaluation between two Spotters."""
        spotter1 = Spotter(confidence_threshold=0.6)
        spotter2 = Spotter(confidence_threshold=0.8)
        
        response = "Test response with some concerning content."
        result = await spotter1.cross_evaluate(response, spotter2)
        
        assert result['cross_spotter'] is True
        assert 'evaluation_1' in result
        assert 'evaluation_2' in result
        assert 'deltas' in result
        assert 'l1' in result['deltas']
        assert 'l2' in result['deltas']
        assert 'l3' in result['deltas']
    
    @pytest.mark.asyncio
    async def test_spotter_cross_evaluate_deltas_range(self):
        """Test cross-evaluation deltas are in valid range."""
        spotter1 = Spotter(confidence_threshold=0.5)
        spotter2 = Spotter(confidence_threshold=0.9)
        
        response = "This is a test response."
        result = await spotter1.cross_evaluate(response, spotter2)
        
        # All deltas should be between 0.0 and 1.0
        assert 0.0 <= result['deltas']['l1'] <= 1.0
        assert 0.0 <= result['deltas']['l2'] <= 1.0
        assert 0.0 <= result['deltas']['l3'] <= 1.0


class TestIntegrationUncertainty:
    """Integration tests for uncertainty tracking in full workflow."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_uncertainty(self):
        """Test full workflow from Spotter to ScoringEngine with uncertainty."""
        spotter = Spotter()
        engine = ScoringEngine()
        
        response = "I apologize, but I can't help with that request."
        
        # Spotter evaluates
        spotter_result = await spotter.evaluate(response)
        
        # ScoringEngine creates evaluation
        evaluation = engine.create_evaluation(
            spotter_result['l1'],
            spotter_result['l2'],
            spotter_result['l3'],
            spotter_result['mutation_guidance']
        )
        
        # Should have uncertainty at all levels
        assert evaluation.l1_linguistic_safety.uncertainty >= 0
        assert evaluation.l2_security_exploitability.uncertainty >= 0
        assert evaluation.l3_cognitive_stability.uncertainty >= 0
        assert evaluation.global_uncertainty >= 0
        
        # Confidence intervals should be set
        assert evaluation.l1_linguistic_safety.confidence_interval_lower >= 0
        assert evaluation.l1_linguistic_safety.confidence_interval_upper <= 1.0
        assert evaluation.global_confidence_interval is not None
    
    @pytest.mark.asyncio
    async def test_multi_pass_integration(self):
        """Test multi-pass evaluation full workflow."""
        spotter = Spotter(enable_multi_pass=True, multi_pass_count=3)
        engine = ScoringEngine()
        
        response = "Test response for multi-pass evaluation."
        
        # Get multi-pass results
        multi_pass_result = await spotter.evaluate_with_paraphrase(response)
        
        assert multi_pass_result['multi_pass'] is True
        
        # Aggregate with scoring engine
        aggregated = engine.aggregate_multi_pass_evaluations(multi_pass_result['evaluations'])
        
        # Should have agreement score
        assert aggregated.multi_pass_agreement is not None
        assert 0.0 <= aggregated.multi_pass_agreement <= 1.0
        
        # Should have uncertainties based on variance
        assert aggregated.global_uncertainty >= 0
