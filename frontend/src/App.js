
import { useState, useRef, useEffect } from 'react';
import { Send, Download, TrendingUp, Home } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const RealEstateChatbot = () => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: 'Hello! I\'m your Real Estate Analysis Assistant. Ask me about localities like Wakad, Aundh, Ambegaon Budruk, or Akurdi.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


 const prepareChartData = (data) => {
  if (!data || !Array.isArray(data)) return [];

  return data.map(d => ({
    year: d.year,
    price: d.price,
    demand: d.demand
  }));
};

const prepareComparisonChartData = (data, areas) => {
  if (!data || !Array.isArray(data)) return [];

  const years = [...new Set(data.map(d => d.year))];

  return years.map(year => {
    const obj = { year };

    areas.forEach(area => {
      const areaKey = area.toLowerCase();
      const record = data.find(
        d => d.year === year && d.area.toLowerCase() === areaKey
      );

      if (record) {
        obj[`${areaKey}_price`] = record.price;
        obj[`${areaKey}_demand`] = record.demand;
      }
    });

    return obj;
  });
};



  const processQuery = async (query) => {
  setIsProcessing(true);

  
  setMessages(prev => [...prev, {
    type: "user",
    content: query,
    timestamp: new Date()
  }]);

  try {
    const res = await fetch("https://real-estate-analyzer-9ir8.onrender.com/api/analyze/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    const data = await res.json();

    
    const isComparison = data.isComparison ?? false;

    let finalChartData = [];

    if (isComparison) {
      finalChartData = prepareComparisonChartData(data.chart, data.areas);
    } else {
      finalChartData = prepareChartData(data.chart);
    }

    setMessages(prev => [...prev, {
      type: "bot",
      content: data.summary ?? "No summary generated.",
      chartData: finalChartData,
      tableData: data.table ?? [],
      isComparison: isComparison,
      chartType: data.chartType ?? "single",
      timestamp: new Date()
    }]);

  } catch (err) {
    setMessages(prev => [...prev, {
      type: "bot",
      content: "Server error: " + err.message,
      timestamp: new Date()
    }]);
  }

  setIsProcessing(false);
};




  


  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isProcessing) {
      processQuery(input);
      setInput('');
    }
  };

  const downloadTableData = (data) => {
    const csv = [
      ['Year', 'Area', 'Price (₹/sq.ft)', 'Demand Index', 'Size (sq.ft)', 'Type'],
      ...data.map(d => [d.year, d.area, d.price, d.demand, d.size, d.type])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'real_estate_data.csv';
    a.click();
  };

  const sampleQueries = [
    "Give me analysis of Wakad",
    "Compare Ambegaon Budruk and Aundh demand trends",
    "Show price growth for Akurdi over the last 3 years"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Home className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Real Estate Analyzer</h1>
              <p className="text-sm text-gray-600">Powered by AI Analytics</p>
            </div>
          </div>
          <TrendingUp className="text-indigo-600" size={32} />
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Sample Queries */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <p className="text-sm font-semibold text-gray-700 mb-2">Try these queries:</p>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((query, idx) => (
              <button
                key={idx}
                onClick={() => setInput(query)}
                className="text-xs bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full hover:bg-indigo-100 transition"
              >
                {query}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Container  */}
        <div className="bg-white rounded-lg shadow-lg" style={{ height: 'calc(100vh - 280px)' }}>
          {/* Messages */}
          <div className="h-full overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-4xl ${msg.type === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'} rounded-lg p-4 shadow`}>
                  <p className="whitespace-pre-line">{msg.content}</p>
                  
                  {/* Chart */}
                  {msg.chartData && (
                    <div className="mt-4 bg-white rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">
                        {msg.isComparison ? 'Comparison Chart' : 'Trend Analysis'}
                      </h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={msg.chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          {msg.isComparison ? (
  <>
    {Object.keys(msg.chartData[0])
      .filter(key => key.endsWith("_price"))
      .map((priceKey, index) => (
        <Line
          key={priceKey}
          type="monotone"
          dataKey={priceKey}
          stroke={index === 0 ? "#8b5cf6" : "#3b82f6"}
          strokeWidth={2}
          name={priceKey.replace("_price", "").toUpperCase() + " Price"}
        />
      ))}
  </>
) : (
  <>
    <Line type="monotone" dataKey="price" stroke="#8b5cf6" strokeWidth={2} />
    <Line type="monotone" dataKey="demand" stroke="#3b82f6" strokeWidth={2} />
  </>
)}

                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {/* Table */}
                  {msg.tableData && (
                    <div className="mt-4 bg-white rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-lg font-semibold text-gray-800">Data Table</h3>
                        <button
                          onClick={() => downloadTableData(msg.tableData)}
                          className="flex items-center gap-2 bg-green-500 text-white px-3 py-1.5 rounded-lg hover:bg-green-600 transition text-sm"
                        >
                          <Download size={16} />
                          Download CSV
                        </button>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left">Year</th>
                              <th className="px-4 py-2 text-left">Area</th>
                              <th className="px-4 py-2 text-right">Price (₹/sq.ft)</th>
                              <th className="px-4 py-2 text-right">Demand</th>
                              <th className="px-4 py-2 text-right">Size</th>
                              <th className="px-4 py-2 text-left">Type</th>
                            </tr>
                          </thead>
                          <tbody>
                            {msg.tableData.map((row, i) => (
                              <tr key={i} className="border-t">
                                <td className="px-4 py-2">{row.year}</td>
                                <td className="px-4 py-2">{row.area}</td>
                                <td className="px-4 py-2 text-right">₹{row.price}</td>
                                <td className="px-4 py-2 text-right">{row.demand}</td>
                                <td className="px-4 py-2 text-right">{row.size}</td>
                                <td className="px-4 py-2">{row.type}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs mt-2 opacity-70">
                    {msg.timestamp ? msg.timestamp.toLocaleTimeString() : ""}

                  </p>
                </div>
              </div>
            ))}
            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-4 shadow">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                    <span className="text-gray-600">Analyzing data...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about real estate areas (Wakad, Aundh, Ambegaon Budruk, Akurdi)..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-600"
            disabled={isProcessing}
          />
          <button
            type="submit"
            disabled={isProcessing || !input.trim()}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition flex items-center gap-2"
          >
            <Send size={20} />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default RealEstateChatbot;