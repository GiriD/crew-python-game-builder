# Kabaddi Game – Comprehensive UI/UX Design Specifications

---

## 1. Color Palette

A fresh, sporty, and professional color palette designed for clarity, energy, and inclusive visibility. All main colors pass WCAG AA accessibility contrast thresholds.

| Purpose                | Name           | Hex        | Usage Description                                     |
|------------------------|----------------|------------|------------------------------------------------------|
| Primary Team A         | Kabaddi Red    | #D84315    | Court edge, Team A uniforms, accent elements         |
| Primary Team B         | Kabaddi Blue   | #1976D2    | Court edge, Team B uniforms, accent elements         |
| Neutral BG             | Court Sand     | #FBE9E7    | Court, background, info areas                        |
| Secondary Accent       | Sport Gold     | #FFD600    | Scoreboard, buttons, highlights                      |
| System UI              | Slate Gray     | #263238    | Main buttons, dark text, overlays, panel backgrounds |
| Disabled/Secondary     | Silver Gray    | #B0BEC5    | Disabled controls, secondary info                    |
| Positive               | Turf Green     | #388E3C    | Success events (successful raid)                     |
| Negative               | Alert Orange   | #FF6F00    | Failure events (out, tackle)                         |
| Breath Meter Full      | Fresh Cyan     | #00BCD4    | Active breath zone                                   |
| Breath Meter Low       | Danger Red     | #FF5252    | Warning breath zone                                  |
| Text/Icons             | White          | #FFFFFF    | High-contrast details, overlay text                  |

**Notes:** Avoid using color alone for feedback; all states have icon, label, and/or animation support.

---

## 2. Typography System

### Font Family Guidelines

- **Headings & Scoreboard:** `Montserrat Bold`, fallback: `Arial Black`, system: sans-serif
- **Body Text, Buttons:** `Roboto Medium`, fallback: `Arial`, system: sans-serif
- **Labels & Microcopy:** `Roboto Regular`, system: sans-serif

### Sizes and Weights

| Use                    | Font           | Size(px) | Weight        | Notes                        |
|------------------------|----------------|----------|--------------|------------------------------|
| Main Title             | Montserrat     |   36     | Bold         | Menu/Game Over screens       |
| Round Label            | Montserrat     |   28     | Bold         | Top of play screen           |
| Scoreboard Numbers     | Montserrat     |   32     | Bold         | Prominent center/side        |
| Button Text            | Roboto         |   20     | Medium       | All interactive buttons      |
| Player Names/Stats     | Roboto         |   18     | Regular      | Overlays, court, subs        |
| Time/Breath Meter      | Roboto         |   16     | Regular      | HUD                          |
| Microcopy/Small Label  | Roboto         |   14     | Regular      | Tooltips, instructions       |

**Letter Spacing:**  
- Headings: 0.03em  
- Button text: 0.02em  
- Body text: normal

**Accessibility:**  
- Minimum text contrast ratio 4.5:1  
- All fonts legible on Sand (#FBE9E7), Slate (#263238), and Blue (#1976D2) backgrounds.

---

## 3. Screen Layout Designs & Descriptions

### 3.1. Main Menu Screen

#### Structure
```
[ Kabaddi Game Logo ]
        |
  [ Start New Match ] (Primary Button)
  [ Team Management ] (Secondary Button)
  [ Settings ]        (Icon, top-right)
  [ How to Play? ]    (Secondary Button)
        |
[ Team A vs Team B Badge ]
        |
[ Footer: Version, Accessibility Link, Credits ]
```

#### Layout Details
- Central vertically-stacked buttons, large touch targets.
- Team badges side-by-side below menu; colored, prominent.
- Minimal background, light Sand/Slate gradient, subtle Kabaddi sport motif.

### 3.2. Gameplay Screen

#### Top Section:
- **Scoreboard Bar:** Centered; Team A (Red) – Score – Team B (Blue)
  - Large numbers, team names (avatars).

#### Main Court Area:
- **Kabaddi Court:** Top-down rectangle, two halves clearly separated by a center line.
  - Court outlined in Team A/B colors (#D84315, #1976D2).
  - Sand (#FBE9E7) fill with faint grid pattern.
  - Player sprites: Circular avatars with jersey numbers, colored by team.
  - Raider: Dynamic border highlight (cyan when breath full, red as breath gets low), "Raider" icon overlay.
  - Defenders: Resting state icons, animated into tackle stance when near raider.

#### Left/Right Side HUD:
- **Breath Meter:** Animated bar with icon, raider's portrait, numeric breath/time left.
- **Current Round:** Top-center, round/time display (large font).
- **Active Substitution:** If substitution in progress, pop-up overlay in court area, semi-transparent.

#### Bottom Section:
- **Action Buttons:** For touch: Move, Tag, Retreat (raider); Tackle (defenders if player-controlled).
- **Pause/Button Bar:** Left corner; Settings, Quit, Resume.
- **Instruction Strip:** Context messages, e.g. "Tap/Tap arrow keys to move Raider!", shown above buttons.

### 3.3. Game Over Screen

- Center: "Game Over!" with winner's badge, final scores, team/raider MVP.
- Action: [ Replay Match ] (Primary), [ Menu ] (Secondary), [ Share Score ] (icon button)
- Panel: "Summary of Raids", successful/failed tackles, substitutions, breath stats.

### 3.4. Team Management Screen

- Two team panels: Editable names, drag-and-drop/sub in/out, preview formation.
- Player avatars, jersey selection (dropdown), stats shown inline.

### 3.5. How to Play/Settings

- Modal or full screen overlay; step-by-step with icons and annotated diagrams.
- Accessibility options: Colorblind modes, text resize slider, sound toggles.

---

## 4. Animation & Transition Specifications

| Element               | Animation Type              | Duration(ms) | Easing    | Notes                                         |
|-----------------------|----------------------------|--------------|-----------|-----------------------------------------------|
| Button Press          | Scale down/up ripple       | 120          | EaseOut   | Material ripple, colored by button type       |
| Screen Transition     | Slide in/fade out panels   | 350          | EaseInOut | Menu <-> Game, panels move left/right         |
| Raider Movement       | Sprite lerp + trails       | per input    | EaseOut   | Leave fading traced line, shows direction     |
| Tag/Tackle Effect     | Quick pulse + particle     | 180          | Linear    | Brief burst, shows event feedback             |
| Breath Meter Change   | Smooth width + color shift | 280          | EaseOut   | Meter shrinks/grows, color animates           |
| Score Change          | Pop number, bounce         | 220          | EaseOut   | Number animates on change                     |
| Raider Out/Win        | Fade, scale, confetti      | 400          | EaseOut   | When outcome decided, show celebration/warn   |
| Overlay Panels        | Fade in/out, slide         | 300          | EaseInOut | e.g., substitution overlay                    |

---

## 5. Visual Effects & Particle System

- **Tag/Tackle Event:**  
  - Small burst of colored confetti/particles at event location, e.g. cyan for tag, orange for tackle.
  - Sound effect sync: short 'whoosh' + kabaddi chant stinger.

- **Breath Meter:**  
  - Pulsing outline, glow effect as breath approaches danger.
  - When breath low (< 20%), periodic shake + flashing warning icon.

- **Score Pop:**  
  - Animated number rise and fade at scoreboard, particle trail (gold).

- **Court Ambient:**  
  - Occasional sparkles or dust puff near movement hotspots, mild, not distracting.
  - Center-line shimmer effect at round start.

- **Victory/Defeat:**  
  - Win: Confetti arc, gold sparkle fills screen edge.
  - Lose: Fade screen to gray, subtle falling 'sand' particles.

---

## 6. Icon & Sprite Design Guidelines

- **Players:**  
  - Simple top-down or isometric circle/silhouette, team color jersey, number/initial label, clear differentiation for raider/defender (border, background halo).
  - Size: min 48x48px for clarity (mobile/desktop).

- **Buttons:**  
  - Material-style icons: Play, Pause, Quit, Info, Settings.
  - Shapes: Rounded corners, 8px radius, 4px padding.
  - Consistent visual language for interactive (primary: gold, secondary: gray).

- **Breath Meter/Status:**  
  - Breath: horizontal bar with stylized lungs icon; dynamic fill by breath %.
  - Tackle/Tag: Lightning bolt (tag), shield (tackle), pop-up above player.

- **Team Badges:**  
  - Simple crest: circular, colored, team icon in center (kabaddi ball / flames / star).

- **Accessibility:**  
  - All icons must have alt text/tooltip descriptions.
  - Contrasting icon color backgrounds; border/halo for low-vision support.

---

## 7. Accessibility Considerations

- **Colorblind mode:**  
  - Swap Team Red/Blue with alternative palette (e.g. Orange #FF9800, Green #4CAF50)
  - All action feedback (tag/tackle/breath low) paired with icon/sound, never color alone.

- **Text Resizing:**  
  - Implement global scale slider in Settings (1x to 1.5x, min 14px).

- **Touch Targets:**  
  - All interactive elements minimum 44x44px.

- **Screen Reader Labels:**  
  - Main navigation, buttons, HUD overlays, event messages annotated.

- **Motion Sensitivity:**  
  - Optional animation reduction toggle; disables non-essential transitions.

- **Contrast:**  
  - Critical info always on slate/white background, never over visual clutter.

---

## 8. Mobile Responsive Design Principles

- **Fluid Layout:**  
  - Use flex layouts for all panels; stack vertically on mobile, side-by-side on wide screens.
  - Auto-scale court and HUD, keep minimum HUD margins 16px.
  - Action buttons bottom-aligned for thumb reach on mobile.
  - Responsive sprites/icons: scale by screen DPI, retain crispness.

- **Orientation:**  
  - Landscape encouraged for gameplay; adapt to portrait for menu/settings.

- **Safe-area Awareness:**  
  - All UI elements within safe zone margins; ensure no controls in notch/cutout area.

- **Touch Input:**  
  - Swipe gestures for menu navigation, tap/hold for player movement (optional).

---

## 9. Asset Creation Guidelines

- **Sprites:**  
  - SVG/vector preferred for scalable crispness.
  - Export fallback PNG @1x, @2x, @3x.

- **Court:**  
  - 16:9 aspect target, simple geometric shapes, high contrast center line.

- **Interface Widgets:**  
  - All buttons/controls with focused and pressed state variants.

- **Icons:**  
  - Clean, consistent line thickness (2px), simple forms, 24, 32, 48px variants.

- **All Assets:**  
  - Provide both dark and light background variants.

---

## 10. Implementation Notes for Developers

- Structure components/screens per the architecture blueprint.
- Centralize theme variables (colors, font sizes) for maintainability.
- All states/events to route through state machine for consistent UI updates.
- Use game’s Observer pattern to propagate UI changes (event triggers score pop, animation, sound).
- Ensure lazy loading of particle/sound assets; optimize for mobile by batching/cleanup.
- All screens/components to be unit-testable.

---

## 11. Visual References (Text Guideline)

- Main Menu: Simple, large logo at top. Gold-accented button stack, clear safe margins.
- Gameplay: Spacious, clean court. Animated avatars. Top bar for scores/round/time. Side HUD for breath/substitution.
- Game Over: Centered result, bright winner highlight, clean actionable buttons.
- Team Management: Two panels, drag-and-drop for substitutions, clearly marked actions.

---

### This UI/UX spec provides all developer direction for visually stunning, professional, accessible, and engaging Kabaddi gameplay experience – ready for modern mobile and desktop platforms. For any additional requests (e.g., Figma/Sketch mockups, asset samples), specify format and required details.