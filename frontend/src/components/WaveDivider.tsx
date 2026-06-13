interface WaveDividerProps {
  topColor?: string;
  bottomColor?: string;
  flip?: boolean;
  className?: string;
}

/**
 * Hand-drawn style wavy divider that flows from topColor into bottomColor.
 * Pass any CSS color (including var(--lavender) etc).
 */
export function WaveDivider({
  topColor = "transparent",
  bottomColor = "var(--cream)",
  flip = false,
  className,
}: WaveDividerProps) {
  return (
    <div
      className={className}
      style={{
        backgroundColor: topColor,
        lineHeight: 0,
        transform: flip ? "scaleX(-1)" : undefined,
      }}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 1440 120"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ display: "block", width: "100%", height: "clamp(60px, 9vw, 120px)" }}
      >
        <path
          d="M0,64 C180,120 320,8 540,40 C760,72 900,120 1120,88 C1280,64 1360,32 1440,56 L1440,120 L0,120 Z"
          fill={bottomColor}
        />
      </svg>
    </div>
  );
}
