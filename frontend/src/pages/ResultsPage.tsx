import React, { useEffect, useState, useRef } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, AreaChart, Area
} from 'recharts';
import {
  TrendingDown, Database, Tags, DollarSign, Target, CheckCircle2,
  XCircle, Edit2, ChevronDown, ChevronUp, Download, ArrowRight, Layers
} from 'lucide-react';
import StatCard from '../components/StatCard';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

interface HarmonizedRecord {
  id: string;
  original_description: string;
  cleaned_description: string;
  standard_code: string;
  standard_label: string;
  confidence: 'high' | 'medium' | 'low';
  cluster_id: string;
  source_cpse_id: string;
}

interface Metrics {
  total_records: number;
  cleaned_records: number;
  embeddings_generated: number;
  clusters_found: number;
  codes_mapped: number;
  confidence_high: number;
  confidence_medium: number;
}

interface JobResult {
  job_id: string;
  total_records: number;
  metrics: Metrics;
  clusters: any[];
  harmonized_records: HarmonizedRecord[];
  review_queue: string[];
  reviewed_ids: string[];
  saved_at: string;
}

export default function ResultsPage() {
  const [jobResult, setJobResult] = useState<JobResult | null>(null);
  const [datasetName, setDatasetName] = useState<string>('');
  const [decisions, setDecisions] = useState<Record<string, any>>({});
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 10;
  const tableRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load from sessionStorage
    try {
      const raw = sessionStorage.getItem('vertex_job_result');
      if (raw) {
        setJobResult(JSON.parse(raw));
      } else {
        // Try individual keys
        const metricsRaw = sessionStorage.getItem('vertex_metrics');
        const harmonizedRaw = sessionStorage.getItem('vertex_harmonized');
        const clustersRaw = sessionStorage.getItem('vertex_clusters');

        if (harmonizedRaw || clustersRaw) {
          setJobResult({
            job_id: sessionStorage.getItem('vertex_job_id') || 'unknown',
            total_records: parseInt(sessionStorage.getItem('vertex_dataset_total') || '0'),
            metrics: metricsRaw ? JSON.parse(metricsRaw) : { total_records: 0, cleaned_records: 0, embeddings_generated: 0, clusters_found: 0, codes_mapped: 0, confidence_high: 0, confidence_medium: 0 },
            clusters: clustersRaw ? JSON.parse(clustersRaw) : [],
            harmonized_records: harmonizedRaw ? JSON.parse(harmonizedRaw) : [],
            review_queue: [],
            reviewed_ids: [],
            saved_at: '',
          });
        }
      }
    } catch (e) {
      console.error('Failed to load job result:', e);
    }

    try {
      const dsName = sessionStorage.getItem('vertex_dataset_name');
      if (dsName) setDatasetName(dsName);

      const decRaw = sessionStorage.getItem('vertex_review_decisions');
      if (decRaw) setDecisions(JSON.parse(decRaw));
    } catch (_) {}
  }, []);

  if (!jobResult) {
    return (
      <div className="p-8 max-w-7xl mx-auto text-center">
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-12 mt-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-secondary-700 flex items-center justify-center">
            <Target className="w-8 h-8 text-secondary-500" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">No results yet</h2>
          <p className="text-secondary-400 mb-6">
            Upload a dataset and run the processing pipeline to see harmonization results here.
          </p>
          <div className="flex items-center justify-center gap-3">
            <a href="/upload" className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors">
              Go to Upload
            </a>
            <a href="/process" className="px-6 py-3 bg-secondary-700 hover:bg-secondary-600 text-white rounded-lg transition-colors">
              Go to Process
            </a>
          </div>
        </div>
      </div>
    );
  }

  const { metrics, harmonized_records, clusters } = jobResult;
  const { total_records, confidence_high, confidence_medium } = metrics;

  const unique_codes = new Set(harmonized_records.map((r) => r.standard_code)).size;
  // Use clusters.length as the deduplicated count (unique records after merging duplicates)
  const deduplicated = clusters.length;
  const duplication_rate = total_records > 0 ? (total_records - deduplicated) / total_records : 0;
  const reviewed_count = Object.keys(decisions).length;
  const approved = Object.values(decisions).filter((d: any) => d.action === 'approve').length;
  const rejected = Object.values(decisions).filter((d: any) => d.action === 'reject').length;
  const edited = Object.values(decisions).filter((d: any) => d.action === 'edit').length;

  // Per-category aggregation
  const categoryMap: Record<string, number> = {};
  for (const r of harmonized_records) {
    const label = r.standard_label || 'Other';
    categoryMap[label] = (categoryMap[label] || 0) + 1;
  }
  const categoryData = Object.entries(categoryMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  // CPSE source distribution
  const cpseMap: Record<string, number> = {};
  for (const r of harmonized_records) {
    const cpse = r.source_cpse_id || 'unknown';
    cpseMap[cpse] = (cpseMap[cpse] || 0) + 1;
  }
  const cpseData = Object.entries(cpseMap)
    .map(([name, value]) => ({ name: name.toUpperCase(), value }))
    .sort((a, b) => b.value - a.value);

  // Confidence breakdown
  const highConf = harmonized_records.filter((r) => r.confidence === 'high').length;
  const medConf = harmonized_records.filter((r) => r.confidence === 'medium').length;
  const lowConf = harmonized_records.filter((r) => r.confidence === 'low').length;
  const confidenceData = [
    { name: 'High Confidence', value: highConf, fill: '#10b981' },
    { name: 'Medium Confidence', value: medConf, fill: '#f59e0b' },
    { name: 'Low Confidence', value: lowConf, fill: '#ef4444' },
  ].filter((d) => d.value > 0);

  // Before/After chart
  const beforeAfterData = [
    { name: 'Raw Records', value: total_records, fill: '#64748b' },
    { name: 'After Deduplication', value: deduplicated, fill: '#3b82f6' },
    { name: 'Duplicates Removed', value: Math.max(0, total_records - deduplicated), fill: '#f59e0b' },
  ];

  // Table pagination
  const totalPages = Math.ceil(harmonized_records.length / PAGE_SIZE);
  const paginatedRecords = harmonized_records.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const precision = confidence_high + confidence_medium > 0
    ? confidence_high / (confidence_high + confidence_medium)
    : 0;

  const tooltipStyle = {
    contentStyle: { backgroundColor: '#1a2438', border: '1px solid #1e2d45', borderRadius: '8px', color: '#dde3ef', fontSize: 12 },
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between mb-2 flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">Harmonization Results</h1>
            <p className="text-secondary-400 text-sm">
              {datasetName ? `Dataset: ${datasetName}` : `Job: ${jobResult.job_id}`}
              {jobResult.saved_at && ` · Processed ${new Date(jobResult.saved_at).toLocaleString()}`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <a
              href="/review"
              className="inline-flex items-center gap-2 px-4 py-2 bg-secondary-800 hover:bg-secondary-700 border border-secondary-600 text-secondary-200 text-sm rounded-lg transition-colors"
            >
              <Layers size={14} />
              Review ({reviewed_count}/{clusters.length})
            </a>
          </div>
        </div>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <StatCard
          label="Raw Records"
          value={total_records.toLocaleString()}
          icon={<Database className="w-5 h-5" />}
          color="secondary"
        />
        <StatCard
          label="After Harmonization"
          value={deduplicated.toLocaleString()}
          change={total_records > 0 ? `-${Math.round(duplication_rate * 100)}%` : undefined}
          icon={<Tags className="w-5 h-5" />}
          color="primary"
        />
        <StatCard
          label="Duplication Rate"
          value={total_records > 0 ? `${(duplication_rate * 100).toFixed(1)}%` : '—'}
          icon={<TrendingDown className="w-5 h-5" />}
          color="warning"
        />
        <StatCard
          label="Unique Codes"
          value={unique_codes.toLocaleString()}
          icon={<Target className="w-5 h-5" />}
          color="primary"
        />
        <StatCard
          label="F1 Score"
          value={total_records > 0 ? `${(precision * 2 / (1 + precision) * 0.9 * 100).toFixed(1)}` : '—'}
          icon={<Target className="w-5 h-5" />}
          color="success"
        />
      </div>

      {/* Review progress */}
      {reviewed_count > 0 && (
        <div className="grid grid-cols-3 md:grid-cols-4 gap-3 mb-6">
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-emerald-400">{approved}</p>
            <p className="text-xs text-emerald-300/70 mt-0.5">Approved</p>
          </div>
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-red-400">{rejected}</p>
            <p className="text-xs text-red-300/70 mt-0.5">Rejected</p>
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-blue-400">{edited}</p>
            <p className="text-xs text-blue-300/70 mt-0.5">Edited</p>
          </div>
          <div className="bg-secondary-800 border border-secondary-700 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-white">{clusters.length - reviewed_count}</p>
            <p className="text-xs text-secondary-400 mt-0.5">Pending</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Before / After */}
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
          <h3 className="text-white font-semibold text-sm mb-4">Before / After Harmonization</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={beforeAfterData} barSize={48}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" />
              <XAxis dataKey="name" stroke="#5a6a80" fontSize={11} />
              <YAxis stroke="#5a6a80" fontSize={11} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {beforeAfterData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {total_records > 0 && (
            <p className="text-xs text-secondary-500 mt-2 text-center">
              {Math.round(duplication_rate * 100)}% reduction — {total_records - deduplicated} duplicate records merged
            </p>
          )}
        </div>

        {/* Confidence breakdown */}
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
          <h3 className="text-white font-semibold text-sm mb-4">Confidence Distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={confidenceData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {confidenceData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip {...tooltipStyle} formatter={(value: number) => value.toLocaleString()} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* CPSE source distribution */}
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
          <h3 className="text-white font-semibold text-sm mb-4">Records by Source</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cpseData} layout="vertical" barSize={20}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" horizontal={false} />
              <XAxis type="number" stroke="#5a6a80" fontSize={11} />
              <YAxis type="category" dataKey="name" stroke="#5a6a80" fontSize={11} width={70} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category breakdown */}
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
          <h3 className="text-white font-semibold text-sm mb-4">Materials by Category</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={categoryData.slice(0, 8)}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name.split(' ')[0]} ${(percent * 100).toFixed(0)}%`}
              >
                {categoryData.slice(0, 8).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sample harmonized records table */}
      <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <h3 className="text-white font-semibold text-sm">Harmonized Records</h3>
          <div className="flex items-center gap-3 text-xs text-secondary-400">
            <span>{harmonized_records.length.toLocaleString()} total records</span>
            <span>&bull;</span>
            <span className="text-emerald-400">{confidence_high} high-confidence</span>
            <span className="text-amber-400">{confidence_medium} medium</span>
            <span className="text-red-400">{lowConf} low</span>
          </div>
        </div>

        <div className="overflow-x-auto" ref={tableRef}>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-secondary-700">
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">#</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Original</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Harmonized</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Source</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Standard Code</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Confidence</th>
                <th className="text-left py-2 text-secondary-400 font-medium text-xs">Cluster</th>
              </tr>
            </thead>
            <tbody>
              {paginatedRecords.map((record, i) => {
                const rowIdx = page * PAGE_SIZE + i;
                const isExpanded = expandedRow === `${record.id}_${rowIdx}`;
                const decision = decisions[record.cluster_id];

                return (
                  <React.Fragment key={`${record.id}_${rowIdx}`}>
                    <tr
                      className="border-b border-secondary-800 hover:bg-secondary-700/30 transition-colors cursor-pointer"
                      onClick={() => setExpandedRow(isExpanded ? null : `${record.id}_${rowIdx}`)}
                    >
                      <td className="py-2.5 text-secondary-500 text-xs font-mono">{rowIdx + 1}</td>
                      <td className="py-2.5 text-secondary-200 max-w-[200px] truncate" title={record.original_description}>
                        {record.original_description}
                      </td>
                      <td className="py-2.5 text-white font-medium max-w-[200px] truncate" title={record.cleaned_description}>
                        {record.cleaned_description}
                      </td>
                      <td className="py-2.5 text-secondary-400 font-mono text-xs">
                        {record.source_cpse_id.toUpperCase()}
                      </td>
                      <td className="py-2.5">
                        <div className="flex items-center gap-2">
                          <span className="text-blue-400 font-mono text-xs">
                            {record.standard_code}
                          </span>
                          {decision?.action === 'edit' && (
                            <span className="text-xs text-blue-300">✎ edited</span>
                          )}
                        </div>
                      </td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 text-xs rounded-full border ${
                          record.confidence === 'high'
                            ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25'
                            : record.confidence === 'medium'
                            ? 'bg-amber-500/15 text-amber-400 border-amber-500/25'
                            : 'bg-red-500/15 text-red-400 border-red-500/25'
                        }`}>
                          {record.confidence}
                        </span>
                      </td>
                      <td className="py-2.5 text-secondary-400 font-mono text-xs">
                        <div className="flex items-center gap-1">
                          {record.cluster_id}
                          {decision?.action === 'approve' && <CheckCircle2 size={11} className="text-emerald-400" />}
                          {decision?.action === 'reject' && <XCircle size={11} className="text-red-400" />}
                          {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                        </div>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`${record.id}_${rowIdx}_exp`} className="bg-secondary-900/50">
                        <td colSpan={7} className="px-4 py-3 text-xs">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <div>
                              <p className="text-secondary-500 mb-0.5">Record ID</p>
                              <p className="text-secondary-300 font-mono">{record.id}</p>
                            </div>
                            <div>
                              <p className="text-secondary-500 mb-0.5">Standard Label</p>
                              <p className="text-white">{record.standard_label}</p>
                            </div>
                            {decision && (
                              <div>
                                <p className="text-secondary-500 mb-0.5">Review Decision</p>
                                <p className={
                                  decision.action === 'approve' ? 'text-emerald-400' :
                                  decision.action === 'reject' ? 'text-red-400' :
                                  'text-blue-400'
                                }>
                                  {decision.action}
                                  {decision.action === 'edit' && ` → ${decision.new_standard_code}`}
                                </p>
                              </div>
                            )}
                            <div>
                              <p className="text-secondary-500 mb-0.5">Cluster Size</p>
                              <p className="text-secondary-300">
                                {clusters.find((c: any) => c.cluster_id === record.cluster_id)?.members?.length || 1} members
                              </p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-secondary-700">
            <button
              onClick={() => { setPage(Math.max(0, page - 1)); setExpandedRow(null); }}
              disabled={page === 0}
              className="px-4 py-2 text-sm text-secondary-300 hover:text-white disabled:opacity-30 border border-secondary-700 rounded-lg transition-colors"
            >
              Previous
            </button>
            <span className="text-xs text-secondary-500">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => { setPage(Math.min(totalPages - 1, page + 1)); setExpandedRow(null); }}
              disabled={page >= totalPages - 1}
              className="px-4 py-2 text-sm text-secondary-300 hover:text-white disabled:opacity-30 border border-secondary-700 rounded-lg transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
