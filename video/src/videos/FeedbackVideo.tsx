import React from "react";
import {Audio, Series, staticFile} from "remotion";
import {ScreenScene, TextScene, colors} from "./shared";

export const FeedbackVideo: React.FC = () => (
  <>
    <Audio src={staticFile("audio/feedback.wav")} volume={0.95} />
    <Series>
      <Series.Sequence durationInFrames={150}>
        <TextScene title="RetailPulse Reflection" lines={["How self-review and validation changed the project.", "What I learned about building credible analytics products."]} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <TextScene
          title="Lesson 1: Credibility before claims"
          lines={[
            "The original churn score was unrealistically perfect.",
            "I removed target leakage and switched to future-window validation.",
            "The resulting metric is lower, but defensible and useful.",
          ]}
          accent={colors.coral}
        />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="04-churn.png" title="Transparent model health" body="The final product exposes AUC, average precision, validation method, and the action queue instead of hiding model limitations." accent={colors.coral} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="05-inventory.png" title="Models must drive decisions" body="Forecasts, segments, churn scores, and inventory formulas now connect directly to exports, queues, and adjustable operating assumptions." />
      </Series.Sequence>
      <Series.Sequence durationInFrames={150}>
        <TextScene
          title="What I would build next"
          lines={[
            "Automated data refresh and drift monitoring.",
            "Authenticated workspaces and role-based access.",
            "Controlled experiments to measure business lift.",
          ]}
        />
      </Series.Sequence>
      <Series.Sequence durationInFrames={120}>
        <TextScene title="Key takeaway" lines={["A strong analytics project must be accurate, understandable, actionable, and reproducible."]} />
      </Series.Sequence>
    </Series>
  </>
);
