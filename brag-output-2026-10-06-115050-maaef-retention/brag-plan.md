# Maaef — four wings, retention cut

Same elements as the four-wings video; re-edited for retention. "Maaef" is now voiced as **Maa-ef** (/mˈɑːɛf/, the client's pick from the three samples).

## What changed in the edit (and why)
- **Voice-first timeline.** `work/build_vo.py` synthesises every line, measures it, lays the lines end to end and then places the cuts. Scene lengths come from the voice, not from fixed 8-second blocks. 75s → **52.8s**.
- **No dead air.** At most 0.3s of silence between lines (0.2s breaths inside a scene, 0.12s after a wing name). Earlier cuts had 1–3s pauses.
- **J-cuts and L-cuts.** Scene changes alternate between a J-cut (the next line starts about 0.35s before the picture cuts) and an L-cut (the current line finishes over the next picture). Wing pages cut straight on the spoken wing name. The voice is never more than 0.35s ahead of its picture.

  | Into | Cut |
  |---|---|
  | who we are | L |
  | currencies | J |
  | four wings | J |
  | .enterprises | on the word "Enterprises" |
  | .studio | J |
  | .media | L |
  | .afterhours | J |
  | choose your crew | L |
  | the loop | J |
  | close | L |

- **Elements land on their words.** Word timings come from each line's phonemes. The four currency boxes land on "attention / precision / trust / time"; the wing tiles on "four / distinct / connected / businesses"; the crew cards on "one arm / pair two / bring / whole collective"; "M." on the spoken "M"; and the logo lockup on the closing "Maaef". On-screen text leads the voice by about 2 frames.
- **Every on-screen beat is voiced.** Each wing's "Worth saying" point is now spoken when its panel appears ("Diagnose, then deliver." / "Small test batches, or bulk runs." / "Planned before it's shot." / "Community, not crowds."). The wing pages stay up 4.6–7s without silence.
- **Minimum holds.** Each scene stays up long enough to read (cover 2.6s, wings at least 4.6s). If a hold pushes a cut later, the following voice moves with it so sync is never lost.
- **Cuts on the grid.** Cuts are snapped to 16th notes at 120 BPM. The music arrangement (groove in, riser into the wings, full band, half-time crew, final chord on the last "Maaef") is generated from the same timeline. The camera moves continuously within every scene, a constant gentle pattern interrupt.
- **SFX.** Only soft swishes under the cuts plus the riser; nothing fires on words.

## Timeline
| Scene | Time | Voice |
|---|---|---|
| cover | 0.00–2.62 | Maaef. The Sovereign Collective. |
| who | 2.62–8.75 | A collective that refuses to be one thing. Consultants, makers, storytellers and hosts, under one roof. |
| currencies | 8.75–12.75 | We trade in four currencies: attention, precision, trust, and time. |
| four wings | 12.75–16.12 | A Lucknow-based group of four distinct but connected businesses. |
| .enterprises | 16.12–23.25 | Enterprises. We find where an institution leaks, fix how it runs, and supply what it needs. Diagnose, then deliver. |
| .studio | 23.25–28.50 | Studios. If it can be printed, produced, or put in a box, we make it! Small test batches, or bulk runs. |
| .media | 28.50–35.25 | Media House. Artists disguised as a media house. We make the scroll stop! Planned before it's shot. |
| .afterhours | 35.25–39.88 | Afterhours. Where a brand stops talking, and starts hosting! Community, not crowds. |
| crew | 39.88–44.00 | Choose your crew. Pick one arm, pair two, or bring the whole collective! |
| loop | 44.00–47.25 | Every arm stands on its own. What one creates, the next amplifies. |
| close | 47.25–52.84 | The more the merrier. We're all about M! Maaef. A Sovereign Collective. |

## Research notes used
- Retention editing: cut dead air ruthlessly; a gap where nothing moves or sounds reads as the video being over ([Opus](https://www.opus.pro/blog/video-editing-tips), [Pixflow](https://pixflow.net/blog/youtube-video-retention-editing/)).
- J- and L-cuts: next audio before the picture (J), or current audio over the next picture (L), for smooth, continuous flow ([TechSmith](https://www.techsmith.com/blog/how-to-edit-videos-l-cuts-and-j-cuts/), [Cutsio](https://cutsio.com/blog/j-cut-vs-l-cut-video-editing-guide)).
- Kinetic typography: sync visual emphasis to vocal emphasis; per-character reveals for headlines, per-word for longer lines; timing precision matters at the frame level ([Todaymade](https://www.todaymade.com/blog/kinetic-typography-examples), [Demotion](https://trydemotion.com/blog/kinetic-typography-secrets)).
