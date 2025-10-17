"""
Constraint parsing and validation utilities.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional
import re


class ConstraintType(Enum):
    """Types of constraints that can be enforced."""
    OUTPUT_FORMAT = "output_format"
    CODE_QUALITY = "code_quality"
    TEST_COVERAGE = "test_coverage"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DEADLINE = "deadline"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    CUSTOM = "custom"


@dataclass
class Constraint:
    """Represents a single constraint on a task."""
    type: ConstraintType
    description: str
    value: Optional[Any] = None
    required: bool = True
    
    def __str__(self) -> str:
        return f"{self.type.value}: {self.description}" + (f" ({self.value})" if self.value else "")


class ConstraintParser:
    """Parses task descriptions to extract constraints."""
    
    # Pattern matching for common constraints
    PATTERNS = {
        ConstraintType.TEST_COVERAGE: [
            (r"(?:test coverage|coverage)\s*(?:>|>=|above|at least)\s*(\d+)%", "value"),
            (r"(\d+)%\s*(?:test )?coverage", "value"),
        ],
        ConstraintType.LANGUAGE: [
            (r"(?:use|using|in|with)\s+(TypeScript|JavaScript|Python|Java|Go|Rust|C\+\+)", "value"),
            (r"(TypeScript|JavaScript|Python|Java|Go|Rust) strict mode", "value"),
        ],
        ConstraintType.FRAMEWORK: [
            (r"(?:use|using)\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)\s+(?:SDK|framework|library)", "value"),
        ],
        ConstraintType.COMPLIANCE: [
            (r"(FIDO2|OAuth2|GDPR|HIPAA|SOC2)\s+(?:compliance|compliant)", "value"),
        ],
        ConstraintType.OUTPUT_FORMAT: [
            (r"(?:generate|create|output)\s+(documentation|docs|API docs|README)", "value"),
            (r"output format:\s*(\w+)", "value"),
        ],
    }
    
    @classmethod
    def parse(cls, task_description: str) -> List[Constraint]:
        """
        Parse task description to extract constraints.
        
        Args:
            task_description: The task description text
            
        Returns:
            List of extracted constraints
        """
        constraints = []
        
        # Extract constraints using patterns
        for constraint_type, patterns in cls.PATTERNS.items():
            for pattern, value_group in patterns:
                matches = re.finditer(pattern, task_description, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if value_group == "value" else None
                    # Convert percentage strings to float
                    if constraint_type == ConstraintType.TEST_COVERAGE and value:
                        value = float(value)
                    
                    constraint = Constraint(
                        type=constraint_type,
                        description=match.group(0),
                        value=value,
                        required=True
                    )
                    constraints.append(constraint)
        
        # Extract explicit requirements (bullet points or numbered lists)
        requirement_patterns = [
            r"[-•]\s*(.+?)(?:\n|$)",
            r"\d+\.\s*(.+?)(?:\n|$)",
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, task_description)
            for match in matches:
                requirement = match.group(1).strip()
                if requirement and len(requirement) > 5:  # Filter out noise
                    constraint = Constraint(
                        type=ConstraintType.CUSTOM,
                        description=requirement,
                        required=True
                    )
                    constraints.append(constraint)
        
        return constraints
    
    @classmethod
    def validate_constraint(cls, constraint: Constraint, output: Any) -> tuple[bool, Optional[str]]:
        """
        Validate if output meets a specific constraint.
        
        Args:
            constraint: The constraint to validate
            output: The output to validate against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation logic - can be extended
        if constraint.type == ConstraintType.TEST_COVERAGE:
            # Placeholder - would need to parse test results
            return True, None
        
        # Default: assume valid (will be checked by review agent)
        return True, None

