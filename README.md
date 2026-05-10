🛡️ Nerva Engine
================

**The Distributed "Central Nervous System" for Python Automation.**

Nerva is a lightweight, high-performance task orchestration framework designed to bridge the gap between your local development environment and a distributed production-grade engine. It allows you to write pure Python logic on your machine and execute it instantly inside a scalable, Dockerized worker cluster.

🚀 The "Nerva" Workflow
-----------------------

Nerva decouples your code from the engine. You don't need to install Nerva as a dependency; you just write code and "push" it to the engine.

1.  **Write**: Create a standard Python function in your tasks/ folder.
    
2.  **Register**: Use the CLI to tell the engine where that function lives.
    
3.  **Trigger**: Fire off the task via the CLI or API and track its lifecycle.
    

🛠️ Installation & Setup
------------------------

### 1\. Launch the Stack

Nerva runs entirely in Docker. Ensure you have Docker and Docker Compose installed.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Clone and enter  git clone https://github.com/gixorian/nerva-engine  cd Nerva  # Setup environment (Set USER_ID/GROUP_ID to match your local user)  cp .env.example .env  # Fire it up  docker compose up -d --build   `

### 2\. Prepare the CLI

The CLI is your remote control for the engine.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python -m venv venv  source venv/bin/bin/activate  # Or venv\Scripts\activate on Windows  pip install -r requirements.txt   `

🔌 Creating & Registering Tasks
-------------------------------

### 1\. Write your Task

Create a folder named tasks/ in the project root. Put your logic in a .py file. Nerva tasks are just **pure Python functions**—no decorators or special imports required.

tasks/my\_operations.py:

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   def calculate_uptime(server_name: str, threshold: int = 99):      # Your logic here      return f"Server {server_name} is healthy at {threshold}%."   `

### 2\. Register with the CLI

Registration creates a "Blueprint" in the Nerva database.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Register a specific task  python cli/nerva.py register tasks/my_operations.py -t calculate_uptime  # OR: Register everything in a file at once  python cli/nerva.py register tasks/my_operations.py --all   `

⚡ Running Tasks
---------------

### Triggering

You can trigger tasks by name. Pass parameters using the -p flag.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python cli/nerva.py trigger CALCULATE_UPTIME -p server_name="prod-01" threshold=98   `

### Monitoring

Track the progress and retrieve results from the database.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # See all registered blueprints and their required params  python cli/nerva.py tasks  # See recent execution history  python cli/nerva.py history  # Get detailed status/result of a specific task ID  python cli/nerva.py status 4   `

🏗️ Architecture
----------------

Nerva is built for high availability and observability:

*   **Gateway (Nginx)**: Load balances incoming API requests.
    
*   **API (FastAPI)**: Manages the task registry and lifecycle.
    
*   **Broker (Redis 8)**: Orchestrates the asynchronous message queue.
    
*   **Workers (Celery)**: Dynamically imports and executes your tasks/ code.
    
*   **Persistence (PostgreSQL 18)**: Stores blueprints and execution results.
    
*   **Dashboard (Flower)**: Real-time queue monitoring at http://localhost:5555.
    

📊 Scale & Maintenance
----------------------

**Scaling Workers:**Need to process thousands of tasks? Scale the worker tier horizontally:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   docker compose up -d --scale worker=5   `

**Cleanup:**To wipe the database and task history:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Using the CLI  python cli/nerva.py purge  # Resetting the entire Docker stack  docker compose down -v   `

### Pro-Tip

Since the Worker uses a Docker Volume mapping (.:/app), any changes you make to your files in tasks/ are reflected **immediately** in the Worker. You don't need to rebuild the container to update your task logic!
