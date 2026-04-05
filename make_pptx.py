from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

TITLE_COLOR = RGBColor(0x1A, 0x56, 0xDB)   # 파랑
ACCENT_COLOR = RGBColor(0x10, 0x7C, 0x41)  # 초록
BG_COLOR = RGBColor(0xF8, 0xF9, 0xFF)
TEXT_COLOR = RGBColor(0x1F, 0x29, 0x37)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

blank_layout = prs.slide_layouts[6]

def add_bg(slide, color=BG_COLOR):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_text_box(slide, text, left, top, width, height,
                 font_size=18, bold=False, color=TEXT_COLOR,
                 align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox

def add_title_slide(title, subtitle_lines):
    slide = prs.slides.add_slide(blank_layout)
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x1A, 0x56, 0xDB)
    W, H = prs.slide_width, prs.slide_height
    add_text_box(slide, title, Inches(1), Inches(2), W - Inches(2), Inches(1.5),
                 font_size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    sub = "\n".join(subtitle_lines)
    add_text_box(slide, sub, Inches(1), Inches(3.8), W - Inches(2), Inches(2),
                 font_size=20, color=RGBColor(0xBF, 0xDB, 0xFF), align=PP_ALIGN.CENTER)

def add_section_slide(title, bullets, note=""):
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    W = prs.slide_width
    # 상단 색 바
    bar = slide.shapes.add_shape(1, 0, 0, W, Inches(0.08))
    bar.fill.solid(); bar.fill.fore_color.rgb = TITLE_COLOR
    bar.line.fill.background()

    add_text_box(slide, title, Inches(0.5), Inches(0.2), W - Inches(1), Inches(0.9),
                 font_size=28, bold=True, color=TITLE_COLOR)

    top = Inches(1.3)
    for bullet in bullets:
        is_sub = bullet.startswith("  ")
        txt = bullet.strip()
        indent = Inches(0.9) if is_sub else Inches(0.5)
        fs = 16 if is_sub else 18
        prefix = "   • " if is_sub else "• "
        add_text_box(slide, prefix + txt, indent, top, W - indent - Inches(0.5), Inches(0.5),
                     font_size=fs, color=TEXT_COLOR)
        top += Inches(0.48) if is_sub else Inches(0.55)

    if note:
        add_text_box(slide, note, Inches(0.5), Inches(6.8), W - Inches(1), Inches(0.5),
                     font_size=13, color=RGBColor(0x6B, 0x72, 0x80))

def add_table_slide(title, headers, rows):
    slide = prs.slides.add_slide(blank_layout)
    add_bg(slide)
    W = prs.slide_width
    bar = slide.shapes.add_shape(1, 0, 0, W, Inches(0.08))
    bar.fill.solid(); bar.fill.fore_color.rgb = TITLE_COLOR
    bar.line.fill.background()
    add_text_box(slide, title, Inches(0.5), Inches(0.2), W - Inches(1), Inches(0.9),
                 font_size=28, bold=True, color=TITLE_COLOR)

    cols = len(headers)
    col_w = (W - Inches(1)) // cols
    tbl = slide.shapes.add_table(len(rows)+1, cols,
                                 Inches(0.5), Inches(1.3),
                                 W - Inches(1), Inches(0.5 * (len(rows)+1))).table
    for c, h in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.text = h
        cell.fill.solid(); cell.fill.fore_color.rgb = TITLE_COLOR
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(14)
        p.runs[0].font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tbl.cell(r+1, c)
            cell.text = str(val)
            if r % 2 == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0xE8, 0xF0, 0xFF)
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
            p = cell.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(13)
            p.runs[0].font.color.rgb = TEXT_COLOR
            p.alignment = PP_ALIGN.CENTER

# ── 슬라이드 생성 ──────────────────────────────────────────

# 1. 표지
add_title_slide(
    "마.스.타 활성화 교사 교육안",
    ["기간: 2026년 4월 ~ 6월 (3개월)",
     "목표: 신규 47명 확보 / 이탈률 50% 감소",
     "대상: 전체 교사 11명"]
)

# 2. 현황 분석
add_section_slide("현황 분석 — 핵심 수치", [
    "전체 관리회원  483명",
    "마.스.타 회원  64명 (13.3%)",
    "스마트 구몬 회원  231명 (47.8%)",
    "미가입 대상  약 188명",
    "월 신규 약 10명  vs  월 이탈 약 13명 → 순감 진행 중",
])

# 3. 교사 분류
add_section_slide("교사 분류", [
    "▶ 우수 교사 (벤치마크 대상)",
    "  김주연 — 점유율 27.5%, 권유 노하우 공유 대상",
    "  김은숙 — 마스타 14명 최다 보유",
    "▶ 집중 육성 대상 (대상 풀 多, 점유율 低)",
    "  이경옥 47명 중 3명 (6.4%)  /  원희선 50명 중 2명 (4.0%)",
    "  박양희 50명 중 2명 (4.0%)  /  최승희 68명 중 7명 (10.3%)",
    "▶ 소규모 관리 교사",
    "  신인숙(16명), 이주아(19명), 김태연(18명)",
])

# 4. 이탈 사유
add_section_slide("이탈 3대 사유", [
    "1.  월 4만원 추가 비용 대비 가치를 못 느낌",
    "2.  추가 학습량 부담으로 포기",
    "3.  교사와 시간 조율 어려움",
])

# 5. 교육 구성
add_table_slide("교육 구성 (총 3회차)",
    ["회차", "주제", "일정"],
    [["1회차", "가치 전달 화법", "4월 첫째 주"],
     ["2회차", "이탈 방어", "4월 셋째 주"],
     ["3회차", "목표 관리 & 실전 점검", "5월 첫째 주"]]
)

# 6. 1회차 화법
add_section_slide("1회차 — 비용 저항 극복 화법", [
    '"4만원이 부담돼요"',
    '  → 주 1회 기준 회당 1만원, 학원 보충수업보다 낮으면서 1:1 맞춤 지도',
    '"교재만 더 푸는 거 아닌가요?"',
    '  → OO의 약한 부분만 집중 보강하는 구조, 진단 결과 기반 설명',
    '"효과를 모르겠어요"',
    '  → 3개월 전 시작한 OO 회원 진단평가 점수 데이터로 제시',
])

# 7. 권유 타이밍
add_section_slide("1회차 — 권유 황금 타이밍", [
    "진단평가 후 결과 공유 시  →  마.스.타 효과 연결",
    "학부모 상담 중 학습 고민 언급 시  →  해결책으로 자연스럽게 제안",
    "스마트 구몬 데이터 리뷰 시  →  약점 영역 기반 제안",
    "",
    "실습: 교사 2인 1조 롤플레이 (3가지 거절 상황 대응 연습)",
])

# 8. 2회차 이탈 방어
add_section_slide("2회차 — 이탈 신호별 교사 조치", [
    "숙제 미완료 2회 연속",
    "  → 분량 30% 축소 → 성공 경험 후 복원",
    '"어려워요" 반복',
    "  → 1단계 하향, 기초 보강 후 복귀",
    '"그만둘까 해요"',
    "  → 48시간 내 전화 상담, 중단 아닌 조정 옵션 제시",
], note="목표: 월 이탈 13명 → 6명 이하")

# 9. 시간 조율
add_section_slide("2회차 — 시간 조율 개선안", [
    "개선안 1  주 중 2개 타임슬롯 제공 (회원 선택)",
    "개선안 2  비대면 보충 지도 병행 (스마트 구몬 연계)",
    "개선안 3  교사 간 회원 시간대 교환 조율",
])

# 10. 3회차 목표
add_table_slide("3회차 — 교사별 3개월 목표",
    ["교사명", "3개월 목표", "월평균"],
    [["김은숙", "10명", "3.3명"],
     ["최승희", "7명", "2.3명"],
     ["원희선", "5명", "1.7명"],
     ["박양희", "5명", "1.7명"],
     ["이경옥", "5명", "1.7명"],
     ["김주연", "4명", "1.3명"],
     ["이경이", "4명", "1.3명"],
     ["합계", "47명", "15.7명"]]
)

# 11. KPI
add_section_slide("3회차 — KPI & 보고 체계", [
    "마.스.타 권유 상담  →  월 8회 이상 (소규모 교사 4회)",
    "이탈 신호 조기 상담  →  발생 48시간 내 100%",
    "기존 회원 이탈  →  0명 목표",
    "",
    "매주 금요일  교사 → 관리자 보고 (신규·가입·이탈 위기)",
    "매월 첫째 주  전체 교사 월간 실적 리뷰 미팅",
])

# 12. 로드맵
add_table_slide("월별 실행 로드맵",
    ["월", "교육", "실행", "점검"],
    [["4월", "1·2회차", "권유 대상 5명 선정 및 상담", "월말 신규·이탈 집계"],
     ["5월", "3회차", "주간 보고 체계 가동", "중간 점검"],
     ["6월", "부진 교사 코칭", "1:1 동행 상담", "최종 평가·시상"]]
)

# 13. 월별 목표
add_table_slide("월별 수치 목표",
    ["월", "신규 목표", "이탈 목표", "순증"],
    [["4월", "13명", "7명↓", "+6명"],
     ["5월", "16명", "6명↓", "+10명"],
     ["6월", "18명", "5명↓", "+13명"],
     ["합계", "47명", "18명↓", "+29명"]]
)

# 14. 성공 기준
add_table_slide("성공 기준",
    ["지표", "현재", "3개월 목표"],
    [["마.스.타 회원 수", "64명", "93명 이상"],
     ["마.스.타 점유율", "13.3%", "약 19%"],
     ["월 이탈", "13명", "6명 이하"],
     ["월 신규", "10명", "16명 이상"]]
)

# ── 2분기 전략 섹션 ──────────────────────────────────────────

# 15. 전략 1 개요
add_section_slide("2분기 전략 1 — 마.스타 순증 +47 달성", [
    "현황: 1분기 -4.5 → 2분기 목표 +47  (최우선 과제)",
    "",
    "월별 배분 목표",
    "  4월  +11  (신학기 체험 전환 집중)",
    "  5월  +12  (입회 본격화)",
    "  6월  +24  (상반기 마감 스퍼트 + 이탈 최소화)",
], note="핵심 전제: 마.스타 퇴회 억제 없이는 순증 달성 불가")

# 16. 대형 교사 집중 공략 (표)
add_table_slide("전략 1-① 대형 교사 집중 공략",
    ["교사명", "현재 마.스타", "점유율", "잔여 대상", "2분기 목표"],
    [["김은숙", "14명", "13.6%", "89명 ★최다", "6~7명"],
     ["최승희", "7명", "10.3%", "61명", "4~5명"],
     ["원희선", "2명", "4.0% ▼", "48명", "3~4명"],
     ["박양희", "2명", "4.0% ▼", "48명", "3~4명"],
     ["이경옥", "3명", "6.4%", "44명", "3명"]]
)

# 17. 우수 교사 노하우 전파
add_section_slide("전략 1-② 우수 교사 노하우 전파", [
    "김주연 교사  (점유율 27.5% — 전체 1위)",
    "  → 4월 교사 미팅에서 권유 화법·성공 사례 공유",
    "  → 저점유율 교사에게 스크립트 직접 적용",
    "",
    "김은숙 교사  (마.스타 14명 — 최다 보유)",
    "  → 대규모 회원 관리 시 권유 타이밍·노하우 공유",
    "",
    "적용 대상: 원희선·박양희·이경이 (점유율 2.9~4.0% 최하위 3인)",
])

# 18. 스마트구몬 전환 + 소규모 교사
add_section_slide("전략 1-③④ 전환 집중 & 소규모 교사 관리", [
    "③ 스마트구몬 → 마.스타 전환 집중",
    "  SKN 계약 회원 중 마.스타 미가입자 교사별 목록화",
    "  이경이 교사 — 점유율 2.9%, 잔여 34명 (전환 가능성 최고)",
    "  → 관리자 동행 상담 우선 투입",
    "",
    "④ 소규모 교사 — 현실적 목표 유지",
    "  신인숙(잔여 13명) / 이주아(18명) / 김태연(17명)",
    "  → 2분기 각 1명 목표 / 권유 상담 월 4회 이상 이행 점검",
], note="전체 합계: 47명 순증 = 대형 교사 20명 + 중형 10명 + 저점유율 전환 17명")

prs.save("d:/Coding/claude/마스타_교사교육안.pptx")
print("완료: 마스타_교사교육안.pptx")
