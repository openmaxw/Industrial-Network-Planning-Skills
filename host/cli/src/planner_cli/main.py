import argparse
import re
import sys
from pathlib import Path

from planner_cli.core_loader import CoreAssetLoadError, discover_repo_root, load_core_assets
from planner_cli.docx_renderer import render_docx
from planner_cli.document_builder import build_document_model
from planner_cli.html_renderer import render_html
from planner_cli.exit_codes import (
    ARGUMENT_ERROR,
    GENERAL_ERROR,
    INPUT_READ_ERROR,
    INPUT_VALIDATION_ERROR,
    OUTPUT_WRITE_ERROR,
    SUCCESS,
)
from planner_cli.input_loader import InputLoadError, load_json_file
from planner_cli.models import CliOptions
from planner_cli.planner import build_plan_bundle
from planner_cli.renderer import render_markdown
from planner_cli.validation import validate_standard_input
from planner_cli.writer import OutputWriteError, write_output


def parse_args(argv: list[str]) -> CliOptions:
    parser = argparse.ArgumentParser(prog="planner")
    subparsers = parser.add_subparsers(dest="command")

    generate = subparsers.add_parser("generate", help="Generate delivery document from standard input JSON")
    generate.add_argument("--input", required=True, dest="input_path")
    generate.add_argument("--output", dest="output_path")
    generate.add_argument("--stdout", action="store_true", dest="stdout")
    generate.add_argument("--strict", action="store_true", dest="strict")
    generate.add_argument("--style", choices=["draft", "formal"], default="draft", dest="style")
    generate.add_argument("--format", choices=["md", "docx", "html"], default="md", dest="format")

    args = parser.parse_args(argv)

    if args.command != "generate":
        parser.print_help(sys.stderr)
        raise SystemExit(ARGUMENT_ERROR)

    if args.stdout and args.output_path and args.format in {"docx", "html"}:
        print("Error: binary/HTML output does not support --stdout.", file=sys.stderr)
        raise SystemExit(ARGUMENT_ERROR)

    if args.stdout and args.output_path:
        print("Error: --stdout and --output cannot be used together.", file=sys.stderr)
        raise SystemExit(ARGUMENT_ERROR)

    return CliOptions(
        input_path=Path(args.input_path),
        output_path=Path(args.output_path) if args.output_path else None,
        stdout=args.stdout,
        strict=args.strict,
        style=args.style,
        format=args.format,
    )


def slugify(text: str) -> str:
    normalized = re.sub(r"\s+", "-", text.strip().lower())
    normalized = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized or "solution"


def derive_output_path(repo_root: Path, project_name: str, fmt: str) -> Path:
    suffix = ".docx" if fmt == "docx" else (".html" if fmt == "html" else ".md")
    return repo_root / "output" / f"{slugify(project_name)}-solution{suffix}"


def run_generate(options: CliOptions) -> int:
    repo_root = discover_repo_root(Path.cwd())

    payload = load_json_file(options.input_path)
    validation_result = validate_standard_input(payload, strict=options.strict)
    if validation_result.errors:
        for item in validation_result.errors:
            print(f"[validation-error] {item}", file=sys.stderr)
        return INPUT_VALIDATION_ERROR

    for item in validation_result.warnings:
        print(f"[validation-warning] {item}", file=sys.stderr)

    assets = load_core_assets(repo_root)
    plan_bundle = build_plan_bundle(payload)

    if options.format == "docx":
        if options.stdout:
            print("Error: DOCX output does not support --stdout.", file=sys.stderr)
            return ARGUMENT_ERROR
        output_path = options.output_path or derive_output_path(repo_root, plan_bundle.project_name, options.format)
        model = build_document_model(plan_bundle, style=options.style)
        render_docx(model, output_path)
        print(f"Generated: {output_path}")
        return SUCCESS

    if options.format == "html":
        output_path = options.output_path or derive_output_path(repo_root, plan_bundle.project_name, options.format)
        model = build_document_model(plan_bundle, style=options.style)
        render_html(model, output_path)
        print(f"Generated: {output_path}")
        return SUCCESS

    markdown = render_markdown(plan_bundle, assets, style=options.style)

    if options.stdout:
        print(markdown)
        return SUCCESS

    output_path = options.output_path or derive_output_path(repo_root, plan_bundle.project_name, options.format)
    write_output(output_path, markdown)
    print(f"Generated: {output_path}")
    return SUCCESS


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        options = parse_args(argv)
        return run_generate(options)
    except SystemExit as exc:
        return int(exc.code)
    except InputLoadError as exc:
        print(str(exc), file=sys.stderr)
        return INPUT_READ_ERROR
    except CoreAssetLoadError as exc:
        print(str(exc), file=sys.stderr)
        return GENERAL_ERROR
    except OutputWriteError as exc:
        print(str(exc), file=sys.stderr)
        return OUTPUT_WRITE_ERROR
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return GENERAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
