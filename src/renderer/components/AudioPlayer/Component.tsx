import { useEffect } from "react";
import { Audio, staticFile } from "remotion";
import type { ComponentMeta } from "../../src/app/types";

type Props = {
  audio_file: string;
};

export const AudioPlayer: React.FC<Props> = ({ audio_file }) => {
  if (!audio_file) return null;

  return <Audio src={staticFile(audio_file)} />;
};

export const audioPlayerMeta: ComponentMeta = {
  allowedParams: [],
  defaults: {},
  renderMode: "overlay",
  requiresData: ["audio_file"],
};