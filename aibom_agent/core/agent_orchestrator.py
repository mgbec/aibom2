"""AIBOM Agent Orchestrator - coordinates all AIBOM analysis workflows."""

import asyncio
from typing import List, Optional

from loguru import logger

from ..config.settings import Settings
from ..models.analysis_result import AnalysisResult, ComparisonResult
from ..services.aibom_generator import AIBOMGenerator
from ..services.bedrock_agent import BedrockAgentService
from ..services.huggingface_service import HuggingFaceService
from ..services.comparison_engine import ComparisonEngine
from ..services.report_generator import ReportGenerator


class AIBOMAgentOrchestrator:
    """
    Orchestrates AIBOM analysis workflows within AgentCore runtime.
    
    This class coordinates between different services to provide
    intelligent AIBOM generation and analysis capabilities.
    """
    
    def __init__(self, settings: Settings, session_id: Optional[str] = None):
        self.settings = settings
        self.session_id = session_id or "default"
        self.settings.ensure_directories()
        
        # Initialize services
        self.hf_service = HuggingFaceService(settings.huggingface)
        self.aibom_generator = AIBOMGenerator(settings.aibom)
        self.bedrock_agent = BedrockAgentService(settings.aws)
        self.comparison_engine = ComparisonEngine()
        self.report_generator = ReportGenerator(settings.output_dir)
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all services."""
        if self._initialized:
            return
            
        logger.info(f"Initializing AIBOM Agent Orchestrator for session: {self.session_id}")
        
        # Initialize services
        await self.hf_service.initialize()
        await self.aibom_generator.initialize()
        await self.bedrock_agent.initialize()
        
        self._initialized = True
        logger.info("AIBOM Agent Orchestrator initialized successfully")
    
    async def analyze_single_model(self, model_name: str) -> AnalysisResult:
        """
        Analyze a single Hugging Face model and generate AIBOM.
        
        Args:
            model_name: Name of the Hugging Face model to analyze
            
        Returns:
            AnalysisResult containing AIBOM and security analysis
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"[Session: {self.session_id}] Starting analysis for model: {model_name}")
        
        try:
            # Step 1: Fetch model information from Hugging Face
            model_info = await self.hf_service.get_model_info(model_name)
            logger.info(f"Retrieved model info for {model_name}")
            
            # Step 2: Generate AIBOM using OWASP generator
            aibom = await self.aibom_generator.generate_aibom(model_info)
            logger.info(f"Generated AIBOM for {model_name}")
            
            # Step 3: Perform security analysis using Bedrock Agent
            security_analysis = await self.bedrock_agent.analyze_security(aibom, model_info)
            logger.info(f"Completed security analysis for {model_name}")
            
            # Step 4: Generate analysis result
            result = AnalysisResult(
                model_name=model_name,
                model_info=model_info,
                aibom=aibom,
                security_analysis=security_analysis,
                timestamp=asyncio.get_event_loop().time()
            )
            
            # Step 5: Generate HTML report
            report_path = await self.report_generator.generate_single_model_report(result)
            result.report_path = report_path
            
            logger.info(f"Analysis completed for {model_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze model {model_name}: {e}")
            raise
    
    async def compare_models(self, model_names: List[str]) -> ComparisonResult:
        """
        Compare multiple Hugging Face models and generate comparative analysis.
        
        Args:
            model_names: List of Hugging Face model names to compare
            
        Returns:
            ComparisonResult containing comparative analysis and report
        """
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"[Session: {self.session_id}] Starting comparative analysis for {len(model_names)} models")
        
        try:
            # Step 1: Analyze each model individually
            analysis_tasks = [self.analyze_single_model(name) for name in model_names]
            individual_results = await asyncio.gather(*analysis_tasks)
            
            # Step 2: Perform comparative analysis
            comparison = await self.comparison_engine.compare_models(individual_results)
            logger.info("Completed comparative analysis")
            
            # Step 3: Generate insights using Bedrock Agent
            insights = await self.bedrock_agent.generate_comparison_insights(comparison)
            logger.info("Generated AI-powered insights")
            
            # Step 4: Create comparison result
            result = ComparisonResult(
                model_names=model_names,
                individual_results=individual_results,
                comparison=comparison,
                insights=insights,
                timestamp=asyncio.get_event_loop().time()
            )
            
            # Step 5: Generate comparative report
            report_path = await self.report_generator.generate_comparison_report(result)
            result.report_path = report_path
            
            logger.info(f"Comparative analysis completed for {len(model_names)} models")
            return result
            
        except Exception as e:
            logger.error(f"Failed to compare models {model_names}: {e}")
            raise