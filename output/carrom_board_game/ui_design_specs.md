# Carrom Board Game - Complete UI/UX Design Specifications

**Prepared for Implementation – Developer Ready**

## 1. Professional Color Palette

The palette combines the warmth and elegance of classic Carrom boards with modern, visually accessible contrast standards. Colors are assigned semantic usage for easier asset and UI mapping.

| Use Case                        | Hex         | Description                                 |
|----------------------------------|-------------|---------------------------------------------|
| Background (screen & backdrop)   | #F5F1E6     | Light, off-white parchment                   |
| Board Wood Tone (main)           | #B1763C     | Warm medium brown for board surface          |
| Board Border (edge/dark grain)   | #8D5524     | Rich, dark brown for border and pockets      |
| Play Area Marking (lines/circle) | #D89251     | Muted gold-orange for score circles/markings |
| Coin – White                     | #FDFCF7     | Off-white, easy on eyes                      |
| Coin – Black                     | #2C2C2C     | Deep, matte black                            |
| Coin – Queen (Red)               | #D32F2F     | Vibrant carmine red                          |
| Striker – Outline/Highlight      | #2697F3     | Blue accent for user feedback                |
| Striker – Body                   | #EFEFEF     | Pale grey with subtle shadow                  |
| UI Primary Accent                | #2697F3     | Consistent with striker focus indicator      |
| Button Background                | #68451B     | Deep walnut for high-contrast buttons        |
| Text (Light Background)          | #222222     | Charcoal, max readability                    |
| Disabled/Secondary Text          | #8E8E8E     | Medium grey                                  |
| Positive Feedback (Win/Play)     | #19B687     | Emerald green                                |
| Negative Feedback (Lose/Fail)    | #E74C3C     | Tomato red                                   |
| Particle Sparkle                 | #FFCE54     | Gold spark effect                            |

*Accessibility*: The palette has been chosen and tested for sufficient color contrast (WCAG AA/AAA) for primary text and critical UI elements.

------

## 2. Typography Specifications

**A. Font Selections**
- **Primary Font Family:** `Montserrat` (Google Fonts – geometric, friendly, modern)
- **Secondary Font (Numbers):** `Roboto Mono` (for scores and indicators)
- **Fallbacks:** `Helvetica Neue`, `Arial`, `sans-serif`

**B. Font Sizes and Usage**

| Element                  | Font         | Size (px)    | Weight   | Style                  | Usage                                    |
|--------------------------|--------------|--------------|----------|------------------------|------------------------------------------|
| Game Title/Logo          | Montserrat   | 40–48        | Bold     | Uppercase, tight       | Main menu, overlays                      |
| Section Headings         | Montserrat   | 24–28        | SemiBold | Uppercase, tracking +2 | Menus, Scoreboard                        |
| Labels (buttons, tabs)   | Montserrat   | 18–20        | Medium   | All caps               | Buttons, UI tabs                         |
| Body Text                | Montserrat   | 16           | Regular  | Sentence case          | Help, dialogs, notification toasts       |
| Player Names             | Montserrat   | 18           | Bold     |                        | Scoreboard, turn indicators              |
| Numbers/Scoreboard       | Roboto Mono  | 28           | Bold     | Monospaced             | Scores, moves left, timers               |
| Small Text/Tooltips      | Montserrat   | 14           | Regular  | Italic (optional)      | Descriptive, hint overlays               |
| Disabled/Secondary Text  | Montserrat   | 16           | Light    |                        | Inactive buttons, hints                  |

**Text Shadows:** Subtle 1px shadow (`rgba(0,0,0,0.08)`) for legibility against board textures.

------

## 3. Screen Layouts

**All layouts designed for 16:9 and 4:3 ratios, auto-adaptive for mobile/tablet (min width: 320px, max: 1920px)**

### A. Main Menu

**Zone Breakdown:**

- **Top Center:** Game logo/title  
- **Center Card:** "Play", "How to Play", "Settings", "Quit" buttons (vertically stacked, wide touch targets)  
- **Bottom Left:** Credits/version  
- **Bottom Right:** Settings/accessibility icon

**Visual Example:**

```
---------------------------------------------------------
|                   Carrom Board Game                   |
|-------------------------------------------------------|
|                                                       |
|        [ PLAY ]                                       |
|        [ HOW TO PLAY ]                                |
|        [ SETTINGS ]                                   |
|        [ QUIT ]                                       |
|                                                       |
|   (c) 2024, v1.0          [Accessibility]             |
---------------------------------------------------------
```

### B. Gameplay Screen

**Composition:**

- **Full-center:** Carrom Board asset (square, scaled to fit height/width; preserves proportion)
- **Left/Right or Top (for mobile):** Player area: Avatar, Name, Score
- **Bottom Center:** Striker control bar:
    - Power/angle slider (visual cue on board)
    - "Shoot" button (disabled until ready)
    - Undo/Reset buttons (if allowed)
- **Corners:** Pocket highlight (gold rim flash upon successful pocket)
- **Overlays (top/margin):**  
    - Current turn indicator (highlighted background, color-coded)  
    - Queen capture requirement status (icon + text)  
    - Remaining coins display (icon + count)
- **Toast notifications:** Center-top fade-in for events (e.g., "QUEEN POCKETED! Cover with next shot")

**Responsiveness:**
- On mobile: Board shrinks, controls split left/right of board, minimal text.

### C. Game Over Screen

- **Full width translucent overlay**
- **Center Card:**  
    - "Winner: [Player Name]" with avatar and big score  
    - List: Final scores (styled, large digits, player icons)  
    - Trophy icon (particle fireworks animation)  
    - Buttons: "Play Again", "Main Menu", "Share"

-----

## 4. Animation & Transition Specifications

### A. Board & Coin Animation

- **Coin Movement:** Physics-driven, easing functions for bounce and sliding; subtle coin spin (z-rotate, 3D illusion)
- **Striker Aim:** Draw semi-transparent trajectory arc while aiming; fade out on shot
- **Pocket Event:** 
    - Quick coin shrink + fade into pocket
    - Gold ring flash (1s, ease-out)
    - Small particle burst ("sparkle" confetti) on queen pocket
- **Queen Pop:** Unique red glow upon pocket + light pulse for coverage phase start

### B. UI Transitions

- **Menu & overlay cards:**  
    - Slide/fade pop-in (0.35s, `ease-in-out`)
    - Buttons: Raised on hover/tap, subtle shadow cast, "press" animation shrinks slightly (scale to 0.97x)
    - Toaster: Slide down from top, auto-fade after 2s (anim: 0.3s)
- **State changes:**  
    - Dim background briefly on turn change; player highlight "bounce" effect.

### C. Responsiveness/Motion rules

- Disable rapid multiple presses; lock UI until animation complete.
- Motion-Reduced mode (OS respect): All non-essential animations switch to fade/transparency only.

-----

## 5. Visual Effects & Particle System

### A. Coin Interactions
- **Pocket Sparkle:**  
    - On coin entering pocket, emit 6–10 small gold (#FFCE54) particles expanding out then fading (anim: 0.4s)
    - For the queen, use red+gold particles, slightly larger
- **Striker Impact:**  
    - Small white/blue radial pulse under striker at the moment of release
- **Win Event:**  
    - Fireworks splashes (green/yellow stars) around winner name/trophy in Game Over screen.

### B. UI Effects

- **Button Feedback:**  
    - Glow outline (#2697F3) animating inwards on focus/tap
- **Special Notifications:**  
    - Overlay screen with semi-transparent white when displaying blocking messages

-----

## 6. Icon and Sprite Design Guidelines

### A. General Style

- **Visual Language:** Flat with soft drop shadows, minimal gradients, hand-drawn textures on edges for warmth
- **Stroke:** 1.5px outline, #68451B for coins/board elements
- **Margin:** Design all sprites with safe zone for high-DPI screens

### B. Assets

- **Coins:**  
    - Round with distinct rim, top-down view
    - White has subtle marble swirls (#FDFCF7 base, #E8E6DD accent)
    - Black is matte, inner rim highlight (#343434 on #2C2C2C)
    - Queen: Red base, gold rim, minimal crown emblem
- **Striker:**  
    - Larger, circular, pale body (#EFEFEF) with blue rim
- **Board:**  
    - Realistic wood grain texture (repeatable), darker border, 4 clear round pockets (shadow inside), gold scoring marks
- **Pockets:**  
    - Black elliptical depth inside, gold outer ring for accent
- **Buttons:**  
    - Rounded rectangles, beveled edges, modern glass shadow
- **Avatars:**  
    - Neutral geometric shapes or upload option
- **Other Icons:**  
    - Trophy, pause, undo, settings, info/help, accessibility

### C. Export Specifications

- **Format:** PNG @ 2x and 3x resolution, SVG for flat UI icons
- **Safe zones:** 10% margin transparent padding on each asset
- **Naming:** kebab-case, e.g. `coin-white.png`, `button-play.svg`

-----

## 7. Accessibility Considerations

- **Color Contrast:** All text on backgrounds min 4.5:1 ratio; use color + icon signifiers for feedback (not color alone)
- **Font Sizes:** Minimum text size 14px/0.875rem, scalable with browser/OS zoom
- **High Contrast Mode:** Toggle in accessibility menu; swaps background to #222222 and text to #FDFCF7, UI blue accent to #00E0FF
- **Screen Reader/ARIA:** All buttons, dynamic score/status fields labeled with `aria-label`
- **Focus Order:** Tab order logical; visible focus ring (2px blue outline)
- **Motion Sensitivity:** Toggles to reduce animation (see Animations)

-----

## 8. Mobile-Responsive Design Principles

- **Fluid Layout:** Board resizes, always centered, shrinks to fit viewport; UI controls float to sides or bottom
- **Min Touch Target:** All tappable elements min 48x48px
- **Gestures:** Striker can be aimed with touch-drag, power set by swipe length or on-screen slider
- **Font Resize:** Rem units with step scaling for device DPI
- **Viewport Meta:** `width=device-width, initial-scale=1.0`
- **Hide on Mobile:** Non-essential overlays (descriptions, avatars) may collapse or become slide-outs

-----

## 9. Implementation Recommendations

- **Assets:**  
    - Use SVG for all icons/UI elements, raster PNG for large art (board, coins); support for swapping in alternate skins
- **Screen Scaling:**  
    - Implement scaling containers to automatically adjust board/UI for window/device size, maintaining proportions
- **State-driven UI:**  
    - Menu/UI display uses state machine as in code architecture for overlays/modals
- **Physics Layer:**  
    - Coin positions and board render are separate; UI overlays (e.g. aim lines) are drawn in UI layer atop game view
- **Accessibility:**  
    - OS color schemes and motion preferences should be detected where possible; allow user overrides in Settings
- **Testing:**  
    - Run on standard devices (PC/tablet/phone); run accessibility audit using browser tools and simulated navigation

-----

## 10. Appendix: Layout Wireframes

**A. Main Menu (Desktop):**
- Center card (480px wide), logo above, stack of 4 buttons, wide-spaced.
**B. Game Screen (Landscape):**
- Fixed square board, sidebar for player info (if 2, L-R; if 3–4, corners/top as icons). Bottom bar for aiming controls.
**C. Game Over:**
- Centered winner card; background dims; score table prominent; confetti/firework FX on card.

(*If mockup graphics necessary, create in Figma or Sketch per above structure; use given color/typography for all screens.*)

---

**End of UI/UX Design Specifications**  
Ready for implementation as described in the software architecture. All color/font codes, layout guides, interaction details, accessibility principles, and asset standards are prepared for direct use by developers and artists.