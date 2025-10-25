"""
Phase 8.E: Advanced Analytics & Reporting - Report Generator
Generate reports in PDF, Excel, HTML formats with charts and tables
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import io
import base64

class ReportGenerator:
    """Generate analytics reports in multiple formats"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_html_report(self, data: Dict, report_type: str = "general") -> str:
        """Generate HTML report with charts"""
        
        if report_type == "general":
            return self._generate_general_html(data)
        elif report_type == "endpoint":
            return self._generate_endpoint_html(data)
        elif report_type == "health":
            return self._generate_health_html(data)
        else:
            return self._generate_custom_html(data)
    
    def _generate_general_html(self, data: Dict) -> str:
        """Generate general usage report HTML"""
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Usage Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-card .subtitle {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}
        
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 400px;
        }}
        
        .table-container {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            overflow-x: auto;
        }}
        
        .table-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background: #f1f3f5;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-success {{
            background: #28a745;
            color: white;
        }}
        
        .badge-warning {{
            background: #ffc107;
            color: #333;
        }}
        
        .badge-danger {{
            background: #dc3545;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 API Usage Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Period: {data.get('period', 'N/A')}</p>
        </div>
        
        <div class="content">
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Requests</h3>
                    <div class="value">{data.get('total_requests', 0):,}</div>
                    <div class="subtitle">API calls made</div>
                </div>
                
                <div class="metric-card">
                    <h3>Success Rate</h3>
                    <div class="value">{data.get('success_rate', 0)}%</div>
                    <div class="subtitle">{data.get('success_count', 0):,} successful</div>
                </div>
                
                <div class="metric-card">
                    <h3>Avg Response Time</h3>
                    <div class="value">{data.get('avg_response_time', 0)}ms</div>
                    <div class="subtitle">Average latency</div>
                </div>
                
                <div class="metric-card">
                    <h3>Error Rate</h3>
                    <div class="value">{data.get('error_rate', 0)}%</div>
                    <div class="subtitle">{data.get('error_count', 0):,} errors</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h2>📈 Performance Metrics</h2>
                <div class="chart-wrapper">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
            
            <div class="table-container">
                <h2>🔝 Top Endpoints</h2>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Endpoint</th>
                            <th>Requests</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Add top endpoints
        top_endpoints = data.get('top_endpoints', [])
        total = data.get('total_requests', 1)
        
        for i, endpoint in enumerate(top_endpoints[:10], 1):
            count = endpoint.get('count', 0)
            percentage = (count / total * 100) if total > 0 else 0
            html += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{endpoint.get('endpoint', 'N/A')}</td>
                            <td>{count:,}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            Generated by Güvenilir Analiz API - Phase 8.E Advanced Analytics & Reporting
        </div>
    </div>
    
    <script>
        // Performance Chart
        const ctx = document.getElementById('performanceChart').getContext('2d');
        
        const percentiles = """ + json.dumps(data.get('percentiles', {})) + """;
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['P50', 'P75', 'P90', 'P95', 'P99'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [
                        percentiles.p50 || 0,
                        percentiles.p75 || 0,
                        percentiles.p90 || 0,
                        percentiles.p95 || 0,
                        percentiles.p99 || 0
                    ],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(102, 126, 234, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(102, 126, 234, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Response Time Percentiles',
                        font: {
                            size: 16
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        return html
    
    def _generate_endpoint_html(self, data: Dict) -> str:
        """Generate endpoint-specific report HTML"""
        endpoint = data.get('endpoint', 'Unknown')
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Endpoint Report: {endpoint}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Same styles as general report */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .content {{ padding: 40px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; }}
        .metric-card h3 {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 10px; }}
        .metric-card .value {{ font-size: 2.5em; font-weight: bold; }}
        .chart-container {{ background: #f8f9fa; padding: 30px; border-radius: 15px; margin-bottom: 30px; }}
        .chart-wrapper {{ position: relative; height: 300px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Endpoint Analytics</h1>
            <p><strong>{endpoint}</strong></p>
            <p>Period: {data.get('period', 'N/A')}</p>
        </div>
        
        <div class="content">
            <div class="metric-card">
                <h3>Total Requests</h3>
                <div class="value">{data.get('total_requests', 0):,}</div>
            </div>
            
            <div class="metric-card">
                <h3>Success Rate</h3>
                <div class="value">{data.get('success_rate', 0)}%</div>
            </div>
            
            <div class="metric-card">
                <h3>Average Response Time</h3>
                <div class="value">{data.get('avg_response_time', 0)}ms</div>
            </div>
            
            <div class="chart-container">
                <h2>Hourly Distribution</h2>
                <div class="chart-wrapper">
                    <canvas id="hourlyChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const hourlyData = """ + json.dumps(data.get('hourly_distribution', [])) + """;
        
        new Chart(document.getElementById('hourlyChart'), {
            type: 'line',
            data: {
                labels: hourlyData.map(h => h.hour),
                datasets: [{
                    label: 'Requests',
                    data: hourlyData.map(h => h.count),
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>
"""
        return html
    
    def _generate_health_html(self, data: Dict) -> str:
        """Generate health report HTML"""
        health_score = data.get('health_score', 0)
        status = data.get('status', 'unknown')
        
        # Color based on status
        color_map = {
            'excellent': '#28a745',
            'good': '#17a2b8',
            'fair': '#ffc107',
            'poor': '#dc3545'
        }
        color = color_map.get(status, '#6c757d')
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>API Health Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
        .container {{ max-width: 800px; width: 100%; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .health-score {{ font-size: 5em; font-weight: bold; margin: 30px 0; color: {color}; text-align: center; }}
        .status {{ font-size: 2em; text-align: center; color: {color}; text-transform: uppercase; font-weight: bold; margin-bottom: 30px; }}
        .components {{ padding: 40px; }}
        .component {{ margin-bottom: 20px; }}
        .component-label {{ font-size: 1.1em; margin-bottom: 10px; color: #333; }}
        .component-bar {{ background: #e9ecef; height: 30px; border-radius: 15px; overflow: hidden; }}
        .component-fill {{ height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); transition: width 0.5s ease; }}
        .chart-container {{ padding: 40px; }}
        .chart-wrapper {{ position: relative; height: 300px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 API Health Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="health-score">{health_score}</div>
        <div class="status">{status}</div>
        
        <div class="components">
            <h2 style="margin-bottom: 20px;">Health Components</h2>
"""
        
        components = data.get('components', {})
        for name, value in components.items():
            html += f"""
            <div class="component">
                <div class="component-label">{name.replace('_', ' ').title()}: {value}%</div>
                <div class="component-bar">
                    <div class="component-fill" style="width: {value}%"></div>
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="healthChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        const components = """ + json.dumps(components) + """;
        
        new Chart(document.getElementById('healthChart'), {
            type: 'radar',
            data: {
                labels: Object.keys(components).map(k => k.replace('_', ' ')),
                datasets: [{
                    label: 'Health Score',
                    data: Object.values(components),
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgb(102, 126, 234)',
                    pointBackgroundColor: 'rgb(102, 126, 234)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(102, 126, 234)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
        return html
    
    def _generate_custom_html(self, data: Dict) -> str:
        """Generate custom report HTML"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Custom Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>Custom Report</h1>
    <pre>{json.dumps(data, indent=2)}</pre>
</body>
</html>
"""
    
    def save_html_report(self, html: str, filename: str) -> str:
        """Save HTML report to file"""
        filepath = self.output_dir / filename
        filepath.write_text(html, encoding='utf-8')
        return str(filepath)
    
    def generate_json_report(self, data: Dict) -> str:
        """Generate JSON report"""
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def save_json_report(self, data: Dict, filename: str) -> str:
        """Save JSON report to file"""
        filepath = self.output_dir / filename
        filepath.write_text(self.generate_json_report(data), encoding='utf-8')
        return str(filepath)
    
    def generate_csv_report(self, data: List[Dict], columns: List[str]) -> str:
        """Generate CSV report"""
        if not data:
            return ""
        
        # Header
        csv = ",".join(columns) + "\n"
        
        # Rows
        for row in data:
            values = [str(row.get(col, "")) for col in columns]
            csv += ",".join(values) + "\n"
        
        return csv
    
    def save_csv_report(self, data: List[Dict], columns: List[str], filename: str) -> str:
        """Save CSV report to file"""
        filepath = self.output_dir / filename
        filepath.write_text(self.generate_csv_report(data, columns), encoding='utf-8')
        return str(filepath)

# Test code
if __name__ == "__main__":
    print("📝 Testing Report Generator...")
    
    generator = ReportGenerator()
    
    # Test data
    test_data = {
        "period": "24h",
        "total_requests": 15420,
        "success_count": 14890,
        "error_count": 530,
        "success_rate": 96.56,
        "error_rate": 3.44,
        "avg_response_time": 145.7,
        "max_response_time": 892.3,
        "min_response_time": 23.1,
        "percentiles": {
            "p50": 112.5,
            "p75": 189.3,
            "p90": 298.7,
            "p95": 412.9,
            "p99": 678.4
        },
        "top_endpoints": [
            {"endpoint": "/api/analyze", "count": 5420},
            {"endpoint": "/api/match-odds", "count": 3210},
            {"endpoint": "/api/system-status", "count": 2130},
            {"endpoint": "/api/leagues", "count": 1890},
            {"endpoint": "/api/cache-stats", "count": 1560}
        ]
    }
    
    # Generate HTML reports
    print("\n📄 Generating General HTML Report...")
    html = generator.generate_html_report(test_data, "general")
    filepath = generator.save_html_report(html, "test_general_report.html")
    print(f"✅ Saved: {filepath}")
    
    print("\n🏥 Generating Health HTML Report...")
    health_data = {
        "health_score": 87.5,
        "status": "good",
        "components": {
            "success_rate": 96.56,
            "speed_score": 78.2,
            "availability_score": 87.8
        },
        "period": "24h"
    }
    html = generator.generate_html_report(health_data, "health")
    filepath = generator.save_html_report(html, "test_health_report.html")
    print(f"✅ Saved: {filepath}")
    
    print("\n💾 Generating JSON Report...")
    filepath = generator.save_json_report(test_data, "test_report.json")
    print(f"✅ Saved: {filepath}")
    
    print("\n📊 Generating CSV Report...")
    csv_data = [
        {"endpoint": "/api/analyze", "count": 5420, "avg_time": 156.7},
        {"endpoint": "/api/match-odds", "count": 3210, "avg_time": 189.3},
        {"endpoint": "/api/system-status", "count": 2130, "avg_time": 45.2}
    ]
    filepath = generator.save_csv_report(csv_data, ["endpoint", "count", "avg_time"], "test_report.csv")
    print(f"✅ Saved: {filepath}")
    
    print("\n✅ Report Generator test complete!")
    print(f"📁 Reports saved in: {generator.output_dir}")
