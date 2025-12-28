"""Data models for analysis results."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class ModelInfo:
    """Information about a Hugging Face model."""
    name: str
    author: str
    description: Optional[str]
    tags: List[str]
    pipeline_tag: Optional[str]
    library_name: Optional[str]
    license: Optional[str]
    downloads: int
    likes: int
    created_at: str
    last_modified: str
    model_size: Optional[int]
    config: Dict[str, Any]
    files: List[Dict[str, Any]]


@dataclass
class AIBOM:
    """AI Bill of Materials structure."""
    bom_format: str
    spec_version: str
    serial_number: str
    version: int
    metadata: Dict[str, Any]
    components: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]
    vulnerabilities: List[Dict[str, Any]]
    compositions: List[Dict[str, Any]]


@dataclass
class SecurityAnalysis:
    """Security analysis results from Bedrock Agent."""
    risk_score: float  # 0-10 scale
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    vulnerabilities: List[Dict[str, Any]]
    compliance_issues: List[Dict[str, Any]]
    recommendations: List[str]
    unsafe_formats: List[str]
    suspicious_files: List[str]
    license_issues: List[str]


@dataclass
class AnalysisResult:
    """Result of analyzing a single model."""
    model_name: str
    model_info: ModelInfo
    aibom: AIBOM
    security_analysis: SecurityAnalysis
    timestamp: float
    report_path: Optional[str] = None
    
    @property
    def security_issues_count(self) -> int:
        """Total number of security issues found."""
        return len(self.security_analysis.vulnerabilities)
    
    @property
    def compliance_gaps_count(self) -> int:
        """Total number of compliance gaps found."""
        return len(self.security_analysis.compliance_issues)


@dataclass
class ModelComparison:
    """Comparison between multiple models."""
    common_components: List[Dict[str, Any]]
    unique_components: Dict[str, List[Dict[str, Any]]]
    security_comparison: Dict[str, Any]
    license_comparison: Dict[str, Any]
    size_comparison: Dict[str, Any]
    dependency_analysis: Dict[str, Any]


@dataclass
class ComparisonInsights:
    """AI-generated insights from model comparison."""
    summary: str
    key_differences: List[str]
    security_recommendations: List[str]
    best_practices: List[str]
    risk_assessment: str


@dataclass
class ComparisonResult:
    """Result of comparing multiple models."""
    model_names: List[str]
    individual_results: List[AnalysisResult]
    comparison: ModelComparison
    insights: ComparisonInsights
    timestamp: float
    report_path: Optional[str] = None
    
    @property
    def security_issues_count(self) -> int:
        """Total security issues across all models."""
        return sum(result.security_issues_count for result in self.individual_results)
    
    @property
    def compliance_gaps_count(self) -> int:
        """Total compliance gaps across all models."""
        return sum(result.compliance_gaps_count for result in self.individual_results)