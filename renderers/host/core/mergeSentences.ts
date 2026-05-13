import type { WordTimestamp, SentenceTimestamp } from "../src/app/types";

export function mergeWordsToSentences(
  words: WordTimestamp[],
  bpmValue: number,
  multiplier: number = 0.672
): SentenceTimestamp[] {
  if (!bpmValue || words.length === 0) return [];

  const beatMs = 60000 / bpmValue;
  const threshold = beatMs * multiplier;

  const result: SentenceTimestamp[] = [];
  let currentWords: WordTimestamp[] = [];

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    currentWords.push(word);

    const isLast = i === words.length - 1;
    const isPunctuation = "，。！？；、：".includes(word.text);
    const gap = isLast ? 0 : words[i + 1].start_ms - word.end_ms;
    const shouldSplit = isLast || isPunctuation || gap > threshold;

    if (shouldSplit && currentWords.length > 0) {
      result.push({
        text: currentWords.map(w => w.text).join(""),
        start_ms: currentWords[0].start_ms,
        end_ms: currentWords[currentWords.length - 1].end_ms,
      });
      currentWords = [];
    }
  }

  return result;
}