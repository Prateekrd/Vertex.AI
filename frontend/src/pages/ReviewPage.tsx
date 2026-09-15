import React, { useState, useEffect } from 'react';
import {
  Check, X, Edit2, ChevronLeft, ChevronRight, AlertCircle, CheckCircle,
  Layers, ArrowRight, Filter
} from 'lucide-react';

interface ClusterMember {
  id: string;
  cleaned_description: string;
  extracted_attrs: Record<string, any>;
  source_cpse_id: string;
  original_description?: string;
}

interface ClusterItem {
  cluster_id: string;
  member_ids: number[];
  representative: string;
  avg_similarity: number;
  confidence: 'high' | 'medium' | 'low';
  standard_code: string;
  standard_label: string;
  members: ClusterMember[];
}

interface ReviewDecision {
  action: 'approve' | 'reject' | 'edit';
  new_standard_code?: string;
}

const STORAGE_KEY = 'vertex_review_decisions';

function loadReviewDecisions(): Record<string, ReviewDecision> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (_) {
    return {};
  }
}

function saveReviewDecisions(d: Record<string, ReviewDecision>) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(d));
}

export default function ReviewPage() {
  const [allClusters, setAllClusters] = useState<ClusterItem[]>([]);
  const [queue, setQueue] = useState<ClusterItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [decision, setDecision] = useState<ReviewDecision | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showCodeEdit, setShowCodeEdit] = useState(false);
  const [editCode, setEditCode] = useState('');
  const [datasetName, setDatasetName] = useState<string>('');
  const [confidenceFilter, setConfidenceFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [decisions, setDecisions] = useState<Record<string, ReviewDecision>>(loadReviewDecisions());
  const [showReviewed, setShowReviewed] = useState(false);

  // Load real clusters from sessionStorage
  useEffect(() => {
    const clustersRaw = sessionStorage.getItem('vertex_clusters');
    const uploadId = sessionStorage.getItem('active_upload_id') || '';
    const dsName = sessionStorage.getItem('vertex_dataset_name') || '';
    setDatasetName(dsName);

    if (clustersRaw) {
      try {
        const parsed: ClusterItem[] = JSON.parse(clustersRaw);
        setAllClusters(parsed);
      } catch (e) {
        console.error('Failed to parse clusters:', e);
        setAllClusters([]);
      }
    }
  }, []);

  // Build filtered queue
  useEffect(() => {
    const reviewed = new Set(Object.keys(decisions));
    const filtered = allClusters.filter((c) => {
      if (showReviewed ? !reviewed.has(c.cluster_id) : reviewed.has(c.cluster_id)) return false;
      if (confidenceFilter !== 'all' && c.confidence !== confidenceFilter) return false;
      return true;
    });
    setQueue(filtered);
    setCurrentIndex(0);
  }, [allClusters, decisions, confidenceFilter, showReviewed]);

  const currentCluster = queue[currentIndex];
  const totalReviewed = Object.keys(decisions).length;
  const reviewProgress = allClusters.length > 0 ? Math.round((totalReviewed / allClusters.length) * 100) : 0;

  const handleApprove = async () => {
    if (!currentCluster) return;
    setSubmitting(true);
    const d: ReviewDecision = { action: 'approve', new_standard_code: currentCluster.standard_code };
    const updated = { ...decisions, [currentCluster.cluster_id]: d };
    setDecisions(updated);
    saveReviewDecisions(updated);
    setDecision(d);
    setTimeout(() => nextItem(), 350);
    setSubmitting(false);
  };

  const handleReject = async () => {
    if (!currentCluster) return;
    setSubmitting(true);
    const d: ReviewDecision = { action: 'reject' };
    const updated = { ...decisions, [currentCluster.cluster_id]: d };
    setDecisions(updated);
    saveReviewDecisions(updated);
    setDecision(d);
    setTimeout(() => nextItem(), 350);
    setSubmitting(false);
  };

  const handleEdit = async () => {
    if (!currentCluster) return;
    setSubmitting(true);
    const d: ReviewDecision = { action: 'edit', new_standard_code: editCode || currentCluster.standard_code };
    const updated = { ...decisions, [currentCluster.cluster_id]: d };
    setDecisions(updated);
    saveReviewDecisions(updated);
    setDecision(d);
    setShowCodeEdit(false);
    setTimeout(() => nextItem(), 350);
    setSubmitting(false);
  };

  const nextItem = () => {
    if (currentIndex < queue.length - 1) {
      setCurrentIndex((i) => i + 1);
      setDecision(null);
      setShowCodeEdit(false);
    }
  };

  const prevItem = () => {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
      setDecision(null);
      setShowCodeEdit(false);
    }
  };

  const confidenceColor = (conf: string) => {
    switch (conf) {
      case 'high':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      default:
        return 'bg-red-500/20 text-red-400 border-red-500/30';
    }
  };

  // ── Empty state ─────────────────────────────────────────────────────────

  if (allClusters.length === 0) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center">
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-12 mt-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-secondary-700 flex items-center justify-center">
            <Layers className="w-8 h-8 text-secondary-500" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">No clusters to review</h2>
          <p className="text-secondary-400 mb-6 max-w-md mx-auto">
            Upload a dataset and run the processing pipeline first. The duplicate clusters found will appear here for review.
          </p>
          <a
            href="/upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors shadow-lg shadow-blue-900/30"
          >
            Go to Upload
            <ArrowRight size={16} />
          </a>
        </div>
      </div>
    );
  }

  if (!currentCluster) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center">
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-12 mt-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-emerald-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">All done!</h2>
          <p className="text-secondary-400 mb-6">
            {showReviewed
              ? 'No reviewed clusters in this filter.'
              : 'No more clusters in this filter. Switch the filter or check reviewed items.'}
          </p>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => setShowReviewed(!showReviewed)}
              className="px-4 py-2 text-sm text-secondary-300 hover:text-white border border-secondary-600 hover:border-secondary-500 rounded-lg transition-colors"
            >
              {showReviewed ? 'Show Unreviewed' : 'Show Reviewed'}
            </button>
            <a
              href="/results"
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              View Results
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </div>
    );
  }

  // ── Main render ────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between mb-4 flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">Duplicate Review</h1>
            <p className="text-secondary-400 text-sm">
              {datasetName ? `Reviewing clusters from: ${datasetName}` : 'Review and approve suggested duplicate clusters'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-secondary-400 text-sm">
              Item {currentIndex + 1} of {queue.length}
            </p>
            <p className="text-secondary-500 text-xs mt-0.5">
              {totalReviewed} of {allClusters.length} reviewed overall
            </p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-1.5 bg-secondary-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 transition-all duration-500 ease-out"
            style={{ width: `${reviewProgress}%` }}
          />
        </div>
        <p className="text-xs text-secondary-500 mt-1">{reviewProgress}% complete</p>

        {/* Filters */}
        <div className="flex items-center gap-2 mt-4 flex-wrap">
          <Filter size={14} className="text-secondary-500" />
          <span className="text-xs text-secondary-500">Filter:</span>
          {(['all', 'high', 'medium', 'low'] as const).map((c) => {
            const count = c === 'all' ? allClusters.length : allClusters.filter((x) => x.confidence === c).length;
            return (
              <button
                key={c}
                onClick={() => setConfidenceFilter(c)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                  confidenceFilter === c
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-secondary-800 border-secondary-700 text-secondary-300 hover:border-secondary-500'
                }`}
              >
                {c} ({count})
              </button>
            );
          })}
          <div className="flex-1" />
          <button
            onClick={() => setShowReviewed(!showReviewed)}
            className={`px-3 py-1 text-xs rounded-full border transition-colors ${
              showReviewed
                ? 'bg-secondary-700 border-secondary-500 text-white'
                : 'bg-secondary-800 border-secondary-700 text-secondary-300 hover:border-secondary-500'
            }`}
          >
            {showReviewed ? 'Showing Reviewed' : 'Hide Reviewed'}
          </button>
        </div>
      </div>

      {/* Cluster Card */}
      <div className="bg-secondary-800 rounded-xl border border-secondary-700 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-secondary-700 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div>
              <p className="text-secondary-400 text-xs">Cluster ID</p>
              <p className="text-white font-mono font-medium text-sm">{currentCluster.cluster_id}</p>
            </div>
            <div>
              <p className="text-secondary-400 text-xs">Members</p>
              <p className="text-white font-mono font-medium text-sm">{currentCluster.members.length}</p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${confidenceColor(currentCluster.confidence)}`}>
            {currentCluster.confidence.toUpperCase()} CONFIDENCE
          </span>
          <div className="flex items-center gap-4 text-secondary-300 text-sm flex-wrap">
            <span>Similarity: <span className="text-white font-mono">{(currentCluster.avg_similarity * 100).toFixed(1)}%</span></span>
            <span>Standard: <span className="text-white font-mono">{currentCluster.standard_code}</span></span>
            <span className="text-secondary-200">{currentCluster.standard_label}</span>
          </div>
        </div>

        {/* Member Comparison */}
        <div className="p-4">
          <p className="text-white font-medium mb-4 text-sm">Candidate Duplicates</p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {currentCluster.members.map((member, idx) => (
              <div key={member.id + idx} className="bg-secondary-900 rounded-lg p-4 border border-secondary-700">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-secondary-400 text-xs font-mono px-2 py-0.5 bg-secondary-800 rounded">
                    {member.source_cpse_id.toUpperCase()}
                  </span>
                  <span className="text-secondary-500 text-xs">#{idx + 1}</span>
                </div>
                <p className="text-white font-medium mb-2 text-sm">
                  {member.cleaned_description}
                </p>
                {member.original_description && member.original_description !== member.cleaned_description && (
                  <p className="text-secondary-500 text-xs italic mb-3 line-clamp-2">
                    Original: "{member.original_description}"
                  </p>
                )}
                {member.extracted_attrs && Object.keys(member.extracted_attrs).length > 0 && (
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(member.extracted_attrs).map(([key, value]) => (
                      <div key={key} className="flex justify-between bg-secondary-800 px-2 py-1 rounded">
                        <span className="text-secondary-400 capitalize">{key.replace('_', ' ')}</span>
                        <span className="text-white font-mono">
                          {value === null || value === undefined ? '—' : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-secondary-700 bg-secondary-900/50">
          {showCodeEdit ? (
            <div className="flex items-center gap-3 flex-wrap">
              <input
                type="text"
                value={editCode}
                onChange={(e) => setEditCode(e.target.value)}
                placeholder="Enter standard code (e.g., 10101503)"
                className="flex-1 px-3 py-2 bg-secondary-700 border border-secondary-600 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <button
                onClick={handleEdit}
                disabled={submitting}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded disabled:opacity-50"
              >
                Save Edit
              </button>
              <button
                onClick={() => setShowCodeEdit(false)}
                className="px-4 py-2 bg-secondary-700 hover:bg-secondary-600 text-white text-sm rounded"
              >
                Cancel
              </button>
            </div>
          ) : decision ? (
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span className="font-medium text-sm text-emerald-300">
                {decision.action === 'approve' && 'Approved'}
                {decision.action === 'reject' && 'Rejected'}
                {decision.action === 'edit' && `Edited to ${decision.new_standard_code}`}
              </span>
              {currentIndex < queue.length - 1 && (
                <button
                  onClick={nextItem}
                  className="ml-auto text-xs text-blue-400 hover:text-blue-300"
                >
                  Next →
                </button>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-3 flex-wrap">
              <button
                onClick={handleApprove}
                disabled={submitting}
                className="flex-1 md:flex-none px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm rounded font-medium disabled:opacity-50 transition-colors"
              >
                <Check className="w-4 h-4 inline mr-1" />
                Approve
              </button>
              <button
                onClick={() => { setShowCodeEdit(true); setEditCode(currentCluster.standard_code); }}
                disabled={submitting}
                className="flex-1 md:flex-none px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded font-medium disabled:opacity-50 transition-colors"
              >
                <Edit2 className="w-4 h-4 inline mr-1" />
                Edit Code
              </button>
              <button
                onClick={handleReject}
                disabled={submitting}
                className="flex-1 md:flex-none px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm rounded font-medium disabled:opacity-50 transition-colors"
              >
                <X className="w-4 h-4 inline mr-1" />
                Reject
              </button>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-secondary-700">
            <button
              onClick={prevItem}
              disabled={currentIndex === 0 || submitting}
              className="px-4 py-2 text-secondary-300 hover:text-white disabled:opacity-30 flex items-center gap-1 text-sm"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </button>
            <span className="text-xs text-secondary-500">
              Decision saved for current
            </span>
            <button
              onClick={nextItem}
              disabled={currentIndex === queue.length - 1 || submitting}
              className="px-4 py-2 text-secondary-300 hover:text-white disabled:opacity-30 flex items-center gap-1 text-sm"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
