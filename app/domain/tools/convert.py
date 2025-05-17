"""Conversion between Pydantic V1 and V2"""

from langchain_core.utils.function_calling import _rm_titles
from langchain_core.utils.json_schema import dereference_refs
from pydantic import BaseModel


def convert_to_openai_tool(
    model: BaseModel,
    *,
    name: str | None = None,
    description: str | None = None,
) -> dict:
    """Convert Pydantic model to function description for LLM"""
    function = convert_pydantic_to_openai_function(
        model, name=name, description=description
    )
    return {"type": "function", "function": function}


def convert_pydantic_to_openai_function(
    model: BaseModel,
    *,
    name: str | None = None,
    description: str | None = None,
    rm_titles: bool = True,
) -> dict:
    """Convert Pydantic model to function description for LLM"""
    model_schema = (
        model.model_json_schema()
        if hasattr(model, "model_json_schema")
        else model.schema()
    )
    schema = dereference_refs(model_schema)
    schema.pop("definitions", None)
    title = schema.pop("title", "")
    default_description = schema.pop("description", "")
    return {
        "name": name or title,
        "description": description or default_description,
        "parameters": _rm_titles(schema) if rm_titles else schema,
    }
