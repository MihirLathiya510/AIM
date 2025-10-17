"""
Tests for refinement loop.
"""

import pytest
from aim_mcp_server.refinement_loop import RefinementLoop
from aim_mcp_server.utils.constraints import Constraint, ConstraintType


@pytest.mark.asyncio
async def test_refine_simple_task():
    """Test refinement loop with simple task."""
    loop = RefinementLoop(max_iterations=3)
    
    constraints = [
        Constraint(
            type=ConstraintType.CUSTOM,
            description="Generate a hello world function",
            required=True
        )
    ]
    
    result = await loop.refine_until_perfect(
        task_description="Write a hello world function in Python",
        constraints=constraints,
        context={}
    )
    
    assert result is not None
    assert result.total_iterations > 0
    assert result.final_output is not None


@pytest.mark.asyncio
async def test_refinement_iterations():
    """Test that refinement loop tracks iterations."""
    loop = RefinementLoop(max_iterations=2)
    
    constraints = [
        Constraint(
            type=ConstraintType.CUSTOM,
            description="Create a complex function",
            required=True
        )
    ]
    
    result = await loop.refine_until_perfect(
        task_description="Create a function to solve a complex problem",
        constraints=constraints,
        context={}
    )
    
    assert len(result.iterations) > 0
    assert result.iterations[0].iteration == 0

