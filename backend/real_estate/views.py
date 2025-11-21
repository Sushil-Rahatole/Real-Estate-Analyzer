
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import pandas as pd
from datetime import datetime
import os

import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


# Mock data (replace with actual Excel file reading)
REAL_ESTATE_DATA = [
    {'year': 2021, 'area': 'Wakad', 'price': 5500, 'demand': 850, 'size': 1200, 'type': '2BHK'},
    {'year': 2022, 'area': 'Wakad', 'price': 6200, 'demand': 920, 'size': 1200, 'type': '2BHK'},
    {'year': 2023, 'area': 'Wakad', 'price': 6800, 'demand': 980, 'size': 1200, 'type': '2BHK'},
    {'year': 2024, 'area': 'Wakad', 'price': 7500, 'demand': 1050, 'size': 1200, 'type': '2BHK'},
    {'year': 2021, 'area': 'Aundh', 'price': 7200, 'demand': 950, 'size': 1400, 'type': '3BHK'},
    {'year': 2022, 'area': 'Aundh', 'price': 7800, 'demand': 1020, 'size': 1400, 'type': '3BHK'},
    {'year': 2023, 'area': 'Aundh', 'price': 8500, 'demand': 1100, 'size': 1400, 'type': '3BHK'},
    {'year': 2024, 'area': 'Aundh', 'price': 9200, 'demand': 1180, 'size': 1400, 'type': '3BHK'},
    {'year': 2021, 'area': 'Ambegaon Budruk', 'price': 4200, 'demand': 680, 'size': 1000, 'type': '2BHK'},
    {'year': 2022, 'area': 'Ambegaon Budruk', 'price': 4600, 'demand': 720, 'size': 1000, 'type': '2BHK'},
    {'year': 2023, 'area': 'Ambegaon Budruk', 'price': 5100, 'demand': 780, 'size': 1000, 'type': '2BHK'},
    {'year': 2024, 'area': 'Ambegaon Budruk', 'price': 5600, 'demand': 840, 'size': 1000, 'type': '2BHK'},
    {'year': 2021, 'area': 'Akurdi', 'price': 3800, 'demand': 620, 'size': 950, 'type': '2BHK'},
    {'year': 2022, 'area': 'Akurdi', 'price': 4100, 'demand': 660, 'size': 950, 'type': '2BHK'},
    {'year': 2023, 'area': 'Akurdi', 'price': 4500, 'demand': 710, 'size': 950, 'type': '2BHK'},
    {'year': 2024, 'area': 'Akurdi', 'price': 4900, 'demand': 760, 'size': 950, 'type': '2BHK'},
]

def load_excel_data(file_path=None):
    """Load data from Excel file or use mock data"""
    if file_path and os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading Excel: {e}")
    return REAL_ESTATE_DATA

def analyze_query(query):
    """Analyze user query to extract intent and areas"""
    query_lower = query.lower()
    areas = ['wakad', 'aundh', 'ambegaon budruk', 'akurdi']
    mentioned_areas = [area for area in areas if area in query_lower]
    
    if not mentioned_areas:
        return None, "Please specify an area (Wakad, Aundh, Ambegaon Budruk, or Akurdi)"
    
    is_comparison = 'compare' in query_lower or len(mentioned_areas) > 1
    is_price = 'price' in query_lower or 'growth' in query_lower
    is_demand = 'demand' in query_lower
    
    
    year_filter = 4
    if 'last' in query_lower:
        import re
        match = re.search(r'last (\d+) years?', query_lower)
        if match:
            year_filter = int(match.group(1))
    
    return {
        'areas': mentioned_areas,
        'is_comparison': is_comparison,
        'is_price': is_price,
        'is_demand': is_demand,
        'year_filter': year_filter
    }, None

def filter_data(data, analysis):
    """Filter data based on analysis"""
    current_year = 2024
    start_year = current_year - analysis['year_filter'] + 1
    
    filtered = [
        d for d in data 
        if d['area'].lower() in analysis['areas'] and d['year'] >= start_year
    ]
    return filtered

def generate_summary(analysis, filtered_data):
    """Generate AI-like summary of the data"""
    areas = analysis['areas']
    
    if analysis['is_comparison'] and len(areas) > 1:
        area1_data = [d for d in filtered_data if d['area'].lower() == areas[0]]
        area2_data = [d for d in filtered_data if d['area'].lower() == areas[1]]
        
        area1_growth = ((area1_data[-1]['price'] - area1_data[0]['price']) / area1_data[0]['price'] * 100)
        area2_growth = ((area2_data[-1]['price'] - area2_data[0]['price']) / area2_data[0]['price'] * 100)
        
        summary = f"""Comparative Analysis: {areas[0].title()} vs {areas[1].title()}

{areas[0].title()} shows a {area1_growth:.1f}% price growth with current average price at ₹{area1_data[-1]['price']}/sq.ft and demand index of {area1_data[-1]['demand']}.

{areas[1].title()} demonstrates {area2_growth:.1f}% price growth with current average price at ₹{area2_data[-1]['price']}/sq.ft and demand index of {area2_data[-1]['demand']}.

{areas[0].title() if area1_growth > area2_growth else areas[1].title()} shows better investment potential based on recent growth trends."""
    else:
        area_data = [d for d in filtered_data if d['area'].lower() == areas[0]]
        price_growth = ((area_data[-1]['price'] - area_data[0]['price']) / area_data[0]['price'] * 100)
        demand_growth = ((area_data[-1]['demand'] - area_data[0]['demand']) / area_data[0]['demand'] * 100)
        
        summary = f"""Real Estate Analysis: {areas[0].title()}

Market Overview: {areas[0].title()} has shown consistent growth over the past {analysis['year_filter']} years with a {price_growth:.1f}% increase in property prices.

Current Metrics:
• Average Price: ₹{area_data[-1]['price']}/sq.ft
• Demand Index: {area_data[-1]['demand']}
• Price Growth: {price_growth:.1f}%
• Demand Growth: {demand_growth:.1f}%

Investment Insights: The locality demonstrates {'strong' if price_growth > 20 else 'moderate' if price_growth > 10 else 'stable'} appreciation potential with {'high' if demand_growth > 15 else 'steady'} demand trends."""
    
    return summary

def prepare_chart_data(filtered_data, is_comparison, areas):
    """Prepare data for chart visualization"""
    if is_comparison:
        years = sorted(list(set(d['year'] for d in filtered_data)))
        chart_data = []
        for year in years:
            data_point = {'year': year}
            for area in areas:
                area_data = next((d for d in filtered_data if d['year'] == year and d['area'].lower() == area), None)
                if area_data:
                    data_point[f'{area}_price'] = area_data['price']
                    data_point[f'{area}_demand'] = area_data['demand']
            chart_data.append(data_point)
        return chart_data
    else:
        return [{'year': d['year'], 'Price': d['price'], 'Demand': d['demand']} for d in filtered_data]

@csrf_exempt
def analyze_real_estate(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=400)

    try:
        body = json.loads(request.body)
        query = body.get("query", "")

        if not query:
            return JsonResponse({"error": "Query is required"}, status=400)
    except Exception as e:
        print("JSON body parse error:", e)
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    
    prompt = f"""
You must reply ONLY in VALID JSON following exactly this schema:

{{
  "summary": "string",
  "chart": [
    {{
      "year": 2021,
      "area": "wakad",
      "price": 5500,
      "demand": 850
    }}
  ],
  "table": [
    {{
      "year": 2021,
      "area": "wakad",
      "price": 5500,
      "demand": 850,
      "size": 1200,
      "type": "2BHK"
    }}
  ],
  "areas": ["wakad"],
  "isComparison": false
}}

RULES:
- DO NOT return markdown
- DO NOT add explanation
- DO NOT add extra fields
- DO NOT rename keys
- `year` must be an integer
- `price`, `demand`, `size` must be numbers
- `area`, `type` must be strings
- If data is missing, fill with null, NOT text
- Response must be plain JSON ONLY

USER QUERY: {query}
"""


    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)

        raw = response.text.strip()

        # Strip markdown fences
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(raw)
        except Exception as e:
            print("\n JSON Decode Failed:", e)
            print("Raw Gemini Output:\n", raw)
            
            # Always return fallback JSON so frontend never breaks
            parsed = {
                "summary": "AI could not generate structured data.",
                "chartData": [],
                "tableData": [],
                "isComparison": False,
                "chartType": "price"
            }

        return JsonResponse(parsed, safe=False)

    except Exception as e:
        model = genai.GenerativeModel("gemini-pro")
        print("\n GEMINI API ERROR:", e)
        # Safe fallback so UI always works
        return JsonResponse({
            "summary": "Server error while generating AI response.",
            "chartData": [],
            "tableData": [],
            "isComparison": False,
            "chartType": "price",
            "error_detail": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def upload_excel(request):
    """Endpoint to upload Excel file"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        excel_file = request.FILES['file']
        df = pd.read_excel(excel_file)
        
        
        required_columns = ['year', 'area', 'price', 'demand']
        if not all(col in df.columns for col in required_columns):
            return JsonResponse({
                'error': f'Excel must contain columns: {", ".join(required_columns)}'
            }, status=400)
        
        response = JsonResponse({
            'message': 'File uploaded successfully',
            'rows': len(df),
            'areas': df['area'].unique().tolist()
        })
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        response = JsonResponse({
            'error': f'Error processing file: {str(e)}'
        }, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response