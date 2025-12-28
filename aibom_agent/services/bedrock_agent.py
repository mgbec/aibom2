"""Bedrock Agent service for AI-powered security analysis."""

import json
from typing import Dict, Any, List

import boto3
from loguru import logger

from ..config.settings import AWSSettings
from ..models.analysis_result import AIBOM, ModelInfo, SecurityAnalysis, ModelComparison, ComparisonInsights


class BedrockAgentService:
    """Service for AI-powered security analysis using AWS Bedrock."""
    
    def __init__(self, settings: AWSSettings):
        self.settings = settings
        self.bedrock_client = None
        self.bedrock_runtime_client = None
    
    async def initialize(self) -> None:
        """Initialize Bedrock clients."""
        logger.info("Initializing Bedrock Agent service...")
        
        self.bedrock_client = boto3.client(
            'bedrock-agent',
            region_name=self.settings.region
        )
        
        self.bedrock_runtime_client = boto3.client(
            'bedrock-agent-runtime',
            region_name=self.settings.region
        )
        
        logger.info("Bedrock Agent service initialized successfully")
    
    async def analyze_security(self, aibom: AIBOM, model_info: ModelInfo) -> SecurityAnalysis:
        """
        Perform AI-powered security analysis of an AIBOM.
        
        Args:
            aibom: The AI Bill of Materials to analyze
            model_info: Additional model information
            
        Returns:
            SecurityAnalysis with risk assessment and recommendations
        """
        logger.info(f"Performing security analysis for model: {model_info.name}")
        
        try:
            # Prepare analysis prompt
            analysis_prompt = self._create_security_analysis_prompt(aibom, model_info)
            
            # Call Bedrock for analysis
            response = await self._invoke_bedrock_model(analysis_prompt)
            
            # Parse response into SecurityAnalysis
            security_analysis = self._parse_security_analysis(response)
            
            logger.info(f"Security analysis completed for {model_info.name}")
            return security_analysis
            
        except Exception as e:
            logger.error(f"Failed to perform security analysis: {e}")
            # Return default analysis on failure
            return self._create_default_security_analysis()
    
    async def generate_comparison_insights(self, comparison: ModelComparison) -> ComparisonInsights:
        """
        Generate AI-powered insights from model comparison.
        
        Args:
            comparison: ModelComparison data
            
        Returns:
            ComparisonInsights with AI-generated analysis
        """
        logger.info("Generating comparison insights...")
        
        try:
            # Prepare comparison prompt
            insights_prompt = self._create_comparison_insights_prompt(comparison)
            
            # Call Bedrock for insights
            response = await self._invoke_bedrock_model(insights_prompt)
            
            # Parse response into ComparisonInsights
            insights = self._parse_comparison_insights(response)
            
            logger.info("Comparison insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate comparison insights: {e}")
            # Return default insights on failure
            return self._create_default_comparison_insights()
    
    def _create_security_analysis_prompt(self, aibom: AIBOM, model_info: ModelInfo) -> str:
        """Create a prompt for security analysis."""
        return f"""
You are a cybersecurity expert specializing in AI/ML model security analysis. 
Analyze the following AI Bill of Materials (AIBOM) and model information to identify security risks.

Model Information:
- Name: {model_info.name}
- Author: {model_info.author}
- License: {model_info.license}
- Downloads: {model_info.downloads}
- Tags: {', '.join(model_info.tags)}
- Pipeline: {model_info.pipeline_tag}

AIBOM Summary:
- Components: {len(aibom.components)}
- Dependencies: {len(aibom.dependencies)}
- Known Vulnerabilities: {len(aibom.vulnerabilities)}

AIBOM Components:
{json.dumps(aibom.components[:10], indent=2)}  # First 10 components

Please provide a comprehensive security analysis in JSON format with:
{{
    "risk_score": <float 0-10>,
    "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
    "vulnerabilities": [
        {{"type": "...", "severity": "...", "description": "...", "cve_id": "..."}}
    ],
    "compliance_issues": [
        {{"category": "...", "issue": "...", "recommendation": "..."}}
    ],
    "recommendations": ["..."],
    "unsafe_formats": ["..."],
    "suspicious_files": ["..."],
    "license_issues": ["..."]
}}

Focus on:
1. Known vulnerabilities in dependencies
2. Unsafe file formats (pickle, etc.)
3. License compliance issues
4. Suspicious or unexpected components
5. Security best practices violations
"""
    
    def _create_comparison_insights_prompt(self, comparison: ModelComparison) -> str:
        """Create a prompt for comparison insights."""
        return f"""
You are an AI/ML expert analyzing differences between multiple AI models.
Generate insights from the following model comparison data.

Common Components: {len(comparison.common_components)}
Unique Components per Model: {comparison.unique_components}
Security Comparison: {comparison.security_comparison}
License Comparison: {comparison.license_comparison}

Please provide insights in JSON format:
{{
    "summary": "Brief overview of key findings",
    "key_differences": ["List of main differences"],
    "security_recommendations": ["Security-focused recommendations"],
    "best_practices": ["Best practice recommendations"],
    "risk_assessment": "Overall risk assessment across models"
}}

Focus on:
1. Security implications of differences
2. Compliance and licensing considerations
3. Performance and reliability factors
4. Best practices for model selection
"""
    
    async def _invoke_bedrock_model(self, prompt: str) -> str:
        """Invoke Bedrock model for analysis."""
        try:
            # Use Claude 3 Sonnet for analysis
            model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Failed to invoke Bedrock model: {e}")
            raise
    
    def _parse_security_analysis(self, response: str) -> SecurityAnalysis:
        """Parse Bedrock response into SecurityAnalysis."""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            
            data = json.loads(json_str)
            
            return SecurityAnalysis(
                risk_score=float(data.get('risk_score', 5.0)),
                risk_level=data.get('risk_level', 'MEDIUM'),
                vulnerabilities=data.get('vulnerabilities', []),
                compliance_issues=data.get('compliance_issues', []),
                recommendations=data.get('recommendations', []),
                unsafe_formats=data.get('unsafe_formats', []),
                suspicious_files=data.get('suspicious_files', []),
                license_issues=data.get('license_issues', [])
            )
            
        except Exception as e:
            logger.error(f"Failed to parse security analysis: {e}")
            return self._create_default_security_analysis()
    
    def _parse_comparison_insights(self, response: str) -> ComparisonInsights:
        """Parse Bedrock response into ComparisonInsights."""
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            
            data = json.loads(json_str)
            
            return ComparisonInsights(
                summary=data.get('summary', 'Analysis completed'),
                key_differences=data.get('key_differences', []),
                security_recommendations=data.get('security_recommendations', []),
                best_practices=data.get('best_practices', []),
                risk_assessment=data.get('risk_assessment', 'Medium risk')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse comparison insights: {e}")
            return self._create_default_comparison_insights()
    
    def _create_default_security_analysis(self) -> SecurityAnalysis:
        """Create default security analysis when AI analysis fails."""
        return SecurityAnalysis(
            risk_score=5.0,
            risk_level="MEDIUM",
            vulnerabilities=[],
            compliance_issues=[],
            recommendations=["Manual security review recommended"],
            unsafe_formats=[],
            suspicious_files=[],
            license_issues=[]
        )
    
    def _create_default_comparison_insights(self) -> ComparisonInsights:
        """Create default comparison insights when AI analysis fails."""
        return ComparisonInsights(
            summary="Comparison analysis completed with limited insights",
            key_differences=["Manual analysis required"],
            security_recommendations=["Perform detailed security review"],
            best_practices=["Follow ML security best practices"],
            risk_assessment="Manual assessment required"
        )
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up Bedrock Agent service...")
        # No specific cleanup needed for boto3 clients
        pass