import React from 'react';
import {
  Sparkles,
  Dna,
  ShieldCheck,
  MapPin,
  Flame,
  Award,
  Users,
  Clock,
  ArrowRight,
  Fingerprint,
  Feather,
} from 'lucide-react';
import { CraftPreset } from '../types';

interface ArtisanHeroProps {
  onSelectCraft: (preset: CraftPreset) => void;
  onExploreDemo: () => void;
  activeCraftId?: string;
}

export const CRAFT_PRESETS: CraftPreset[] = [
  {
    id: 'madurai-sungudi',
    craftName: 'Madurai Sungudi',
    artisanName: 'Meenakshi Ammal',
    origin: 'Madurai, Tamil Nadu, India',
    heritage: 'GI Tag No. 53 · 2000-Year Sourashtra Tradition',
    experienceYears: 40,
    tagline: '4,500 knots tied by hand per sari with cotton thread resist',
    accentColor: 'from-amber-500 to-craft-crimson-700',
    avatarSeed: 'Meenakshi',
    description: `I start by washing the pure Madurai silk in warm water to remove starch. The water must be warm to the wrist — if too hot, the silk loses its natural lustre. Once damp and heavy like cool water, I spread it flat and mark a 1.5 cm grid with chalk using a very light touch. Then I pinch a 3-4 mm peak with thumb and forefinger, wrap strong cotton thread tightly three times, feeling the slight pushback resistance, and tie a double knot. After 4,500 knots, it enters the 80°C pomegranate rind crimson dye bath for 20 minutes before the soft 'snap' of scissors reveals the crisp white circles.`,
  },
  {
    id: 'kashmir-pashmina',
    craftName: 'Kashmir Pashmina Spinning',
    artisanName: 'Ghulam Nabi',
    origin: 'Srinagar, Kashmir, India',
    heritage: 'GI Tag Craft · Raw Changthangi Mountain Cashmere',
    experienceYears: 35,
    tagline: 'Spinning 12-micron raw fleece on the ancestral Yender wheel',
    accentColor: 'from-blue-600 to-indigo-900',
    avatarSeed: 'Ghulam',
    description: `The raw Pashm comes from Changthangi goats living at 14,000 feet. The fibre is so delicate — 12 to 14 microns — that no machine in the world can spin it without snapping. You must spin it on the wooden Yender wheel. My fingertips gently roll the spindle; you must feel the fleece breathe between your thumbs. If your breath is uneven, the yarn becomes lumpy. We paste it with pounded rice water for stiffness before the handloom weaving begins.`,
  },
  {
    id: 'oaxaca-zapotec',
    craftName: 'Oaxaca Zapotec Weaving',
    artisanName: 'Don Mateo',
    origin: 'Teotitlán del Valle, Oaxaca, Mexico',
    heritage: 'Zapotec Indigenous Heritage · Pre-Columbian Loom',
    experienceYears: 48,
    tagline: 'Cochineal insect and wild indigo natural dyes on pedal loom',
    accentColor: 'from-rose-600 to-amber-700',
    avatarSeed: 'Mateo',
    description: `We card and hand-spin local churro wool. For the sacred scarlet red, we crush dried cochineal insects that live on the nopal cactus. Add lime juice, and the red turns bright orange; add wood ash, and it shifts to deep purple. You feel the wool in the dye vat: when it grabs the pigment, the texture turns grippy. On the foot loom, the wooden shuttle must rhythmically beat in time with your breath to keep the geometric diamonds symmetrical.`,
  },
  {
    id: 'bastar-dhokra',
    craftName: 'Bastar Dhokra Casting',
    artisanName: 'Shanti Bai',
    origin: 'Bastar, Chhattisgarh, India',
    heritage: '4,000-Year Lost-Wax Metal Casting · Mohenjo-daro Lineage',
    experienceYears: 28,
    tagline: 'Beeswax thread modelling over clay cores fired in pit kilns',
    accentColor: 'from-amber-600 to-stone-800',
    avatarSeed: 'Shanti',
    description: `Dhokra has been made the same way since the Dancing Girl of Mohenjo-daro 4,000 years ago. We shape a core of ant-hill clay and cow dung, then roll natural beeswax into long fine threads through a wooden press. We coil the wax threads onto the clay to form the jewelry, animals, and goddesses. We pack two more layers of river clay over the wax, bake it in a ground furnace of sal wood, and pour molten bell metal into the channel. The wax melts away, giving its soul to the metal.`,
  },
];

export const ArtisanHero: React.FC<ArtisanHeroProps> = ({
  onSelectCraft,
  onExploreDemo,
  activeCraftId = 'madurai-sungudi',
}) => {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-[#090b14] via-[#120f26] to-[#1c122e] text-white shadow-2xl border border-white/10 mb-10">
      
      {/* Background Graphic & Hero Image */}
      <div className="relative w-full h-[380px] sm:h-[460px] lg:h-[520px] overflow-hidden">
        {/* The Master Artisan Image */}
        <img
          src="/artisan_hero.jpg"
          alt="Master artisans of traditional crafts: weaving, Sungudi knot-tying, woodcarving, ceramics, and basketry connected by Skill DNA"
          className="w-full h-full object-cover object-center brightness-90 filter contrast-105 scale-100 hover:scale-102 transition-transform duration-1000 ease-out"
        />

        {/* Ambient Gradient Overlays for High-Contrast Text Legibility */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#090b14] via-[#090b14]/70 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#090b14]/90 via-[#090b14]/50 to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-craft-amber-400/20 via-transparent to-transparent pointer-events-none" />

        {/* Floating Holographic Knowledge Badges (Reflecting the image) */}
        <div className="hidden lg:block absolute top-8 right-10 z-20 space-y-3 pointer-events-none">
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-3.5 shadow-2xl flex items-center gap-3 animate-pulse">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-craft-amber-500 to-craft-crimson-700 flex items-center justify-center text-white shadow-lg">
              <Fingerprint className="w-5 h-5 text-craft-amber-200" />
            </div>
            <div>
              <div className="text-[10px] font-bold tracking-widest uppercase text-craft-amber-300">
                Tacit Judgment Captured
              </div>
              <div className="text-xs font-semibold text-white">
                "3 wraps · 4mm pinch · tactile snap"
              </div>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-3.5 shadow-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-800 flex items-center justify-center text-white shadow-lg">
              <ShieldCheck className="w-5 h-5 text-indigo-200" />
            </div>
            <div>
              <div className="text-[10px] font-bold tracking-widest uppercase text-indigo-300">
                GI Heritage Authenticated
              </div>
              <div className="text-xs font-semibold text-white">
                Madurai Sungudi · GI Tag #53
              </div>
            </div>
          </div>
        </div>

        {/* Hero Narrative Overlay Content */}
        <div className="absolute bottom-6 left-6 right-6 sm:bottom-10 sm:left-10 sm:right-10 z-20 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold tracking-wide uppercase bg-craft-amber-400/20 border border-craft-amber-400/40 text-craft-amber-300 backdrop-blur-sm mb-3">
            <Flame className="w-3.5 h-3.5 text-craft-amber-400 animate-bounce" />
            Preserving Intangible Cultural Heritage
          </div>

          <h1 className="text-2xl sm:text-4xl lg:text-5xl font-bold font-serif-heading tracking-tight text-white leading-tight sm:leading-tight mb-3">
            The knowledge that lives in hands <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-craft-amber-300 via-amber-200 to-rose-300">
              deserves to live forever.
            </span>
          </h1>

          <p className="text-xs sm:text-sm lg:text-base text-stone-300 leading-relaxed max-w-2xl font-sans mb-5">
            Traditional masters carry decades of sensory knowledge in their fingertips — the exact resistance of a knot,
            the temperature of natural indigo, the sound of thread releasing. SKILL DNA turns unspoken intuition into permanent, interactive masterclasses with Strands Multi-Agent AI.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onExploreDemo}
              className="inline-flex items-center gap-2 px-5 py-2.5 sm:px-6 sm:py-3 rounded-xl text-xs sm:text-sm font-bold text-craft-indigo-950 bg-gradient-to-r from-craft-amber-400 via-craft-amber-300 to-amber-200 hover:from-craft-amber-300 hover:to-amber-100 shadow-lg shadow-amber-900/30 transition-all hover:scale-102 cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-craft-indigo-950" />
              Explore Sungudi Demo
              <ArrowRight className="w-4 h-4" />
            </button>
            <span className="text-xs text-stone-400 hidden sm:inline">
              40 years of knowledge digitised in 30 seconds
            </span>
          </div>
        </div>
      </div>

      {/* Global Heritage Statistics Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-white/10 border-t border-b border-white/10 bg-black/40 backdrop-blur-md">
        <div className="p-4 sm:p-5 text-center">
          <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-white font-serif-heading">
            6.46M+
          </div>
          <div className="text-xs font-semibold text-craft-amber-300 mt-0.5">
            Artisans in India
          </div>
          <div className="text-[10px] text-stone-400 mt-0.5">
            64% are women (PIB 2026)
          </div>
        </div>

        <div className="p-4 sm:p-5 text-center">
          <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-white font-serif-heading">
            318
          </div>
          <div className="text-xs font-semibold text-rose-300 mt-0.5">
            GI-Protected Crafts
          </div>
          <div className="text-[10px] text-stone-400 mt-0.5">
            Across 455 craft categories
          </div>
        </div>

        <div className="p-4 sm:p-5 text-center">
          <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-white font-serif-heading">
            4,000 Yrs
          </div>
          <div className="text-xs font-semibold text-indigo-300 mt-0.5">
            Oldest Living Craft Tradition
          </div>
          <div className="text-[10px] text-stone-400 mt-0.5">
            Bastar Dhokra · Mohenjo-daro lineage
          </div>
        </div>

        <div className="p-4 sm:p-5 text-center">
          <div className="text-xl sm:text-2xl lg:text-3xl font-bold text-white font-serif-heading text-craft-amber-400">
            &lt; 20
          </div>
          <div className="text-xs font-semibold text-craft-amber-300 mt-0.5">
            Master Knot-Tiers Remaining
          </div>
          <div className="text-[10px] text-stone-400 mt-0.5">
            At risk of permanent loss (The Hindu)
          </div>
        </div>
      </div>

      {/* Global Craft Showcase Selector */}
      <div className="p-6 sm:p-8 bg-gradient-to-b from-[#120f26] to-[#090b14]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <span className="text-[10px] font-bold tracking-widest uppercase text-craft-amber-400 flex items-center gap-1.5">
              <Feather className="w-3.5 h-3.5" />
              Living Craft Traditions
            </span>
            <h2 className="text-lg sm:text-xl font-bold text-white font-serif-heading mt-0.5">
              Select a Mastercraft to Digitize or Learn
            </h2>
          </div>
          <p className="text-xs text-stone-400 max-w-sm">
            Click any craft below to load authentic artisan field notes directly into the workshop.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {CRAFT_PRESETS.map((preset) => {
            const isSelected = activeCraftId === preset.id;
            return (
              <div
                key={preset.id}
                onClick={() => onSelectCraft(preset)}
                className={`group relative rounded-2xl p-4.5 border transition-all duration-300 cursor-pointer ${
                  isSelected
                    ? 'border-craft-amber-400 bg-white/10 shadow-xl ring-2 ring-craft-amber-400/40 -translate-y-1'
                    : 'border-white/10 bg-white/5 hover:bg-white/8 hover:border-white/20'
                }`}
              >
                {/* Header with Origin & Badge */}
                <div className="flex items-center justify-between text-[11px] text-stone-400 mb-2">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-craft-amber-400" />
                    {preset.origin.split(',')[0]}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-white/10 text-white font-semibold text-[10px]">
                    {preset.experienceYears} Yrs Master
                  </span>
                </div>

                {/* Craft Title & Artisan */}
                <h3 className="text-base font-bold text-white font-serif-heading mb-1 group-hover:text-craft-amber-200 transition-colors">
                  {preset.craftName}
                </h3>
                <p className="text-xs text-craft-amber-300/90 font-medium mb-2.5">
                  Artisan: {preset.artisanName}
                </p>

                <p className="text-xs text-stone-300 line-clamp-2 leading-relaxed mb-4">
                  {preset.tagline}
                </p>

                {/* Footer Action */}
                <div className="flex items-center justify-between pt-3 border-t border-white/10 text-xs">
                  <span className="text-[11px] text-stone-400 font-mono">
                    {preset.heritage.split('·')[0]}
                  </span>
                  <span className={`font-semibold flex items-center gap-1 ${
                    isSelected ? 'text-craft-amber-300' : 'text-stone-400 group-hover:text-white'
                  }`}>
                    {isSelected ? 'Loaded' : 'Load Craft'}
                    <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
