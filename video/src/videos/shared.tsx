import React from "react";
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";

export const colors = {
  navy: "#13233b",
  teal: "#20a493",
  coral: "#d85f57",
  canvas: "#f5f7fa",
  ink: "#162033",
  muted: "#667085",
  white: "#ffffff",
};

export const Fade: React.FC<React.PropsWithChildren<{delay?: number}>> = ({children, delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [delay, delay + 0.55 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  const y = interpolate(frame, [delay, delay + 0.55 * fps], [24, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return <div style={{opacity, transform: `translateY(${y}px)`}}>{children}</div>;
};

export const Brand: React.FC = () => (
  <div style={{fontSize: 32, fontWeight: 800, color: colors.white}}>
    Retail<span style={{color: colors.teal}}>Pulse</span>
  </div>
);

export const ScreenScene: React.FC<{
  image: string;
  title: string;
  body: string;
  accent?: string;
}> = ({image, title, body, accent = colors.teal}) => (
  <AbsoluteFill style={{backgroundColor: colors.canvas, fontFamily: "Arial, sans-serif", padding: 64}}>
    <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28}}>
      <Brand />
      <div style={{color: colors.muted, fontSize: 22}}>AI retail operations intelligence</div>
    </div>
    <div style={{display: "grid", gridTemplateColumns: "1.55fr 0.8fr", gap: 40, flex: 1}}>
      <Fade>
        <div style={{height: 790, background: colors.white, border: "1px solid #dfe4ea", borderRadius: 12, overflow: "hidden", boxShadow: "0 22px 60px rgba(19,35,59,.12)"}}>
          <Img src={staticFile(`screens/${image}`)} style={{width: "100%", height: "100%", objectFit: "cover", objectPosition: "top left"}} />
        </div>
      </Fade>
      <div style={{display: "flex", flexDirection: "column", justifyContent: "center"}}>
        <Fade delay={8}>
          <div style={{width: 64, height: 6, background: accent, marginBottom: 28}} />
          <div style={{fontSize: 58, lineHeight: 1.05, fontWeight: 800, color: colors.ink, marginBottom: 28}}>{title}</div>
          <div style={{fontSize: 28, lineHeight: 1.5, color: colors.muted}}>{body}</div>
        </Fade>
      </div>
    </div>
  </AbsoluteFill>
);

export const TextScene: React.FC<{title: string; lines: string[]; accent?: string}> = ({
  title,
  lines,
  accent = colors.teal,
}) => (
  <AbsoluteFill style={{backgroundColor: colors.navy, color: colors.white, fontFamily: "Arial, sans-serif", padding: 96}}>
    <Brand />
    <div style={{display: "flex", flex: 1, alignItems: "center"}}>
      <div style={{maxWidth: 1500}}>
        <Fade>
          <div style={{width: 72, height: 7, background: accent, marginBottom: 30}} />
          <div style={{fontSize: 72, lineHeight: 1.05, fontWeight: 800, marginBottom: 46}}>{title}</div>
        </Fade>
        {lines.map((line, index) => (
          <Fade key={line} delay={12 + index * 7}>
            <div style={{display: "flex", gap: 18, alignItems: "flex-start", fontSize: 32, lineHeight: 1.45, color: "#d8e0eb", marginBottom: 20}}>
              <span style={{color: accent, fontWeight: 800}}>●</span>
              <span>{line}</span>
            </div>
          </Fade>
        ))}
      </div>
    </div>
  </AbsoluteFill>
);
