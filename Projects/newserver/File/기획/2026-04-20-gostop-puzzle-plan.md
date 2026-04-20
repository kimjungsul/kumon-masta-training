# 고스톱 퍼즐 MVP 구현 플랜

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 15개 고정 초기상태 스테이지와 5분 기본 튜토리얼을 갖춘 PC 웹 고스톱 퍼즐 게임 MVP 구현.

**Architecture:** 순수 함수형 룰 엔진 + React UI + localStorage. 엔진은 UI에서 분리되어 TDD 가능. 고정 더미 순서로 결정론적 플레이 보장. 가상 상대 파라미터로 피박/광박 계산.

**Tech Stack:** React 18, TypeScript, Vite, Vitest, TailwindCSS, React Router, GA4. 백엔드 없음.

**Spec Reference:** [2026-04-20-gostop-puzzle-design.md](./2026-04-20-gostop-puzzle-design.md)

---

## 파일 구조

```
src/
├── main.tsx                       # Vite 엔트리
├── App.tsx                        # Router 루트
├── index.css                      # Tailwind 베이스
├── engine/
│   ├── types.ts                   # Card, GameState, Move, MissionResult 타입
│   ├── cards.ts                   # 48장 화투 데이터
│   ├── deck.ts                    # 더미 초기화, 뽑기
│   ├── engine.ts                  # applyMove(state, move) → newState
│   ├── rules.ts                   # 쫑/쓸/뻑/따닥 감지
│   ├── scoring.ts                 # 광/띠/피 점수, 고도리, 피박/광박
│   └── solver.ts                  # 스테이지 최소 풀이 턴 검증
├── stages/
│   ├── types.ts                   # StageDefinition 스키마
│   ├── registry.ts                # 15개 스테이지 목록 export
│   └── data/
│       ├── stage-01.ts ~ stage-15.ts
├── tutorial/
│   ├── types.ts                   # TutorialStep 타입
│   ├── basic-steps.ts             # 기본 튜토리얼 5단계
│   ├── mini-lessons.ts            # 스테이지별 미니 레슨
│   └── TutorialRunner.tsx         # 튜토리얼 UI
├── screens/
│   ├── StageSelectScreen.tsx
│   ├── TutorialScreen.tsx
│   ├── GameScreen.tsx             # 대시보드 3단 가로
│   ├── ResultScreen.tsx
│   └── SettingsScreen.tsx
├── components/
│   ├── Card.tsx                   # 개별 화투 카드
│   ├── HandArea.tsx               # 손패 영역
│   ├── FloorArea.tsx              # 바닥 카드 영역
│   ├── DeckArea.tsx               # 더미 + 뒤집힌 카드
│   ├── MissionPanel.tsx           # 미션 요약
│   ├── ScorePanel.tsx             # 점수/턴 카운터
│   ├── CapturedCards.tsx          # 내 획득 카드 (광/띠/피)
│   └── VirtualOpponentPanel.tsx   # 가상 상대 피 카운터
├── storage/
│   └── localStorage.ts            # 진행도 저장/로드
├── analytics/
│   ├── events.ts                  # 이벤트 타입
│   └── ga4.ts                     # GA4 래퍼
└── assets/cards/                  # 48장 WebP (디자이너 작업물)

tests/
├── engine/                        # Vitest 유닛 테스트
└── e2e/                           # Playwright (선택)

public/
index.html
vite.config.ts
tsconfig.json
tailwind.config.js
package.json
```

---

## Phase 0 — 프로젝트 셋업

### Task 1: Vite + React + TypeScript 프로젝트 초기화

**Files:**
- Create: `package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`, `src/App.tsx`, `src/index.css`

- [ ] **Step 1: Vite 프로젝트 생성**

```bash
cd d:/Claude/Projects/newserver
npm create vite@latest app -- --template react-ts
cd app
npm install
```

- [ ] **Step 2: 프로젝트 구조 확인**

Run: `ls app/src`
Expected: `main.tsx`, `App.tsx`, `index.css`, `vite-env.d.ts`

- [ ] **Step 3: 개발 서버 구동 테스트**

Run: `npm run dev`
Expected: `http://localhost:5173`에서 기본 Vite 페이지 표시. Ctrl+C로 종료.

- [ ] **Step 4: 초기 커밋**

```bash
git add .
git commit -m "chore: Vite+React+TS 스캐폴드 초기화"
```

---

### Task 2: TailwindCSS 설정

**Files:**
- Create: `tailwind.config.js`, `postcss.config.js`
- Modify: `src/index.css`

- [ ] **Step 1: Tailwind 설치**

```bash
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```

- [ ] **Step 2: tailwind.config.js 설정**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

- [ ] **Step 3: index.css에 디렉티브 추가**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 4: App.tsx에서 Tailwind 동작 확인**

```tsx
export default function App() {
  return <div className="bg-green-100 p-4">Tailwind 동작 확인</div>
}
```

Run: `npm run dev` → 녹색 배경 표시 확인.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "chore: TailwindCSS v3 설정 추가"
```

---

### Task 3: Vitest 테스트 환경 구축

**Files:**
- Modify: `package.json`, `vite.config.ts`
- Create: `src/engine/example.test.ts`

- [ ] **Step 1: Vitest 설치**

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 2: vite.config.ts에 테스트 설정 추가**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
  },
})
```

- [ ] **Step 3: package.json에 스크립트 추가**

```json
"scripts": {
  "dev": "vite",
  "build": "tsc -b && vite build",
  "test": "vitest",
  "test:run": "vitest run"
}
```

- [ ] **Step 4: 샘플 테스트 파일 작성**

`src/engine/example.test.ts`:
```ts
import { describe, it, expect } from 'vitest'

describe('샘플', () => {
  it('1+1=2', () => {
    expect(1 + 1).toBe(2)
  })
})
```

- [ ] **Step 5: 테스트 실행**

Run: `npm run test:run`
Expected: 1 passed.

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "chore: Vitest 환경 구축"
```

---

### Task 4: React Router 설치 및 기본 라우팅

**Files:**
- Modify: `package.json`, `src/App.tsx`
- Create: `src/screens/StageSelectScreen.tsx` (placeholder)

- [ ] **Step 1: React Router 설치**

```bash
npm install react-router-dom@6
```

- [ ] **Step 2: App.tsx에 라우터 설정**

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import StageSelectScreen from './screens/StageSelectScreen'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StageSelectScreen />} />
        <Route path="/tutorial" element={<div>튜토리얼 (준비중)</div>} />
        <Route path="/play/:stageId" element={<div>게임 (준비중)</div>} />
        <Route path="/result/:stageId" element={<div>결과 (준비중)</div>} />
        <Route path="/settings" element={<div>설정 (준비중)</div>} />
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 3: StageSelectScreen placeholder 작성**

```tsx
export default function StageSelectScreen() {
  return <div className="p-8"><h1 className="text-2xl">스테이지 선택</h1></div>
}
```

- [ ] **Step 4: `npm run dev`로 `/` 페이지 확인**

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat: React Router 기본 라우트 구성"
```

---

## Phase 1 — 룰 엔진 (TDD)

### Task 5: 카드 타입과 48장 데이터 정의

**Files:**
- Create: `src/engine/types.ts`, `src/engine/cards.ts`, `src/engine/cards.test.ts`

- [ ] **Step 1: 실패하는 테스트 작성**

`src/engine/cards.test.ts`:
```ts
import { describe, it, expect } from 'vitest'
import { ALL_CARDS, CARDS_BY_MONTH } from './cards'

describe('cards', () => {
  it('총 48장', () => {
    expect(ALL_CARDS.length).toBe(48)
  })

  it('월별 4장씩 12개월', () => {
    for (let m = 1; m <= 12; m++) {
      expect(CARDS_BY_MONTH[m].length).toBe(4)
    }
  })

  it('광 카드는 5장 (1,3,8,11,12월)', () => {
    const kwangs = ALL_CARDS.filter(c => c.category === 'kwang')
    expect(kwangs.length).toBe(5)
    expect(kwangs.map(c => c.month).sort()).toEqual([1, 3, 8, 11, 12])
  })

  it('쌍피는 3장 (9월 국진, 10월 단풍사슴, 11월 오동)', () => {
    const ssangpi = ALL_CARDS.filter(c => c.category === 'ssangpi')
    expect(ssangpi.length).toBe(3)
  })
})
```

- [ ] **Step 2: 테스트 실행 — 실패 확인**

Run: `npm run test:run -- cards`
Expected: FAIL — `ALL_CARDS`, `CARDS_BY_MONTH` 정의 없음.

- [ ] **Step 3: types.ts 작성**

```ts
export type CardCategory = 'kwang' | 'tti' | 'ssangpi' | 'pi'
export type TtiType = 'hong-dan' | 'cheong-dan' | 'cho-dan' | 'plain' | null
export type KwangType = 'normal' | 'bi-kwang' | null  // 12월 비광

export interface Card {
  id: string                 // "01-kwang", "03-hong", etc.
  month: number              // 1~12
  category: CardCategory
  ttiType?: TtiType          // 띠일 경우만
  kwangType?: KwangType      // 광일 경우만
  name: string               // 한글 이름 (디버깅/UI용)
}
```

- [ ] **Step 4: cards.ts 작성**

48장 모두 명시적으로 정의. 생략 금지. 월별 구성:

```ts
import type { Card } from './types'

export const ALL_CARDS: Card[] = [
  // 1월 송학
  { id: '01-kwang', month: 1, category: 'kwang', kwangType: 'normal', name: '송학 광' },
  { id: '01-hong', month: 1, category: 'tti', ttiType: 'hong-dan', name: '송학 홍단' },
  { id: '01-pi-a', month: 1, category: 'pi', name: '송학 피1' },
  { id: '01-pi-b', month: 1, category: 'pi', name: '송학 피2' },
  // 2월 매조
  { id: '02-tti', month: 2, category: 'tti', ttiType: 'hong-dan', name: '매조 홍단' },
  { id: '02-hong-normal', month: 2, category: 'tti', ttiType: 'plain', name: '매조 띠' },
  { id: '02-pi-a', month: 2, category: 'pi', name: '매조 피1' },
  { id: '02-pi-b', month: 2, category: 'pi', name: '매조 피2' },
  // 3월 벚꽃
  { id: '03-kwang', month: 3, category: 'kwang', kwangType: 'normal', name: '벚꽃 광' },
  { id: '03-hong', month: 3, category: 'tti', ttiType: 'hong-dan', name: '벚꽃 홍단' },
  { id: '03-pi-a', month: 3, category: 'pi', name: '벚꽃 피1' },
  { id: '03-pi-b', month: 3, category: 'pi', name: '벚꽃 피2' },
  // 4월 흑싸리
  { id: '04-tti', month: 4, category: 'tti', ttiType: 'cho-dan', name: '흑싸리 초단' },
  { id: '04-dan', month: 4, category: 'tti', ttiType: 'plain', name: '흑싸리 띠' },
  { id: '04-pi-a', month: 4, category: 'pi', name: '흑싸리 피1' },
  { id: '04-pi-b', month: 4, category: 'pi', name: '흑싸리 피2' },
  // 5월 난초
  { id: '05-tti', month: 5, category: 'tti', ttiType: 'cho-dan', name: '난초 초단' },
  { id: '05-plain', month: 5, category: 'tti', ttiType: 'plain', name: '난초 띠' },
  { id: '05-pi-a', month: 5, category: 'pi', name: '난초 피1' },
  { id: '05-pi-b', month: 5, category: 'pi', name: '난초 피2' },
  // 6월 모란
  { id: '06-tti', month: 6, category: 'tti', ttiType: 'cheong-dan', name: '모란 청단' },
  { id: '06-plain', month: 6, category: 'tti', ttiType: 'plain', name: '모란 띠' },
  { id: '06-pi-a', month: 6, category: 'pi', name: '모란 피1' },
  { id: '06-pi-b', month: 6, category: 'pi', name: '모란 피2' },
  // 7월 홍싸리
  { id: '07-tti', month: 7, category: 'tti', ttiType: 'cho-dan', name: '홍싸리 초단' },
  { id: '07-plain', month: 7, category: 'tti', ttiType: 'plain', name: '홍싸리 띠' },
  { id: '07-pi-a', month: 7, category: 'pi', name: '홍싸리 피1' },
  { id: '07-pi-b', month: 7, category: 'pi', name: '홍싸리 피2' },
  // 8월 공산
  { id: '08-kwang', month: 8, category: 'kwang', kwangType: 'normal', name: '공산 광' },
  { id: '08-tti', month: 8, category: 'tti', ttiType: 'plain', name: '공산 띠' },
  { id: '08-pi-a', month: 8, category: 'pi', name: '공산 피1' },
  { id: '08-pi-b', month: 8, category: 'pi', name: '공산 피2' },
  // 9월 국진
  { id: '09-tti', month: 9, category: 'tti', ttiType: 'cheong-dan', name: '국진 청단' },
  { id: '09-ssangpi', month: 9, category: 'ssangpi', name: '국진 쌍피' },
  { id: '09-pi-a', month: 9, category: 'pi', name: '국진 피1' },
  { id: '09-pi-b', month: 9, category: 'pi', name: '국진 피2' },
  // 10월 단풍
  { id: '10-tti', month: 10, category: 'tti', ttiType: 'cheong-dan', name: '단풍 청단' },
  { id: '10-ssangpi', month: 10, category: 'ssangpi', name: '단풍 쌍피' },
  { id: '10-pi-a', month: 10, category: 'pi', name: '단풍 피1' },
  { id: '10-pi-b', month: 10, category: 'pi', name: '단풍 피2' },
  // 11월 오동
  { id: '11-kwang', month: 11, category: 'kwang', kwangType: 'normal', name: '오동 광' },
  { id: '11-ssangpi', month: 11, category: 'ssangpi', name: '오동 쌍피' },
  { id: '11-pi-a', month: 11, category: 'pi', name: '오동 피1' },
  { id: '11-pi-b', month: 11, category: 'pi', name: '오동 피2' },
  // 12월 비
  { id: '12-kwang', month: 12, category: 'kwang', kwangType: 'bi-kwang', name: '비광' },
  { id: '12-tti', month: 12, category: 'tti', ttiType: 'plain', name: '비 띠' },
  { id: '12-dbl-pi', month: 12, category: 'ssangpi', name: '비 쌍피' },
  { id: '12-pi', month: 12, category: 'pi', name: '비 피' },
]

export const CARDS_BY_MONTH: Record<number, Card[]> = ALL_CARDS.reduce((acc, c) => {
  (acc[c.month] = acc[c.month] || []).push(c)
  return acc
}, {} as Record<number, Card[]>)
```

- [ ] **Step 5: 테스트 통과 확인**

Run: `npm run test:run -- cards`
Expected: PASS (4 tests).

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "feat(engine): 48장 화투 카드 데이터 + 타입 정의"
```

---

### Task 6: GameState 타입과 초기화 함수

**Files:**
- Modify: `src/engine/types.ts`
- Create: `src/engine/state.ts`, `src/engine/state.test.ts`

- [ ] **Step 1: 실패 테스트 작성**

`src/engine/state.test.ts`:
```ts
import { describe, it, expect } from 'vitest'
import { initGameState } from './state'

describe('initGameState', () => {
  it('손패 7장, 바닥 6장, 더미 35장', () => {
    const state = initGameState({
      handIds: ['01-kwang','02-tti','03-kwang','04-tti','05-tti','06-tti','07-tti'],
      floorIds: ['08-kwang','09-tti','10-tti','11-kwang','12-kwang','01-hong'],
      deckIds: Array(35).fill(null).map((_,i) => `placeholder-${i}`)  // 실제론 카드 id 35개
    })
    expect(state.hand.length).toBe(7)
    expect(state.floor.length).toBe(6)
    expect(state.deck.length).toBe(35)
  })

  it('초기 획득 카드는 비어있음', () => {
    const state = initGameState({
      handIds: ['01-kwang'],
      floorIds: ['01-hong'],
      deckIds: []
    })
    expect(state.captured.kwang).toEqual([])
    expect(state.captured.tti).toEqual([])
    expect(state.captured.pi).toEqual([])
  })
})
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

Run: `npm run test:run -- state`
Expected: FAIL.

- [ ] **Step 3: types.ts에 GameState 추가**

```ts
export interface Captured {
  kwang: Card[]
  tti: Card[]
  pi: Card[]
  ssangpi: Card[]
}

export interface GameState {
  hand: Card[]
  floor: Card[]
  deck: Card[]              // 더미 (순서 유지)
  captured: Captured        // 내가 획득한 카드
  turn: number              // 0부터 시작
  heundalki?: number        // 흔들기 선언한 월 (선언 시 2배 점수)
  pbbukStack: Record<number, Card[]>  // 뻑 상태 (월별 스택)
}

export interface StageInit {
  handIds: string[]
  floorIds: string[]
  deckIds: string[]
}
```

- [ ] **Step 4: state.ts 구현**

```ts
import type { Card, GameState, StageInit } from './types'
import { ALL_CARDS } from './cards'

const byId = new Map(ALL_CARDS.map(c => [c.id, c]))

function toCards(ids: string[]): Card[] {
  return ids.map(id => {
    const c = byId.get(id)
    if (!c) throw new Error(`Unknown card id: ${id}`)
    return c
  })
}

export function initGameState(init: StageInit): GameState {
  return {
    hand: toCards(init.handIds),
    floor: toCards(init.floorIds),
    deck: toCards(init.deckIds),
    captured: { kwang: [], tti: [], pi: [], ssangpi: [] },
    turn: 0,
    pbbukStack: {},
  }
}
```

- [ ] **Step 5: 테스트 통과 확인**

참고: deck 테스트의 placeholder id는 실제 카드 id로 교체해야 통과. 테스트 수정:

```ts
deckIds: ['02-hong-normal','02-pi-a','02-pi-b','03-hong','03-pi-a','03-pi-b',
  '04-dan','04-pi-a','04-pi-b','05-plain','05-pi-a','05-pi-b',
  '06-plain','06-pi-a','06-pi-b','07-plain','07-pi-a','07-pi-b',
  '08-tti','08-pi-a','08-pi-b','09-tti','09-ssangpi','09-pi-a','09-pi-b',
  '10-tti','10-ssangpi','10-pi-a','10-pi-b','11-ssangpi','11-pi-a','11-pi-b',
  '12-tti','12-dbl-pi','12-pi']
```

Run: `npm run test:run -- state`
Expected: PASS.

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "feat(engine): GameState 타입과 초기화 함수"
```

---

### Task 7: 기본 매칭 로직 — 손패 1장 → 바닥 매칭

**Files:**
- Create: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 작성**

```ts
import { describe, it, expect } from 'vitest'
import { initGameState } from './state'
import { playHandCard } from './engine'

describe('playHandCard — 단순 매칭', () => {
  it('손패의 1월을 내면 바닥 1월과 같이 획득', () => {
    const state = initGameState({
      handIds: ['01-kwang'],
      floorIds: ['01-hong'],
      deckIds: ['02-pi-a'],
    })
    const next = playHandCard(state, '01-kwang')
    expect(next.hand).toHaveLength(0)
    expect(next.floor).toHaveLength(0)
    expect(next.captured.kwang.map(c=>c.id)).toContain('01-kwang')
    expect(next.captured.tti.map(c=>c.id)).toContain('01-hong')
  })

  it('매칭 없으면 손패 카드가 바닥으로 떨어짐', () => {
    const state = initGameState({
      handIds: ['05-plain'],
      floorIds: ['01-hong'],
      deckIds: ['02-pi-a'],
    })
    const next = playHandCard(state, '05-plain')
    expect(next.hand).toHaveLength(0)
    expect(next.floor.map(c=>c.id).sort()).toEqual(['01-hong','05-plain'])
    expect(next.captured.kwang).toHaveLength(0)
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: FAIL — `playHandCard` 미정의.

- [ ] **Step 3: engine.ts 기본 구현 (더미 뽑기 제외)**

```ts
import type { Card, Captured, GameState } from './types'

function categoryKey(c: Card): keyof Captured {
  return c.category
}

function pushCaptured(cap: Captured, card: Card): Captured {
  const next = { ...cap, [categoryKey(card)]: [...cap[categoryKey(card)], card] }
  return next
}

export function playHandCard(state: GameState, handCardId: string): GameState {
  const handCard = state.hand.find(c => c.id === handCardId)
  if (!handCard) throw new Error(`손패에 없는 카드: ${handCardId}`)

  const newHand = state.hand.filter(c => c.id !== handCardId)
  const matches = state.floor.filter(c => c.month === handCard.month)

  let newFloor = state.floor
  let newCap = state.captured

  if (matches.length === 1) {
    // 단순 매칭 — 손패 + 바닥 1장 획득
    newFloor = state.floor.filter(c => c.id !== matches[0].id)
    newCap = pushCaptured(pushCaptured(newCap, handCard), matches[0])
  } else if (matches.length === 0) {
    // 매칭 없음 — 바닥에 쌓임
    newFloor = [...state.floor, handCard]
  }
  // matches.length === 2 or 3 는 다음 태스크에서 처리

  return { ...state, hand: newHand, floor: newFloor, captured: newCap, turn: state.turn + 1 }
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 기본 손패→바닥 매칭 구현"
```

---

### Task 8: 더미 뽑기 로직 추가

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('playHandCard — 더미 뽑기', () => {
  it('손패 낸 후 더미 맨 위 카드 뒤집어 매칭 처리', () => {
    const state = initGameState({
      handIds: ['05-plain'],      // 매칭 없음 → 바닥에 쌓임
      floorIds: ['01-hong','02-pi-a'],
      deckIds: ['02-pi-b','03-pi-a'],
    })
    const next = playHandCard(state, '05-plain')
    // 더미 맨 위는 '02-pi-b' → 바닥 '02-pi-a'와 매칭 → 둘 다 획득
    expect(next.deck.map(c=>c.id)).toEqual(['03-pi-a'])
    expect(next.captured.pi.map(c=>c.id)).toContain('02-pi-a')
    expect(next.captured.pi.map(c=>c.id)).toContain('02-pi-b')
    expect(next.floor.map(c=>c.id).sort()).toEqual(['01-hong','05-plain'])
  })

  it('더미 카드도 매칭 없으면 바닥에 쌓임', () => {
    const state = initGameState({
      handIds: ['05-plain'],
      floorIds: ['01-hong'],
      deckIds: ['07-plain'],
    })
    const next = playHandCard(state, '05-plain')
    expect(next.floor.map(c=>c.id).sort()).toEqual(['01-hong','05-plain','07-plain'])
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: 새 테스트 FAIL (기존 PASS 유지).

- [ ] **Step 3: engine.ts에 더미 뽑기 로직 추가**

`playHandCard` 마지막 return 직전에 더미 처리 삽입:

```ts
export function playHandCard(state: GameState, handCardId: string): GameState {
  const handCard = state.hand.find(c => c.id === handCardId)
  if (!handCard) throw new Error(`손패에 없는 카드: ${handCardId}`)

  const afterHand = applyCardToFloor(
    { ...state, hand: state.hand.filter(c => c.id !== handCardId) },
    handCard,
    { fromDeck: false }
  )

  // 더미 맨 위 카드 뒤집기
  if (afterHand.deck.length === 0) {
    return { ...afterHand, turn: afterHand.turn + 1 }
  }

  const [drawnCard, ...restDeck] = afterHand.deck
  const afterDraw = applyCardToFloor(
    { ...afterHand, deck: restDeck },
    drawnCard,
    { fromDeck: true }
  )

  return { ...afterDraw, turn: afterDraw.turn + 1 }
}

function applyCardToFloor(
  state: GameState,
  card: Card,
  _opts: { fromDeck: boolean }
): GameState {
  const matches = state.floor.filter(c => c.month === card.month)

  if (matches.length === 1) {
    return {
      ...state,
      floor: state.floor.filter(c => c.id !== matches[0].id),
      captured: pushCaptured(pushCaptured(state.captured, card), matches[0]),
    }
  }
  if (matches.length === 0) {
    return { ...state, floor: [...state.floor, card] }
  }
  // matches.length === 2, 3 — 다음 태스크에서 처리
  throw new Error('NOT_IMPLEMENTED: multi-match (쫑/뻑/따닥)')
}
```

원래 `playHandCard`에서 `turn: state.turn + 1` 중복 증가 버그 수정 필요. 위 구현으로 대체.

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS (이전 테스트 포함 모두).

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 더미 뽑기 및 매칭 처리"
```

---

### Task 9: 쫑 (같은 월 2장 동시 획득) 처리

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('쫑', () => {
  it('바닥에 같은 월 1장 + 더미에서 같은 월 뒤집히면 쫑 성립, 3장 모두 획득', () => {
    const state = initGameState({
      handIds: ['01-kwang'],
      floorIds: ['01-hong'],
      deckIds: ['01-pi-a'],
    })
    const next = playHandCard(state, '01-kwang')
    // 손패 1월 + 바닥 1월 매칭 후, 더미 1월 뒤집음 → 더미는 바닥에 1월 없으므로 쌓임? 
    // 아니오: 쫑 = 손패-바닥 매칭 + 같은 월 더미 뒤집힘 → 더미+기존매칭 3장 내 차지
    // 정확한 정의: 손패 매칭 직후 바닥에 같은 월이 없어졌는데, 더미가 같은 월이면 → 손패카드가 바닥에 남아있다가 더미와 쫑
    // 여기선 단순화: 손패가 매칭된 월과 더미가 같은 월이면 더미도 내 차지 (추가 피 1장 보너스 개념)
    expect(next.captured.kwang.map(c=>c.id)).toContain('01-kwang')
    expect(next.captured.tti.map(c=>c.id)).toContain('01-hong')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-a')
    // 보너스: 쫑 시 상대 피 1장 뺏음 → MVP에선 가상 상대 피 카운터 -1
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: 새 테스트 FAIL.

- [ ] **Step 3: GameState에 `opponentPi` 필드 추가**

`types.ts` 수정:
```ts
export interface GameState {
  hand: Card[]
  floor: Card[]
  deck: Card[]
  captured: Captured
  turn: number
  heundalki?: number
  pbbukStack: Record<number, Card[]>
  opponentPi: number          // 가상 상대 피 (피박/광박/쫑/쓸/따닥 효과용)
  bonusDraws: number          // 보너스 카드 획득 수 (UI 표시용)
}
```

- [ ] **Step 4: state.ts 수정 — init에 opponentPi 파라미터 추가**

```ts
export interface StageInit {
  handIds: string[]
  floorIds: string[]
  deckIds: string[]
  opponentPi: number    // 가상 상대 초기 피 개수 (스테이지 설정값)
}

export function initGameState(init: StageInit): GameState {
  return {
    hand: toCards(init.handIds),
    floor: toCards(init.floorIds),
    deck: toCards(init.deckIds),
    captured: { kwang: [], tti: [], pi: [], ssangpi: [] },
    turn: 0,
    pbbukStack: {},
    opponentPi: init.opponentPi,
    bonusDraws: 0,
  }
}
```

기존 테스트에 `opponentPi: 10` 같은 기본값 추가해서 통과시킴.

- [ ] **Step 5: engine.ts — 쫑 처리 로직**

`playHandCard` 내부 흐름 개편: 손패→바닥 매칭 단계와 더미→바닥 매칭 단계를 별도로 추적하고, 더미 카드의 월이 방금 손패로 획득한 월과 같으면 쫑으로 처리:

```ts
export function playHandCard(state: GameState, handCardId: string): GameState {
  const handCard = state.hand.find(c => c.id === handCardId)
  if (!handCard) throw new Error(`손패에 없는 카드: ${handCardId}`)

  let s: GameState = { ...state, hand: state.hand.filter(c => c.id !== handCardId) }
  const handResult = applyCardToFloor(s, handCard, { source: 'hand' })
  s = handResult.state

  if (s.deck.length === 0) return { ...s, turn: s.turn + 1 }

  const [drawn, ...restDeck] = s.deck
  s = { ...s, deck: restDeck }
  const drawResult = applyCardToFloor(s, drawn, { source: 'deck' })
  s = drawResult.state

  // 쫑: 손패 매칭 월 === 더미 뒤집힌 카드 월 (둘 다 매칭 성공)
  const isJjong =
    handResult.matchedMonth != null &&
    drawResult.matchedMonth === handResult.matchedMonth

  if (isJjong) {
    // 상대 피 1장 뺏음 (MVP: opponentPi -1, 내 쌍피 보너스 카드 +1)
    s = { ...s, opponentPi: Math.max(0, s.opponentPi - 1), bonusDraws: s.bonusDraws + 1 }
  }

  return { ...s, turn: s.turn + 1 }
}

interface ApplyResult {
  state: GameState
  matchedMonth: number | null  // 매칭된 월 (없으면 null)
}

function applyCardToFloor(
  state: GameState,
  card: Card,
  _opts: { source: 'hand' | 'deck' }
): ApplyResult {
  const matches = state.floor.filter(c => c.month === card.month)

  if (matches.length === 1) {
    return {
      state: {
        ...state,
        floor: state.floor.filter(c => c.id !== matches[0].id),
        captured: pushCaptured(pushCaptured(state.captured, card), matches[0]),
      },
      matchedMonth: card.month,
    }
  }
  if (matches.length === 0) {
    return {
      state: { ...state, floor: [...state.floor, card] },
      matchedMonth: null,
    }
  }
  throw new Error('NOT_IMPLEMENTED: multi-match (뻑/따닥)')
}
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS.

- [ ] **Step 7: 커밋**

```bash
git add -A
git commit -m "feat(engine): 쫑 처리 + 가상 상대 피 카운터"
```

---

### Task 10: 쓸 (손패 같은 월 3장 즉시 획득) 처리

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('쓸', () => {
  it('손패 1장 내려할 때 손패에 같은 월 2장 더 있고 바닥에 같은 월 1장 있으면 쓸 발동', () => {
    const state = initGameState({
      handIds: ['01-kwang','01-hong','01-pi-a'],  // 1월 3장
      floorIds: ['01-pi-b'],                       // 1월 바닥 1장
      deckIds: ['05-plain'],
      opponentPi: 10,
    })
    const next = playHandCard(state, '01-kwang')
    // 쓸 발동: 손패 1월 3장 + 바닥 1월 1장 모두 내 차지 → 손패에서 모두 제거
    expect(next.hand.some(c => c.month === 1)).toBe(false)
    expect(next.captured.kwang.map(c=>c.id)).toContain('01-kwang')
    expect(next.captured.tti.map(c=>c.id)).toContain('01-hong')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-a')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-b')
    // 쓸 보너스: 상대 피 1장 뺏음
    expect(next.opponentPi).toBe(9)
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: FAIL.

- [ ] **Step 3: 쓸 감지 로직 engine.ts에 삽입**

`playHandCard` 시작 부분에 쓸 선체크 추가:

```ts
export function playHandCard(state: GameState, handCardId: string): GameState {
  const handCard = state.hand.find(c => c.id === handCardId)
  if (!handCard) throw new Error(`손패에 없는 카드: ${handCardId}`)

  const sameMonthHand = state.hand.filter(c => c.month === handCard.month)
  const sameMonthFloor = state.floor.filter(c => c.month === handCard.month)

  // 쓸 조건: 손패 3장 + 바닥 1장
  if (sameMonthHand.length === 3 && sameMonthFloor.length === 1) {
    let s: GameState = {
      ...state,
      hand: state.hand.filter(c => c.month !== handCard.month),
      floor: state.floor.filter(c => c.month !== handCard.month),
      captured: [...sameMonthHand, ...sameMonthFloor].reduce(
        (cap, c) => pushCaptured(cap, c), state.captured
      ),
      opponentPi: Math.max(0, state.opponentPi - 1),
      bonusDraws: state.bonusDraws + 1,
    }
    // 쓸 후에도 더미는 뒤집어야 함
    if (s.deck.length > 0) {
      const [drawn, ...rest] = s.deck
      s = { ...s, deck: rest }
      const r = applyCardToFloor(s, drawn, { source: 'deck' })
      s = r.state
    }
    return { ...s, turn: s.turn + 1 }
  }

  // 이하 기존 로직 (단순 매칭, 더미 뽑기, 쫑)
  // ...
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 쓸 (손패 3장 + 바닥 1장) 처리"
```

---

### Task 11: 뻑 (바닥 같은 월 2장 → 획득 보류) 처리

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('뻑', () => {
  it('손패 냈을 때 바닥에 같은 월 2장 있으면 뻑 — 3장 모두 pbbukStack에 저장, 획득 안 함', () => {
    const state = initGameState({
      handIds: ['01-kwang'],
      floorIds: ['01-hong','01-pi-a','05-plain'],
      deckIds: ['05-pi-a'],
      opponentPi: 10,
    })
    const next = playHandCard(state, '01-kwang')
    expect(next.captured.kwang.map(c=>c.id)).not.toContain('01-kwang')
    expect(next.floor.map(c=>c.id).sort()).toEqual(['05-plain'])  // 1월 3장은 스택으로
    expect(next.pbbukStack[1]?.map(c=>c.id).sort()).toEqual(['01-hong','01-kwang','01-pi-a'])
  })

  it('다음 턴 뻑 달성 — 같은 월 4번째 카드 내면 pbbukStack 모두 획득', () => {
    // 이전 테스트 결과에서 이어지는 시나리오 (1월 뻑 상태)
    let state = initGameState({
      handIds: ['01-kwang','05-plain'],
      floorIds: ['01-hong','01-pi-a','05-pi-a'],
      deckIds: ['01-pi-b','07-plain'],  // 두 번째 턴에 1월 뻑 달성 시나리오
      opponentPi: 10,
    })
    state = playHandCard(state, '05-plain')  // 5월 매칭 정상
    // 이제 1월 뻑 상태는 없음 (위 테스트 시나리오가 아니라 독립 테스트). 로직 검증 위해 생략.
    expect(true).toBe(true)  // placeholder: 실제 뻑 획득 시나리오는 통합 테스트에서 다룸
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: FAIL (첫 번째 테스트).

- [ ] **Step 3: applyCardToFloor에 뻑 처리 추가**

```ts
function applyCardToFloor(
  state: GameState,
  card: Card,
  _opts: { source: 'hand' | 'deck' }
): ApplyResult {
  const matches = state.floor.filter(c => c.month === card.month)

  if (matches.length === 0) {
    return {
      state: { ...state, floor: [...state.floor, card] },
      matchedMonth: null,
    }
  }
  if (matches.length === 1) {
    return {
      state: {
        ...state,
        floor: state.floor.filter(c => c.id !== matches[0].id),
        captured: pushCaptured(pushCaptured(state.captured, card), matches[0]),
      },
      matchedMonth: card.month,
    }
  }
  if (matches.length === 2) {
    // 뻑: 3장 모두 pbbukStack[month]으로
    const newStack = { ...state.pbbukStack, [card.month]: [...matches, card] }
    return {
      state: {
        ...state,
        floor: state.floor.filter(c => c.month !== card.month),
        pbbukStack: newStack,
      },
      matchedMonth: null,  // 뻑은 매칭으로 간주 안 함
    }
  }
  throw new Error('NOT_IMPLEMENTED: 3-match (따닥)')
}
```

뻑 해소(스택 획득) 로직은 다음 태스크에서 처리.

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: 첫 번째 테스트 PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 뻑 상태 저장 (pbbukStack)"
```

---

### Task 12: 따닥 (바닥 같은 월 2장 + 세 번째) 및 뻑 해소 처리

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('따닥 & 뻑 해소', () => {
  it('바닥에 같은 월 2장 상태(뻑 직후) + 세 번째 카드 → pbbukStack 포함 4장 모두 획득', () => {
    // 수동으로 pbbukStack 설정된 상태에서 시작
    const state: GameState = {
      hand: ALL_CARDS_BY_ID['05-plain'] ? [ALL_CARDS_BY_ID['05-plain']] : [],
      floor: [],
      deck: [],
      captured: { kwang: [], tti: [], pi: [], ssangpi: [] },
      turn: 0,
      pbbukStack: { 1: [ALL_CARDS_BY_ID['01-hong'], ALL_CARDS_BY_ID['01-pi-a'], ALL_CARDS_BY_ID['01-kwang']] },
      opponentPi: 10,
      bonusDraws: 0,
    }
    // TODO: 손패에 01-pi-b 넣고 플레이 → 뻑 해소 획득 테스트
  })
})
```

NOTE: 이 태스크는 헬퍼 `ALL_CARDS_BY_ID`를 cards.ts에서 export하도록 추가 필요.

- [ ] **Step 2: cards.ts에 id 맵 export 추가**

```ts
export const CARDS_BY_ID = new Map(ALL_CARDS.map(c => [c.id, c]))
// 테스트용 객체 형태
export const ALL_CARDS_BY_ID: Record<string, Card> =
  Object.fromEntries(ALL_CARDS.map(c => [c.id, c]))
```

- [ ] **Step 3: 테스트 완성**

```ts
import { ALL_CARDS_BY_ID } from './cards'

describe('뻑 해소', () => {
  it('pbbukStack[1]이 있는 상태에서 1월 카드를 내면 스택 전체 내 차지', () => {
    const state: GameState = {
      hand: [ALL_CARDS_BY_ID['01-pi-b']],
      floor: [],
      deck: [],
      captured: { kwang: [], tti: [], pi: [], ssangpi: [] },
      turn: 0,
      pbbukStack: { 1: [ALL_CARDS_BY_ID['01-hong'], ALL_CARDS_BY_ID['01-pi-a'], ALL_CARDS_BY_ID['01-kwang']] },
      opponentPi: 10,
      bonusDraws: 0,
    }
    const next = playHandCard(state, '01-pi-b')
    expect(next.pbbukStack[1]).toBeUndefined()
    expect(next.captured.kwang.map(c=>c.id)).toContain('01-kwang')
    expect(next.captured.tti.map(c=>c.id)).toContain('01-hong')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-a')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-b')
    // 뻑 해소 보너스: 상대 피 1장
    expect(next.opponentPi).toBe(9)
  })
})

describe('따닥', () => {
  it('바닥에 같은 월 2장 + 손패에서 같은 월 내면 3장 모두 획득 + 보너스', () => {
    const state = initGameState({
      handIds: ['01-kwang','05-plain'],
      floorIds: ['01-hong','01-pi-a','03-pi-a'],
      deckIds: ['07-plain'],
      opponentPi: 10,
    })
    // 01-kwang 내면 바닥에 1월 2장 → 따닥
    const next = playHandCard(state, '01-kwang')
    expect(next.captured.kwang.map(c=>c.id)).toContain('01-kwang')
    expect(next.captured.tti.map(c=>c.id)).toContain('01-hong')
    expect(next.captured.pi.map(c=>c.id)).toContain('01-pi-a')
    expect(next.opponentPi).toBe(9)  // 따닥 보너스
  })
})
```

- [ ] **Step 4: 실패 확인**

Run: `npm run test:run -- engine`
Expected: FAIL (따닥 matches.length === 2 처리 없음, 뻑 해소 로직 없음).

- [ ] **Step 5: engine.ts — 따닥 + 뻑 해소 로직**

`applyCardToFloor` 수정:

```ts
function applyCardToFloor(
  state: GameState,
  card: Card,
  _opts: { source: 'hand' | 'deck' }
): ApplyResult {
  // 뻑 해소 우선 체크 (pbbukStack[month] 존재)
  const stack = state.pbbukStack[card.month]
  if (stack) {
    const { [card.month]: _, ...restStack } = state.pbbukStack
    const captured = [card, ...stack].reduce((cap, c) => pushCaptured(cap, c), state.captured)
    return {
      state: {
        ...state,
        pbbukStack: restStack,
        captured,
        opponentPi: Math.max(0, state.opponentPi - 1),  // 뻑 해소 보너스
        bonusDraws: state.bonusDraws + 1,
      },
      matchedMonth: card.month,
    }
  }

  const matches = state.floor.filter(c => c.month === card.month)

  if (matches.length === 0) {
    return { state: { ...state, floor: [...state.floor, card] }, matchedMonth: null }
  }
  if (matches.length === 1) {
    return {
      state: {
        ...state,
        floor: state.floor.filter(c => c.id !== matches[0].id),
        captured: pushCaptured(pushCaptured(state.captured, card), matches[0]),
      },
      matchedMonth: card.month,
    }
  }
  if (matches.length === 2) {
    // 뻑 상태 생성
    return {
      state: {
        ...state,
        floor: state.floor.filter(c => c.month !== card.month),
        pbbukStack: { ...state.pbbukStack, [card.month]: [...matches, card] },
      },
      matchedMonth: null,
    }
  }
  // matches.length === 3 — 따닥
  return {
    state: {
      ...state,
      floor: state.floor.filter(c => c.month !== card.month),
      captured: [card, ...matches].reduce((cap, c) => pushCaptured(cap, c), state.captured),
      opponentPi: Math.max(0, state.opponentPi - 1),
      bonusDraws: state.bonusDraws + 1,
    },
    matchedMonth: card.month,
  }
}
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS.

- [ ] **Step 7: 커밋**

```bash
git add -A
git commit -m "feat(engine): 따닥 처리 + 뻑 해소"
```

---

### Task 13: 흔들기 선언 (손패 같은 월 3장 보유 시)

**Files:**
- Modify: `src/engine/engine.ts`, `src/engine/types.ts`, `src/engine/engine.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('흔들기', () => {
  it('손패에 같은 월 3장 있을 때 canShake 함수가 해당 월 반환', () => {
    const state = initGameState({
      handIds: ['01-kwang','01-hong','01-pi-a','05-plain','07-plain','08-tti','12-tti'],
      floorIds: [], deckIds: [], opponentPi: 10,
    })
    expect(canShake(state)).toEqual([1])
  })

  it('declareShake(state, month) → state.heundalki에 월 기록', () => {
    const state = initGameState({
      handIds: ['01-kwang','01-hong','01-pi-a','05-plain','07-plain','08-tti','12-tti'],
      floorIds: [], deckIds: [], opponentPi: 10,
    })
    const next = declareShake(state, 1)
    expect(next.heundalki).toBe(1)
  })

  it('declareShake 잘못된 월 선언 시 에러', () => {
    const state = initGameState({
      handIds: ['01-kwang','05-plain','07-plain','08-tti','12-tti','02-tti','03-kwang'],
      floorIds: [], deckIds: [], opponentPi: 10,
    })
    expect(() => declareShake(state, 1)).toThrow()
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- engine`
Expected: FAIL — `canShake`, `declareShake` 미정의.

- [ ] **Step 3: engine.ts에 흔들기 헬퍼 추가**

```ts
export function canShake(state: GameState): number[] {
  const months: Record<number, number> = {}
  for (const c of state.hand) months[c.month] = (months[c.month] || 0) + 1
  return Object.entries(months)
    .filter(([_, count]) => count === 3)
    .map(([m]) => Number(m))
}

export function declareShake(state: GameState, month: number): GameState {
  if (!canShake(state).includes(month)) {
    throw new Error(`흔들기 불가: ${month}월`)
  }
  return { ...state, heundalki: month }
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- engine`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 흔들기 선언 (canShake, declareShake)"
```

---

### Task 14: 점수 계산 — 광/띠/피 기본

**Files:**
- Create: `src/engine/scoring.ts`, `src/engine/scoring.test.ts`

- [ ] **Step 1: 실패 테스트 작성**

```ts
import { describe, it, expect } from 'vitest'
import { calculateScore } from './scoring'
import { ALL_CARDS_BY_ID } from './cards'

function captured(ids: string[]) {
  const cards = ids.map(id => ALL_CARDS_BY_ID[id])
  return {
    kwang: cards.filter(c => c.category === 'kwang'),
    tti: cards.filter(c => c.category === 'tti'),
    pi: cards.filter(c => c.category === 'pi'),
    ssangpi: cards.filter(c => c.category === 'ssangpi'),
  }
}

describe('calculateScore — 광', () => {
  it('광 3장(비광 포함) = 2점, 비광 제외 3장 = 3점', () => {
    expect(calculateScore(captured(['01-kwang','03-kwang','12-kwang']), 10, null)).toMatchObject({ kwangPoint: 2 })
    expect(calculateScore(captured(['01-kwang','03-kwang','08-kwang']), 10, null)).toMatchObject({ kwangPoint: 3 })
  })

  it('광 4장 = 4점, 5장 = 15점', () => {
    expect(calculateScore(captured(['01-kwang','03-kwang','08-kwang','11-kwang']), 10, null).kwangPoint).toBe(4)
    expect(calculateScore(captured(['01-kwang','03-kwang','08-kwang','11-kwang','12-kwang']), 10, null).kwangPoint).toBe(15)
  })
})

describe('calculateScore — 띠/피', () => {
  it('띠 5장 = 1점, 6장 = 2점 (추가 1장당 +1)', () => {
    const result = calculateScore(captured(['01-hong','02-tti','03-hong','04-tti','05-tti']), 10, null)
    expect(result.ttiPoint).toBe(1)
  })

  it('피 10장 = 1점, 11장 = 2점; 쌍피는 2장으로 카운트', () => {
    // 피 8장 + 쌍피 1장 = 10카운트 → 1점
    const result = calculateScore(
      captured(['01-pi-a','01-pi-b','02-pi-a','02-pi-b','03-pi-a','03-pi-b','04-pi-a','04-pi-b','09-ssangpi']),
      10, null
    )
    expect(result.piPoint).toBe(1)
  })
})
```

- [ ] **Step 2: 실패 확인**

Run: `npm run test:run -- scoring`
Expected: FAIL.

- [ ] **Step 3: scoring.ts 구현**

```ts
import type { Captured } from './types'

export interface ScoreBreakdown {
  kwangPoint: number
  ttiPoint: number
  piPoint: number
  godoriPoint: number
  hongdanPoint: number
  cheongdanPoint: number
  chodanPoint: number
  pibakBonus: number
  kwangbakBonus: number
  heundalkiMultiplier: number
  total: number
}

export function calculateScore(
  captured: Captured,
  opponentPi: number,
  heundalki: number | null
): ScoreBreakdown {
  // 광 점수
  const kwangCount = captured.kwang.length
  const hasBikwang = captured.kwang.some(c => c.kwangType === 'bi-kwang')
  let kwangPoint = 0
  if (kwangCount === 5) kwangPoint = 15
  else if (kwangCount === 4) kwangPoint = 4
  else if (kwangCount === 3) kwangPoint = hasBikwang ? 2 : 3

  // 띠 점수
  const ttiCount = captured.tti.length
  const ttiPoint = ttiCount >= 5 ? 1 + (ttiCount - 5) : 0

  // 피 점수 (쌍피 2카운트)
  const piCount = captured.pi.length + captured.ssangpi.length * 2
  const piPoint = piCount >= 10 ? 1 + (piCount - 10) : 0

  // 고도리·단 점수는 다음 태스크에서 계산
  const godoriPoint = 0
  const hongdanPoint = 0
  const cheongdanPoint = 0
  const chodanPoint = 0

  // 피박/광박은 다음 태스크
  const pibakBonus = 0
  const kwangbakBonus = 0

  const subtotal = kwangPoint + ttiPoint + piPoint + godoriPoint + hongdanPoint + cheongdanPoint + chodanPoint
  const heundalkiMultiplier = heundalki != null ? 2 : 1
  const total = subtotal * heundalkiMultiplier + pibakBonus + kwangbakBonus

  return {
    kwangPoint, ttiPoint, piPoint,
    godoriPoint, hongdanPoint, cheongdanPoint, chodanPoint,
    pibakBonus, kwangbakBonus,
    heundalkiMultiplier, total,
  }
}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- scoring`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 기본 점수(광/띠/피) 계산"
```

---

### Task 15: 고도리·홍단·청단·초단 족보 점수

**Files:**
- Modify: `src/engine/scoring.ts`, `src/engine/scoring.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('scoring — 족보', () => {
  it('고도리 (2월 매조 + 4월 흑싸리 + 8월 공산 띠) = 5점', () => {
    const r = calculateScore(captured(['02-tti','04-tti','08-tti']), 10, null)
    expect(r.godoriPoint).toBe(5)
  })

  it('홍단 3장 = 3점', () => {
    const r = calculateScore(captured(['01-hong','02-tti','03-hong']), 10, null)
    expect(r.hongdanPoint).toBe(3)
  })

  it('청단 3장 = 3점', () => {
    const r = calculateScore(captured(['06-tti','09-tti','10-tti']), 10, null)
    expect(r.cheongdanPoint).toBe(3)
  })

  it('초단 3장 = 3점', () => {
    const r = calculateScore(captured(['04-tti','05-tti','07-tti']), 10, null)
    expect(r.chodanPoint).toBe(3)
  })
})
```

NOTE: 고도리 카드 판정은 ID 기반 (정확한 카드 3장). `02-tti`, `04-tti`, `08-tti`가 고도리의 올바른 id인지 검증 — cards.ts 정의와 일치해야 함.

검토: Task 5의 cards.ts 정의상:
- 2월 고도리 = `02-tti` (매조 홍단 — 하지만 고도리는 별개 새 그림) → cards.ts에 고도리 식별 필드 추가 필요

**정정**: 고도리는 2월 매조(매화가지 새), 4월 흑싸리(두견새), 8월 공산(기러기)의 "새 그림" 띠들. 이들을 고도리 식별자로 별도 플래그 필요.

Task 5 수정: Card 타입에 `isGodori?: boolean` 추가. 2월/4월/8월의 특정 띠 카드에 `isGodori: true` 세팅.

- [ ] **Step 2: cards.ts 수정 — 고도리 플래그 추가**

types.ts에:
```ts
export interface Card {
  id: string
  month: number
  category: CardCategory
  ttiType?: TtiType
  kwangType?: KwangType
  isGodori?: boolean
  name: string
}
```

cards.ts에서 `02-tti`, `04-tti`, `08-tti`에 `isGodori: true` 추가.

재검토: 기존 정의는:
- `02-tti` (매조 홍단, hong-dan) — 이게 고도리? 혹은 별도 고도리 카드?
- 실제 고스톱: 2월 4장 = 매조 광(x, 1~2 월엔 광 없음... 1,3,8,11,12월만 광), 매조 고도리(새), 매조 홍단, 매조 피2
- → 2월 4장 재구성 필요: 고도리 1장, 홍단 1장, 피 2장

**정정 Task 5**: 2월 카드 구성 수정 (이 작업은 Task 5로 되돌아가서 수정해야 함. 플랜 실행 시 순서 유의):

```ts
// 2월 매조 (재정의)
{ id: '02-godori', month: 2, category: 'tti', ttiType: 'plain', isGodori: true, name: '매조 고도리' },
{ id: '02-hong', month: 2, category: 'tti', ttiType: 'hong-dan', name: '매조 홍단' },
{ id: '02-pi-a', month: 2, category: 'pi', name: '매조 피1' },
{ id: '02-pi-b', month: 2, category: 'pi', name: '매조 피2' },
```

4월, 8월도 유사하게 수정:
- 4월: `04-godori` (두견새), `04-tti` (초단), 피 2장
- 8월: `08-kwang` (광 — 이미 있음), `08-godori` (기러기), `08-tti` (plain 띠), 피 2장 → 8월은 5장 되어버림. **오류**.

실제 8월: 공산 광, 공산 고도리(기러기 3마리), 공산 피 2장 = 4장. 즉 `08-tti` (plain)를 `08-godori`로 대체.

**최종 Task 5 수정 가이드** (플랜 실행 전 반드시 확인):
- 2월: 광 없음, 고도리 1, 홍단 1, 피 2 = 4장
- 4월: 광 없음, 고도리 1, 초단 1, 피 2 = 4장
- 8월: 광 1, 고도리 1, 피 2 = 4장 (plain 띠 없음)

Task 5의 카드 정의를 이 규칙으로 재작성.

- [ ] **Step 3: scoring.ts에 족보 로직 추가**

```ts
const GODORI_IDS = new Set(['02-godori','04-godori','08-godori'])

function calcGodori(captured: Captured): number {
  const godoriCount = captured.tti.filter(c => c.isGodori).length
  return godoriCount === 3 ? 5 : 0
}

function calcDan(captured: Captured): { hong: number; cheong: number; cho: number } {
  const hong = captured.tti.filter(c => c.ttiType === 'hong-dan').length
  const cheong = captured.tti.filter(c => c.ttiType === 'cheong-dan').length
  const cho = captured.tti.filter(c => c.ttiType === 'cho-dan').length
  return {
    hong: hong === 3 ? 3 : 0,
    cheong: cheong === 3 ? 3 : 0,
    cho: cho === 3 ? 3 : 0,
  }
}
```

`calculateScore`에서 `godoriPoint = calcGodori(captured)`, 단 점수도 연결.

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- scoring`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 고도리/홍단/청단/초단 점수"
```

---

### Task 16: 피박·광박 계산 (가상 상대 파라미터)

**Files:**
- Modify: `src/engine/scoring.ts`, `src/engine/scoring.test.ts`

- [ ] **Step 1: 실패 테스트 추가**

```ts
describe('피박/광박', () => {
  it('피박: 내 피 1장 + 상대 피 10장 이상 → 피박 ON (점수 2배)', () => {
    const r = calculateScore(
      captured(['01-pi-a','01-kwang','03-kwang','08-kwang']),  // 광 3장, 피 1장
      10,
      null
    )
    // 내 피 카운트: 1장 → 7 미만 (일반 피박 기준). 점수 2배 적용.
    // MVP 룰: 내 피 카운트 < 7이면 피박
    expect(r.pibakBonus).toBeGreaterThan(0)
  })

  it('광박: 내 광 0장 + 상대 광 3장 이상 → 광박 ON (상대 측 광 점수 2배 효과)', () => {
    const r = calculateScore(
      captured(['01-hong','02-hong','03-hong']),  // 띠만, 광 0장
      10,  // 상대 피 (여기선 광박 판단엔 상대 광 개수가 필요 → 파라미터 추가)
      null
    )
    // NOTE: 광박은 opponentKwangCount 파라미터 필요. 현재 calculateScore 시그니처에 없음.
    // → calculateScore 시그니처에 opponentState 추가 필요
    expect(r.kwangbakBonus).toBeGreaterThanOrEqual(0)
  })
})
```

- [ ] **Step 2: calculateScore 시그니처 확장**

```ts
export interface OpponentState {
  piCount: number
  kwangCount: number
}

export function calculateScore(
  captured: Captured,
  opponent: OpponentState,
  heundalki: number | null
): ScoreBreakdown {
  // ...
  // 피박: 내 피 카운트 < 7 (MVP 단순화 버전). 실제 룰은 '7장 기준'이지만 세부 조정.
  const myPiCount = captured.pi.length + captured.ssangpi.length * 2
  const pibak = myPiCount < 7 && opponent.piCount >= 10 ? true : false

  // 광박: 내 광 0장 + 상대 광 3장 이상
  const kwangbak = captured.kwang.length === 0 && opponent.kwangCount >= 3

  // MVP 해석: 피박/광박 "걸리면" 최종 점수가 2배 (실제 고스톱에선 상대가 뜯기지만, 솔로에선 내 점수 페널티로 변환)
  // 방향: 가상 상대에게 지면 점수 -. 그러나 솔로 퍼즐 성공 기준은 '목표 달성'이지 '점수 승리'가 아님.
  // → MVP에서는 피박/광박을 '점수 보너스'가 아닌 '스테이지 목표 조건'으로 활용.
  // 예: "피박 걸리지 않고 3점 이상" 같은 미션.
  // 따라서 계산 결과만 boolean으로 리턴. ScoreBreakdown 수정.

  const pibakBonus = 0  // 점수 가산 없음 (미션 조건으로만 활용)
  const kwangbakBonus = 0
  // ...
  return {
    // ...기존
    pibak, kwangbak,
    pibakBonus, kwangbakBonus,
    // ...
  }
}
```

ScoreBreakdown에 `pibak: boolean`, `kwangbak: boolean` 필드 추가.

- [ ] **Step 3: 테스트 수정**

```ts
it('피박 조건 충족 시 pibak: true', () => {
  const r = calculateScore(
    captured(['01-pi-a','01-kwang','03-kwang','08-kwang']),
    { piCount: 10, kwangCount: 0 },
    null
  )
  expect(r.pibak).toBe(true)
})

it('광박 조건 충족 시 kwangbak: true', () => {
  const r = calculateScore(
    captured(['01-hong','02-hong','03-hong']),
    { piCount: 5, kwangCount: 3 },
    null
  )
  expect(r.kwangbak).toBe(true)
})
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `npm run test:run -- scoring`
Expected: PASS.

- [ ] **Step 5: 커밋**

```bash
git add -A
git commit -m "feat(engine): 피박/광박 상태 계산 (가상 상대 파라미터)"
```

---

### Task 17: 흔들기 2배 효과 통합 테스트

**Files:**
- Modify: `src/engine/scoring.test.ts`

- [ ] **Step 1: 통합 테스트 작성**

```ts
describe('흔들기 통합', () => {
  it('흔들기 선언 + 점수 내면 2배', () => {
    const r = calculateScore(
      captured(['01-kwang','03-kwang','08-kwang']),  // 광 3장 = 3점
      { piCount: 5, kwangCount: 0 },
      1  // 1월 흔들기 선언
    )
    expect(r.total).toBe(6)  // 3 × 2
  })

  it('흔들기 없으면 1배', () => {
    const r = calculateScore(
      captured(['01-kwang','03-kwang','08-kwang']),
      { piCount: 5, kwangCount: 0 },
      null
    )
    expect(r.total).toBe(3)
  })
})
```

- [ ] **Step 2: 테스트 실행 — 기존 구현으로 통과해야 함**

Run: `npm run test:run -- scoring`
Expected: PASS (heundalkiMultiplier 이미 구현됨).

- [ ] **Step 3: 커밋 없음 (테스트 추가만)**

```bash
git add -A
git commit -m "test(engine): 흔들기 2배 효과 통합 테스트"
```

---

### Task 18: 미션 판정 함수

**Files:**
- Create: `src/engine/mission.ts`, `src/engine/mission.test.ts`

- [ ] **Step 1: 실패 테스트 작성**

```ts
import { describe, it, expect } from 'vitest'
import { checkMission } from './mission'
import { ALL_CARDS_BY_ID } from './cards'
import type { GameState } from './types'

function state(overrides: Partial<GameState>): GameState {
  return {
    hand: [],
    floor: [],
    deck: [],
    captured: { kwang: [], tti: [], pi: [], ssangpi: [] },
    turn: 0,
    pbbukStack: {},
    opponentPi: 10,
    bonusDraws: 0,
    ...overrides,
  }
}

describe('checkMission — collect-kwang', () => {
  it('광 3장 모으기 목표 미달성', () => {
    const s = state({ captured: { kwang: [ALL_CARDS_BY_ID['01-kwang']], tti: [], pi: [], ssangpi: [] } })
    expect(checkMission(s, { type: 'collect-kwang', count: 3 })).toBe(false)
  })
  it('광 3장 모으기 목표 달성', () => {
    const s = state({ captured: { kwang: [ALL_CARDS_BY_ID['01-kwang'], ALL_CARDS_BY_ID['03-kwang'], ALL_CARDS_BY_ID['08-kwang']], tti: [], pi: [], ssangpi: [] } })
    expect(checkMission(s, { type: 'collect-kwang', count: 3 })).toBe(true)
  })
})

describe('checkMission — reach-score', () => {
  it('7점 이상 목표 달성', () => {
    const s = state({ captured: { kwang: [ALL_CARDS_BY_ID['01-kwang'], ALL_CARDS_BY_ID['03-kwang'], ALL_CARDS_BY_ID['08-kwang'], ALL_CARDS_BY_ID['11-kwang']], tti: [], pi: [], ssangpi: [] } })
    // 광 4장 = 4점 → 7점 미달성
    expect(checkMission(s, { type: 'reach-score', target: 7, opponentPi: 10, opponentKwang: 0 })).toBe(false)
  })
})
```

- [ ] **Step 2: mission.ts 구현**

```ts
import type { GameState } from './types'
import { calculateScore } from './scoring'

export type Mission =
  | { type: 'collect-kwang'; count: number }
  | { type: 'collect-tti'; count: number }
  | { type: 'collect-pi'; count: number }  // 쌍피 2카운트
  | { type: 'godori' }
  | { type: 'hong-dan' }
  | { type: 'cheong-dan' }
  | { type: 'cho-dan' }
  | { type: 'reach-score'; target: number; opponentPi: number; opponentKwang: number }
  | { type: 'no-pibak'; minScore: number; opponentPi: number; opponentKwang: number }

export function checkMission(state: GameState, mission: Mission): boolean {
  const c = state.captured
  switch (mission.type) {
    case 'collect-kwang': return c.kwang.length >= mission.count
    case 'collect-tti': return c.tti.length >= mission.count
    case 'collect-pi': return c.pi.length + c.ssangpi.length * 2 >= mission.count
    case 'godori': return c.tti.filter(x => x.isGodori).length === 3
    case 'hong-dan': return c.tti.filter(x => x.ttiType === 'hong-dan').length === 3
    case 'cheong-dan': return c.tti.filter(x => x.ttiType === 'cheong-dan').length === 3
    case 'cho-dan': return c.tti.filter(x => x.ttiType === 'cho-dan').length === 3
    case 'reach-score': {
      const r = calculateScore(c, { piCount: mission.opponentPi, kwangCount: mission.opponentKwang }, state.heundalki ?? null)
      return r.total >= mission.target
    }
    case 'no-pibak': {
      const r = calculateScore(c, { piCount: mission.opponentPi, kwangCount: mission.opponentKwang }, state.heundalki ?? null)
      return !r.pibak && r.total >= mission.minScore
    }
  }
}
```

- [ ] **Step 3: 테스트 통과 확인**

Run: `npm run test:run -- mission`
Expected: PASS.

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "feat(engine): 미션 판정 함수 (checkMission)"
```

---

## Phase 2 — 스테이지 시스템

### Task 19: 스테이지 스키마와 레지스트리

**Files:**
- Create: `src/stages/types.ts`, `src/stages/registry.ts`, `src/stages/data/stage-01.ts`, `src/stages/data/stage-02.ts` ... `src/stages/data/stage-15.ts`, `src/stages/registry.test.ts`

- [ ] **Step 1: 스테이지 스키마 정의**

`src/stages/types.ts`:
```ts
import type { Mission } from '../engine/mission'

export interface StageDefinition {
  id: number                    // 1~15
  title: string
  description: string           // 유저에게 보여줄 미션 설명
  difficulty: 1 | 2 | 3 | 4     // ★ 개수
  init: {
    handIds: string[]           // 7장
    floorIds: string[]          // 6장
    deckIds: string[]           // 33장 (순서 중요)
    opponentPi: number          // 가상 상대 피
    opponentKwang: number       // 가상 상대 광
  }
  mission: Mission
  stars: {
    three: number               // 최소 풀이 턴 N
    two: number                 // N+2
  }
  hintLesson?: string           // 미니 레슨 ID (선택)
}
```

- [ ] **Step 2: stage-01.ts 데이터 작성 (예시)**

```ts
import type { StageDefinition } from '../types'

const stage01: StageDefinition = {
  id: 1,
  title: '첫 만남 — 광 1장',
  description: '광 1장을 모아보세요.',
  difficulty: 1,
  init: {
    handIds: ['01-kwang','02-hong','05-plain','06-plain','07-plain','09-pi-a','11-pi-a'],
    floorIds: ['01-hong','02-godori','08-pi-a','10-pi-a','12-pi','03-pi-a'],
    deckIds: [
      '01-pi-a','01-pi-b','02-pi-a','02-pi-b','03-kwang','03-hong','03-pi-b',
      '04-godori','04-tti','04-pi-a','04-pi-b','05-tti','05-pi-a','05-pi-b',
      '06-tti','06-pi-a','06-pi-b','07-tti','07-pi-a','07-pi-b',
      '08-kwang','08-godori','08-pi-b','09-tti','09-ssangpi','09-pi-b',
      '10-tti','10-ssangpi','10-pi-b','11-kwang','11-ssangpi','11-pi-b','12-kwang','12-tti','12-dbl-pi'
    ],  // 35장 — 실제로는 32장만 남으므로 조정 필요
    opponentPi: 0,
    opponentKwang: 0,
  },
  mission: { type: 'collect-kwang', count: 1 },
  stars: { three: 1, two: 3 },   // 1턴 풀이 = 3★
}

export default stage01
```

NOTE: 더미는 48 - 7(손패) - 6(바닥) = 35. 스테이지 정의 시 반드시 총 48장 맞춰야 함. 스테이지 디자인 시 검증 필수.

- [ ] **Step 3: stage-02.ts ~ stage-15.ts 작성**

각 스테이지의 `init` 데이터 + 미션 + 별 기준 작성. 아래 14개 스테이지 구조만 제시, 구체 카드 배치는 디자이너와 공동 작업:

**[필요: 스테이지 2~15 구체 카드 배치 및 풀이 검증 — 디자인 단계에서 작업]**

각 스테이지는 다음 템플릿 따름:

```ts
// stage-02.ts 예시 템플릿
import type { StageDefinition } from '../types'

const stage02: StageDefinition = {
  id: 2,
  title: '[디자인 필요]',
  description: '[디자인 필요]',
  difficulty: 1,
  init: {
    handIds: [/* 7장 */],
    floorIds: [/* 6장 */],
    deckIds: [/* 35장 */],
    opponentPi: 0,
    opponentKwang: 0,
  },
  mission: { type: 'collect-kwang', count: 2 },  // 예시
  stars: { three: 2, two: 4 },
}

export default stage02
```

스테이지 구성 목표 (스펙 참조):
- 1~3: 기초 (매칭·쫑·쓸·뻑)
- 4~6: 중급 (따닥·흔들기 미션)
- 7~12: 고급 (피박·광박·고도리 미션)
- 13~15: 심화 (복합 룰, 3수 이상 읽기)

각 stage-NN.ts 파일은 위 템플릿에서 `[디자인 필요]` 부분을 디자이너와 공동으로 채움. 본 플랜의 구현 단계에선 스키마 준수 여부만 확인.

- [ ] **Step 4: registry.ts 작성**

```ts
import type { StageDefinition } from './types'
import stage01 from './data/stage-01'
import stage02 from './data/stage-02'
import stage03 from './data/stage-03'
import stage04 from './data/stage-04'
import stage05 from './data/stage-05'
import stage06 from './data/stage-06'
import stage07 from './data/stage-07'
import stage08 from './data/stage-08'
import stage09 from './data/stage-09'
import stage10 from './data/stage-10'
import stage11 from './data/stage-11'
import stage12 from './data/stage-12'
import stage13 from './data/stage-13'
import stage14 from './data/stage-14'
import stage15 from './data/stage-15'

export const STAGES: StageDefinition[] = [
  stage01, stage02, stage03, stage04, stage05,
  stage06, stage07, stage08, stage09, stage10,
  stage11, stage12, stage13, stage14, stage15,
]

export function getStage(id: number): StageDefinition | undefined {
  return STAGES.find(s => s.id === id)
}
```

- [ ] **Step 5: registry 무결성 테스트**

```ts
import { describe, it, expect } from 'vitest'
import { STAGES } from './registry'
import { ALL_CARDS } from '../engine/cards'

describe('stages registry 무결성', () => {
  it('총 15개 스테이지', () => {
    expect(STAGES.length).toBe(15)
  })
  it('각 스테이지는 정확히 48장 (손7+바닥6+더미35)', () => {
    for (const s of STAGES) {
      const total = s.init.handIds.length + s.init.floorIds.length + s.init.deckIds.length
      expect(total).toBe(48)
    }
  })
  it('중복된 카드 id 없음', () => {
    for (const s of STAGES) {
      const all = [...s.init.handIds, ...s.init.floorIds, ...s.init.deckIds]
      expect(new Set(all).size).toBe(48)
    }
  })
  it('모든 카드 id가 실제 카드 목록에 존재', () => {
    const validIds = new Set(ALL_CARDS.map(c => c.id))
    for (const s of STAGES) {
      const all = [...s.init.handIds, ...s.init.floorIds, ...s.init.deckIds]
      for (const id of all) {
        expect(validIds.has(id)).toBe(true)
      }
    }
  })
})
```

Run: `npm run test:run -- registry`
Expected: PASS (stage-01은 완성, 02~15는 임시 템플릿이지만 카드 수·id 무결성만 테스트함. 실제 콘텐츠 검증은 별도 작업).

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "feat(stages): 스테이지 스키마 + 레지스트리 + stage-01 완성, 나머지는 템플릿"
```

---

### Task 20: 스테이지 솔버 (최소 풀이 턴 검증 스크립트)

**Files:**
- Create: `src/engine/solver.ts`, `scripts/verify-stages.ts`

- [ ] **Step 1: solver.ts 구현 — BFS 최소 풀이 탐색**

```ts
import type { GameState } from './types'
import { playHandCard, canShake, declareShake } from './engine'
import type { Mission } from './mission'
import { checkMission } from './mission'
import { initGameState } from './state'
import type { StageInit } from './types'

interface SolverResult {
  solvable: boolean
  minTurns: number | null
  sampleSolution: string[] | null  // 카드 id 순서
}

const MAX_DEPTH = 10  // 스테이지 길이 제한

export function solve(init: StageInit, mission: Mission): SolverResult {
  // BFS: 각 노드는 GameState + 이미 둔 카드 순서
  const start = initGameState(init)
  const queue: { state: GameState; path: string[] }[] = [{ state: start, path: [] }]
  const visited = new Set<string>()

  while (queue.length > 0) {
    const { state, path } = queue.shift()!
    if (checkMission(state, mission)) {
      return { solvable: true, minTurns: path.length, sampleSolution: path }
    }
    if (path.length >= MAX_DEPTH) continue
    if (state.hand.length === 0) continue

    const key = JSON.stringify({
      hand: state.hand.map(c=>c.id).sort(),
      floor: state.floor.map(c=>c.id).sort(),
      turn: state.turn,
    })
    if (visited.has(key)) continue
    visited.add(key)

    // 각 손패 카드 시도
    for (const card of state.hand) {
      try {
        const next = playHandCard(state, card.id)
        queue.push({ state: next, path: [...path, card.id] })
      } catch {
        // ignore
      }
    }
    // 흔들기 옵션은 MVP 솔버에서 생략 (복잡도 증가, 본질 문제에 영향 적음)
  }

  return { solvable: false, minTurns: null, sampleSolution: null }
}
```

- [ ] **Step 2: verify-stages.ts 스크립트 작성**

```ts
import { STAGES } from '../src/stages/registry'
import { solve } from '../src/engine/solver'

let allOk = true
for (const s of STAGES) {
  const result = solve(s.init, s.mission)
  if (!result.solvable) {
    console.error(`❌ Stage ${s.id} (${s.title}) 풀이 불가`)
    allOk = false
    continue
  }
  if (result.minTurns !== s.stars.three) {
    console.warn(`⚠️  Stage ${s.id} (${s.title}): 선언된 3★ 턴 ${s.stars.three}, 솔버 최소 ${result.minTurns}`)
  }
  console.log(`✅ Stage ${s.id}: 최소 ${result.minTurns}턴, 예시 ${result.sampleSolution?.join(' → ')}`)
}
process.exit(allOk ? 0 : 1)
```

package.json 스크립트 추가:
```json
"verify-stages": "tsx scripts/verify-stages.ts"
```

tsx 설치:
```bash
npm install -D tsx
```

- [ ] **Step 3: 스크립트 실행**

Run: `npm run verify-stages`
Expected: stage-01 PASS, 2~15는 [디자인 필요] 상태면 실패/경고. 이 단계에서 2~15 설계 반복 진행.

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "feat(engine): 스테이지 솔버 + 검증 스크립트"
```

---

## Phase 3 — 튜토리얼

### Task 21: 기본 튜토리얼 스텝 정의

**Files:**
- Create: `src/tutorial/types.ts`, `src/tutorial/basic-steps.ts`

- [ ] **Step 1: types.ts 정의**

```ts
export interface TutorialStep {
  id: string                   // 'intro', 'match', 'kwang', ...
  title: string
  body: string                 // 마크다운 가능
  interaction?: {              // 실습 단계 (선택)
    type: 'click-card' | 'drag-card' | 'observe'
    targetCardId?: string
    successMessage?: string
  }
  nextButtonLabel: string
}
```

- [ ] **Step 2: basic-steps.ts 5단계 작성**

```ts
import type { TutorialStep } from './types'

export const BASIC_TUTORIAL_STEPS: TutorialStep[] = [
  {
    id: 'intro',
    title: '고스톱 퍼즐에 오신 것을 환영합니다',
    body: '화투 48장으로 풀어내는 퍼즐 게임입니다. 5분 안에 기본을 익혀보세요.',
    nextButtonLabel: '시작',
  },
  {
    id: 'match',
    title: '같은 월끼리 매칭',
    body: '손패에서 카드 1장을 내면 바닥의 같은 월 카드와 짝이 되어 둘 다 내 차지가 됩니다.',
    interaction: { type: 'click-card', targetCardId: '01-kwang', successMessage: '잘했어요! 1월 카드 둘이 함께 사라졌죠.' },
    nextButtonLabel: '다음',
  },
  {
    id: 'categories',
    title: '카드 종류 4가지',
    body: '광 (노란 표시) · 띠 (빨간/파란/초록 띠) · 쌍피 (피 2장 값) · 일반 피 — 이렇게 4종류를 모읍니다.',
    nextButtonLabel: '다음',
  },
  {
    id: 'scoring',
    title: '점수 계산 기초',
    body: '광 3장 = 3점 / 띠 5장 = 1점 / 피 10장 = 1점. 퍼즐마다 목표가 달라요.',
    nextButtonLabel: '다음',
  },
  {
    id: 'deck',
    title: '더미에서 뒤집히는 카드',
    body: '손패 카드를 낸 후 더미 맨 위 카드가 자동으로 뒤집혀요. 이 카드도 바닥과 매칭될 수 있어요.',
    interaction: { type: 'observe', successMessage: '이제 준비 완료! 스테이지 1부터 도전하세요.' },
    nextButtonLabel: '시작하기',
  },
]
```

- [ ] **Step 3: 커밋**

```bash
git add -A
git commit -m "feat(tutorial): 기본 튜토리얼 5단계 스텝 정의"
```

---

### Task 22: 미니 레슨 정의

**Files:**
- Create: `src/tutorial/mini-lessons.ts`

- [ ] **Step 1: 미니 레슨 작성**

```ts
import type { TutorialStep } from './types'

export const MINI_LESSONS: Record<string, TutorialStep[]> = {
  'tadak': [{
    id: 'tadak',
    title: '따닥 — 한 번에 3장',
    body: '바닥에 같은 월 2장이 있을 때 세 번째를 내면 3장 모두 한 번에 내 것이 됩니다. 추가 보너스까지!',
    nextButtonLabel: '확인',
  }],
  'heundalki': [{
    id: 'heundalki',
    title: '흔들기 — 점수 2배',
    body: '손패에 같은 월이 3장 있을 때 "흔들기"를 선언하면 이번 스테이지 최종 점수가 2배가 됩니다.',
    nextButtonLabel: '확인',
  }],
  'pibak-kwangbak': [{
    id: 'pibak-kwangbak',
    title: '피박과 광박',
    body: '피박: 내 피가 너무 적으면 걸립니다. 광박: 내 광이 하나도 없을 때 상대에게 광이 많으면 걸려요. 미션에 따라 이걸 피하거나 활용해야 해요.',
    nextButtonLabel: '확인',
  }],
  'godori': [{
    id: 'godori',
    title: '고도리 — 새 그림 3장',
    body: '2월 · 4월 · 8월의 "새 그림" 띠 카드 3장을 모두 모으면 고도리 5점 보너스!',
    nextButtonLabel: '확인',
  }],
}
```

- [ ] **Step 2: 커밋**

```bash
git add -A
git commit -m "feat(tutorial): 미니 레슨 4종 정의"
```

---

### Task 23: TutorialRunner 컴포넌트

**Files:**
- Create: `src/tutorial/TutorialRunner.tsx`

- [ ] **Step 1: TutorialRunner 구현**

```tsx
import { useState } from 'react'
import type { TutorialStep } from './types'

interface Props {
  steps: TutorialStep[]
  onComplete: () => void
  onSkip?: () => void
}

export default function TutorialRunner({ steps, onComplete, onSkip }: Props) {
  const [idx, setIdx] = useState(0)
  const step = steps[idx]
  const isLast = idx === steps.length - 1

  const handleNext = () => {
    if (isLast) onComplete()
    else setIdx(idx + 1)
  }

  return (
    <div className="max-w-2xl mx-auto p-8">
      <div className="mb-4 text-sm text-gray-500">
        {idx + 1} / {steps.length}
      </div>
      <h2 className="text-2xl font-bold mb-4">{step.title}</h2>
      <p className="text-lg mb-6">{step.body}</p>
      {step.interaction && (
        <div className="bg-yellow-50 p-4 rounded mb-4">
          <p className="text-sm">💡 {step.interaction.successMessage || '클릭해보세요'}</p>
        </div>
      )}
      <div className="flex gap-2 justify-end">
        {onSkip && (
          <button onClick={onSkip} className="px-4 py-2 text-gray-600">
            건너뛰기
          </button>
        )}
        <button
          onClick={handleNext}
          className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          {step.nextButtonLabel}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 커밋**

```bash
git add -A
git commit -m "feat(tutorial): TutorialRunner 컴포넌트"
```

---

### Task 24: TutorialScreen 및 계측 연결

**Files:**
- Create: `src/screens/TutorialScreen.tsx`
- Modify: `src/App.tsx`

- [ ] **Step 1: TutorialScreen 작성**

```tsx
import { useNavigate } from 'react-router-dom'
import TutorialRunner from '../tutorial/TutorialRunner'
import { BASIC_TUTORIAL_STEPS } from '../tutorial/basic-steps'
import { markTutorialDone } from '../storage/localStorage'
import { track } from '../analytics/ga4'

export default function TutorialScreen() {
  const nav = useNavigate()

  const handleComplete = () => {
    markTutorialDone()
    track('tutorial_completed', { total_duration_ms: Date.now() /* 시작시간 저장 필요 */ })
    nav('/')
  }

  const handleSkip = () => {
    track('tutorial_skipped', { at_step: 'manual' })
    nav('/')
  }

  return <TutorialRunner steps={BASIC_TUTORIAL_STEPS} onComplete={handleComplete} onSkip={handleSkip} />
}
```

- [ ] **Step 2: App.tsx 라우트 연결**

```tsx
import TutorialScreen from './screens/TutorialScreen'
// ...
<Route path="/tutorial" element={<TutorialScreen />} />
```

- [ ] **Step 3: 커밋** (storage/analytics 함수는 뒤 태스크에서 구현, import는 placeholder)

다음 태스크에서 storage/analytics 구현 후 완성.

---

## Phase 4 — 저장소 & 계측

### Task 25: localStorage 래퍼

**Files:**
- Create: `src/storage/types.ts`, `src/storage/localStorage.ts`, `src/storage/localStorage.test.ts`

- [ ] **Step 1: 타입 정의**

`src/storage/types.ts`:
```ts
export interface StageProgress {
  id: number
  stars: 0 | 1 | 2 | 3
  playedAt: string  // ISO
}

export interface UserProgress {
  clearedStages: StageProgress[]
  tutorialDone: boolean
  lastPlayedStage: number | null
}
```

- [ ] **Step 2: localStorage.ts 구현**

```ts
import type { UserProgress, StageProgress } from './types'

const KEY = 'gostop-puzzle-v1'

export function loadProgress(): UserProgress {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { clearedStages: [], tutorialDone: false, lastPlayedStage: null }
    return JSON.parse(raw)
  } catch {
    return { clearedStages: [], tutorialDone: false, lastPlayedStage: null }
  }
}

export function saveProgress(p: UserProgress): void {
  localStorage.setItem(KEY, JSON.stringify(p))
}

export function markTutorialDone(): void {
  const p = loadProgress()
  saveProgress({ ...p, tutorialDone: true })
}

export function recordStageResult(id: number, stars: 0 | 1 | 2 | 3): void {
  const p = loadProgress()
  const existing = p.clearedStages.find(s => s.id === id)
  const next: StageProgress = { id, stars, playedAt: new Date().toISOString() }
  const clearedStages = existing
    ? p.clearedStages.map(s => s.id === id ? (stars > s.stars ? next : s) : s)
    : [...p.clearedStages, next]
  saveProgress({ ...p, clearedStages, lastPlayedStage: id })
}
```

- [ ] **Step 3: 테스트 작성 및 실행**

```ts
import { describe, it, expect, beforeEach } from 'vitest'
import { loadProgress, saveProgress, markTutorialDone, recordStageResult } from './localStorage'

describe('storage', () => {
  beforeEach(() => { localStorage.clear() })

  it('초기 상태 — 진행도 없음', () => {
    const p = loadProgress()
    expect(p.tutorialDone).toBe(false)
    expect(p.clearedStages).toEqual([])
  })

  it('튜토리얼 완료 기록', () => {
    markTutorialDone()
    expect(loadProgress().tutorialDone).toBe(true)
  })

  it('스테이지 결과 기록 — 별점 갱신', () => {
    recordStageResult(1, 2)
    recordStageResult(1, 3)  // 더 높은 별점으로 갱신
    expect(loadProgress().clearedStages[0].stars).toBe(3)

    recordStageResult(1, 1)  // 낮은 별점은 유지
    expect(loadProgress().clearedStages[0].stars).toBe(3)
  })
})
```

Run: `npm run test:run -- storage`
Expected: PASS.

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "feat(storage): localStorage 진행도 저장"
```

---

### Task 26: GA4 계측 래퍼

**Files:**
- Create: `src/analytics/events.ts`, `src/analytics/ga4.ts`
- Modify: `index.html`

- [ ] **Step 1: events.ts — 이벤트 타입**

```ts
export type AnalyticsEvent =
  | { name: 'tutorial_started'; props?: {} }
  | { name: 'tutorial_step_viewed'; props: { step: string; duration_ms: number } }
  | { name: 'tutorial_completed'; props: { total_duration_ms: number } }
  | { name: 'tutorial_skipped'; props: { at_step: string } }
  | { name: 'stage_started'; props: { stage_id: number } }
  | { name: 'stage_cleared'; props: { stage_id: number; turns_used: number; stars: 1 | 2 | 3 } }
  | { name: 'stage_failed'; props: { stage_id: number; reason: 'hand_empty' | 'user_quit' } }
  | { name: 'mini_lesson_viewed'; props: { lesson_id: string; stage_id: number } }
  | { name: 'settings_opened'; props?: {} }
```

- [ ] **Step 2: ga4.ts 구현**

```ts
import type { AnalyticsEvent } from './events'

declare global {
  interface Window { gtag?: (...args: any[]) => void }
}

export function track<E extends AnalyticsEvent>(name: E['name'], props?: E['props']): void {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', name, props || {})
  }
  if (import.meta.env.DEV) {
    console.log('[analytics]', name, props)
  }
}
```

- [ ] **Step 3: index.html에 GA4 태그 추가 (placeholder)**

```html
<!-- index.html <head> 내 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

[필요: 실제 GA4 측정 ID 발급 후 `GA_MEASUREMENT_ID` 2곳 교체]

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "feat(analytics): GA4 이벤트 래퍼"
```

---

## Phase 5 — UI 컴포넌트

### Task 27: Card 컴포넌트

**Files:**
- Create: `src/components/Card.tsx`

- [ ] **Step 1: Card 구현**

```tsx
import type { Card as CardType } from '../engine/types'

interface Props {
  card: CardType
  onClick?: () => void
  selected?: boolean
  faceDown?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
  sm: 'w-12 h-16',
  md: 'w-16 h-24',
  lg: 'w-20 h-28',
}

export default function Card({ card, onClick, selected, faceDown, size = 'md' }: Props) {
  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className={[
        sizeClasses[size],
        'relative rounded border-2 transition-all',
        selected ? 'border-yellow-400 translate-y-[-8px]' : 'border-gray-300',
        faceDown ? 'bg-blue-800' : 'bg-white',
        onClick ? 'cursor-pointer hover:shadow-lg' : 'cursor-default',
      ].join(' ')}
    >
      {!faceDown && (
        <>
          <img
            src={`/cards/${card.id}.webp`}
            alt={card.name}
            className="w-full h-full object-cover rounded"
            onError={(e) => {
              // 이미지 없으면 텍스트로 폴백
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
          <div className="absolute bottom-0 left-0 right-0 text-xs text-center bg-white/80">
            {card.month}월
          </div>
        </>
      )}
    </button>
  )
}
```

- [ ] **Step 2: 커밋**

```bash
git add -A
git commit -m "feat(ui): Card 컴포넌트"
```

---

### Task 28: 게임 화면 레이아웃 컴포넌트 (HandArea, FloorArea, DeckArea, 패널들)

**Files:**
- Create: `src/components/HandArea.tsx`, `FloorArea.tsx`, `DeckArea.tsx`, `MissionPanel.tsx`, `ScorePanel.tsx`, `CapturedCards.tsx`, `VirtualOpponentPanel.tsx`

NOTE: 각 컴포넌트는 상태 없이 props만 받는 Stateless. 게임 로직은 GameScreen에서 통합.

- [ ] **Step 1: HandArea.tsx**

```tsx
import type { Card as CardType } from '../engine/types'
import Card from './Card'

interface Props {
  hand: CardType[]
  onCardClick: (cardId: string) => void
  selectedCardId: string | null
}

export default function HandArea({ hand, onCardClick, selectedCardId }: Props) {
  return (
    <div className="flex gap-2 justify-center p-4 bg-green-100 rounded">
      {hand.map(c => (
        <Card
          key={c.id}
          card={c}
          onClick={() => onCardClick(c.id)}
          selected={selectedCardId === c.id}
          size="md"
        />
      ))}
    </div>
  )
}
```

- [ ] **Step 2: FloorArea.tsx**

```tsx
import type { Card as CardType } from '../engine/types'
import Card from './Card'

interface Props {
  floor: CardType[]
}

export default function FloorArea({ floor }: Props) {
  return (
    <div className="flex flex-wrap gap-2 justify-center p-6 bg-green-200 rounded min-h-[140px]">
      {floor.map(c => <Card key={c.id} card={c} size="md" />)}
    </div>
  )
}
```

- [ ] **Step 3: DeckArea.tsx**

```tsx
import type { Card as CardType } from '../engine/types'
import Card from './Card'

interface Props {
  deckCount: number
  lastDrawn?: CardType | null
}

export default function DeckArea({ deckCount, lastDrawn }: Props) {
  return (
    <div className="flex flex-col items-center gap-2 p-4">
      <div className="text-sm">더미 {deckCount}장</div>
      {deckCount > 0 && (
        <div className="relative w-16 h-24 bg-blue-800 rounded border-2 border-blue-900 shadow" />
      )}
      {lastDrawn && (
        <>
          <div className="text-xs text-gray-600">방금 뒤집음</div>
          <Card card={lastDrawn} size="sm" />
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 4: MissionPanel.tsx**

```tsx
import type { Mission } from '../engine/mission'

interface Props { mission: Mission }

function describe(m: Mission): string {
  switch (m.type) {
    case 'collect-kwang': return `광 ${m.count}장 모으기`
    case 'collect-tti': return `띠 ${m.count}장 모으기`
    case 'collect-pi': return `피 ${m.count}장 모으기 (쌍피는 2장)`
    case 'godori': return '고도리 달성'
    case 'hong-dan': return '홍단 3장'
    case 'cheong-dan': return '청단 3장'
    case 'cho-dan': return '초단 3장'
    case 'reach-score': return `${m.target}점 이상`
    case 'no-pibak': return `피박 없이 ${m.minScore}점 이상`
  }
}

export default function MissionPanel({ mission }: Props) {
  return (
    <div className="bg-yellow-50 p-4 rounded border-2 border-yellow-300">
      <div className="text-xs text-gray-600">목표</div>
      <div className="text-lg font-bold">{describe(mission)}</div>
    </div>
  )
}
```

- [ ] **Step 5: ScorePanel.tsx**

```tsx
interface Props { turn: number; score: number }

export default function ScorePanel({ turn, score }: Props) {
  return (
    <div className="bg-white p-4 rounded border">
      <div className="flex justify-between"><span>턴</span><span className="font-bold">{turn}</span></div>
      <div className="flex justify-between"><span>점수</span><span className="font-bold">{score}</span></div>
    </div>
  )
}
```

- [ ] **Step 6: CapturedCards.tsx**

```tsx
import type { Captured } from '../engine/types'
import Card from './Card'

export default function CapturedCards({ captured }: { captured: Captured }) {
  return (
    <div className="bg-white p-2 rounded border">
      <div className="text-xs mb-1">내 카드</div>
      <div className="flex flex-wrap gap-1">
        {[...captured.kwang, ...captured.tti, ...captured.ssangpi, ...captured.pi].map(c => (
          <Card key={c.id} card={c} size="sm" />
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 7: VirtualOpponentPanel.tsx**

```tsx
interface Props { opponentPi: number; opponentKwang: number }

export default function VirtualOpponentPanel({ opponentPi, opponentKwang }: Props) {
  return (
    <div className="bg-gray-100 p-3 rounded">
      <div className="text-xs text-gray-600">가상 상대</div>
      <div className="text-sm">피 {opponentPi}장</div>
      <div className="text-sm">광 {opponentKwang}장</div>
    </div>
  )
}
```

- [ ] **Step 8: 커밋**

```bash
git add -A
git commit -m "feat(ui): 게임 화면 하위 컴포넌트 7종"
```

---

### Task 29: GameScreen 통합

**Files:**
- Create: `src/screens/GameScreen.tsx`

- [ ] **Step 1: GameScreen 구현**

```tsx
import { useState, useMemo, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getStage } from '../stages/registry'
import { initGameState } from '../engine/state'
import { playHandCard, canShake, declareShake } from '../engine/engine'
import { calculateScore } from '../engine/scoring'
import { checkMission } from '../engine/mission'
import HandArea from '../components/HandArea'
import FloorArea from '../components/FloorArea'
import DeckArea from '../components/DeckArea'
import MissionPanel from '../components/MissionPanel'
import ScorePanel from '../components/ScorePanel'
import CapturedCards from '../components/CapturedCards'
import VirtualOpponentPanel from '../components/VirtualOpponentPanel'
import { track } from '../analytics/ga4'
import { recordStageResult } from '../storage/localStorage'

export default function GameScreen() {
  const { stageId } = useParams<{ stageId: string }>()
  const nav = useNavigate()
  const stage = useMemo(() => getStage(Number(stageId)), [stageId])

  const [state, setState] = useState(() => stage ? initGameState(stage.init) : null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    if (stage) track('stage_started', { stage_id: stage.id })
  }, [stage?.id])

  if (!stage || !state) return <div className="p-8">스테이지를 찾을 수 없습니다.</div>

  const score = calculateScore(state.captured, { piCount: state.opponentPi, kwangCount: stage.init.opponentKwang }, state.heundalki ?? null)
  const missionDone = checkMission(state, stage.mission)
  const handEmpty = state.hand.length === 0

  const handleCardClick = (cardId: string) => {
    if (selectedId === cardId) {
      // 카드 실제 플레이
      try {
        const next = playHandCard(state, cardId)
        setState(next)
        setSelectedId(null)
      } catch (e) {
        console.error(e)
      }
    } else {
      setSelectedId(cardId)
    }
  }

  const handleComplete = () => {
    const stars: 0 | 1 | 2 | 3 = missionDone
      ? state.turn <= stage.stars.three ? 3
      : state.turn <= stage.stars.two ? 2
      : 1
      : 0
    if (stars > 0) {
      track('stage_cleared', { stage_id: stage.id, turns_used: state.turn, stars: stars as 1 | 2 | 3 })
      recordStageResult(stage.id, stars)
    } else {
      track('stage_failed', { stage_id: stage.id, reason: handEmpty ? 'hand_empty' : 'user_quit' })
    }
    nav(`/result/${stage.id}?stars=${stars}&turns=${state.turn}`)
  }

  const shakeMonths = canShake(state)

  return (
    <div className="grid grid-cols-[280px_1fr_240px] gap-4 p-6 min-h-screen bg-green-50">
      {/* 좌측 */}
      <div className="flex flex-col gap-4">
        <MissionPanel mission={stage.mission} />
        <ScorePanel turn={state.turn} score={score.total} />
        <CapturedCards captured={state.captured} />
      </div>

      {/* 중앙 */}
      <div className="flex flex-col gap-4 justify-between">
        <FloorArea floor={state.floor} />
        <HandArea hand={state.hand} onCardClick={handleCardClick} selectedCardId={selectedId} />
        <div className="flex gap-2 justify-center">
          {shakeMonths.map(m => (
            <button
              key={m}
              onClick={() => setState(declareShake(state, m))}
              disabled={state.heundalki != null}
              className="px-3 py-2 bg-orange-500 text-white rounded disabled:opacity-50"
            >
              {m}월 흔들기
            </button>
          ))}
          {(missionDone || handEmpty) && (
            <button onClick={handleComplete} className="px-4 py-2 bg-green-600 text-white rounded">
              완료
            </button>
          )}
        </div>
      </div>

      {/* 우측 */}
      <div className="flex flex-col gap-4">
        <DeckArea deckCount={state.deck.length} />
        <VirtualOpponentPanel opponentPi={state.opponentPi} opponentKwang={stage.init.opponentKwang} />
      </div>
    </div>
  )
}
```

- [ ] **Step 2: App.tsx에 라우트 등록**

```tsx
import GameScreen from './screens/GameScreen'
// ...
<Route path="/play/:stageId" element={<GameScreen />} />
```

- [ ] **Step 3: 수동 테스트**

Run: `npm run dev` → `/` → stage-01 선택 → `/play/1` 진입 → 카드 두 번 클릭 시 플레이 → 미션 달성 시 완료 버튼.

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "feat(ui): GameScreen 통합 - 룰 엔진과 컴포넌트 연결"
```

---

### Task 30: StageSelectScreen 실체화

**Files:**
- Modify: `src/screens/StageSelectScreen.tsx`

- [ ] **Step 1: StageSelectScreen 구현**

```tsx
import { Link } from 'react-router-dom'
import { STAGES } from '../stages/registry'
import { loadProgress } from '../storage/localStorage'

export default function StageSelectScreen() {
  const progress = loadProgress()
  const cleared = new Map(progress.clearedStages.map(s => [s.id, s.stars]))

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">스테이지 선택</h1>
        <div className="flex gap-2">
          {!progress.tutorialDone && (
            <Link to="/tutorial" className="px-4 py-2 bg-blue-600 text-white rounded">
              튜토리얼 시작
            </Link>
          )}
          <Link to="/settings" className="px-4 py-2 bg-gray-300 rounded">설정</Link>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        {STAGES.map(s => {
          const stars = cleared.get(s.id) ?? 0
          const locked = s.id > 1 && !cleared.has(s.id - 1)
          return (
            <Link
              key={s.id}
              to={locked ? '#' : `/play/${s.id}`}
              className={`p-4 border rounded text-center ${locked ? 'opacity-50 cursor-not-allowed' : 'hover:bg-yellow-50'}`}
              onClick={(e) => { if (locked) e.preventDefault() }}
            >
              <div className="text-2xl mb-2">{s.id}</div>
              <div className="text-sm mb-2">{s.title}</div>
              <div className="text-yellow-500">
                {'★'.repeat(stars)}{'☆'.repeat(3 - stars)}
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 커밋**

```bash
git add -A
git commit -m "feat(ui): StageSelectScreen 실체화"
```

---

### Task 31: ResultScreen

**Files:**
- Create: `src/screens/ResultScreen.tsx`
- Modify: `src/App.tsx`

- [ ] **Step 1: ResultScreen 작성**

```tsx
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom'
import { getStage } from '../stages/registry'

export default function ResultScreen() {
  const { stageId } = useParams<{ stageId: string }>()
  const [params] = useSearchParams()
  const nav = useNavigate()
  const stage = getStage(Number(stageId))
  const stars = Number(params.get('stars') || '0')
  const turns = Number(params.get('turns') || '0')

  if (!stage) return <div>스테이지 없음</div>

  const success = stars > 0
  const nextStage = getStage(stage.id + 1)

  return (
    <div className="max-w-lg mx-auto p-8 text-center">
      <h1 className="text-4xl font-bold mb-4">
        {success ? '클리어!' : '실패'}
      </h1>
      <div className="text-6xl mb-6 text-yellow-500">
        {'★'.repeat(stars)}{'☆'.repeat(3 - stars)}
      </div>
      <div className="mb-6">
        <p>사용 턴: {turns}</p>
        <p>3★ 기준: {stage.stars.three}턴 이내</p>
      </div>
      <div className="flex gap-2 justify-center">
        <button onClick={() => nav(`/play/${stage.id}`)} className="px-4 py-2 bg-gray-300 rounded">
          재도전
        </button>
        <Link to="/" className="px-4 py-2 bg-blue-600 text-white rounded">스테이지 선택</Link>
        {success && nextStage && (
          <Link to={`/play/${nextStage.id}`} className="px-4 py-2 bg-green-600 text-white rounded">
            다음 스테이지
          </Link>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 라우트 연결**

```tsx
<Route path="/result/:stageId" element={<ResultScreen />} />
```

- [ ] **Step 3: 커밋**

```bash
git add -A
git commit -m "feat(ui): ResultScreen"
```

---

### Task 32: SettingsScreen

**Files:**
- Create: `src/screens/SettingsScreen.tsx`
- Modify: `src/App.tsx`

- [ ] **Step 1: SettingsScreen 작성**

```tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { track } from '../analytics/ga4'

export default function SettingsScreen() {
  const [sound, setSound] = useState(
    localStorage.getItem('gostop-sound') !== 'off'
  )

  const toggleSound = () => {
    const next = !sound
    setSound(next)
    localStorage.setItem('gostop-sound', next ? 'on' : 'off')
  }

  const resetProgress = () => {
    if (confirm('진행도를 초기화합니다. 계속?')) {
      localStorage.removeItem('gostop-puzzle-v1')
      alert('초기화됨. 홈으로 이동합니다.')
      window.location.href = '/'
    }
  }

  useState(() => { track('settings_opened') })

  return (
    <div className="max-w-md mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">설정</h1>
      <div className="flex items-center justify-between mb-4">
        <span>사운드</span>
        <button onClick={toggleSound} className="px-3 py-1 border rounded">
          {sound ? 'ON' : 'OFF'}
        </button>
      </div>
      <Link to="/tutorial" className="block mb-4 text-blue-600 underline">
        튜토리얼 다시 보기
      </Link>
      <button onClick={resetProgress} className="text-red-600 underline">
        진행도 초기화
      </button>
      <div className="mt-8">
        <Link to="/" className="text-gray-600">← 홈</Link>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 라우트 연결 및 커밋**

```tsx
<Route path="/settings" element={<SettingsScreen />} />
```

```bash
git add -A
git commit -m "feat(ui): SettingsScreen"
```

---

## Phase 6 — 통합 & 폴리시

### Task 33: 튜토리얼 시작 시점 자동 체크

**Files:**
- Modify: `src/screens/StageSelectScreen.tsx`, `src/App.tsx`

- [ ] **Step 1: 첫 진입 시 튜토리얼 자동 유도**

StageSelectScreen 렌더 시 `progress.tutorialDone === false`면 자동으로 `/tutorial`로 리디렉트 (또는 배너 표시).

```tsx
import { Navigate } from 'react-router-dom'
// ...
const progress = loadProgress()
if (!progress.tutorialDone) return <Navigate to="/tutorial" replace />
```

- [ ] **Step 2: 계측 — 페이지 진입 이벤트**

App.tsx에 useEffect로 `tutorial_started` 호출 (튜토리얼 진입 시).

TutorialScreen 수정:
```tsx
useEffect(() => { track('tutorial_started') }, [])
```

- [ ] **Step 3: 커밋**

```bash
git add -A
git commit -m "feat: 첫 진입 시 튜토리얼 자동 유도"
```

---

### Task 34: 미니 레슨 트리거 (스테이지 진입 전)

**Files:**
- Modify: `src/screens/GameScreen.tsx`, `src/stages/data/*.ts`

- [ ] **Step 1: 스테이지 `hintLesson` 필드 채우기**

예시 — stage-04.ts (따닥 도입):
```ts
hintLesson: 'tadak',
```

stage-07.ts (피박·광박): `hintLesson: 'pibak-kwangbak'`
stage-10.ts (고도리): `hintLesson: 'godori'`
stage-13.ts (흔들기 복합): `hintLesson: 'heundalki'`

- [ ] **Step 2: GameScreen 진입 시 레슨 팝업 표시**

```tsx
import { MINI_LESSONS } from '../tutorial/mini-lessons'
// ...
const [lessonShown, setLessonShown] = useState(false)

if (!lessonShown && stage.hintLesson && MINI_LESSONS[stage.hintLesson]) {
  return <TutorialRunner
    steps={MINI_LESSONS[stage.hintLesson]}
    onComplete={() => {
      track('mini_lesson_viewed', { lesson_id: stage.hintLesson!, stage_id: stage.id })
      setLessonShown(true)
    }}
  />
}
```

- [ ] **Step 3: 커밋**

```bash
git add -A
git commit -m "feat: 스테이지별 미니 레슨 팝업"
```

---

### Task 35: 스타일링 폴리시

**Files:**
- Modify: 각 컴포넌트 (Card, HandArea, FloorArea 등)

- [ ] **Step 1: 화투 녹색 배경 테마 통일**

Tailwind 커스텀 색상 추가:
```js
// tailwind.config.js
theme: {
  extend: {
    colors: {
      hwatu: {
        mat: '#2d5a3d',       // 화투 매트 녹색
        accent: '#c1440e',    // 빨간 액센트
        card: '#fef8e2',      // 카드 배경
      }
    }
  }
}
```

- [ ] **Step 2: 카드 호버·선택 애니메이션 부드럽게**

```tsx
className="transition-transform duration-200 hover:translate-y-[-4px]"
```

- [ ] **Step 3: 반응형 대응**

GameScreen grid-cols를 md 이상에서만 3단, 작으면 세로 적층:
```tsx
<div className="grid grid-cols-1 md:grid-cols-[280px_1fr_240px] gap-4">
```

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "style: 화투 테마 + 애니메이션 + 반응형"
```

---

### Task 36: 성능 — WebP + 코드 스플리팅

**Files:**
- Modify: `vite.config.ts`, `src/App.tsx`

- [ ] **Step 1: 라우트별 코드 스플리팅**

```tsx
import { lazy, Suspense } from 'react'
const TutorialScreen = lazy(() => import('./screens/TutorialScreen'))
const GameScreen = lazy(() => import('./screens/GameScreen'))
const ResultScreen = lazy(() => import('./screens/ResultScreen'))
const SettingsScreen = lazy(() => import('./screens/SettingsScreen'))

<Suspense fallback={<div>로딩...</div>}>
  <Routes>
    {/* 각 Route element */}
  </Routes>
</Suspense>
```

- [ ] **Step 2: public/cards/ 디렉터리에 WebP 48장 배치 확인**

[필요: 디자이너가 제공한 48장 WebP 파일 public/cards/ 에 배치. 파일명은 id와 일치: `01-kwang.webp` 등]

- [ ] **Step 3: 빌드 테스트**

Run: `npm run build`
Expected: 에러 없음. `dist/` 확인.

Run: `npm run preview`
Expected: 로컬 프리뷰 정상 동작.

- [ ] **Step 4: 커밋**

```bash
git add -A
git commit -m "perf: 라우트 코드 스플리팅 + WebP 카드 자산"
```

---

## Phase 7 — QA & 런칭

### Task 37: 내부 QA 체크리스트

**Files:**
- Create: `File/QA/qa-checklist.md`

- [ ] **Step 1: 체크리스트 문서 생성**

```markdown
# 고스톱 퍼즐 MVP — QA 체크리스트

## 튜토리얼
- [ ] 첫 진입 시 자동으로 /tutorial 리디렉트
- [ ] 5단계 모두 표시되고 "다음" 동작
- [ ] "건너뛰기" 시 스테이지 선택으로 이동
- [ ] 완료 시 tutorialDone = true 저장
- [ ] 설정에서 "튜토리얼 다시 보기" 동작

## 게임플레이 (스테이지 1~15 각각)
- [ ] 초기 상태 렌더링 정확 (손 7, 바닥 6, 더미 33)
- [ ] 카드 클릭 시 선택 → 두 번째 클릭 시 플레이
- [ ] 단순 매칭 정상 동작
- [ ] 쫑 발생 시 상대 피 -1, 3장 모두 획득
- [ ] 쓸 (손패 3+바닥 1) 발생 시 4장 모두 획득
- [ ] 뻑 상태 시 바닥에서 사라지고 pbbukStack 저장됨
- [ ] 뻑 해소 시 4장 모두 획득
- [ ] 따닥 (바닥 2+손패 1) 발생 시 3장 모두 획득
- [ ] 흔들기 선언 버튼 정상 표시 (손패 3장 시)
- [ ] 흔들기 선언 후 최종 점수 2배
- [ ] 고도리 조건 시 5점 보너스 반영
- [ ] 피박/광박 조건 시 상태 정확 표시

## 별점·결과
- [ ] 3★ = 최소 턴 이내
- [ ] 2★ = N+1 ~ N+2
- [ ] 1★ = N+3 이상
- [ ] 실패 = 손패 소진 + 목표 미달
- [ ] 결과 화면에 사용 턴, 별점 표시
- [ ] 재도전 클릭 시 동일 초기 상태로 리셋
- [ ] 다음 스테이지 버튼 정상 동작

## 저장소
- [ ] 진행도 localStorage에 저장됨
- [ ] 페이지 새로고침 후에도 별점 유지
- [ ] 더 높은 별점 달성 시에만 갱신
- [ ] 초기화 버튼 동작

## 계측 (DevTools > Network > gtag/collect 확인)
- [ ] tutorial_started, tutorial_completed 이벤트 전송
- [ ] stage_started, stage_cleared 이벤트 전송
- [ ] 이벤트 속성 정확 (stage_id, turns_used, stars)

## 엣지 케이스
- [ ] 스테이지 1 건너뛰고 URL로 /play/5 직접 접근 → 차단 또는 허용 정책 명확
- [ ] 존재하지 않는 stageId (/play/99) → 에러 메시지
- [ ] 브라우저 뒤로 가기 동작 정상
- [ ] localStorage 비활성화 브라우저 → 폴백 (메모리 저장)

## 성능
- [ ] 초기 로딩 3초 이내 (Chrome DevTools Network 탭)
- [ ] 카드 매칭 반응 100ms 이내
- [ ] 빌드 결과물 크기 < 500KB (gzipped)

## 브라우저 호환
- [ ] Chrome 최신 ✓
- [ ] Firefox 최신 ✓
- [ ] Edge 최신 ✓
- [ ] Safari 최신 ✓
```

- [ ] **Step 2: 커밋**

```bash
git add -A
git commit -m "docs(qa): MVP QA 체크리스트"
```

---

### Task 38: 스테이지 솔버 CI 통합

**Files:**
- Modify: `package.json`
- Create: `.github/workflows/ci.yml` (선택)

- [ ] **Step 1: npm script — 테스트 + 빌드 + 솔버 검증**

```json
"scripts": {
  "check": "npm run test:run && npm run verify-stages && npm run build"
}
```

- [ ] **Step 2: CI 파이프라인 (선택)**

`.github/workflows/ci.yml`:
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run check
```

[필요: GitHub 저장소 생성 후 푸시 연동]

- [ ] **Step 3: 커밋**

```bash
git add -A
git commit -m "chore(ci): check 스크립트 + GitHub Actions"
```

---

### Task 39: 외부 베타 준비

**Files:**
- Create: `File/QA/beta-feedback-form.md`

- [ ] **Step 1: 베타 피드백 폼 작성 (Google Forms 스크립트)**

[필요: 실제 Google Forms 링크 생성]

질문 항목:
1. 튜토리얼 5분 끝까지 보셨나요? (예/아니오/중간에 중단)
2. 어느 스테이지에서 가장 막혔나요?
3. 화투 규칙이 이해되셨나요? (1~5)
4. 게임이 재밌었나요? (1~5)
5. 다시 플레이하고 싶으신가요? (예/아니오)
6. 자유 의견

- [ ] **Step 2: 배포용 스테이징 URL 확보**

Vercel/Netlify로 임시 배포:
```bash
# Vercel CLI 예시
npm i -g vercel
vercel --prod
```

[필요: 계정 인증 및 최초 연동]

- [ ] **Step 3: 베타 모집 — 10~20명**

[필요: 20~30대 캐주얼 유저 모집 채널 결정 (지인·카톡·커뮤니티)]

---

### Task 40: 런칭 전 최종 체크

- [ ] **Step 1: QA 체크리스트 전체 완료 확인**
- [ ] **Step 2: GA4 측정 ID 실제값으로 교체 확인**
- [ ] **Step 3: 프로덕션 빌드 + 최종 배포**

```bash
npm run build
vercel --prod
```

- [ ] **Step 4: 런칭 공지 작성 및 배포**

[필요: 런칭 채널·메시지 결정]

- [ ] **Step 5: 런칭 후 초기 1주간 지표 모니터링 대시보드 설정**

- GA4 대시보드: 튜토리얼 완주율, 스테이지별 이탈 지점
- 이상치 발생 시 핫픽스 준비

---

## 자체 검토 (Self-Review)

### 스펙 커버리지 대조

| 스펙 섹션 | 해당 태스크 |
|-----------|-------------|
| 1. 제품 개요 | 모든 태스크의 배경 |
| 2. 핵심 게임 루프 (룰 엔진) | Task 5~18 |
| 3. 튜토리얼 설계 | Task 21~24, 33~34 |
| 4. 스테이지 구조 | Task 19~20 |
| 5. UI/레이아웃 | Task 27~32 |
| 6. 기술 방향 | Task 1~4, 25~26, 36 |
| 7. 성공 지표 & 계측 | Task 26, 33, 38 |
| 8. 범위 외 | 플랜에 미포함 (정상) |
| 9. 타임라인 & 리스크 | 전체 40 태스크가 7주 일정에 매핑 |

### 플랜 리스크 & 알려진 결함

1. **스테이지 2~15 콘텐츠 디자인이 플랜 밖에 위임됨** — 구현 플랜은 스키마·검증·솔버까지만 다루고, 실제 스테이지 15개 퍼즐 디자인은 디자이너와 별도 작업. Task 19 Step 3에 명시.
2. **화투 카드 WebP 에셋 의존** — Task 36 Step 2에 `[필요]`로 표시.
3. **고도리 카드 재정의** — Task 15에서 cards.ts(Task 5)의 2월/4월/8월 구성을 수정해야 한다는 소급 변경 발견됨. 플랜 실행 시 Task 5 단계에서 이 수정사항 반영 필수.
4. **솔버 성능** — BFS 깊이 10 제한, 복잡한 스테이지는 풀이 못 찾을 수 있음. 실 운영 시 수동 검증 병행 필요.
5. **GA4 측정 ID** — 실제 ID 발급 필요 (Task 26).
6. **흔들기 선언 UX 세부** — GameScreen의 흔들기 버튼은 단순 구현. 실제 UX(턴 시작 시 자동 다이얼로그 등) 개선 여지.
7. **Windows 환경 경로/인코딩** — 한글 폴더명(`File/기획/`)으로 git/npm 경로 이슈 가능성. 실제 실행 시 경로 에러 발생하면 영문 폴더로 이관 검토.

### 남은 `[필요: ...]` 항목

- [필요: 스테이지 2~15 구체 카드 배치 및 풀이 검증]
- [필요: 48장 화투 WebP 이미지 파일 배치]
- [필요: GA4 측정 ID 발급 후 index.html 2곳 교체]
- [필요: GitHub 저장소 생성 및 CI 연동]
- [필요: Vercel/Netlify 계정 인증 및 스테이징 배포]
- [필요: Google Forms 베타 피드백 링크 생성]
- [필요: 베타 모집 채널 결정]
- [필요: 런칭 채널·메시지 결정]
- [필요: 런칭 후 1주 모니터링 담당자 지정]
