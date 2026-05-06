export interface WordTimestamp {
  text: string;
  start_ms: number;
  end_ms: number;
}

export interface SentenceTimestamp {
  text: string;
  start_ms: number;
  end_ms: number;
}

export interface BPMData {
  detected_bpm: number;
  model: string;
  manual_override: boolean;
}

export interface AnalysisData {
  lyrics: {
    words: WordTimestamp[];
    sentences: SentenceTimestamp[];
  };
  bpm: BPMData;
  merge_multiplier: number;
}
