## Obsidian MCP: Direct Vault Interaction
This is a Model Context Protocol (MCP) server designed to enable AI tools, such as Claude Desktop, to directly interact with your local Obsidian vault's file system. This allows large language models (LLMs) to perform actions like searching for notes, retrieving content, creating new notes, and listing directory contents within your Obsidian vault.

### Features
- Intelligent Search: Allows LLMs to search your vault for notes based on content and filenames.
- Content Retrieval: Fetch the full content of any specific note.
- Directory Listing: List files and subdirectories within any part of your vault.
- Direct File System Access: Operates independently of Obsidian's running state or the Local REST API plugin.
### Setup Guide
Follow these steps to get your Obsidian MCP server up and running.

1. Project Setup & Dependencies
It's highly recommended to use a virtual environment for dependency management. This project uses uv for lightning-fast package installation and virtual environment management.

- Clone the repository:
```Bash
git clone https://github.com/DerMoehre/obsidian-mcp.git
cd obsidian-mcp
```

- Create and activate a virtual environment with uv:
```Bash
uv venv
source .venv/bin/activate
```

- Install project dependencies:
```Bash
uv pip install -e .
```
This command installs all required packages, including fastmcp, pydantic, httpx, typer, ruff, and python-dotenv.

2. Configure Your Obsidian Vault Path
The server needs to know the exact path to your Obsidian vault.

- Create a .env file: In the root of your project directory, create a new file named .env.
- Add your vault path: Open the .env file and add the following line, replacing /path/to/your/obsidian/vault with the actual absolute path to your Obsidian vault's root directory (e.g., /Users/yourusername/folder/obsidian/vault).

`OBSIDIAN_VAULT_ROOT=/path/to/your/obsidian/vault`
Important: Do not use quotes around the path.

3. Integrate with Claude Desktop
To allow Claude Desktop to use your MCP server, you need to configure it in `claude_desktop_config.json`.

- Locate claude_desktop_config.json:

    - On macOS, this file is typically located at: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - On Windows, it's usually at: `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`
- Add your MCP configuration: Open the `claude_desktop_config.json` file and add an entry for `ObsidianVault` under the `"mcp"` section.

    ```JSON
    {
    "mcp": {
        "ObsidianVault": {
        "command": "/path/to/your/obsidian-mcp/.venv/bin/python",
        "args": [
            "/path/to/your/obsidian-mcp/main.py"
        ]
        }
    },
    // ... other Claude Desktop settings ...
    }
    ```

    - Replace `/path/to/your/obsidian-mcp/` with the actual absolute path to your `obsidian-mcp` project directory.
    - Ensure the command points to the python executable inside your virtual environment.
    - Ensure the args points to your project's main.py file.
- Restart Claude Desktop: After saving `claude_desktop_config.json`, close and reopen Claude Desktop for the changes to take effect.

### Development Workflow (Optional but Recommended)
This project is set up with `ruff` for linting and formatting, and `pre-commit` hooks to automate code quality checks.

- Install `pre-commit` hooks:

    ```Bash
    pre-commit install
    ```
    This will ensure that ruff runs automatically every time you make a git commit.

- Run `ruff` manually (for a first pass):

    ```Bash 
    ruff format .
    ruff check --fix .
    ```
    These commands will automatically format your code and fix many linting errors according to the pyproject.toml configuration.
