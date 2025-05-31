import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field

script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, ".env")
load_dotenv(dotenv_path)

_vault_path_from_env = os.getenv("OBSIDIAN_VAULT_ROOT")
OBSIDIAN_VAULT_ROOT = _vault_path_from_env

if not isinstance(OBSIDIAN_VAULT_ROOT, str):
    raise TypeError(
        f"OBSIDIAN_VAULT_ROOT must be a string, but got {type(OBSIDIAN_VAULT_ROOT)}"
    )

mcp = FastMCP(name="Obsidian MCP")


def _validate_path(base_path: str, relative_path: str) -> str:
    # Ensure inputs are strings and not None
    if not isinstance(base_path, str) or base_path is None:
        raise TypeError("base_path must be a string")
    if not isinstance(relative_path, str) or relative_path is None:
        raise TypeError("relative_path must be a string")

    abs_base_path = os.path.abspath(base_path)

    abs_full_path = os.path.abspath(os.path.join(base_path, relative_path))

    if not abs_full_path.startswith(abs_base_path):
        raise ValueError("Attempted path traversal. Access denied.")

    return abs_full_path


# --- Define Pydantic Models for Tool Inputs (Improves AI understanding) ---
# class SearchQuery(BaseModel):
# query: str = Field(description="The search query to use within the Obsidian vault.")


class FilePath(BaseModel):
    path: str = Field(description="The path to the file relative to the vault root.")


# --- Define MCP Tools ---
@mcp.tool()
async def search_obsidian_vault(
    query: str = Field(
        description="The search query to use within the Obsidian vault."
    ),
) -> str:  # Your tool name.
    """
    Searches the Obsidian vault for notes matching the query.
    Returns a summarized list of matching file paths and content snippets.
    """
    if query is None:
        return "Error: No search query was provided. Please specify what to search for."

    results = []

    try:
        for root, _dirs, files in os.walk(OBSIDIAN_VAULT_ROOT):
            for file in files:
                if file.endswith(".md"):  # Only process Markdown files
                    try:
                        current_full_file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(
                            current_full_file_path, OBSIDIAN_VAULT_ROOT
                        )
                        if query.lower() in file.lower():
                            results.append(f"File (filename match): {relative_path}")
                            continue

                        try:
                            validated_full_path_for_open = _validate_path(
                                OBSIDIAN_VAULT_ROOT, relative_path
                            )
                            with open(
                                validated_full_path_for_open, encoding="utf-8"
                            ) as f:
                                content = f.read()

                            if query.lower() in content.lower():
                                snippet_start = content.lower().find(query.lower())
                                snippet = content[
                                    max(0, snippet_start - 50) : min(
                                        len(content),
                                        snippet_start + len(input.query) + 100,
                                    )
                                ]
                                results.append(
                                    f"File (content match): {relative_path}\n"
                                    f"Snippet: {snippet}..."
                                )

                        except Exception as e:
                            results.append(
                                f"Problem file: {os.path.join(root, file)} (Error: {e})"
                            )

                    except Exception as e:
                        results.append(
                            f"Problem file: {os.path.join(root, file)} (Error: {e})"
                        )
    except TypeError:
        return (
            "Internal server error: Could not access vault files."
            "Please check server logs."
        )
    except Exception:
        return "Internal server error: An unexpected error occurred."

    if results:
        return "Search Results:\n" + "\n---\n".join(results)
    else:
        return "No results found for your query."


@mcp.tool()
async def get_note_by_uri(search_input: FilePath) -> str:
    """
    Retrieves the full content of an Obsidian note by its vault-relative path or URI.
    Provide the path to the note (e.g., 'Daily Notes/2025-05-28.md').
    """
    try:
        full_path = _validate_path(OBSIDIAN_VAULT_ROOT, search_input.path)
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: Note not found at path: {search_input.path}"
    except ValueError as e:
        return f"Error: Invalid path - {e}"
    except Exception as e:
        return f"Error reading note content: {e}"


# --- Main entry point to run the server ---
if __name__ == "__main__":
    print("Starting FastMCP server for Obsidian...")
    mcp.run(transport="stdio")
