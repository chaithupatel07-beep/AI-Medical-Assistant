export function HeroIllustration() {
  return (
    <div className="relative mx-auto w-full max-w-lg">
      <div className="absolute -inset-4 rounded-3xl bg-gradient-to-tr from-blue-600/15 via-cyan-500/15 to-sky-300/20 blur-2xl" />
      <svg
        viewBox="0 0 520 420"
        className="relative w-full rounded-3xl border border-blue-100 bg-white/95 p-4 shadow-soft"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        role="img"
        aria-label="AI Medical Assistant Healthcare Illustration"
      >
        <defs>
          <linearGradient id="medBlue" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#06B6D4" />
          </linearGradient>
          <linearGradient id="softCard" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#F8FAFC" />
            <stop offset="100%" stopColor="#EFF6FF" />
          </linearGradient>
        </defs>

        <rect x="20" y="20" width="480" height="380" rx="24" fill="url(#softCard)" />
        <rect x="44" y="46" width="270" height="170" rx="18" fill="#FFFFFF" stroke="#DBEAFE" strokeWidth="2" />
        <rect x="64" y="68" width="90" height="14" rx="7" fill="#BFDBFE" />
        <rect x="64" y="92" width="180" height="10" rx="5" fill="#E2E8F0" />
        <path
          d="M64 155 H108 L124 126 L142 182 L162 140 L178 155 H292"
          stroke="url(#medBlue)"
          strokeWidth="4.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        <rect x="334" y="46" width="142" height="114" rx="18" fill="url(#medBlue)" />
        <circle cx="405" cy="90" r="24" fill="#FFFFFF" fillOpacity="0.2" />
        <path d="M405 76 V104 M391 90 H419" stroke="#FFFFFF" strokeWidth="5" strokeLinecap="round" />
        <rect x="360" y="128" width="90" height="10" rx="5" fill="#FFFFFF" fillOpacity="0.85" />

        <rect x="44" y="236" width="206" height="136" rx="18" fill="#FFFFFF" stroke="#E0F2FE" strokeWidth="2" />
        <circle cx="78" cy="272" r="18" fill="#ECFEFF" />
        <path d="M72 272 H84 M78 266 V278" stroke="#06B6D4" strokeWidth="3" strokeLinecap="round" />
        <rect x="108" y="262" width="110" height="10" rx="5" fill="#0F172A" fillOpacity="0.85" />
        <rect x="108" y="280" width="84" height="8" rx="4" fill="#94A3B8" />
        <rect x="64" y="310" width="166" height="14" rx="7" fill="#EFF6FF" />
        <rect x="64" y="310" width="116" height="14" rx="7" fill="url(#medBlue)" />
        <rect x="64" y="336" width="128" height="10" rx="5" fill="#CBD5E1" />

        <rect x="268" y="182" width="208" height="190" rx="18" fill="#FFFFFF" stroke="#DBEAFE" strokeWidth="2" />
        <rect x="290" y="206" width="144" height="28" rx="12" fill="#EFF6FF" />
        <rect x="304" y="216" width="96" height="8" rx="4" fill="#2563EB" />
        <rect x="310" y="248" width="144" height="34" rx="12" fill="#ECFEFF" />
        <rect x="324" y="261" width="104" height="8" rx="4" fill="#0891B2" />
        <rect x="290" y="298" width="164" height="50" rx="12" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1.5" />
        <circle cx="316" cy="323" r="12" fill="#DCFCE7" />
        <path d="M311 323 L315 327 L323 318" stroke="#16A34A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <rect x="338" y="314" width="94" height="8" rx="4" fill="#334155" />
        <rect x="338" y="329" width="68" height="7" rx="3.5" fill="#94A3B8" />
      </svg>
    </div>
  );
}
