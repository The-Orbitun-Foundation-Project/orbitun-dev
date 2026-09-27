from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..dependencies import get_session, get_current_tenant_id
from ..schemas.variables import VariableOutput
from ..models.variables import Variable
from ..models.rules import Rule
from ..models.policies import Policy

router = APIRouter(
    prefix="/api/policies/{policy_id}/rules/{rule_id}/variables",
    tags=["Variables Management"],
)

@router.get("/variables", response_model=list[VariableOutput])
def get_variables(
    policy_id: int,
    rule_id: int,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> list[VariableOutput]:
    """
    Get all variables for a rule, ensuring tenant ownership.
    """
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if the policy belongs to the current tenant
    if policy.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Check if the rule belongs to the policy
    if rule.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Rule not found in this policy")

    query = select(Variable).where(Variable.rule_id == rule_id)
    variables = session.exec(query).all()
    return variables


@router.put("/{variable_id}", response_model=VariableOutput)
def modify_variable(
    policy_id: int,
    rule_id: int,
    variable_id: int,
    new_variable_value: str,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> VariableOutput:
    """
    Modify a variable's value, ensuring tenant ownership.
    """
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if the policy belongs to the current tenant
    if policy.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Check if the rule belongs to the policy
    if rule.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Rule not found in this policy")

    variable = session.get(Variable, variable_id)
    if not variable:
        raise HTTPException(status_code=404, detail="Variable not found")

    # Check if the variable belongs to the rule
    if variable.rule_id != rule_id:
        raise HTTPException(status_code=404, detail="Variable not found in this rule")

    variable.variable_value = new_variable_value
    session.commit()
    session.refresh(variable)
    return variable
