// Inline SVG icons ported verbatim from the design prototype. Decorative by
// default (aria-hidden); pass `title` to expose the icon to assistive tech.
import type { ReactNode, SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number; title?: string };

function Svg({ size = 20, title, strokeWidth = 2, children, ...rest }: IconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden={title ? undefined : true}
      role={title ? "img" : undefined}
      {...rest}
    >
      {title ? <title>{title}</title> : null}
      {children}
    </svg>
  );
}

export const AccessibilityIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="12" cy="4" r="1.6" />
    <path d="M12 6.5v6h5l3 5" />
    <path d="M16 14.5a6 6 0 1 1-7-4.6" />
  </Svg>
);

export const SunIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="4.2" />
    <path d="M12 2v2.5M12 19.5V22M4 12H1.5M22.5 12H20M5.2 5.2 6.9 6.9M17.1 17.1l1.7 1.7M18.8 5.2 17.1 6.9M6.9 17.1 5.2 18.8" />
  </Svg>
);

export const MoonIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
  </Svg>
);

export const SearchIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="m21 21-4.3-4.3" />
  </Svg>
);

export const EmptySearchIcon = (p: IconProps) => (
  <Svg strokeWidth={1.8} {...p}>
    <circle cx="11" cy="11" r="7" />
    <path d="m21 21-4.3-4.3M8.5 11h5" />
  </Svg>
);

export const ExternalIcon = (p: IconProps) => (
  <Svg strokeWidth={2.2} {...p}>
    <path d="M7 17 17 7M9 7h8v8" />
  </Svg>
);

export const CalendarIcon = (p: IconProps) => (
  <Svg {...p}>
    <rect x="3" y="4.5" width="18" height="16" rx="2" />
    <path d="M3 9h18M8 2.5v4M16 2.5v4M12 13v4M10 15h4" />
  </Svg>
);

export const ShareIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="18" cy="5" r="2.5" />
    <circle cx="6" cy="12" r="2.5" />
    <circle cx="18" cy="19" r="2.5" />
    <path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6" />
  </Svg>
);

export const CodeIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="m8 6-5 6 5 6M16 6l5 6-5 6" />
  </Svg>
);

export const MenuIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="M4 7h16M4 12h16M4 17h16" />
  </Svg>
);

export const CheckIcon = (p: IconProps) => (
  <Svg strokeWidth={2.6} {...p}>
    <path d="M20 6 9 17l-5-5" />
  </Svg>
);

export const InfoIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8h.01M11 12h1v4h1" />
  </Svg>
);

export const RssIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="M5 5a14 14 0 0 1 14 14M5 11a8 8 0 0 1 8 8" />
    <circle cx="6" cy="18" r="1.6" fill="currentColor" stroke="none" />
  </Svg>
);

export const LibrasIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="M7 11V6a1.5 1.5 0 0 1 3 0v4" />
    <path d="M10 9.5V4.5a1.5 1.5 0 0 1 3 0V10" />
    <path d="M13 10V6a1.5 1.5 0 0 1 3 0v5" />
    <path d="M16 11.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-1.5a6 6 0 0 1-5.1-2.9L4 14.2a1.5 1.5 0 0 1 2.5-1.6L8 14.2" />
  </Svg>
);

export const AudioIcon = (p: IconProps) => (
  <Svg {...p}>
    <path d="M4 9v6h3.5L13 19V5L7.5 9H4z" />
    <path d="M16.5 8.5a5 5 0 0 1 0 7" />
    <path d="M19 6a9 9 0 0 1 0 12" />
  </Svg>
);

export const WheelchairIcon = (p: IconProps) => (
  <Svg {...p}>
    <circle cx="9" cy="4.4" r="1.7" />
    <path d="M9 7v5.2h4.4L16 18" />
    <path d="M13 12.5a5 5 0 1 1-4.4-2.4" />
  </Svg>
);
