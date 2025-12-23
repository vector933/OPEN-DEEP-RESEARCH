"""
Session Context Manager
=======================
Handles intelligent context awareness for follow-up queries.
Implements behavioral rules for maintaining paper context across conversation.
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class QueryIntent(Enum):
    """Types of user query intents."""
    NEW_RESEARCH = "new_research"
    SUMMARY_REQUEST = "summary_request"
    METHODOLOGY_REQUEST = "methodology_request"
    FINDINGS_REQUEST = "findings_request"
    COMPARISON_REQUEST = "comparison_request"
    REFERENCE_REQUEST = "reference_request"
    CLARIFICATION_REQUEST = "clarification_request"
    FOLLOWUP_VAGUE = "followup_vague"


@dataclass
class SessionContext:
    """Represents the current session's context."""
    chat_id: int
    last_research_topic: Optional[str] = None
    last_paper_title: Optional[str] = None
    last_papers: List[Dict] = None
    last_report: Optional[str] = None
    last_methodology: Optional[str] = None
    last_findings: Optional[str] = None
    
    def __post_init__(self):
        if self.last_papers is None:
            self.last_papers = []


class ContextAwareIntentDetector:
    """
    Detects user intent with session context awareness.
    
    Core Behavioral Rules:
    1. Maintain Context: Prioritize information from earlier in session
    2. Session Persistence: Follow-up questions refer to previous papers
    3. Clarification: Vague questions default to previously discussed paper
    """
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        QueryIntent.SUMMARY_REQUEST: [
            r'\b(summarize|summary|tldr|brief|overview)\b',
            r'\b(what (was|is) (it|this|that) about)\b',
            r'\b(give me (a|the) summary)\b',
            r'\b(recap|brief overview)\b',
            r'\bwhat did (we|you) (discuss|find|talk about)\b',
        ],
        QueryIntent.METHODOLOGY_REQUEST: [
            r'\b(methodology|method|approach|technique)\b',
            r'\b(how (did|was|were) (they|it|the study))\b',
            r'\b(research (method|design|approach))\b',
            r'\b(what (approach|method) (did|was))\b',
            r'\b(experimental (design|setup|procedure))\b',
            r'\b(sample size|data collection|analysis)\b',
        ],
        QueryIntent.FINDINGS_REQUEST: [
            r'\b(findings|results|outcomes|conclusions?)\b',
            r'\b(what (did they|was) (find|discover|conclude))\b',
            r'\b(key (findings|results|takeaways))\b',
            r'\b(main (results|conclusions))\b',
        ],
        QueryIntent.COMPARISON_REQUEST: [
            r'\b(compare|comparison|versus|vs\.?|difference)\b',
            r'\b(how (does|is) (it|this) (different|similar))\b',
            r'\b(contrast (with|to))\b',
            r'\b(similarities (and|or) differences)\b',
        ],
        QueryIntent.REFERENCE_REQUEST: [
            r'\b(references?|citations?|sources?|papers?)\b',
            r'\b(which papers?|what (papers|sources))\b',
            r'\b(bibliography|works cited)\b',
            r'\b(show (me )?(the )?(papers|sources|references))\b',
        ],
    }
    
    # Pronouns and vague references that indicate context dependency
    CONTEXT_INDICATORS = [
        r'\b(this|that|it|the paper|the study|the article)\b',
        r'\b(previously|earlier|before|above)\b',
        r'\b(tell me more|more (about|on|info))\b',
        r'\b(what about|how about)\b',
        r'^(and|also|additionally)\b',
    ]
    
    def detect_intent(
        self, 
        query: str, 
        conversation_history: List[Dict],
        current_context: SessionContext
    ) -> Tuple[QueryIntent, float]:
        """
        Detect user's intent from query and context.
        
        Args:
            query: User's current query
            conversation_history: Previous messages in session
            current_context: Current session context
            
        Returns:
            Tuple of (QueryIntent, confidence_score)
        """
        query_lower = query.lower().strip()
        
        # Check for explicit intent patterns first
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent, 0.9
        
        # Check if query contains context indicators
        has_context_indicator = any(
            re.search(pattern, query_lower) 
            for pattern in self.CONTEXT_INDICATORS
        )
        
        # If very short query with context indicators and we have history
        if has_context_indicator and conversation_history:
            # This is a vague follow-up - assume it's about previous topic
            return QueryIntent.FOLLOWUP_VAGUE, 0.7
        
        # Check if query is very short (< 5 words) and we have context
        word_count = len(query.split())
        if word_count < 5 and current_context.last_research_topic:
            return QueryIntent.FOLLOWUP_VAGUE, 0.6
        
        # Default: treat as new research query
        return QueryIntent.NEW_RESEARCH, 0.5
    
    def should_use_context(self, intent: QueryIntent) -> bool:
        """Check if this intent should use session context."""
        return intent in [
            QueryIntent.SUMMARY_REQUEST,
            QueryIntent.METHODOLOGY_REQUEST,
            QueryIntent.FINDINGS_REQUEST,
            QueryIntent.REFERENCE_REQUEST,
            QueryIntent.FOLLOWUP_VAGUE,
        ]


class ReportExtractor:
    """
    Extracts specific sections from research reports.
    Handles methodology, findings, and summary extraction.
    """
    
    @staticmethod
    def extract_summary(report: str) -> str:
        """
        Extract or generate a 3-paragraph summary.
        
        Format:
        - Paragraph 1: Context/Background
        - Paragraph 2: Key Findings
        - Paragraph 3: Conclusions/Implications
        """
        # Try to find existing summary section
        summary_match = re.search(
            r'#+\s*(?:Summary|Executive Summary|Overview)(.*?)(?=\n#+|\Z)',
            report,
            re.DOTALL | re.IGNORECASE
        )
        
        if summary_match:
            return summary_match.group(1).strip()
        
        # If no summary section, extract first few paragraphs
        paragraphs = [p.strip() for p in report.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        
        if len(paragraphs) >= 3:
            return '\n\n'.join(paragraphs[:3])
        
        # Fallback: return first 500 characters
        return report[:500] + "..."
    
    @staticmethod
    def extract_methodology(report: str) -> Optional[str]:
        """
        Extract methodology section with bullet points.
        
        Returns details like:
        - Sample size
        - Variables
        - Experimental design
        - Data analysis techniques
        """
        # Look for methodology section
        methodology_patterns = [
            r'#+\s*(?:Methodology|Methods?|Research Design)(.*?)(?=\n#+|\Z)',
            r'#+\s*(?:Experimental Setup|Approach)(.*?)(?=\n#+|\Z)',
        ]
        
        for pattern in methodology_patterns:
            match = re.search(pattern, report, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_findings(report: str) -> Optional[str]:
        """Extract key findings section."""
        findings_patterns = [
            r'#+\s*(?:Key Findings|Findings|Results)(.*?)(?=\n#+|\Z)',
            r'#+\s*(?:Main Results|Outcomes)(.*?)(?=\n#+|\Z)',
        ]
        
        for pattern in findings_patterns:
            match = re.search(pattern, report, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_references(report: str) -> Optional[str]:
        """Extract references section."""
        ref_match = re.search(
            r'#+\s*(?:References|Bibliography|Sources)(.*?)(?=\n#+|\Z)',
            report,
            re.DOTALL | re.IGNORECASE
        )
        
        if ref_match:
            return ref_match.group(1).strip()
        
        return None


class SessionContextManager:
    """
    Main context manager that coordinates intent detection and response routing.
    
    Implements core behavioral rules for context-aware research assistant.
    """
    
    def __init__(self):
        self.intent_detector = ContextAwareIntentDetector()
        self.extractor = ReportExtractor()
    
    def build_context(self, chat_id: int, messages: List[Dict]) -> SessionContext:
        """
        Build session context from message history.
        
        Args:
            chat_id: Current chat session ID
            messages: All messages in the session
            
        Returns:
            SessionContext with extracted information
        """
        context = SessionContext(chat_id=chat_id)
        
        if not messages:
            return context
        
        # Get the most recent research query and report
        for msg in reversed(messages):
            query = msg.get('query', '')
            report = msg.get('report', '')
            
            if not context.last_research_topic and len(query.split()) > 3:
                context.last_research_topic = query
            
            if not context.last_report and report:
                context.last_report = report
                context.last_methodology = self.extractor.extract_methodology(report)
                context.last_findings = self.extractor.extract_findings(report)
                
                # Try to extract paper title from report
                # Usually the first heading or mentioned in first paragraph
                first_lines = report.split('\n')[:5]
                for line in first_lines:
                    if line.strip().startswith('#'):
                        context.last_paper_title = line.strip('#').strip()
                        break
            
            # If we have all needed context, stop
            if context.last_research_topic and context.last_report:
                break
        
        return context
    
    def process_query(
        self,
        query: str,
        chat_id: int,
        messages: List[Dict]
    ) -> Dict:
        """
        Process user query with context awareness.
        
        Returns routing decision and context.
        
        Args:
            query: User's query
            chat_id: Chat session ID
            messages: Conversation history
            
        Returns:
            Dict with:
                - intent: Detected intent
                - should_research: Whether to run full research
                - context: Session context
                - response_hint: Suggested response approach
        """
        # Build session context
        context = self.build_context(chat_id, messages)
        
        # Detect intent
        intent, confidence = self.intent_detector.detect_intent(
            query, messages, context
        )
        
        # Determine routing
        should_research = intent == QueryIntent.NEW_RESEARCH
        
        # Build response hints
        response_hint = self._build_response_hint(intent, context)
        
        return {
            'intent': intent.value,
            'confidence': confidence,
            'should_research': should_research,
            'context': context,
            'response_hint': response_hint,
            'has_previous_context': bool(context.last_report),
        }
    
    def _build_response_hint(
        self, 
        intent: QueryIntent, 
        context: SessionContext
    ) -> str:
        """Build a hint for how to respond based on intent and context."""
        
        if not context.last_report:
            return "No previous research found. Proceed with new research."
        
        hints = {
            QueryIntent.SUMMARY_REQUEST: (
                f"Extract summary from previous research about: {context.last_research_topic}"
            ),
            QueryIntent.METHODOLOGY_REQUEST: (
                f"Extract methodology from previous research about: {context.last_research_topic}"
            ),
            QueryIntent.FINDINGS_REQUEST: (
                f"Extract findings from previous research about: {context.last_research_topic}"
            ),
            QueryIntent.REFERENCE_REQUEST: (
                f"Extract references from previous research about: {context.last_research_topic}"
            ),
            QueryIntent.FOLLOWUP_VAGUE: (
                f"User is asking about previous topic: {context.last_research_topic}. "
                "Clarify what specific aspect they want to know."
            ),
        }
        
        return hints.get(intent, "Proceed with new research.")
    
    def generate_contextual_response(
        self,
        intent: QueryIntent,
        context: SessionContext,
        query: str
    ) -> str:
        """
        Generate a response using session context.
        Does NOT require new research.
        
        Args:
            intent: Detected query intent
            query: Original user query
            context: Session context
            
        Returns:
            Formatted response string
        """
        if not context.last_report:
            return "I don't have any previous research to reference. Please ask a research question first."
        
        # Handle different intents
        if intent == QueryIntent.SUMMARY_REQUEST:
            summary = self.extractor.extract_summary(context.last_report)
            return self._format_summary_response(
                context.last_research_topic,
                summary
            )
        
        elif intent == QueryIntent.METHODOLOGY_REQUEST:
            methodology = context.last_methodology or self.extractor.extract_methodology(context.last_report)
            return self._format_methodology_response(
                context.last_research_topic,
                methodology
            )
        
        elif intent == QueryIntent.FINDINGS_REQUEST:
            findings = context.last_findings or self.extractor.extract_findings(context.last_report)
            return self._format_findings_response(
                context.last_research_topic,
                findings
            )
        
        elif intent == QueryIntent.REFERENCE_REQUEST:
            references = self.extractor.extract_references(context.last_report)
            return self._format_references_response(references)
        
        elif intent == QueryIntent.FOLLOWUP_VAGUE:
            return self._format_clarification_response(
                context.last_research_topic,
                query
            )
        
        return "I'm not sure how to respond. Could you be more specific?"
    
    def _format_summary_response(self, topic: str, summary: str) -> str:
        """Format summary in 3-paragraph structure."""
        return f"""## Summary: {topic}

{summary}

---
*This summary is extracted from our previous research discussion.*
"""
    
    def _format_methodology_response(self, topic: str, methodology: Optional[str]) -> str:
        """Format methodology with bullet points."""
        if not methodology:
            return f"**Methodology for: {topic}**\n\nNo explicit methodology section was found in the previous research. The research covered various aspects of this topic through academic paper analysis."
        
        return f"""## Methodology: {topic}

{methodology}

---
*This methodology is extracted from our previous research discussion.*
"""
    
    def _format_findings_response(self, topic: str, findings: Optional[str]) -> str:
        """Format findings section."""
        if not findings:
            return f"**Key Findings for: {topic}**\n\nPlease refer to the full report from our previous discussion for detailed findings."
        
        return f"""## Key Findings: {topic}

{findings}

---
*These findings are extracted from our previous research discussion.*
"""
    
    def _format_references_response(self, references: Optional[str]) -> str:
        """Format references section."""
        if not references:
            return "**References**\n\nNo references section was found in the previous research."
        
        return f"""## References

{references}
"""
    
    def _format_clarification_response(self, topic: str, query: str) -> str:
        """Ask for clarification when query is vague."""
        return f"""I see you're asking about our previous discussion on **{topic}**.

Could you clarify what you'd like to know? For example:
- **"Give me a summary"** - For a concise overview
- **"What was the methodology?"** - For research methods used
- **"What were the key findings?"** - For main results
- **"Show me the references"** - For source papers

Or ask a new specific question about this topic!
"""
