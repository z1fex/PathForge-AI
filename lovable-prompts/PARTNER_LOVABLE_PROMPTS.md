# 🚀 PathForge AI — Lovable Frontend Prompts

> **Project:** AI-powered career guidance platform  
> **Design Reference:** Cereal Club NFT website aesthetic  
> **Design DNA:** Pastel color blocks, bold chunky uppercase fonts, wavy organic section dividers, pill-shaped buttons, playful but professional, Gen-Z energy meets career tech  

---

## 🎨 DESIGN SYSTEM (Read Before All Prompts)

**Color Palette (section by section, rotating):**
- Hero: Lavender/Soft Purple `#C9B8E8` → light gradient
- Section 2: Sky Blue `#A8D8EA`
- Section 3: Sunny Yellow `#FFE566`
- Section 4: Cream/Beige `#FFF5D6`
- Section 5: Bubblegum Pink `#FFB3C6`
- Section 6: Mint Green `#A8E6CF`
- Footer: Periwinkle Blue `#B3C6F0`

**Typography:**
- Headings: `Fredoka One` or `Boogaloo` (Google Fonts) — heavy, chunky, all-caps, bold, black
- Body: `Nunito` or `Poppins` — clean, rounded, readable
- All section headings: UPPERCASE, no letter spacing, super large (60–80px)

**UI Elements:**
- Buttons: Pill/stadium shape, thick black 2–3px border, yellow fill (`#FFE566`) or cream fill, bold uppercase text
- Cards: Polaroid-style with slight rotation (-3° to +3°), thick black border, white/pastel background
- Section dividers: Wavy SVG curves between sections (organic, hand-drawn feel)
- Marquee/ticker: Horizontal scrolling text banner with ⭐ or 🌟 emoji separators
- Icons: Use emoji or simple outlined cartoon-style icons

**Animations:**
- Marquee banners auto-scroll left
- Cards float/bob gently on hover
- Buttons scale up slightly on hover with shadow pop
- Page sections fade-in as user scrolls

---

## 📋 PROMPT 1 — Project Setup & Global Design System

```
Build a career guidance web app called "PathForge AI" using React + Tailwind CSS. 

Set up the global design system with these exact specifications:

FONTS (import from Google Fonts):
- Headings: "Fredoka One" — bold, chunky, playful
- Body: "Nunito" — clean and rounded

COLOR PALETTE (CSS variables):
--color-lavender: #C9B8E8
--color-sky: #A8D8EA
--color-yellow: #FFE566
--color-cream: #FFF5D6
--color-pink: #FFB3C6
--color-mint: #A8E6CF
--color-periwinkle: #B3C6F0
--color-black: #1A1A1A
--color-white: #FFFFFF

GLOBAL STYLES:
- Each page section has a full-width, solid pastel background (alternating between the palette colors above)
- Between every section, add a wavy SVG divider shape that flows organically from one color block to the next (like a hand-drawn wave)
- All section headings: Fredoka One, UPPERCASE, 60–72px, color #1A1A1A
- All primary buttons: pill-shaped (border-radius: 50px), thick 2.5px solid black border, background #FFE566, Fredoka One font, uppercase, padding 14px 36px — on hover: scale(1.05) with drop-shadow
- All secondary buttons: same shape but cream/white background
- Cards: white or light pastel background, thick 2px black border, border-radius 16px, subtle box-shadow, slight CSS rotation transform (-2deg to 2deg) for polaroid effect
- Scrolling marquee banner component: full-width, 60px tall, bold uppercase text, star ⭐ separators, auto-scrolling left animation, distinct background color

Create a reusable WaveDivider component, a MarqueeBanner component, and a PillButton component as the foundation.
```

---

## 📋 PROMPT 2 — Hero + How It Works + Visual Roadmap

```
Using the established design system, build these 3 sections back to back with wavy SVG dividers between each:

— SECTION 1: HERO (lavender background #C9B8E8)
Navbar: "PathForge AI" logo left, yellow pill "Get Started →" right.
Center: Fredoka One 72px heading "YOUR DREAM JOB IS ONE ROADMAP AWAY." + Nunito subtitle "Input your target job title and get a personalized visual roadmap, certifications, salary insights, and top companies hiring now." + large pill search bar (white, black border) with placeholder "e.g. Machine Learning Engineer..." and attached yellow "FORGE MY PATH 🚀" button. Below the bar: 3 floating badge pills — "🎯 Visual Milestones" | "💰 Salary Insights" | "🏢 Top Hiring Companies" (subtle bob animation).

— SECTION 2: HOW IT WORKS (sky blue background #A8D8EA)
Heading: "HOW IT WORKS". Three horizontal polaroid cards (alternating rotation -2°, 0°, +2°):
1. 🎯 "TELL US YOUR GOAL" — Type your dream job, we do the rest.
2. 🗺️ "GET YOUR ROADMAP" — AI generates milestones, skills, certs, prerequisites.
3. 🚀 "LAND THE JOB" — See who's hiring, expected salary, and curated courses.

— SECTION 3: VISUAL ROADMAP (yellow background #FFE566)
Heading: "YOUR VISUAL ROADMAP". Horizontal scrollable milestone timeline for "Machine Learning Engineer" — circular nodes connected by thick dashed lines, each node numbered and labeled. On hover: tooltip polaroid card showing milestone name, time estimate, and key skill. Show 6 milestones: CS Fundamentals → Python & DSA → Statistics & ML → Deep Learning → ML Projects → Interview Prep. CTA button below: "GENERATE MY ROADMAP →".
```

---

## 📋 PROMPT 3 — Skills & Certs + Companies Hiring + Salary Expectations + Courses

```
Continue building PathForge AI with these 4 sections, all using the established pastel + polaroid design system with wavy dividers between each:

— SECTION 4: WHAT YOU'LL NEED (cream background #FFF5D6)
Heading: "WHAT YOU'LL NEED". Three polaroid cards side by side:
1. Purple header — "🛠️ SKILLS NEEDED": tag cloud of pill badges (Python, TensorFlow, SQL, Docker, Git, Cloud).
2. Blue header — "🏅 CERTIFICATIONS": numbered list of 4 certs with issuer, time, and small "VIEW CERT →" link.
3. Pink header — "📚 BACKGROUND NEEDED": short paragraph on prerequisites + 3 badge pills.

— SECTION 5: WHO'S HIRING (pink background #FFB3C6)
Heading: "WHO'S HIRING RIGHT NOW 🔥". Horizontally scrollable row of 6 company polaroid cards (← → arrows). Each card: company initial logo, name, role, location badge pills, "VIEW JOBS →" button. Companies: Google, Meta, Amazon, Microsoft, OpenAI, Apple. Below cards: auto-scrolling marquee banner "⭐ GOOGLE ⭐ META ⭐ AMAZON ⭐ MICROSOFT ⭐ OPENAI ⭐ APPLE ⭐ NETFLIX ⭐ STRIPE ⭐".

— SECTION 6: SALARY EXPECTATIONS (mint background #A8E6CF)
Heading: "WHAT TO EXPECT 💰". Three polaroid salary tier cards: Entry ($75K–$110K, sky header), Mid ($110K–$160K, yellow header + "MOST COMMON" badge), Senior ($160K–$250K+, pink header). Below: simple horizontal bar chart "SALARY BY COMPANY" with 5 companies, pastel-colored bars, value labels.

— SECTION 7: LEARN FROM THE BEST (lavender background #C9B8E8)
Heading: "LEARN FROM THE BEST 📺". 2-row grid of 6 course polaroid cards — each with: colored thumbnail placeholder + ▶️, channel name, bold course title, duration badge, skill tags, "WATCH NOW →" button. Courses: StatQuest, 3Blue1Brown, Andrej Karpathy, CS50 Harvard, fast.ai, Andrew Ng ML Specialization. CTA below: "SEE ALL COURSES →".
```

---

## 📋 PROMPT 4 — RAG Chatbot + FAQ + Footer + Polish

```
Build the final 3 sections of PathForge AI and do a complete responsive polish pass:

— SECTION 8: RAG CHATBOT (periwinkle background #B3C6F0)
Heading: "ASK ANYTHING 🤖". Centered chat UI card (max-width 800px, white, black border, border-radius 24px). Components: periwinkle header bar with "PathForge AI Advisor 🤖" + green "● ONLINE" badge. Chat area with 3 pre-loaded messages: AI greets user → User says "I want to be an MLE at Google" → AI responds with key skills needed. AI bubbles: lavender, left-aligned. User bubbles: yellow, right-aligned. Below chat: 3 suggested question pills ("What certs do I need? 📜" / "What's the salary? 💰" / "Who's hiring? 🏢"). Input bar with "SEND →" yellow pill button.

— SECTION 9: FAQ (pink background #FFB3C6)
Heading: "GOT QUESTIONS? 🙋". Accordion list (max-width 800px, centered) — cream rounded cards, black border, Fredoka One uppercase questions, "+" icon that rotates to "×" on open. Include: What is PathForge AI? / Is it free? / How accurate is the salary data? / How does the RAG chatbot work? / What jobs are supported? (smooth expand/collapse animation).

— FOOTER (periwinkle #B3C6F0)
Top: marquee banner "🌟 PATHFORGE AI 🌟 VISUAL ROADMAPS 🌟 SALARY INSIGHTS 🌟 AI ADVISOR 🌟 WHO'S HIRING 🌟". Main footer: 4 columns — Brand (logo + tagline + social icons) / Features links / Resources links / Company links. Bottom black strip: "© 2025 PathForge AI. Built for students and career changers everywhere."

— RESPONSIVE + POLISH PASS:
Mobile: single column, headings 36px, cards stack vertically. Tablet: 2-col grids, 48px headings.
Animations: milestone nodes pulse, company cards lift on hover (translateY -8px), salary bars animate in on scroll (0 → final width), chatbot send button has ripple effect, all sections fade-in on scroll via Intersection Observer. Add a "BACK TO TOP ↑" yellow pill button fixed bottom-right on scroll. All buttons/links have focus-visible outlines for accessibility.
```

---

## 🗂️ BUILD ORDER

| Step | Prompt | Covers |
|------|--------|--------|
| 1 | Prompt 1 | Design system, fonts, reusable components |
| 2 | Prompt 2 | Hero, How It Works, Visual Roadmap |
| 3 | Prompt 3 | Skills/Certs, Companies, Salary, Courses |
| 4 | Prompt 4 | Chatbot, FAQ, Footer, Polish |

---

## 💡 QUICK TIPS FOR LOVABLE

- **Start with Prompt 1** in a fresh project before anything else.
- If Lovable forgets the style, paste this reminder: *"Keep Fredoka One headings, rotating pastel section backgrounds, wavy SVG dividers, and pill-shaped black-bordered yellow buttons."*
- **Backend API endpoints your partner needs to build:** `POST /api/roadmap`, `GET /api/companies?role=`, `GET /api/salary?role=&level=`, `GET /api/courses?role=`, `POST /api/chat`, `GET /api/certifications?role=`

---

*Generated for PathForge AI — June 2026*

---

## 📋 PROMPT 5 — Chatbot Sidebar + UI Fixes

```
Make the following targeted changes across the entire PathForge AI app:

— 1. FLOATING CHATBOT SIDEBAR (replaces the chatbot section AND the back-to-top button)
- Completely REMOVE the full "ASK ANYTHING 🤖" section from the page.
- In its place, add a persistent floating button fixed to the bottom-right corner (24px from bottom, 24px from right).
- The button is a circular icon (64px diameter), white background, 2.5px black border, subtle box-shadow.
- Inside the button: use the green cereal bowl character with pink headphones (cartoonish, kawaii-style face — like a friendly mascot avatar). This is the chatbot face/icon.
- On hover: button scales to 1.1x with a deeper shadow and a small tooltip appears above it: "Chat with PathForge 🤖" (cream pill, black border, Nunito 13px).
- On click: a sidebar slides in from the RIGHT (width 380px, full viewport height, fixed position, z-index 999, white background, 2.5px black left border, smooth slideInRight CSS transition 300ms ease).
- Sidebar contents:
  • Header strip (periwinkle #B3C6F0): the green cereal bowl avatar (40px) + "PathForge Advisor 🤖" in Fredoka One + green "● ONLINE" badge + an "✕" close button (pill, black border) on the far right.
  • Chat message area (flex-grow, scrollable): AI bubbles left-aligned lavender (#C9B8E8), user bubbles right-aligned yellow (#FFE566), both rounded 18px, Nunito 16px.
  • Pre-loaded opening message from AI: "Hey! 👋 I'm your PathForge advisor. What's your dream job? I'll map out your entire career path!"
  • 3 suggested pill buttons: "Build my roadmap 🗺️" / "Salary for my role 💰" / "Who's hiring me? 🏢"
  • Input bar at bottom: white rounded input + yellow "SEND →" pill button.
- Clicking the ✕ or clicking outside the sidebar closes it (slides back out right).

— 2. REMOVE ALL HORIZONTAL SCROLLERS / SCROLLBARS
- Remove every instance of overflow-x: scroll / horizontal scrollbar from the entire site — this includes the company cards row, the course cards row, and any other scrollable containers.
- Replace the company cards horizontal scroll with a 3×2 CSS grid (3 columns, 2 rows) that fits all 6 cards neatly within the section. On tablet: 2×3 grid. On mobile: 1-column stack.
- Replace the course cards horizontal scroll with a 3×2 CSS grid as well (already done in Prompt 3 — confirm no scrollbar exists).

— 3. FIX THE "WHO'S HIRING" SECTION
- Center-align the section heading "WHO'S HIRING RIGHT NOW 🔥" (it is currently left-aligned).
- Remove the ← → arrow navigation buttons entirely.
- Remove the black scrolling marquee band that shows company names with gold stars (the black ticker strip). Replace it with a row of 6 pastel-colored rounded badge pills (one per company), evenly spaced, each with the company name in Fredoka One bold — colors alternating from the palette (lavender, sky, yellow, pink, mint, cream). These sit below the cards as a decorative "also hiring" indicator, no animation, no scrolling.
- Remove the horizontal scroller/scrollbar that appears under the company icons.

— 4. FIX TOOLTIP CLIPPING ON ROADMAP MILESTONES
- The milestone node hover tooltip cards are being clipped/cut off at the top when they appear above the node.
- Fix this by setting the milestone timeline container to overflow: visible (not hidden), and ensure the tooltip has position: absolute with a high z-index (z-index: 50) so it renders above all surrounding elements without being clipped.
- If the node is near the top of the viewport, the tooltip should appear BELOW the node instead of above (use JS to detect proximity to top: if node's top offset < 120px, flip tooltip to bottom).
```

---

## 📋 PROMPT 6 — Minor UI Fixes

```
Make these 3 targeted fixes:

— 1. CHATBOT FLOATING BUTTON — LARGER SIZE
Increase the floating chatbot icon button from 64px to 84px diameter. Scale the avatar/mascot image inside it accordingly so it fills the circle well. The hover scale stays at 1.1x.

— 2. SALARY CARDS — FIX "MOST COMMON" BADGE ON MID CARD
The "MOST COMMON" badge on the MID salary card is overflowing/sticking out above the card's top edge, showing a pink bleed. Fix this by:
- Moving the badge INSIDE the yellow header strip of the MID card — position it in the top-right corner of the header, fully contained within the card bounds (no overflow).
- The badge: small rounded pill, black background, white Nunito bold text "MOST COMMON", font-size 11px, padding 3px 10px. No absolute positioning that escapes the card boundary.
- Ensure the card itself has overflow: hidden so nothing bleeds out of the rounded corners.

— 3. VISUAL ROADMAP SECTION — REDUCE EMPTY SPACE
There is too much vertical whitespace between the subtitle ("Sample path for MACHINE LEARNING ENGINEER") and the milestone nodes row below it. 
- Reduce the padding-top / margin-top of the milestone timeline container from whatever it currently is down to 24px max.
- The heading, subtitle, and milestone row should feel visually tight and intentional — not like there's a gap or missing content.
```
