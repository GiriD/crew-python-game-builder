---

# Carrom Board Game: Comprehensive Audio System Design Document

## 1. Overview

This document details the audio system for a digital Carrom Board Game. Specifications include a complete library of sound effects, musical requirements and cues, audio implementation mapping to game events, feedback system integration, file format recommendations, mixing/balance strategies, performance considerations, and guidelines for integration (e.g., with pygame’s mixer module).

Target Goals:
- Recreate the tactile, wood-on-wood sensation of physical Carrom.
- Enhance user feedback and immersion without distraction.
- Support accessibility, configurability, and high performance on typical hardware.


---

## 2. Sound Effect Library Specifications

### 2.1. Essential Sound Effect List

| SFX ID | Name                       | Trigger/Event                                            | Description / Notes                                                             |
|--------|----------------------------|----------------------------------------------------------|---------------------------------------------------------------------------------|
| SFX01  | Striker Aim Start          | Striker selected for aiming                              | Soft, anticipatory pluck or brush sound                                         |
| SFX02  | Striker Pull Back          | Player pulls striker to aim                              | Rising frictional sliding sound (damped, not loud)                              |
| SFX03  | Striker Release / Shoot    | Player releases striker to shoot                         | Distinct striker snapping or thwack sound (primary tactile feedback)            |
| SFX04  | Striker Hits Coin          | Striker collides with any coin (initiate physics)        | Solid wooden click/knock (short, clear)                                         |
| SFX05  | Coin Hits Coin             | Coin-to-coin collision during physics                    | Lighter click, softer than striker, randomize slightly for variation            |
| SFX06  | Coin Hits Board Edge       | Coin or striker bounces off edge/wall                    | Dull wooden thud (with subtle resonance), volume based on speed                  |
| SFX07  | Coin Pocketed (normal)     | Coin falls into pocket                                   | Coin dropping into cup/small pit, with short wood scrape (distinct from Queen)  |
| SFX08  | Queen Pocketed             | Queen is pocketed                                        | Slightly more resonant/tinkly drop, with subtle chime overlay                   |
| SFX09  | Coin Settling Stop         | Coin comes to rest (optional, when all stop moving)      | Very subtle, brief scrape or “shush” sound                                      |
| SFX10  | Turn End                   | All coins stopped, game state advances                   | Short, soft notification “ding” (non-intrusive)                                 |
| SFX11  | Invalid Action/Error       | Illegal move, invalid input                              | “Thud” or soft buzz, subtle, non-annoying (not loud buzzer)                     |
| SFX12  | Score Updated              | Player score changes                                     | Soft reward jingle, optional                                                    |
| SFX13  | Queen Cover Success/Fail   | Cover move attempt (success/fail)                        | Short celebratory chime (success), soft descending “uh-oh” tone (fail)          |
| SFX14  | Game Start                 | Game loading, first turn                                 | Very brief, classic Carrom “wood tap” and intro “flourish”                      |
| SFX15  | Game Over/Victory          | Game finishes, player wins/match ends                    | Short victory jingle (layered with board ambience), end credits theme           |
| SFX16  | Menu/UI Button             | Menu navigation, buttons                                 | Muted click, with slight variation for realism                                  |
| SFX17  | Inactive Background Ambience (optional) | During menus, board idle                     | Ambient boardroom or soft indoor crowd noise (very low level, looped)           |

### 2.2. Variation & Randomization
- For repeated actions (STRIKER/COIN hits), create 3–5 slightly randomized versions to avoid repetitiveness.
- Volume attenuation/envelope for distance/intensity (e.g. weak hits → softer).
- Layering: Combine base thud/click with light reverberation or wood resonance.

### 2.3. Spatialization (Stereo Panning)
- If feasible, pan hit/pocketing sounds based on object X position on board (left/right).
- Simple: map board X coords to left/right pan in pygame.mixer channel.


---

## 3. Background Music Requirements

### 3.1. Music Style & Mood
- **Style:** Light, acoustic, relaxing. Incorporate Indian/ethnic acoustic elements (e.g., tabla, sitar, hand percussion) but avoid overpowering.
- **Mood:** Casual, welcoming, focused, with subtle competitive undertones during turns.

### 3.2. Tracks & Loops

| Track Type          | Length      | Looping | Usage                                                                                |
|---------------------|-------------|---------|--------------------------------------------------------------------------------------|
| Main Menu Theme     | 30–60 sec   | Yes     | On main/menu screens; calm, inviting, no jarring intros.                             |
| Gameplay Loop       | 2–3 min     | Yes     | During turns/play; stay minimal to not mask SFX, can become more energetic per turn.  |
| Victory/Result Theme| 15–30 sec   | No      | On game end, winner screen, lightly celebratory but dignified.                        |

### 3.3. Transitions and Ducking
- Fade-in/out on music when switching between screens or scenes.
- Use ducking: Lower (attenuate) music volume briefly upon major SFX (esp. “Striker Shoot”, “Queen Pocketed”, Victory).

### 3.4. Optional Advanced
- Adaptive stingers (short accent motifs) when critical coins are pocketed (Queen), for heightened player feedback.

---

## 4. Audio Feedback System Design

### 4.1. Event Mapping

Every important in-game event must trigger immediate, corresponding sound, mapped as follows:

| Game Event                           | Audio Event/SFX                   | Notes                                                  |
|---------------------------------------|-----------------------------------|--------------------------------------------------------|
| Enter “AIM” State                     | SFX01: Aim Start                  | Subtle pluck/cue                                       |
| Start Pulling Striker                 | SFX02: Pull Back                  | Dynamic based on pull strength (optional)              |
| Release Striker (Shoot)               | SFX03: Shoot                      | Priority, no latency                                   |
| Striker hits coin                     | SFX04: Striker Hits Coin          | Mix with SFX05 for multi-object collision              |
| Coin–coin collision                   | SFX05: Coin Hits Coin             | Layered for multiple coins hit simultaneously          |
| Coin hits board edge                  | SFX06: Coin Hits Board Edge       |                                                        |
| Coin pocketed                         | SFX07: Coin Pocketed              | For Queen use SFX08                                    |
| Queen pocketed                        | SFX08: Queen Pocketed             | Add stinger if using adaptive music cues               |
| All coins/striker at rest             | SFX09: Coin Settling Stop         | Audio cue for next state OR turn end                   |
| End of turn (TURN_END)                | SFX10: Turn End                   |                                                        |
| Invalid move/error                    | SFX11: Invalid Action/Error       |                                                        |
| Score update                          | SFX12: Score Updated              | Optional jingle                                        |
| Queen cover attempt                   | SFX13: Queen Cover Success/Fail   | Two variants; depends on game logic outcome            |
| Game start/init                       | SFX14: Game Start                 |                                                        |
| Game over/victory/defeat              | SFX15: Game Over/Victory          |                                                        |
| UI menu navigation                    | SFX16: Menu/UI Button             |                                                        |
| On menu/board idle                    | SFX17: Ambience                   | Looped, very quiet                                     |

### 4.2. Immediate Feedback Criteria
- **Timing:** All non-music SFX must play with no perceptible delay (<50 ms preferred, as close to 0 as possible using pygame.mixer).
- **Mix Priority:** During core gameplay, SFX always take precedence (duck background music on "heavy" SFX triggers).

### 4.3. Accessibility & Settings
- Separate music and SFX volume sliders in settings UI.
- “Mute All” toggle plus SFX-only or Music-only toggles for accessibility.
- Optional “minimal sound” mode: disables background music and ambient tracks for single-device games.


---

## 5. Audio Implementation Guidelines

### 5.1. File Format & Quality

#### 5.1.1. Formats

| Content Type | Format(s)           | Bitrate / Sample Rate            | Notes                                    |
|--------------|---------------------|----------------------------------|------------------------------------------|
| SFX          | `.ogg` (primary), `.wav` (fallback) | 44.1 kHz, 16-bit PCM (mono/stereo)      | `.ogg` for size/looping, `.wav` for low latency (pygame) |
| Music        | `.ogg`              | 44.1 kHz, minimum 96kbps (128+ preferred), stereo | Fade in/out at loop points for seamless cycling |

#### 5.1.2. Performance & Loading
- Preload core SFX at game start (keep lightweight).
- Stream background music if long (do not load entire tracks if large).
- Use separate channels for SFX and music in pygame.mixer.
- Keep peak concurrent SFX below 8–12 (for most systems).

### 5.2. Timing and Synchronization

- All SFX must be triggered from event callbacks in game logic (e.g., after physics resolves a collision or turn state changes).
- Use Pygame’s pygame.mixer.Channel for layering (e.g., assign distinct logical channels: SFX, music, ambience).
- Fade & cross-fade music over 300-800 ms for scene transitions.
- If physics simulation is slow/capped, ensure SFX are not delayed; fire "hits" as soon as colliders report events.

### 5.3. Mixing and Balance

#### Default Mix Levels (Relative)

| Track Type       | Relative dB (ref. 0dB) | Description               |
|------------------|-----------------------|---------------------------|
| Striker Shot     | 0 dB                  | Prominent on shot         |
| Coin Hits        | -4 dB                  | Layered, secondary        |
| Pocketed Coin    | -2 dB                  | Satisfying, clear         |
| Menu/UI SFX      | -6 dB                  | Non-distracting           |
| Game Music       | -12 to -18 dB          | Subtle, out of way        |
| Ambience         | -18 to -24 dB          | Barely audible            |
| Error/Invalid    | -1 dB                  | Prominent but non-shrill  |

- Headroom: Avoid SFX peaks >-1 dBFS; normalize all exported assets.
- Compress long audio tracks gently to prevent huge volume swings (for consistency).
- Avoid overlaps: gracefully cut or fade a previous SFX if new, more important SFX triggers on the same channel.
- For multi-coin hits within one frame, play strongest/loudest SFX, then weakest or layer with gain reduction.

---

## 6. Audio Event Mapping (Code-level)

Example: How various game events connect to audio system (pseudo-code for integration with pygame.mixer):

```python
# Inside relevant system (e.g. PhysicsEngine or Scorer)
if state == GameState.SHOOT and striker.collides_with(coin):
    audio_system.play('striker_hit_coin', pan=striker.x_pos/board.width)
if board.coin_is_pocketed(coin):
    if coin.is_queen:
        audio_system.play('queen_pocketed')
        audio_system.duck_music(duration=1.0)
    else:
        audio_system.play('coin_pocketed')
if state == GameState.TURN_END:
    audio_system.play('turn_end')
# UI button
input_handler.on_menu_click = lambda: audio_system.play('menu_button')
```

- Use a centralized AudioManager with event subscriptions (observer pattern).
- Expose `play(sfx_name, pan=None, volume=None)` interface.
- For settings, allow dynamic adjustment of SFX/music volume via expose_audio_settings().

---

## 7. Performance Considerations

- Minimize file sizes for mobile/low-end platforms by compressing SFX to OGG (mono if not spatialized).
- Batch load SFX assets, but stream music (avoid memory spikes).
- Prevent audio stutter: don’t load new SFX from disk during gameplay, keep file handles open.
- For coin pools/object reuse: clean up or release SFX only when object truly exits play (object pooling compatible).
- Use fixed number of audio channels, prioritize SFX, override least important ones if all are busy.
- Use dirty rects technique for graphics does not affect audio, but keep audio polling decoupled from render loop.

---

## 8. Audio Assets Folder Organization

```
/assets/audio/
    /sfx/
      striker_aim_start1.ogg
      striker_aim_start2.ogg
      striker_shoot1.ogg
      coin_hit1.ogg
      coin_hit2.ogg
      coin_pocketed.ogg
      queen_pocketed.ogg
      ...etc.
    /music/
      main_menu.ogg
      gameplay_loop.ogg
      victory_theme.ogg
    /ambience/
      boardroom_idle.ogg
config/
    audio_settings.json
```

---

## 9. Audio System Scalability and Extensibility

- Easily add new SFX for power-ups, new coin types, alternate board skins.
- Support for downloadable “sound packs” by keeping assets referenced by ID (not hard-coded path).
- Extend event mapping via config files (sound-event mapping in JSON).

---

## 10. Audio API (pygame Mixer) – Core Integration Guidelines

- Mixer initialization: `pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)`
- Preload SFX as `pygame.mixer.Sound` objects.
- Music: Use `pygame.mixer.music` for looped background tracks. Music loaded/streamed, not all in RAM.
- Channels: Use `pygame.mixer.Channel(n)` for SFX grouping (e.g., one for main shots/hits, one for UI, one for ambience).
- Pan implementation (if desired): adjust left/right channel volumes based on object X position.
- Attach audio events via observer pattern: systems (Physics, Scorer, InputHandler) notify AudioManager.

---

## 11. Accessibility and User Settings

- Sound/Music volume sliders and mute.
- Option to turn off/enable individual categories (Music / SFX / Ambience).
- Optional “High Contrast Audio” mode: increases SFX/mutes music for low visibility situations.

---

## 12. Reference & Testing

- Ensure consistent mix on reference speakers/headphones.
- Test on at least 2 output scenarios: laptop speakers (mid/low end), headphones (full-range).
- Extensive QA to verify SFX triggers always on correct event (esp. simultaneous/rapid coin interactions).

---

## 13. Summary Table: Asset Mapping

| SFX ID | Sample Name                 | Event Hook                                   | Mixing Level (dBFS) | Pan        |
|--------|-----------------------------|----------------------------------------------|---------------------|------------|
| SFX03  | striker_shoot1.ogg          | Striker release/shot                         |  0                  | Based on X |
| SFX04  | striker_hit_coin1.ogg       | Striker/coin collision                       | -4                  | Based on X |
| SFX07  | coin_pocketed.ogg           | Coin falls in pocket                         | -2                  | Based on X |
| SFX08  | queen_pocketed.ogg          | Queen pocketed                               | 0                   | Based on X |
| SFX15  | victory_theme.ogg           | Game over – winner                           | 0 (music)           | Center     |
| SFX16  | menu_click1.ogg             | UI button/menu                               | -6                  | Center     |
| etc.   | ...                         | ...                                          | ...                 | ...        |

---

# End of Audio System Specification

---