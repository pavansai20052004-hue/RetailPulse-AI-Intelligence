import React from "react";
import {Audio, Series, staticFile} from "remotion";
import {ScreenScene, TextScene, colors} from "./shared";

export const DemoVideo: React.FC = () => (
  <>
    <Audio src={staticFile("audio/demo.wav")} volume={0.95} />
    <Series>
      <Series.Sequence durationInFrames={150}>
        <TextScene
          title="RetailPulse"
          lines={[
            "An end-to-end AI retail intelligence platform.",
            "Descriptive, predictive, and prescriptive analytics in one workflow.",
            "397,884 cleaned transactions with reviewer-ready exports.",
          ]}
        />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="01-overview.png" title="Executive Overview" body="Revenue, orders, customers, market performance, data quality, and model health are visible in one operational workspace." />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="02-forecast.png" title="Demand Forecast" body="A 90-day forecast includes uncertainty bands and a true holdout MAPE, so planning decisions have visible confidence." />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="03-customers.png" title="Customer Intelligence" body="K-Means segments customers by value and behavior, with direct retention and growth plays for every group." />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="04-churn.png" title="Churn Risk" body="Leakage-safe, time-based validation produces a prioritized retention action queue and exportable risk scores." accent={colors.coral} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <ScreenScene image="05-inventory.png" title="Inventory Control" body="Scenario controls recalculate ABC priority, EOQ, safety stock, and reorder points for supply-chain planning." />
      </Series.Sequence>
      <Series.Sequence durationInFrames={150}>
        <TextScene
          title="Built for review. Ready for extension."
          lines={[
            "Reproducible Python package, tests, Docker, and Render blueprint.",
            "Comprehensive PDF report and downloadable operational datasets.",
            "Public source, deployment, and submission assets prepared.",
          ]}
        />
      </Series.Sequence>
    </Series>
  </>
);
