from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..dependencies import get_session, get_current_tenant_id
from ..schemas.rules import RuleOutput
from ..schemas.defaults import DefaultRuleSC, DefaultVariableSC
from ..schemas.variables import VariableOutput
from ..models.policies import Policy
from ..models.rules import Rule
from ..models.variables import Variable
from ..models.defaults import DefaultRule, DefaultVariable
from ..models.tenants import Tenant

router = APIRouter(prefix="/api/policies/{policy_id}/rules", tags=["Rules Management"])

@router.post("/rules", response_model=RuleOutput)
def add_rule_to_policy(
    policy_id: int,
    rule_name: str,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> RuleOutput:
    """
    Add a rule to a policy, ensuring tenant ownership.
    """
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if the policy belongs to the current tenant
    if policy.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    rule_query = select(DefaultRule).where(DefaultRule.name == rule_name)
    default_rule = session.exec(rule_query).first() # Changed to first()
    if not default_rule:
        raise HTTPException(status_code=404, detail="Default Rule not found")

    rule = Rule(policy_id=policy_id, name=default_rule.name)
    session.add(rule)
    session.commit()
    session.refresh(rule)

    variables_query = select(DefaultVariable).where(DefaultVariable.rule_id == default_rule.id)
    default_variables = session.exec(variables_query).all()
    if default_variables:  # if the rule has variables execute this , then empty list automatic by the the schema
        for __vars__ in default_variables:
            variables = Variable(
                rule_id=rule.id,  # Use the newly created rule's ID
                variable=__vars__.variable,
                variable_value=__vars__.variable_value,
            )
            session.add(variables)
            session.commit()
            session.refresh(variables)
    return rule


@router.get("/rules", response_model=list[RuleOutput])
def get_policy_rules(
    policy_id: int,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> list[RuleOutput]:
    """
    Get all rules for a policy, ensuring tenant ownership.
    """
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if the policy belongs to the current tenant
    if policy.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    query = select(Rule).where(Rule.policy_id == policy_id)
    rules = session.exec(query).all()
    return rules


@router.get("/{rule_id}", response_model=RuleOutput)
def get_rule(
    policy_id: int,
    rule_id: int,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> RuleOutput:
    """
    Get a specific rule by ID, ensuring tenant ownership.
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
    
    if rule.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Rule not found in this policy")

    return rule


@router.post("/{rule_id}", response_model=RuleOutput)
def add_rule(
    policy_id: int,
    rule_id: int,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
) -> RuleOutput:
    """
    Add a rule to a policy, ensuring tenant ownership.
    """
    policy = session.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Check if the policy belongs to the current tenant
    if policy.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    rule = session.get(DefaultRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Default Rule not found")

    # Check if the rule is already assigned to the policy
    policy_rule = session.exec(select(Rule).where(Rule.policy_id == policy_id, Rule.name == rule.name)).first()
    if policy_rule:
        raise HTTPException(status_code=400, detail="Rule already assigned to this policy")

    new_rule = Rule(policy_id=policy_id, name=rule.name)
    session.add(new_rule)
    session.commit()
    session.refresh(new_rule)

    variables_query = select(DefaultVariable).where(DefaultVariable.rule_id == rule.id)
    default_variables = session.exec(variables_query).all()
    if default_variables:  # if the rule has variables execute this , then empty list automatic by the the schema
        for __vars__ in default_variables:
            variables = Variable(
                rule_id=new_rule.id,  # Use the newly created rule's ID
                variable=__vars__.variable,
                variable_value=__vars__.variable_value,
            )
            session.add(variables)
            session.commit()
            session.refresh(variables)
    return new_rule


@router.delete("/{rule_id}")
def delete_policy(
    policy_id: int,
    rule_id: int,
    current_tenant_id: int = Depends(get_current_tenant_id),
    session: Session = Depends(get_session),
):
    """
    Delete a rule from a policy, ensuring tenant ownership.
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
    
    if rule.policy_id != policy_id:
        raise HTTPException(status_code=404, detail="Rule not found in this policy")

    session.delete(rule)
    session.commit()
