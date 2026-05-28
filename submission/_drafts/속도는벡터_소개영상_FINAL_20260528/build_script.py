#!/usr/bin/env python3
"""v2: audio 한국어 발음 (TTS) + 자막 아라비아 숫자 (visual) 분리"""
import subprocess, re
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips

SRT = '/Users/hyunbin/Capstone/submission/_drafts/속도는벡터_소개영상_한국어자막_SRT_20260528.srt'
DOWNLOAD = Path('/Users/hyunbin/Downloads/download')
OUT_TTS = Path('/tmp/tts/edge_v2')
OUT_MERGED = Path('/Users/hyunbin/Downloads/final_v2_merged')
OUT_BURN = Path('/Users/hyunbin/Downloads/final_v2_burnin')
FINAL = Path('/Users/hyunbin/Downloads/속도는벡터_소개영상_FINAL_v2.mp4')
for p in [OUT_TTS, OUT_MERGED, OUT_BURN]:
    p.mkdir(parents=True, exist_ok=True)

VOICE = 'ko-KR-InJoonNeural'
FONT = '/System/Library/Fonts/AppleSDGothicNeo.ttc'

SEGMENT_MAP = {
    1:  'ADAPT_NO_IDX_step_pick_202605281615.mp4',
    2:  'VAQ_Ask_Hot_sale_cust_202605281615.mp4',
    3:  'VAQ_vec_stacked_boxes_202605281615.mp4',
    4:  'Database_optimizer_decides_plan_202605281615.mp4',
    5:  'Cardinality_and_Selectivity_defi…_202605281615.mp4',
    6:  'Two_panels_showing_estimates_202605281615.mp4',
    7:  '10000x_gap_Bad_Good_202605281615.mp4',
    8:  'Fixed_pgvec_33.3%_VBASE_50%_202605281615.mp4',
    9:  'Exqutor_No_Index_Sample_202605281615.mp4',
    10: '4_Step_SQL_Pick_N=385_202605281615.mp4',
    11: 'Pick_N_boxes_arrows_202605281615.mp4',
    12: 'Q_Better_way_BASE_PICK_202605281615.mp4',
    13: 'Three_ways_BASE_ONLY_BOTH_202605281615.mp4',
    14: 'Arrows_merge_into_center_box_202605281615.mp4',
    15: 'Data_and_Vars_panels_202605281615.mp4',
    16: 'Number_reveal_with_equation_202605281615.mp4',
    17: '13_7_Sets_S1_S2_202605281615.mp4',
    18: '89.1%_Q-error_better_202605281615.mp4',
    19: 'Two_bars_comparing_values_202605281615.mp4',
    20: 'Time_bars_comparison_data_202605281615.mp4',
    21: 'Plan_Pick_circles_comparison_202605281615.mp4',
    22: 'Same_Time_Better_Plan_202605281615.mp4',
    23: 'Run_SQL_Card_Plan_OK_202605281615.mp4',
    24: '5.70x_fast_vs_base_202605281615.mp4',
    25: 'Next_A_B_panels_202605281615.mp4',
    26: 'Thank_You_Q_and_A_202605281615.mp4',
}

# AUDIO entries (TTS용 — 정본 SRT, 한국어 발음 표기)
with open(SRT) as f:
    content = f.read()
audio_entries = {}
for block in re.split(r'\n\n+', content.strip()):
    lines = block.strip().split('\n')
    if len(lines) >= 3:
        num = int(lines[0])
        text = ' '.join(lines[2:]).strip()
        audio_entries[num] = text

# VISUAL entries (자막용 — 아라비아 숫자 + 한국어)
visual_entries = {
    1: '안녕하세요, 속도는 벡터 팀,\n발표 시작하겠습니다.',
    2: '벡터 증강 분석 쿼리, VAQ.\n관계형 조건과 벡터 유사도가 한 SQL 안에 결합됩니다.',
    3: '예시 쿼리에서 관계형 조건과\n벡터 유사도 임계값 0.86이 한 SQL 안에 결합됩니다.',
    4: '옵티마이저는 카디널리티를 추정해 plan을 결정합니다.\n추정이 틀리면 plan 전체가 바뀝니다.',
    5: '카디널리티는 조건을 만족하는 결과 행 수,\n선택도는 그 비율입니다.',
    6: '카디널리티 추정이 틀리면\n실행 계획이 통째로 바뀝니다.',
    7: '카디널리티 한 곳이 잘못되면\n같은 쿼리가 최대 10,000배 느려집니다.',
    8: '기존 시스템은 고정 비율로 가정합니다.\npgvector 33.3%, VBASE 50%, DuckDB 100%',
    9: 'Exqutor는 인덱스가 있으면 인덱스를,\n없으면 적응적 표본 추출을 사용합니다.',
    10: '적응적 표본 추출은 표본 추출, 카디널리티 추정,\nQ-error 측정, 표본 크기 조정의 4단계입니다.',
    11: '기존은 N을 얼마로 둘지에 집중.\n본 연구는 같은 N 안에서 표본을 어떻게 선택할지에 집중합니다.',
    12: '본 연구의 질문.\n카디널리티 추정을 더 잘할 수 있는 표본 추출 방식은 무엇인가.',
    13: '베이스라인 단독, method 단독 대체.\nmethod 단독은 특정 쿼리에서 안정적이지 못합니다.',
    14: '본 연구는 베이스라인과 분포 인지 method 추정값을\n산술 평균한 결합 방식을 사용합니다.',
    15: '실험은 5개 데이터셋과 4개 조작변인 위에서 진행.\n데이터 크기, 선택도, 계층 수, 표본 추출 방식.',
    16: '총 1,508가지 조합에서\n베이스라인과 결합 방식을 직접 비교했습니다.',
    17: '분포 인지 표본 추출 13개 method를\n7개 패러다임으로 분류했습니다.',
    18: '전체 1,508 측정 중 1,344 셀에서\n결합 방식이 더 낮은 Q-error. 비율 89.1%',
    19: '평균 Q-error: Base 1.4582, Combined 1.4019.\n결합 방식이 평균적으로 더 정확합니다.',
    20: 'pgvector 5,677ms, Base 977.6ms,\nCombined 983.5ms로 사실상 동일합니다.',
    21: '최적 plan 선택률: 156 중 91 → 156 중 148.\n58.3% → 94.9% 향상',
    22: '결합 방식은 평균 응답 시간을 동등하게 유지하면서\n최적 plan 선택률을 크게 높였습니다.',
    23: '최종 엔진에서 결합 카디널리티를 적용하면\n옵티마이저가 정답 plan을 골라 인덱스 스캔으로 실행됩니다.',
    24: '결합 방식 최종 엔진은\npgvector 기본 대비 5.70배 응답 시간을 단축했습니다.',
    25: '향후 연구는 두 갈래.\n검증 범위 확장 + 히스토리 인지 적응적 표본 추출.',
    26: '이상으로 발표를 마치겠습니다.\n감사합니다.',
}

# Step 1: TTS (rate +0%, natural)
print(f"=== TTS (rate=0%, natural) ===")
for num in sorted(audio_entries.keys()):
    text = audio_entries[num]
    mp3 = OUT_TTS / f"{num:02d}.mp3"
    if mp3.exists() and mp3.stat().st_size > 1000:
        continue
    cmd = ['edge-tts', '--voice', VOICE, '--rate=+0%', '--text', text, '--write-media', str(mp3)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        print(f"  {num:02d}.mp3 ({mp3.stat().st_size//1024}KB)")

# Step 2: Merge audio + video
print(f"\n=== Merge ===")
for num in sorted(SEGMENT_MAP.keys()):
    src_video = DOWNLOAD / SEGMENT_MAP[num]
    if not src_video.exists():
        candidates = list(DOWNLOAD.glob('*' + SEGMENT_MAP[num][:20] + '*'))
        if candidates: src_video = candidates[0]
        else: continue
    audio = OUT_TTS / f"{num:02d}.mp3"
    out = OUT_MERGED / f"{num:02d}.mp4"
    cmd = ['ffmpeg', '-y', '-i', str(src_video), '-i', str(audio),
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
           '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-t', '8', str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0: print(f"  ✅ {num:02d}.mp4")

# Step 3: Burn-in 자막 (visual entries, 28pt 하단)
print(f"\n=== 자막 burn-in (28pt 하단, 영상 안 가림) ===")
for num in range(1, 27):
    src = OUT_MERGED / f"{num:02d}.mp4"
    dst = OUT_BURN / f"{num:02d}.mp4"
    if not src.exists(): continue
    text = visual_entries.get(num, '')
    try:
        clip = VideoFileClip(str(src))
        w, h = clip.size
        sub = (TextClip(
            text=text,
            font=FONT,
            font_size=28,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(int(w * 0.85), None),
            text_align='center',
        )
        .with_duration(clip.duration)
        .with_position(('center', h - 90)))  # 하단 90px
        final = CompositeVideoClip([clip, sub])
        final.write_videofile(
            str(dst), codec='libx264', audio_codec='aac',
            preset='ultrafast', threads=4, logger=None,
        )
        clip.close(); final.close(); sub.close()
        print(f"  ✅ {num:02d}.mp4")
    except Exception as e:
        print(f"  ❌ {num:02d}: {e}")

# Step 4: Concat
print(f"\n=== Concat ===")
clips = []
for num in range(1, 27):
    p = OUT_BURN / f"{num:02d}.mp4"
    if p.exists(): clips.append(VideoFileClip(str(p)))
if clips:
    final = concatenate_videoclips(clips, method='compose')
    final.write_videofile(
        str(FINAL), codec='libx264', audio_codec='aac',
        preset='medium', threads=4, logger=None,
    )
    for c in clips: c.close()
    final.close()
    print(f"\n✅ 최종: {FINAL}\n   크기: {FINAL.stat().st_size // 1024 // 1024}MB")
