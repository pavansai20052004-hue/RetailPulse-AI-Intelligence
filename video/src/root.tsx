import React from "react";
import {Composition} from "remotion";
import {DemoVideo} from "./videos/DemoVideo";
import {FeedbackVideo} from "./videos/FeedbackVideo";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="RetailPulseDemo"
      component={DemoVideo}
      durationInFrames={1350}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="RetailPulseFeedback"
      component={FeedbackVideo}
      durationInFrames={1050}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
);
