from planner_cli.models import ValidationResult

REQUIRED_TOP_LEVEL_FIELDS = [
    "project",
    "currentNetwork",
    "assets",
    "communications",
    "openItems",
]

RECOMMENDED_TOP_LEVEL_FIELDS = [
    "survey",
    "addressing",
    "security",
    "design",
]

REQUIRED_PROJECT_FIELDS = ["name", "customer", "objective", "scope"]
MINIMUM_RUNNABLE_HINTS = [
    ("currentNetwork.topology", "缺少现状网络基础描述"),
    ("communications.flows", "缺少初步通信或访问关系"),
    ("project.constraints", "缺少约束条件"),
]


def _get_nested(payload: dict, dotted_path: str):
    current = payload
    for segment in dotted_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def _has_content(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_has_content(item) for item in value)
    if isinstance(value, dict):
        return bool(value)
    return True


def validate_standard_input(payload: dict, strict: bool = False) -> ValidationResult:
    result = ValidationResult()

    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        if field_name not in payload:
            result.errors.append(f"Missing top-level field: {field_name}")

    for field_name in RECOMMENDED_TOP_LEVEL_FIELDS:
        if field_name not in payload:
            result.warnings.append(f"Recommended top-level field is missing: {field_name}")

    project = payload.get("project")
    if project is None:
        return result

    if not isinstance(project, dict):
        result.errors.append("Field 'project' must be an object.")
        return result

    for field_name in REQUIRED_PROJECT_FIELDS:
        value = project.get(field_name)
        if not _has_content(value):
            result.errors.append(f"Missing required project field: project.{field_name}")

    for path, warning in MINIMUM_RUNNABLE_HINTS:
        if not _has_content(_get_nested(payload, path)):
            result.warnings.append(warning)

    if not _has_content(_get_nested(payload, "openItems.siteVerification")) and not _has_content(_get_nested(payload, "openItems.customerConfirmation")):
        result.warnings.append("缺少明确待确认项，建议补充现场复核项或客户确认项。")

    if strict and result.warnings:
        result.errors.extend(f"Strict mode: {warning}" for warning in result.warnings)
        result.warnings.clear()

    return result
