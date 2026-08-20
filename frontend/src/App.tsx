import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Users, Camera, Activity, MapPin, Bell, Search, LayoutDashboard, Settings, Menu, X, PlaySquare, FileText, Filter } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Legend } from 'recharts';

// Empty data state for fresh start
const activityData = [
  { name: '08:00', violations: 0 },
  { name: '10:00', violations: 0 },
  { name: '12:00', violations: 0 },
  { name: '14:00', violations: 0 },
  { name: '16:00', violations: 0 },
  { name: '18:00', violations: 0 },
  { name: '20:00', violations: 0 },
];

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [allViolations, setAllViolations] = useState<any[]>([]);
  const [selectedEvidence, setSelectedEvidence] = useState<number | null>(null);
  const [settingsEmail, setSettingsEmail] = useState('rishi11gowda@gmail.com');
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  // Fetch real-time violations from the Edge AI Node API
  useEffect(() => {
    const fetchViolations = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/violations');
        if (response.ok) {
          const data = await response.json();
          setAllViolations(data);
        }
      } catch (error) {
        console.error("Failed to fetch violations from Edge AI Node", error);
      }
    };

    fetchViolations();
    const interval = setInterval(fetchViolations, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  // Filter violations based on search
  const filteredViolations = allViolations.filter(v => 
    (v.plate_number || '').toLowerCase().includes(searchQuery.toLowerCase()) || 
    (String(v.gps_latitude) || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Views Components
  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: "Total Violations Today", value: allViolations.length.toString(), icon: AlertTriangle, color: "text-rose-400", bg: "bg-rose-400/10", border: "border-rose-500/20" },
          { title: "Helmet Violations", value: allViolations.filter(v => (v.violation_type || '') === 'NO_HELMET').length.toString(), icon: Users, color: "text-amber-400", bg: "bg-amber-400/10", border: "border-amber-500/20" },
          { title: "Active Helmets", value: "2", icon: Shield, color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-500/20" },
          { title: "Avg. Confidence", value: "92%", icon: Activity, color: "text-indigo-400", bg: "bg-indigo-400/10", border: "border-indigo-500/20" },
        ].map((stat, i) => (
          <div key={i} className={`p-5 rounded-2xl bg-slate-900/40 backdrop-blur-sm border ${stat.border} flex flex-col gap-3 hover:bg-slate-800/40 transition-colors group relative overflow-hidden`}>
            <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full ${stat.bg} blur-2xl group-hover:bg-opacity-20 transition-all`}></div>
            <div className="flex items-center justify-between relative z-10">
              <span className="text-slate-400 text-sm font-medium">{stat.title}</span>
              <div className={`p-2 rounded-lg ${stat.bg} ${stat.color}`}>
                <stat.icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-3xl font-bold text-slate-100 relative z-10">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-100">Violation Activity</h2>
            <select className="bg-slate-950 border border-slate-800 text-sm rounded-lg px-3 py-1 text-slate-300 focus:outline-none focus:border-indigo-500">
              <option>Today</option>
              <option>This Week</option>
              <option>This Month</option>
            </select>
          </div>
          <div className="flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorViolations" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} itemStyle={{ color: '#c7d2fe' }} />
                <Area type="monotone" dataKey="violations" stroke="#818cf8" strokeWidth={2} fillOpacity={1} fill="url(#colorViolations)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Camera className="w-4 h-4 text-emerald-400" /> Live Edge Node
            </h2>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-xs text-emerald-400 font-medium">ONLINE</span>
            </div>
          </div>
          <div className="relative flex-1 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex items-center justify-center min-h-[200px] group">
            <img src="http://localhost:5000/video_feed" alt="Live Camera Feed" className="absolute inset-0 w-full h-full object-cover opacity-80" onError={(e) => { setTimeout(() => { (e.target as HTMLImageElement).src = 'http://localhost:5000/video_feed?' + new Date().getTime(); }, 2000); }} />
            <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1517006846663-8a9d1808bfa0?q=80&w=600&auto=format&fit=crop')] bg-cover bg-center opacity-10 mix-blend-luminosity -z-10"></div>
            <div className="absolute bottom-3 left-3 flex flex-col gap-1 z-10">
              <span className="text-[10px] font-mono text-emerald-400 bg-black/50 px-1.5 py-0.5 rounded backdrop-blur-md">NODE: HELMET-001</span>
            </div>
          </div>
          <button onClick={() => setActiveTab('live')} className="mt-4 w-full py-2 bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-indigo-500/20">
            View Full Stream
          </button>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-100">Recent Violations</h2>
          <button onClick={() => setActiveTab('violations')} className="text-sm text-indigo-400 hover:text-indigo-300 font-medium">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-xs uppercase text-slate-500 tracking-wider">
                <th className="pb-3 font-medium px-2">Violation Type</th>
                <th className="pb-3 font-medium px-2">License Plate</th>
                <th className="pb-3 font-medium px-2">Location</th>
                <th className="pb-3 font-medium px-2">Time</th>
                <th className="pb-3 font-medium px-2">Action</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {allViolations.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500 font-medium">No violations recorded yet. The database is empty.</td>
                </tr>
              ) : (
                allViolations.slice(0, 4).map((v) => (
                  <tr key={v.violation_id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-2">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${(v.violation_type || '') === 'NO_HELMET' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                        {(v.violation_type || '').replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-4 px-2"><div className="font-mono text-slate-300 bg-slate-950 px-2 py-1 rounded border border-slate-800 inline-block">{v.plate_number}</div></td>
                    <td className="py-4 px-2 text-slate-400">{v.gps_latitude}, {v.gps_longitude}</td>
                    <td className="py-4 px-2 text-slate-400">{v.timestamp}</td>
                    <td className="py-4 px-2">
                      <button onClick={() => setSelectedEvidence(v.violation_id)} className="text-indigo-400 hover:text-indigo-300 font-medium text-xs bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-1.5 rounded-lg transition-colors border border-indigo-500/20">
                        Review Evidence
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderLiveCamera = () => (
    <div className="flex flex-col h-full bg-slate-900/40 rounded-2xl border border-slate-800 overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-3">
          <Camera className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-slate-100">Live Surveillance Stream</h2>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> LIVE
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-colors">Switch Camera</button>
          <button className="px-3 py-1.5 text-xs font-medium bg-indigo-500 hover:bg-indigo-600 rounded-lg text-white transition-colors">Record Clip</button>
        </div>
      </div>
      <div className="flex-1 relative bg-black flex items-center justify-center p-4">
        <img src="http://localhost:5000/video_feed" alt="Live Camera Feed" className="w-full h-full object-contain rounded-xl border border-slate-800 shadow-2xl" onError={(e) => { setTimeout(() => { (e.target as HTMLImageElement).src = 'http://localhost:5000/video_feed?' + new Date().getTime(); }, 2000); }} />
        <div className="absolute top-8 left-8 flex flex-col gap-2 opacity-80">
           <div className="bg-black/60 backdrop-blur text-emerald-400 font-mono text-sm px-3 py-1 rounded border border-emerald-500/30">NODE: HELMET-001 (MAIN JUNCTION)</div>
           <div className="bg-black/60 backdrop-blur text-slate-300 font-mono text-sm px-3 py-1 rounded border border-slate-700">YOLOv8 INT8 INFERENCE ACTIVE</div>
        </div>
      </div>
    </div>
  );

  const renderViolations = () => (
    <div className="p-6 rounded-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-slate-100">Violation Database</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors border border-slate-700">
          <Filter className="w-4 h-4" /> Filter Records
        </button>
      </div>
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-slate-900/90 backdrop-blur-md z-10">
            <tr className="border-b border-slate-800 text-xs uppercase text-slate-500 tracking-wider">
              <th className="pb-3 pt-4 font-medium px-4">ID</th>
              <th className="pb-3 pt-4 font-medium px-4">Violation Type</th>
              <th className="pb-3 pt-4 font-medium px-4">License Plate</th>
              <th className="pb-3 pt-4 font-medium px-4">Location</th>
              <th className="pb-3 pt-4 font-medium px-4">Timestamp</th>
              <th className="pb-3 pt-4 font-medium px-4">Status</th>
              <th className="pb-3 pt-4 font-medium px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {filteredViolations.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-slate-500 font-medium">Database is completely empty. Ready to capture new records.</td>
              </tr>
            ) : (
              filteredViolations.map((v) => (
                <tr key={v.violation_id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-4 text-slate-500 font-mono">#{v.violation_id}</td>
                  <td className="py-4 px-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${(v.violation_type || '') === 'NO_HELMET' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                      {(v.violation_type || '').replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-4 px-4"><div className="font-mono text-slate-200 bg-slate-950 px-2 py-1 rounded border border-slate-700 inline-block">{v.plate_number}</div></td>
                  <td className="py-4 px-4 text-slate-400">{v.gps_latitude}, {v.gps_longitude}</td>
                  <td className="py-4 px-4 text-slate-400">{v.timestamp}</td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-1 rounded-md text-[11px] font-semibold ${v.status === 'Pending' ? 'bg-yellow-500/20 text-yellow-500' : v.status === 'Reviewed' ? 'bg-emerald-500/20 text-emerald-500' : 'bg-blue-500/20 text-blue-500'}`}>
                      {v.status}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    <button onClick={() => setSelectedEvidence(v.violation_id)} className="text-indigo-400 hover:text-indigo-300 font-medium text-xs bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-1.5 rounded-lg transition-colors border border-indigo-500/20">
                      Review
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800">
        <h2 className="text-lg font-semibold text-slate-100 mb-6">Violations by Type (Weekly)</h2>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={activityData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false}/>
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }} />
              <Legend />
              <Bar dataKey="violations" name="No Helmet" stackId="a" fill="#f59e0b" radius={[0, 0, 4, 4]} />
              <Bar dataKey="violations" name="Triple Riding" stackId="a" fill="#f43f5e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="max-w-2xl bg-slate-900/40 backdrop-blur-sm border border-slate-800 rounded-2xl p-8">
      <h2 className="text-xl font-bold text-slate-100 mb-6 flex items-center gap-2"><Settings className="w-5 h-5 text-indigo-400"/> System Settings</h2>
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Confidence Threshold (%)</label>
          <input type="range" min="50" max="100" defaultValue="85" className="w-full accent-indigo-500" />
          <div className="flex justify-between text-xs text-slate-500 mt-1"><span>50%</span><span>85%</span><span>100%</span></div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Email Alert Recipient</label>
          <input 
            type="email" 
            value={settingsEmail}
            onChange={(e) => setSettingsEmail(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-indigo-500" 
          />
        </div>
        <div className="pt-4 border-t border-slate-800">
          <button onClick={() => alert("Settings Saved!")} className="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-lg transition-colors shadow-lg shadow-indigo-500/20">Save Configuration</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900/80 backdrop-blur-xl border-r border-slate-800 transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 flex flex-col`}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-slate-800">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-xl tracking-tight">
            <Shield className="w-6 h-6" />
            <span>SmartHelmet</span>
          </div>
          <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setSidebarOpen(false)}>
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'live', label: 'Live Camera', icon: Camera },
            { id: 'violations', label: 'Violations', icon: AlertTriangle },
            { id: 'analytics', label: 'Analytics', icon: Activity },
            { id: 'settings', label: 'Settings', icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${activeTab === item.id ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setSidebarOpen(true)}>
              <Menu className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold capitalize text-slate-100">{activeTab.replace('-', ' ')}</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative hidden md:block">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input 
                type="text" 
                placeholder="Search plate numbers..." 
                value={searchQuery}
                onChange={(e) => {setSearchQuery(e.target.value); setActiveTab('violations');}}
                className="bg-slate-950 border border-slate-800 rounded-full pl-9 pr-4 py-1.5 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all text-slate-200 placeholder-slate-500 w-64"
              />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <div className="max-w-7xl mx-auto h-full">
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'live' && renderLiveCamera()}
            {activeTab === 'violations' && renderViolations()}
            {activeTab === 'analytics' && renderAnalytics()}
            {activeTab === 'settings' && renderSettings()}
          </div>
        </div>
      </main>

      {/* Evidence Modal */}
      {selectedEvidence && (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col">
            <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
              <h3 className="font-semibold text-lg flex items-center gap-2"><FileText className="w-5 h-5 text-indigo-400"/> Evidence Package #{selectedEvidence}</h3>
              <button onClick={() => setSelectedEvidence(null)} className="text-slate-400 hover:text-white"><X className="w-6 h-6"/></button>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Snapshot</h4>
                <div className="aspect-video bg-slate-950 rounded-lg border border-slate-700 overflow-hidden relative group cursor-pointer">
                   <img src={`http://localhost:5000/api/snapshots/${selectedEvidence}`} alt="Snapshot" className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" onError={(e) => {(e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?q=80&w=600&auto=format&fit=crop';}}/>
                   <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40"><Search className="w-8 h-8 text-white"/></div>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-slate-400 uppercase tracking-wider">Video Clip</h4>
                <div className="aspect-video bg-slate-950 rounded-lg border border-slate-700 overflow-hidden relative flex items-center justify-center group cursor-pointer">
                  <PlaySquare className="w-12 h-12 text-slate-600 group-hover:text-indigo-400 transition-colors" />
                </div>
              </div>
            </div>
            <div className="px-6 py-4 bg-slate-800/30 border-t border-slate-700 flex justify-end gap-3 items-center">
              {sendSuccess && <span className="text-sm text-emerald-400 font-medium mr-2">Report Sent to {settingsEmail}!</span>}
              <button onClick={() => {setSelectedEvidence(null); setSendSuccess(false);}} className="px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700 rounded-lg transition-colors border border-slate-600">Dismiss</button>
              <button 
                onClick={async () => {
                  try {
                    const res = await fetch('http://localhost:5000/send_report', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ email: settingsEmail, id: selectedEvidence })
                    });
                    if (res.ok) {
                      setSendSuccess(true);
                      setTimeout(() => setSendSuccess(false), 4000);
                    } else {
                      alert('Failed to send email');
                    }
                  } catch (err) {
                    alert('Error sending email');
                  }
                }} 
                className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors shadow-lg ${sendSuccess ? 'bg-emerald-500 shadow-emerald-500/20' : 'bg-rose-500 hover:bg-rose-600 shadow-rose-500/20'}`}
              >
                {sendSuccess ? 'Report Sent!' : 'Send Report via Server'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
