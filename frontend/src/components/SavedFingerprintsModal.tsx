import React, { useEffect, useState } from 'react';
import { X, Dna, Calendar, MapPin, ExternalLink, Loader2 } from 'lucide-react';
import { FingerprintSummary } from '../types';
import { fetchFingerprintsList, fetchFingerprintFile } from '../api';

interface SavedFingerprintsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectFingerprint: (data: any) => void;
}

export const SavedFingerprintsModal: React.FC<SavedFingerprintsModalProps> = ({
  isOpen,
  onClose,
  onSelectFingerprint,
}) => {
  const [list, setList] = useState<FingerprintSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      setError(null);
      setList([]);
      fetchFingerprintsList()
        .then((res) => {
          setList(res.fingerprints || []);
        })
        .catch((err) => {
          setError(err.message || 'Failed to load fingerprints list');
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleLoad = async (filename: string) => {
    try {
      setLoading(true);
      const res = await fetchFingerprintFile(filename);
      onSelectFingerprint(res.fingerprint);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to load fingerprint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="hud-glass-amber rounded-3xl max-w-xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden border border-white/15">
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-900/60 border border-purple-500/40 text-craft-amber-400 flex items-center justify-center">
              <Dna className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-serif-heading">
                Saved Craft Skill Fingerprints
              </h3>
              <p className="text-xs text-stone-400">
                Preserved knowledge graphs in local archive
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-stone-400 hover:text-white hover:bg-white/10 rounded-xl transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 overflow-y-auto space-y-3 flex-1">
          {loading && (
            <div className="py-12 text-center text-stone-400 flex flex-col items-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-craft-amber-400" />
              <span className="text-xs">Loading saved fingerprints...</span>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-xs text-rose-300">
              {error}
            </div>
          )}

          {!loading && list.length === 0 && !error && (
            <div className="py-12 text-center text-stone-400">
              <Dna className="w-10 h-10 mx-auto text-stone-600 mb-2" />
              <p className="text-sm font-semibold text-stone-300">No saved fingerprints found yet</p>
              <p className="text-xs text-stone-500 mt-1">
                Synthesize a craft in the Artisan Studio to automatically save it here.
              </p>
            </div>
          )}

          {!loading &&
            list.map((fp) => (
              <div
                key={fp.filename}
                className="p-4.5 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-craft-amber-400/50 transition-all flex items-center justify-between gap-4"
              >
                <div>
                  <h4 className="text-sm font-bold text-white font-serif-heading">
                    {fp.craft_name}
                  </h4>
                  <p className="text-xs text-stone-400 mt-0.5">
                    Artisan: <strong className="text-stone-300">{fp.artisan_name}</strong> • v{fp.version}
                  </p>
                  <div className="flex items-center gap-3 text-[11px] text-stone-500 mt-2">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-craft-amber-400" />
                      {fp.created_at ? new Date(fp.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                    <span>{fp.techniques_count} techniques</span>
                    <span>{fp.materials_count} materials</span>
                  </div>
                </div>

                <button
                  onClick={() => handleLoad(fp.filename)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 to-craft-amber-300 hover:from-craft-amber-300 hover:to-amber-200 rounded-xl shadow-xs transition-all shrink-0 cursor-pointer"
                >
                  Load
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
