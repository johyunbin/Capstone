# 속도는벡터 소개영상 FINAL v2 (2026-05-28)

## 최종 결과
- **`속도는벡터_소개영상_FINAL_v2.mp4`** (14MB, 3:22, 1280×720)
- 26 segment 결합 + 한국어 자막 burn-in (아라비아 숫자 표기)
- audio: edge-tts ko-KR-InJoonNeural (Microsoft Azure Neural)
- video: Gemini Flow Veo 3.1

## 폴더
- `26_segments_burnin/` — 자막 burn-in 26 segment (storyboard 재편집 시 사용)
- `26_segments_merged/` — 자막 없는 26 segment (audio + video만, 자막 재편집 시 사용)
- `build_script.py` — 재생성 Python script (audio + 자막 + concat)

## 사용된 도구
- **edge-tts** (Microsoft Azure Neural Voice, 한국어 InJoonNeural)
- **ffmpeg** (audio + video merge, concat)
- **moviepy** (자막 burn-in, Apple SD Gothic Neo 28pt)
- **Gemini Flow Veo 3.1 Quality** (시각 컨텐츠 26 segment)

## 발음 표기 분리
- **Audio** (TTS 입력): 한국어 발음 표기 ("일 점 사 오 팔 이")
- **자막** (visual): 아라비아 숫자 ("1.4582", "89.1%", "5,677ms")

## 정본 SRT
- `submission/_drafts/속도는벡터_소개영상_한국어자막_SRT_20260528.srt` (26 entry)

---
*세션 종료: 2026-05-28*
