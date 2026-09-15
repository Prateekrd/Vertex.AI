import React, { useState, useCallback } from 'react';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle, Play } from 'lucide-react';
import { uploadAPI } from '../api/client';

const StatusIcon = ({ ok }: { ok: boolean }) =>
  ok ? (
    <CheckCircle className="w-4 h-4 text-success-500" />
  ) : (
    <AlertCircle className="w-4 h-4 text-warning-500" />
  );

export default function UploadPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [samples, setSamples] = useState<any[]>([]);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Load sample datasets on mount
  React.useEffect(() => {
    uploadAPI
      .getSamples()
      .then((res) => {
        const data = res.data;
        setSamples(data.samples || []);
      })
      .catch((err) => {
        console.warn('Could not load samples:', err);
      });
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    setUploadedFile(file);
    setError(null);
    setUploadResult(null);
    // Parse preview (first 5 rows) + save ALL records to sessionStorage
    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = (ev.target?.result as string) || '';
      const lines = text.split('\n').filter((l) => l.trim());
      const header = lines[0]?.split(',').map((h) => h.trim()) || [];
      const allRows = lines.slice(1).map((line) => {
        const values = line.split(',');
        return Object.fromEntries(
          header.map((h, i) => [h, values[i]?.trim() || '']),
        );
      });
      setPreview(allRows.slice(0, 5));

      // Persist full dataset for downstream tabs
      try {
        const normalized = allRows.map((row, i) => {
          const descCol = Object.keys(row).find((k) =>
            /desc|name|item|material|title|product/i.test(k)
          );
          const idCol = Object.keys(row).find((k) => /^(id|mat|material_?id|item_?id|sku)$/i.test(k));
          const cpseCol = Object.keys(row).find((k) => /cpse|source|vendor|supplier/i.test(k));
          return {
            id: idCol ? row[idCol] : `mat_${String(i + 1).padStart(4, '0')}`,
            description: descCol ? row[descCol] : Object.values(row).find((v) => typeof v === 'string' && v.length > 5) as string || `Material ${i + 1}`,
            source_cpse_id: cpseCol ? row[cpseCol] : 'cpse_a',
            raw: row,
          };
        }).filter((r) => r.description);

        sessionStorage.setItem('vertex_raw_records', JSON.stringify(normalized));
        sessionStorage.setItem('vertex_dataset_name', file.name);
        sessionStorage.setItem('vertex_dataset_total', String(normalized.length));
      } catch (e) {
        console.warn('Failed to save raw records:', e);
      }
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;
    setIsUploading(true);
    setError(null);
    try {
      const res = await uploadAPI.uploadFile(uploadedFile);
      setUploadResult(res.data);
      if (res.data?.upload_id) {
        sessionStorage.setItem('active_upload_id', res.data.upload_id);
      }
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadSample = async (sampleId: string) => {
    try {
      const res = await uploadAPI.loadSample(sampleId);
      const sample = samples.find((s) => s.id === sampleId);
      setUploadResult({
        upload_id: sampleId,
        total_records: res.data.total_records,
        processed: res.data.total_records,
        message: res.data.message + (sample ? ` (${sample.file})` : ''),
        source: 'sample',
        raw_records: Array.from({ length: res.data.total_records }, (_, i) => i + 1),
      });
      // Show a preview of first records
      setPreview(res.data.first_record ? [res.data.first_record] : []);

      // Persist the sample records for downstream tabs
      const sampleRecords = res.data.records || res.data.raw_records || [];
      const normalized = sampleRecords.length > 0
        ? sampleRecords.map((row: any, i: number) => ({
            id: row.id || row.material_id || `mat_${String(i + 1).padStart(4, '0')}`,
            description: row.description || row.name || row.material_name || row.material || JSON.stringify(row),
            source_cpse_id: row.source_cpse_id || row.cpse_id || sampleId,
            raw: row,
          }))
        : [];
      if (normalized.length === 0 && res.data.first_record) {
        normalized.push({
          id: 'mat_0001',
          description: JSON.stringify(res.data.first_record),
          source_cpse_id: sampleId,
          raw: res.data.first_record,
        });
      }
      sessionStorage.setItem('vertex_raw_records', JSON.stringify(normalized));
      sessionStorage.setItem('vertex_dataset_name', sample?.file || sampleId);
      sessionStorage.setItem('vertex_dataset_total', String(res.data.total_records));
    } catch (err: any) {
      setError(err.message || 'Failed to load sample');
    }
  };

  const canProcess = uploadResult && uploadResult.total_records > 0;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Upload Material Data
        </h1>
        <p className="text-secondary-400">
          Upload a CSV or Excel file with material master records, or load a sample
          CPSE dataset to start the harmonization pipeline.
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <div
        className="border-2 border-dashed border-secondary-600 rounded-lg p-10 text-center cursor-pointer transition-colors hover:border-primary-500 hover:bg-primary-900/5"
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragEnter={(e) => {
          e.preventDefault();
          e.currentTarget.style.borderColor = '#3b82f6';
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          e.currentTarget.style.borderColor = '';
        }}
      >
        <UploadIcon className="w-12 h-12 text-secondary-500 mx-auto mb-4" />
        <p className="text-secondary-300 mb-2">
          Drag & drop a CSV/Excel file here, or click to browse
        </p>
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileSelect}
          className="hidden"
          id="file-input"
        />
        <label
          htmlFor="file-input"
          className="inline-block px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg cursor-pointer transition-colors"
        >
          Choose File
        </label>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-danger-500/10 border border-danger-500/30 rounded-lg">
          <p className="text-danger-400">{error}</p>
        </div>
      )}

      {/* Preview */}
      {uploadedFile && preview.length > 0 && (
        <div className="mt-6 bg-secondary-800 rounded-lg border border-secondary-700 p-4">
          <h3 className="text-white font-medium mb-3">
            Preview: {uploadedFile.name}
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-secondary-700">
                  {Object.keys(preview[0]).map((key) => (
                    <th key={key} className="text-left py-2 text-secondary-300">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, i) => (
                  <tr key={i} className="border-b border-secondary-800">
                    {Object.values(row).map((val: any, j) => (
                      <td key={j} className="py-2 text-secondary-200">
                        {val || '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sample Datasets */}
      <div className="mt-8">
        <h3 className="text-xl font-semibold text-white mb-4">
          Or load a sample CPSE dataset
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {samples.map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleLoadSample(sample.id)}
              className="p-4 bg-secondary-800 border border-secondary-700 rounded-lg text-left hover:border-primary-500 hover:bg-secondary-700 transition-all"
            >
              <FileText className="w-6 h-6 text-primary-400 mb-2" />
              <h4 className="text-white font-medium">{sample.id}</h4>
              <p className="text-secondary-400 text-sm mt-1">
                {sample.file}
              </p>
              <span className="text-xs text-secondary-500">
                Click to load and preview
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Upload Result & Process Button */}
      {uploadResult && (
        <div className="mt-8 p-6 bg-secondary-800 rounded-lg border border-secondary-700">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-5 h-5 text-success-500" />
            <div>
              <p className="text-white font-medium">
                {uploadResult.message}
              </p>
              <p className="text-sm text-secondary-400">
                {uploadResult.total_records} records ready for processing
              </p>
            </div>
          </div>
          {canProcess && (
            <button
              onClick={() => {
                // Navigate to process page
                window.location.href = '/process';
              }}
              className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
            >
              <Play className="w-5 h-5" />
              Start Harmonization
            </button>
          )}
        </div>
      )}
    </div>
  );
}
