"""Comparison engine for analyzing differences between models."""

from typing import List, Dict, Any, Set
from collections import defaultdict

from loguru import logger

from ..models.analysis_result import AnalysisResult, ModelComparison


class ComparisonEngine:
    """Engine for comparing multiple AI models and their AIBOMs."""
    
    async def compare_models(self, results: List[AnalysisResult]) -> ModelComparison:
        """
        Compare multiple model analysis results.
        
        Args:
            results: List of AnalysisResult objects to compare
            
        Returns:
            ModelComparison with detailed comparison data
        """
        logger.info(f"Comparing {len(results)} models")
        
        try:
            # Extract components from all models
            all_components = self._extract_all_components(results)
            
            # Find common and unique components
            common_components = self._find_common_components(all_components)
            unique_components = self._find_unique_components(all_components)
            
            # Compare security aspects
            security_comparison = self._compare_security(results)
            
            # Compare licenses
            license_comparison = self._compare_licenses(results)
            
            # Compare sizes
            size_comparison = self._compare_sizes(results)
            
            # Analyze dependencies
            dependency_analysis = self._analyze_dependencies(results)
            
            comparison = ModelComparison(
                common_components=common_components,
                unique_components=unique_components,
                security_comparison=security_comparison,
                license_comparison=license_comparison,
                size_comparison=size_comparison,
                dependency_analysis=dependency_analysis
            )
            
            logger.info("Model comparison completed successfully")
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare models: {e}")
            raise
    
    def _extract_all_components(self, results: List[AnalysisResult]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract components from all models."""
        all_components = {}
        
        for result in results:
            all_components[result.model_name] = result.aibom.components
        
        return all_components
    
    def _find_common_components(self, all_components: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find components that are common across all models."""
        if not all_components:
            return []
        
        # Get component names from first model
        model_names = list(all_components.keys())
        first_model_components = {
            comp.get('name', ''): comp 
            for comp in all_components[model_names[0]]
        }
        
        common_components = []
        
        # Check which components exist in all models
        for comp_name, comp_data in first_model_components.items():
            is_common = True
            
            for model_name in model_names[1:]:
                model_comp_names = {comp.get('name', '') for comp in all_components[model_name]}
                if comp_name not in model_comp_names:
                    is_common = False
                    break
            
            if is_common:
                common_components.append({
                    **comp_data,
                    'found_in_models': model_names
                })
        
        return common_components
    
    def _find_unique_components(self, all_components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Find components that are unique to each model."""
        unique_components = {}
        
        # Get all component names across all models
        all_comp_names = set()
        model_comp_names = {}
        
        for model_name, components in all_components.items():
            comp_names = {comp.get('name', '') for comp in components}
            model_comp_names[model_name] = comp_names
            all_comp_names.update(comp_names)
        
        # Find unique components for each model
        for model_name, components in all_components.items():
            unique_to_model = []
            
            for comp in components:
                comp_name = comp.get('name', '')
                
                # Check if this component exists in other models
                is_unique = True
                for other_model, other_comp_names in model_comp_names.items():
                    if other_model != model_name and comp_name in other_comp_names:
                        is_unique = False
                        break
                
                if is_unique:
                    unique_to_model.append(comp)
            
            unique_components[model_name] = unique_to_model
        
        return unique_components
    
    def _compare_security(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Compare security aspects across models."""
        security_comparison = {
            'risk_scores': {},
            'risk_levels': {},
            'vulnerability_counts': {},
            'compliance_issue_counts': {},
            'highest_risk_model': '',
            'lowest_risk_model': '',
            'common_vulnerabilities': [],
            'unique_vulnerabilities': {}
        }
        
        risk_scores = {}
        
        for result in results:
            model_name = result.model_name
            security = result.security_analysis
            
            risk_scores[model_name] = security.risk_score
            security_comparison['risk_scores'][model_name] = security.risk_score
            security_comparison['risk_levels'][model_name] = security.risk_level
            security_comparison['vulnerability_counts'][model_name] = len(security.vulnerabilities)
            security_comparison['compliance_issue_counts'][model_name] = len(security.compliance_issues)
        
        # Find highest and lowest risk models
        if risk_scores:
            security_comparison['highest_risk_model'] = max(risk_scores, key=risk_scores.get)
            security_comparison['lowest_risk_model'] = min(risk_scores, key=risk_scores.get)
        
        return security_comparison
    
    def _compare_licenses(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Compare license information across models."""
        license_comparison = {
            'licenses_by_model': {},
            'common_licenses': [],
            'license_conflicts': [],
            'unlicensed_models': []
        }
        
        all_licenses = set()
        
        for result in results:
            model_license = result.model_info.license
            license_comparison['licenses_by_model'][result.model_name] = model_license
            
            if model_license:
                all_licenses.add(model_license)
            else:
                license_comparison['unlicensed_models'].append(result.model_name)
        
        # Find common licenses (if any)
        license_counts = defaultdict(int)
        for result in results:
            if result.model_info.license:
                license_counts[result.model_info.license] += 1
        
        # Licenses that appear in multiple models
        license_comparison['common_licenses'] = [
            license for license, count in license_counts.items() 
            if count > 1
        ]
        
        return license_comparison
    
    def _compare_sizes(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Compare model sizes."""
        size_comparison = {
            'sizes_by_model': {},
            'largest_model': '',
            'smallest_model': '',
            'average_size': 0,
            'size_distribution': {}
        }
        
        sizes = {}
        valid_sizes = []
        
        for result in results:
            model_size = result.model_info.model_size
            sizes[result.model_name] = model_size
            size_comparison['sizes_by_model'][result.model_name] = model_size
            
            if model_size:
                valid_sizes.append(model_size)
        
        if valid_sizes:
            size_comparison['largest_model'] = max(sizes, key=lambda k: sizes[k] or 0)
            size_comparison['smallest_model'] = min(sizes, key=lambda k: sizes[k] or float('inf'))
            size_comparison['average_size'] = sum(valid_sizes) / len(valid_sizes)
        
        return size_comparison
    
    def _analyze_dependencies(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Analyze dependencies across models."""
        dependency_analysis = {
            'dependencies_by_model': {},
            'common_dependencies': [],
            'unique_dependencies': {},
            'dependency_conflicts': []
        }
        
        all_deps = {}
        
        for result in results:
            model_deps = result.aibom.dependencies
            dependency_analysis['dependencies_by_model'][result.model_name] = model_deps
            all_deps[result.model_name] = {dep.get('name', ''): dep for dep in model_deps}
        
        # Find common dependencies
        if all_deps:
            first_model = list(all_deps.keys())[0]
            common_dep_names = set(all_deps[first_model].keys())
            
            for model_name in list(all_deps.keys())[1:]:
                common_dep_names &= set(all_deps[model_name].keys())
            
            dependency_analysis['common_dependencies'] = list(common_dep_names)
        
        return dependency_analysis