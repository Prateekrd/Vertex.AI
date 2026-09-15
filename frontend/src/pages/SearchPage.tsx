import React, { useState, useEffect, useMemo } from 'react';
import { Search as SearchIcon, Tag, FileText, AlertCircle, Database } from 'lucide-react';

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

function tokenize(s: string): string[] {
  return s.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter((w) => w.length > 1);
}

function score(queryTokens: string[], docTokens: string[]): number {
  if (queryTokens.length === 0 || docTokens.length === 0) return 0;
  const set = new Set(docTokens);
  const matched = queryTokens.filter((t) => set.has(t)).length;
  return matched / queryTokens.length;
}

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Array<{ record: HarmonizedRecord; similarity_score: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [harmonized, setHarmonized] = useState<HarmonizedRecord[]>([]);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem('vertex_harmonized');
    if (raw) {
      try {
        setHarmonized(JSON.parse(raw));
        setHasData(true);
      } catch (_) {}
    }
  }, []);

  const exampleQueries = useMemo(() => {
    if (harmonized.length === 0) return [];
    const seen = new Set<string>();
    const samples: string[] = [];
    for (const r of harmonized) {
      const tokens = tokenize(r.cleaned_description);
      // Take first 3-4 tokens
      const q = tokens.slice(0, Math.min(4, tokens.length)).join(' ');
      if (q && !seen.has(q) && samples.length < 6) {
        seen.add(q);
        samples.push(q);
      }
      if (samples.length >= 6) break;
    }
    return samples;
  }, [harmonized]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);

    // Try real API first
    try {
      const res = await fetch('/api/v1/search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 20 }),
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        setLoading(false);
        return;
      }
    } catch (_) {}

    // Local search over harmonized data
    if (harmonized.length === 0) {
      setResults([]);
      setLoading(false);
      return;
    }

    const queryTokens = tokenize(query);
    const scored = harmonized
      .map((record) => {
        const cleanedTokens = tokenize(record.cleaned_description);
        const originalTokens = tokenize(record.original_description);
        const sClean = score(queryTokens, cleanedTokens);
        const sOrig = score(queryTokens, originalTokens);
        return {
          record,
          similarity_score: Math.max(sClean, sOrig * 0.85),
        };
      })
      .filter((r) => r.similarity_score > 0.15)
      .sort((a, b) => b.similarity_score - a.similarity_score)
      .slice(0, 20);

    setResults(scored);
    setLoading(false);
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-1">Search & Lookup</h1>
        <p className="text-secondary-400 text-sm">
          {hasData
            ? `Searching across ${harmonized.length.toLocaleString()} harmonized records from your dataset`
            : 'Search any material description to find duplicates across all CPSE datasets.'}
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={hasData ? 'e.g., stainless steel pipe 10mm' : 'e.g., SS Pipe 10mm x 5m'}
            className="w-full pl-12 pr-4 py-4 bg-secondary-800 border border-secondary-700 rounded-lg text-white placeholder-secondary-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-base"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full mt-3 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors disabled:opacity-50 shadow-lg shadow-blue-900/20"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Example queries */}
      {!searched && exampleQueries.length > 0 && (
        <div className="mb-6">
          <p className="text-secondary-400 text-xs mb-3">Try from your dataset:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((q, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(q);
                  setTimeout(() => {
                    const form = document.querySelector('form') as HTMLFormElement;
                    form.requestSubmit();
                  }, 50);
                }}
                className="px-3 py-1.5 bg-secondary-800 hover:bg-secondary-700 text-secondary-200 text-xs rounded-full border border-secondary-700 hover:border-secondary-500 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {searched && (
        <div className="bg-secondary-800 rounded-xl border border-secondary-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold text-sm">
              Results for "{query}"
            </h3>
            <span className="text-secondary-400 text-xs">
              {results.length} matches
            </span>
          </div>

          {results.length === 0 ? (
            <div className="text-center py-12">
              <AlertCircle className="w-12 h-12 text-secondary-500 mx-auto mb-3" />
              <p className="text-secondary-400 text-sm">
                {hasData
                  ? 'No matches found in your harmonized records.'
                  : 'Upload a dataset first to search within your records.'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {results.map((result, i) => {
                const sim = result.similarity_score * 100;
                const colorClass =
                  sim >= 75 ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25' :
                  sim >= 50 ? 'bg-amber-500/15 text-amber-400 border-amber-500/25' :
                  'bg-secondary-700 text-secondary-300 border-secondary-600';
                return (
                  <div
                    key={`${result.record.id}_${i}`}
                    className="bg-secondary-900 rounded-lg p-4 border border-secondary-700 hover:border-blue-500/40 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-white font-medium text-sm mb-1.5">
                          {result.record.cleaned_description}
                        </p>
                        {result.record.original_description && result.record.original_description !== result.record.cleaned_description && (
                          <p className="text-secondary-500 text-xs italic mb-2 truncate">
                            Original: "{result.record.original_description}"
                          </p>
                        )}
                        <div className="flex items-center gap-2 flex-wrap text-xs">
                          <span className="text-blue-400 font-mono bg-blue-500/10 px-1.5 py-0.5 rounded">
                            {result.record.standard_code}
                          </span>
                          <span className="text-secondary-300">{result.record.standard_label}</span>
                          <span className="text-secondary-600">·</span>
                          <span className="text-secondary-400 font-mono">{result.record.source_cpse_id.toUpperCase()}</span>
                          <span className="text-secondary-600">·</span>
                          <span className="text-secondary-500 font-mono">{result.record.id}</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${colorClass}`}>
                          {sim.toFixed(1)}%
                        </span>
                        <span className="text-xs text-secondary-500">
                          {result.record.confidence}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {!hasData && !searched && (
        <div className="bg-secondary-800/50 rounded-xl border border-dashed border-secondary-700 p-6 text-center">
          <Database className="w-10 h-10 text-secondary-600 mx-auto mb-3" />
          <p className="text-secondary-400 text-sm">
            No harmonized data found. Upload a dataset and run the pipeline to enable search.
          </p>
        </div>
      )}
    </div>
  );
}
