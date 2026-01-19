# Red Set ProtoCell UI - Visual Guide

## Authentication Page

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║                    [Animated Grid Pattern]                 ║
║                                                            ║
║      ┌─────────────────────────────────────────┐          ║
║      │                                         │          ║
║      │         🛡️ [Red Shield Logo]           │          ║
║      │                                         │          ║
║      │      RED SET PROTOCELL                  │          ║
║      │   Autonomous AI Red Teaming System      │          ║
║      │                                         │          ║
║      │   ┌─────────────────────────────┐      │          ║
║      │   │ Backend: [OpenAI ▼]         │      │          ║
║      │   └─────────────────────────────┘      │          ║
║      │                                         │          ║
║      │   ┌─────────────────────────────┐      │          ║
║      │   │ 🔒 API Key: *************** │      │          ║
║      │   └─────────────────────────────┘      │          ║
║      │                                         │          ║
║      │   ┌─────────────────────────────┐      │          ║
║      │   │   Begin Red Teaming [→]     │      │          ║
║      │   └─────────────────────────────┘      │          ║
║      │                                         │          ║
║      │   Defense-Only | Zero-Retention         │          ║
║      │                                         │          ║
║      └─────────────────────────────────────────┘          ║
║                                                            ║
║   ⚠️  Security Notice: Your API key is stored locally     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

**Design Elements:**
- Dark background (#0a0a0a) with animated grid pattern
- Glassmorphism card (semi-transparent with backdrop blur)
- Red accent color (#ef4444) for logo and buttons
- Smooth fade-in animation
- White text on dark background

---

## Dashboard Layout

```
╔═════════════════════════════════════════════════════════════════════════════════════════╗
║  HEADER                                                                                 ║
║  ┌──┬─────────────────────────────┬──────────────────┬────────────────────────────┐  ║
║  │🛡│ RED SET PROTOCELL           │  ● RUNNING       │ [▶ Start] [⏸ Pause] [■ Stop]│  ║
║  │ │ Session: rsp_20260108_...   │                  │                             │  ║
║  └──┴─────────────────────────────┴──────────────────┴────────────────────────────┘  ║
╠═════════════════════════════════════════════════════════════════════════════════════════╣
║  MAIN CONTENT (3 COLUMNS)                                                               ║
║                                                                                         ║
║  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐        ║
║  │ LIVE ATTACK FEED     │  │ METRICS PANEL        │  │ COST TRACKER         │        ║
║  │ ━━━━━━━━━━━━━━━━━━━━ │  │ ━━━━━━━━━━━━━━━━━━━━ │  │ ━━━━━━━━━━━━━━━━━━━━ │        ║
║  │                      │  │ [Stat] [Stat] [Stat] │  │ $2.45 / $10.00       │        ║
║  │ ┌──────────────────┐ │  │ [Stat] [Stat] [Stat] │  │ ▓▓▓▓▓░░░░░ 24%      │        ║
║  │ │ Round 12 • 14:32 │ │  │                      │  │                      │        ║
║  │ │ ⚠️ CRITICAL       │ │  │ ┌──────────────────┐ │  │ Used: 24%           │        ║
║  │ │                  │ │  │ │ [Score Chart]    │ │  │ Remaining: $7.55    │        ║
║  │ │ Domain: jailbreak│ │  │ │    📈            │ │  └──────────────────────┘        ║
║  │ │ Strategy: lexical│ │  │ └──────────────────┘ │                               ║
║  │ │                  │ │  │                      │  ┌──────────────────────┐        ║
║  │ │ Prompt: "Ignore  │ │  │ ┌──────────────────┐ │  │ ATTACK CONFIG        │        ║
║  │ │ previous..."     │ │  │ │ [Pie Chart]      │ │  │ ━━━━━━━━━━━━━━━━━━━━ │        ║
║  │ │                  │ │  │ └──────────────────┘ │  │                      │        ║
║  │ │ Response: "I     │ │  │                      │  │ Max Rounds: [100]    │        ║
║  │ │ cannot help..."  │ │  │ ┌──────────────────┐ │  │ Max Cost: [$10.00]   │        ║
║  │ │                  │ │  │ │ [Bar Chart]      │ │  │ Mutation: ▓▓░ 70%   │        ║
║  │ │ Scores:          │ │  │ └──────────────────┘ │  │ [x] Halt Critical    │        ║
║  │ │ Global: ▓▓▓ 87%  │ │  └──────────────────────┘  │                      │        ║
║  │ │ L1: 82% L2: 91%  │ │                           │ Domains:             │        ║
║  │ │ L3: 88%          │ │  ┌──────────────────────┐  │ [x] Injection        │        ║
║  │ └──────────────────┘ │  │ CUSTOM PROMPT        │  │ [x] Jailbreak        │        ║
║  │                      │  │ ━━━━━━━━━━━━━━━━━━━━ │  │ [ ] PII Extraction   │        ║
║  │ ┌──────────────────┐ │  │                      │  │                      │        ║
║  │ │ Round 11 • 14:30 │ │  │ ┌──────────────────┐ │  │ Strategies:          │        ║
║  │ │ 🟡 MEDIUM        │ │  │ │ Enter custom     │ │  │ [x] Lexical          │        ║
║  │ │ ...              │ │  │ │ prompt here...   │ │  │ [x] Encoding         │        ║
║  │ └──────────────────┘ │  │ │                  │ │  │ [ ] Structural       │        ║
║  │                      │  │ └──────────────────┘ │  └──────────────────────┘        ║
║  │ ┌──────────────────┐ │  │                      │                               ║
║  │ │ Round 10 • 14:28 │ │  │ [Execute Prompt →]   │                               ║
║  │ │ 🟢 SAFE          │ │  └──────────────────────┘                               ║
║  │ └──────────────────┘ │                                                          ║
║  └──────────────────────┘                                                          ║
║                                                                                         ║
╚═════════════════════════════════════════════════════════════════════════════════════════╝
```

**Design Elements:**

### Header
- Logo + Title on left
- Status indicator in center (color-coded dot + text)
- Control buttons on right
- Glass panel styling with subtle border

### Live Attack Feed (Left Column)
- Scrollable container with attack cards
- Each card shows:
  - Round number and timestamp
  - Severity badge (color-coded)
  - Attack metadata (domain, strategy, mutation)
  - Full prompt and response text
  - Score breakdown with progress bars
  - Blocked indicator if applicable
- Newest attacks appear at top
- Smooth slide-in animation

### Metrics Panel (Center Column)
- Top: 4 stat cards in grid
  - Icon + Label + Large Number + Subtitle
  - Color-coded icons
- Bottom: 3 charts in grid
  - Line chart: Score history
  - Pie chart: Severity distribution
  - Bar chart: Attack domains
- All charts update in real-time

### Cost Tracker (Right Top)
- Large cost display: Current / Max
- Animated progress bar
  - Green: < 80%
  - Yellow: 80-100%
  - Red: 100%+
- Warning messages at thresholds
- Stats: Used % and Remaining $

### Attack Configuration (Right Bottom)
- Scrollable panel
- Settings: Sliders and inputs
- Domain selection: Clickable cards with checkmarks
- Strategy selection: Clickable cards with checkmarks
- Halt on critical: Toggle checkbox

### Custom Prompt (Center Bottom)
- Multi-line text area
- Character counter
- Execute button
- Disabled when session not running

---

## Color Palette

```
🎨 Primary Colors:
┌────────┬────────┬────────┐
│ Black  │  Red   │ White  │
│ #0a0a0a│#ef4444 │#ffffff │
└────────┴────────┴────────┘

🎨 Supporting Colors:
┌────────┬────────┬────────┐
│Dark Bg │Red Dark│ Gray   │
│ #1a1a1a│#dc2626 │#9ca3af │
└────────┴────────┴────────┘

🎨 Severity Colors:
┌────────┬────────┬────────┬────────┬────────┐
│  Safe  │  Low   │ Medium │  High  │Critical│
│#22c55e │#eab308 │#f97316 │#ef4444 │#dc2626 │
└────────┴────────┴────────┴────────┴────────┘
```

---

## Glassmorphism Effects

```
Glass Panel Properties:
├─ Background: rgba(26, 26, 26, 0.7)
├─ Backdrop Filter: blur(10px)
├─ Border: 1px solid rgba(255, 255, 255, 0.1)
├─ Border Radius: 16px
└─ Box Shadow: 0 8px 32px rgba(0, 0, 0, 0.37)

Hover Effects:
├─ Border Color: #ef4444
├─ Transform: translateY(-2px) or translateX(4px)
└─ Transition: all 0.3s ease

Button Effects:
├─ Primary: Red gradient background
├─ Secondary: Glass background with border
└─ Hover: Lift up with shadow
```

---

## Animations

```
1. Page Load:
   ├─ Fade in with slide up
   └─ Duration: 0.5s

2. Attack Cards:
   ├─ Slide in from right
   └─ Duration: 0.5s

3. Status Dot:
   ├─ Pulse effect when running
   └─ Duration: 2s loop

4. Progress Bars:
   ├─ Smooth width transition
   └─ Duration: 0.5s

5. Cost Bar Shine:
   ├─ Shimmer effect left to right
   └─ Duration: 2s loop

6. Grid Background:
   ├─ Slow diagonal movement
   └─ Duration: 20s loop
```

---

## Responsive Breakpoints

```
Desktop (1400px+):
┌─────────────────────────────────┐
│ [Live Feed] [Metrics] [Config]  │
└─────────────────────────────────┘

Tablet (1024px - 1400px):
┌──────────────────────┐
│ [Live Feed] [Config] │
│ [Metrics (full width)]│
└──────────────────────┘

Mobile (< 1024px):
┌──────────────┐
│ [Live Feed]  │
│ [Metrics]    │
│ [Config]     │
└──────────────┘
```

---

## Interactive Elements

### Buttons
- Hover: Lift up 2px with shadow
- Active: Scale down 98%
- Disabled: 50% opacity, no hover

### Selection Cards
- Default: Glass with border
- Hover: Red border, lift up
- Selected: Red border, red tint background, checkmark

### Inputs
- Focus: Red border with glow
- Valid: Standard border
- Error: Red border (if validation added)

### Charts
- Hover tooltips with data details
- Smooth data transitions
- Legend highlighting

---

## Typography

```
Font Family: 'Inter', sans-serif

Headings:
├─ H1: 28px, weight 800, letter-spacing -0.5px
├─ H2: 20px, weight 700
└─ H3: 16px, weight 700

Body:
├─ Regular: 14px, weight 400
├─ Small: 12px, weight 400
└─ Tiny: 11px, weight 400

Code/Monospace:
└─ 'Courier New', monospace (for IDs, timestamps)

Special:
├─ Stat Values: 36px, weight 800
├─ Cost Display: 36px, weight 800
└─ Badges: 11px, weight 700, uppercase, letter-spacing 0.5px
```

---

This visual guide provides a comprehensive overview of the UI design and layout. The actual implementation matches these mockups with high fidelity.
