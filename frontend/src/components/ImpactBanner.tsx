import React, { useEffect, useRef, useState } from 'react';
import { Users, Award, MapPin, Globe } from 'lucide-react';

interface StatCardProps {
  icon: React.ReactNode;
  value: string;
  numericValue: number;
  suffix: string;
  label: string;
  sublabel: string;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, value, numericValue, suffix, label, sublabel, color }) => {
  const [displayed, setDisplayed] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true;
          const duration = 1400;
          const start = performance.now();
          const animate = (now: number) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplayed(Math.floor(eased * numericValue));
            if (progress < 1) requestAnimationFrame(animate);
            else setDisplayed(numericValue);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [numericValue]);

  return (
    <div ref={ref} className="flex-1 min-w-0 flex flex-col items-center text-center px-4 py-5 relative group">
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center mb-3 ${color} shadow-lg ring-1 ring-white/10 group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      <div className="text-2xl sm:text-3xl font-bold text-white font-serif-heading tracking-tight leading-none">
        {displayed.toLocaleString()}{suffix}
      </div>
      <div className="text-xs sm:text-sm font-semibold text-white/90 mt-1">{label}</div>
      <div className="text-[11px] text-white/50 mt-0.5 leading-tight">{sublabel}</div>
    </div>
  );
};

export const ImpactBanner: React.FC = () => {
  return (
    <div className="w-full bg-gradient-to-r from-craft-indigo-950 via-[#1a0a3a] to-craft-crimson-900 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1">
        {/* Top line */}
        <div className="flex items-center justify-center gap-2 py-2 border-b border-white/10 mb-1">
          <Globe className="w-3.5 h-3.5 text-craft-amber-400" />
          <p className="text-[11px] font-semibold text-white/60 tracking-widest uppercase">
            Global Platform · Pilot: Madurai Sungudi, Tamil Nadu, India · Any Craft · Any Language
          </p>
          <Globe className="w-3.5 h-3.5 text-craft-amber-400" />
        </div>

        {/* Stats row */}
        <div className="flex items-stretch divide-x divide-white/10">
          <StatCard
            icon={<Users className="w-5 h-5 text-white" />}
            value="6.46M"
            numericValue={6460000}
            suffix=""
            label="Artisans in India"
            sublabel="64% are women · PIB 2026"
            color="bg-gradient-to-br from-blue-600 to-indigo-700"
          />
          <StatCard
            icon={<Award className="w-5 h-5 text-white" />}
            value="318"
            numericValue={318}
            suffix=""
            label="GI-Tagged Crafts"
            sublabel="Most with undocumented technique"
            color="bg-gradient-to-br from-craft-crimson-700 to-rose-800"
          />
          <StatCard
            icon={<MapPin className="w-5 h-5 text-white" />}
            value="20"
            numericValue={20}
            suffix="<"
            label="Sungudi Hand-Tiers Left"
            sublabel="Madurai · The Hindu, 2019"
            color="bg-gradient-to-br from-craft-amber-600 to-orange-700"
          />
          <StatCard
            icon={<Globe className="w-5 h-5 text-white" />}
            value="∞"
            numericValue={455}
            suffix="+"
            label="Craft Categories"
            sublabel="Any craft · Any language · Worldwide"
            color="bg-gradient-to-br from-emerald-600 to-teal-700"
          />
        </div>

        {/* Bottom tagline */}
        <div className="text-center py-2 border-t border-white/10 mt-1">
          <p className="text-xs text-white/40 italic font-serif-heading">
            "The knowledge that lives in hands deserves to live forever."
          </p>
        </div>
      </div>
    </div>
  );
};
