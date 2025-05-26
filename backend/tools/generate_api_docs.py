#!/usr/bin/env python3
"""
Genera documentación HTML interactiva de la API basada en los resultados de prueba.
Ejecutar después de test_endpoints.py:

python backend/tools/generate_api_docs.py
"""
import json
import os
from pathlib import Path

# Configuración
OUTPUT_DIR = Path("docs")
MARKDOWN_FILE = OUTPUT_DIR / "API_DOCUMENTATION.md"
HTML_FILE = OUTPUT_DIR / "api_documentation.html"
RESULTS_FILE = OUTPUT_DIR / "api_test_results.json"

# Plantilla HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentación API Pomodoro Forest</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 2rem;
            padding-bottom: 2rem;
            background-color: #f8f9fa;
        }
        .header {
            background-color: #2E8B57;
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-radius: 0.5rem;
        }
        .endpoint {
            margin-bottom: 1.5rem;
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            overflow: hidden;
        }
        .endpoint-header {
            display: flex;
            align-items: center;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
        }
        .method {
            font-weight: bold;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            margin-right: 1rem;
            min-width: 4rem;
            text-align: center;
        }
        .method-get { background-color: #d1ecf1; color: #0c5460; }
        .method-post { background-color: #d4edda; color: #155724; }
        .method-put { background-color: #fff3cd; color: #856404; }
        .method-delete { background-color: #f8d7da; color: #721c24; }
        .endpoint-body {
            padding: 0 1.5rem 1.5rem;
            display: none;
        }
        .status-success { color: #155724; }
        .status-error { color: #721c24; }
        .response-container {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .nav-tabs { margin-bottom: 1rem; }
        .copy-btn {
            float: right;
            font-size: 0.8rem;
        }
        pre {
            background-color: #f8f9fa;
            padding: 0.75rem;
            border-radius: 0.25rem;
            white-space: pre-wrap;
        }
        .table-endpoints th,
        .table-endpoints td {
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header text-center">
            <h1>API Pomodoro Forest</h1>
            <p class="lead">Documentación interactiva generada automáticamente</p>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card mb-4">
                    <div class="card-header">
                        <h2 class="h5 mb-0">Resumen de endpoints</h2>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-endpoints">
                                <thead>
                                    <tr>
                                        <th>Endpoint</th>
                                        <th>Método</th>
                                        <th>Descripción</th>
                                        <th>Estado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {{ENDPOINTS_TABLE}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <ul class="nav nav-tabs" id="categoryTabs" role="tablist">
            {{CATEGORY_TABS}}
        </ul>
        
        <div class="tab-content" id="categoryTabContent">
            {{CATEGORY_CONTENT}}
        </div>
        
        <footer class="mt-5 text-center text-muted">
            <p>Generado el {{TIMESTAMP}} • Pomodoro Forest API Documentation</p>
        </footer>
    </div>
    
    <script>
        function toggleEndpoint(id) {
            const body = document.getElementById('endpoint-body-' + id);
            if (body.style.display === 'block') {
                body.style.display = 'none';
            } else {
                body.style.display = 'block';
            }
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Copiado al portapapeles');
            });
        }
    </script>
</body>
</html>
"""

def read_results():
    """Lee los resultados de las pruebas."""
    if not RESULTS_FILE.exists():
        print(f"Error: No se encontró el archivo de resultados {RESULTS_FILE}")
        print("Intentando crear un archivo de resultados vacío para la demostración...")
        
        # Crear algunos resultados de demostración
        demo_results = [
            {
                "success": True,
                "endpoint": "/api/docs",
                "method": "GET",
                "status_code": 200,
                "message": "Documentación de ejemplo",
                "response": {"message": "Esta es una respuesta de ejemplo"},
                "elapsed": 123.45
            }
        ]
        
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(demo_results, f, indent=2)
        
        return demo_results
    
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_endpoints_table(results):
    """Genera la tabla de resumen de endpoints."""
    table_rows = []
    
    for result in results:
        endpoint = result["endpoint"]
        method = result["method"]
        success = result["success"]
        status = result["status_code"]
        
        method_class = f"method-{method.lower()}"
        status_class = "status-success" if success else "status-error"
        
        # Extractar descripción del endpoint
        description = endpoint.split("/")[-1].replace("-", " ").title()
        if description == "":
            parts = endpoint.split("/")
            if len(parts) > 2:
                description = parts[2].replace("-", " ").title()
            else:
                description = "Raíz"
        
        row = f"""
        <tr>
            <td>{endpoint}</td>
            <td><span class="method {method_class}">{method}</span></td>
            <td>{description}</td>
            <td class="{status_class}">{status}</td>
        </tr>
        """
        table_rows.append(row)
    
    return "".join(table_rows)

def generate_category_tabs(results):
    """Genera las pestañas de categorías."""
    categories = set()
    
    for result in results:
        path = result["endpoint"].split("/")
        if len(path) > 1:
            category = path[1] or "root"
        else:
            category = "root"
        categories.add(category)
    
    tabs = []
    for i, category in enumerate(sorted(categories)):
        active = "active" if i == 0 else ""
        selected = "true" if i == 0 else "false"
        
        tab = f"""
        <li class="nav-item" role="presentation">
            <button class="nav-link {active}" id="{category}-tab" data-bs-toggle="tab" 
                    data-bs-target="#{category}-content" type="button" role="tab" 
                    aria-controls="{category}-content" aria-selected="{selected}">
                {category.upper()}
            </button>
        </li>
        """
        tabs.append(tab)
    
    return "".join(tabs)

def generate_category_content(results):
    """Genera el contenido de las pestañas de categorías."""
    endpoints_by_category = {}
    
    for i, result in enumerate(results):
        path = result["endpoint"].split("/")
        if len(path) > 1:
            category = path[1] or "root"
        else:
            category = "root"
        
        if category not in endpoints_by_category:
            endpoints_by_category[category] = []
        
        endpoints_by_category[category].append((i, result))
    
    content_sections = []
    for i, category in enumerate(sorted(endpoints_by_category.keys())):
        active = "show active" if i == 0 else ""
        
        endpoints_content = []
        for endpoint_idx, (idx, endpoint) in enumerate(endpoints_by_category[category]):
            method = endpoint["method"]
            path = endpoint["endpoint"]
            status = endpoint["status_code"]
            success = endpoint["success"]
            
            method_class = f"method-{method.lower()}"
            status_class = "status-success" if success else "status-error"
            
            response_json = json.dumps(endpoint.get("response", {}), indent=2)
            
            endpoint_html = f"""
            <div class="endpoint">
                <div class="endpoint-header" onclick="toggleEndpoint({idx})">
                    <div class="method {method_class}">{method}</div>
                    <div class="path">{path}</div>
                    <div class="ms-auto status {status_class}">{status}</div>
                </div>
                <div class="endpoint-body" id="endpoint-body-{idx}">
                    <div class="row">
                        <div class="col-md-12">
                            <h4 class="h6">Respuesta</h4>
                            <div class="response-container">
                                <button class="btn btn-sm btn-outline-secondary copy-btn" 
                                        onclick="copyToClipboard('{response_json.replace("'", "\\'")}')">
                                    Copiar
                                </button>
                                <pre><code>{response_json}</code></pre>
                            </div>
                            <p class="small text-muted">Tiempo de respuesta: {endpoint.get('elapsed', 0):.2f}ms</p>
                        </div>
                    </div>
                </div>
            </div>
            """
            endpoints_content.append(endpoint_html)
        
        section = f"""
        <div class="tab-pane fade {active}" id="{category}-content" role="tabpanel" aria-labelledby="{category}-tab">
            <div class="mb-4">
                <h3 class="h4">Endpoints de {category.upper()}</h3>
                <p class="text-muted">Total: {len(endpoints_by_category[category])} endpoints</p>
            </div>
            {"".join(endpoints_content)}
        </div>
        """
        content_sections.append(section)
    
    return "".join(content_sections)

def generate_html_docs(results):
    """Genera la documentación HTML."""
    import datetime
    
    endpoints_table = generate_endpoints_table(results)
    category_tabs = generate_category_tabs(results)
    category_content = generate_category_content(results)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = HTML_TEMPLATE \
        .replace("{{ENDPOINTS_TABLE}}", endpoints_table) \
        .replace("{{CATEGORY_TABS}}", category_tabs) \
        .replace("{{CATEGORY_CONTENT}}", category_content) \
        .replace("{{TIMESTAMP}}", timestamp)
    
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Documentación HTML generada en: {HTML_FILE}")

def main():
    """Función principal."""
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    
    results = read_results()
    if results:
        generate_html_docs(results)
    else:
        print("No se pudieron leer los resultados de las pruebas. "
              "Ejecuta primero test_endpoints.py con la opción --output=json")

if __name__ == "__main__":
    main()