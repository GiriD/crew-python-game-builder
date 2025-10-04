# Kabaddi Game – Comprehensive Audio System Design Document

## 1. Sound Effect Library Specifications

### Action/Event Sound Effects

| Game Event                        | Sound Description           | File Name (suggestion)         | Timing & Notes                                  |
|------------------------------------|----------------------------|-------------------------------|-------------------------------------------------|
| Menu navigation                    | Click, selection blip      | ui_menu_select.wav             | Immediate, on button/key press                  |
| Start round whistle                | Short referee whistle      | game_whistle_start.wav         | At round start                                  |
| End round whistle                  | Longer referee whistle     | game_whistle_end.wav           | At round end                                    |
| Player movement                    | Footsteps (soft/fast)      | sfx_footstep1.wav<br>sfx_footstep2.wav   | When raider/defenders move, loop/random scatter |
| Raider breath/chanting             | "Kabaddi, kabaddi…" loop   | raider_chant_loop.wav          | Looped while breath meter > 0                   |
| Breath running low                 | Warning beep/cough         | breath_warning.wav             | When breath meter < 25% (repeat at intervals)   |
| Tag event                         | Sharp tag sound (slap/pop) | tag_slap.wav                   | When tag occurs; sync to animation frame        |
| Successful tackle                  | Body hit/grapple grunt     | tackle_grunt.wav               | When defenders tackle raider                    |
| Raiders escapes tackle             | Quick exhale sound         | raider_escape.wav              | On successful escape                            |
| Out-of-bounds/foul                 | Short buzzer/crowd gasp    | foul_buzzer.wav                | When boundary rule broken                       |
| Scoring/Point award                | Score ding/crowd cheer     | point_award.wav<br>crowd_cheer.wav | When points given; after raid/tackle outcome    |
| Team substitution                  | Sub in/out whistle + crowd | substitute_whistle.wav         | On substitution                                 |
| Countdown ticking (last 10s round) | Accelerating clock tick    | timer_tick.wav                 | Loop ticks, increase rate final 3 seconds       |
| Game Over                         | Victory/fanfare music      | game_victory.wav<br>game_defeat.wav | At match completion                            |
| Pause/Resume game                  | UI swoosh/pulse            | ui_pause.wav<br>ui_resume.wav  | Immediate, on pause/unpause                     |

**File Format Recommendation**:  
- .wav, 16-bit PCM, mono or stereo (44.1 kHz) for real-time performance and zero latency with pygame.mixer.

### Ambient & Crowd Audio

| Event/Location           | Description           | File Name           | Behavior                  |
|-------------------------|-----------------------|---------------------|---------------------------|
| Stadium ambience        | Low crowd murmur      | crowd_ambience.wav  | Play low-loop, start of round |
| Excited crowd roar      | Intense cheer         | crowd_roar.wav      | On scoring, end-of-round  |
| Negative crowd reaction | Boo/gasp              | crowd_boo.wav       | On foul/out               |

Use layered volumes and fade-in/out for ambience when transitioning rounds.

---

## 2. Background Music Requirements

### Mood Settings

| Game State        | Mood/Style                | Track Name              | Looping Details                                 |
|-------------------|--------------------------|-------------------------|-------------------------------------------------|
| Main menu         | Upbeat, modern Indian pop | bg_menu_theme.wav       | Loop, fade as match starts                      |
| Round active      | Energetic, tense          | bg_round_action.wav     | Loop, looped per round, ducked for major SFX    |
| Raid phase        | Rhythm, heartbeat, suspense| bg_raid_phase.wav      | Overlay, ducked for raider chant or major SFX   |
| End round         | Triumphant/calm           | bg_end_round_theme.wav  | Fade in at round end, 5–15 sec length           |
| Game Over         | Victory/defeat themes     | bg_win_theme.wav<br>bg_lose_theme.wav | Play non-loop, fade out to credits              |

**Music File Format Recommendation**:  
- .ogg Vorbis for background tracks (compressed, efficient streaming).
- .wav for short, time-critical stingers (e.g., fanfare).

### Integration Guide

- Use pygame.mixer.music for main background tracks (.ogg).
- SFX and event stingers via pygame.mixer.Sound (.wav).
- Set `music.set_volume()` and `sound.set_volume()` separately for mixing.
- Support crossfade when switching tracks between states.

---

## 3. Audio Feedback System Design

### Interactive Audio Feedback Mapping

| UI Element/Game Mechanic      | Feedback Sound/Event         | User Action     | Result                                                |
|------------------------------|------------------------------|-----------------|-------------------------------------------------------|
| Raider breath meter           | Continuous chant             | Holding "kabaddi" key | Loop chant; stops/mutes when key released/leaves zone |
| Breath meter critical zone    | Warning sound/beep           | Meter <25%      | Play warning, visually highlight breath meter         |
| Collision/Tag                | Tag SFX                      | Raider tags defender | SFX plays, animation sync                             |
| Tackle Attempt               | Tackle grunt                 | Defender collides raider | On impact, SFX magnitude based on # defenders         |
| Points/Score change          | Ding + crowd cheer           | Score updated   | SFX, optionally pop up on UI                          |
| Pause/Resume                 | UI feedback pulse/swoosh     | Menu navigation | Immediate, avoids confusion                           |
| Game state change            | Whistle/fanfare              | Transition      | Triggers at round/game over, fade/fade-out music      |
| Timer urgent                 | Tick SFX                     | Last 10s of round | Ticking intensifies till round end                    |

**Volume Ducking:**  
- Auto-lower background music during raid phase, tag/tackle, crowd events.
- Prioritize breath/chant and point SFX over music.

**Settings UI Exposure:**

- Main menu: “Volume Settings” slider for:
    - Master Volume
    - Music Volume
    - SFX Volume
    - Mute/Unmute toggles
- Ensure settings are saved in config and reloaded.

---

## 4. Audio File Formats & Quality Recommendations

### File Type Guidelines

- **Sound Effects (SFX):** `.wav` recommended for instantaneous playback, mono/stereo as appropriate.
- **Music & Long Ambience:** `.ogg` for compression and streaming, stereo, 44.1 kHz.
- **Max file size for single SFX:** <250 KB
- **Music tracks:** Optimized for looping, <3 MB per track.

### Implementation Notes:

- Normalize all SFX to consistent loudness (LUFS -16 for game mix).
- Peak level: SFX –6 dBFS, Music –9 dBFS (leave headroom for mixing).
- All files named logically, stored in `assets/sounds/`.

---

## 5. Audio Event Mapping (Pygame Integration)

Here’s a mapping table for code implementation:

| Game Event                     | Pygame Handler            | Recommended Timing |
|------------------------------- |--------------------------|-------------------|
| All game SFX                   | pygame.mixer.Sound()      | Immediate         |
| Background music               | pygame.mixer.music.load() + play() | On state change   |
| Volume change/mute             | `.set_volume(val)`        | Via settings UI   |
| Looping ambient/chant          | `.play(loops=-1)`         | Start of round/raid|
| Music fade/crossfade           | `.fadeout(ms)` / `.set_endevent()` | On round/game transitions |

Example (Python):
```python
# Play sound effect
pygame.mixer.Sound("assets/sounds/tag_slap.wav").play()

# Start background music loop
pygame.mixer.music.load("assets/sounds/bg_round_action.ogg")
pygame.mixer.music.play(-1)  # loop indefinitely
pygame.mixer.music.set_volume(0.5)

# Duck music during SFX
def play_tag_sfx():
    pygame.mixer.music.set_volume(0.2)       # Lower music volume
    pygame.mixer.Sound("tag_slap.wav").play()
    pygame.mixer.music.set_volume(0.5)       # Restore music volume

# Fade out music at game over
pygame.mixer.music.fadeout(2000)             # 2 seconds fade
```

---

## 6. Mixing & Balance Guidelines

### Mixing Strategy

- **Relative Volumes**:
    - Tag/tackle SFX: Loudest, clear and immediate.
    - Breath/chant: Prominent during raid, lower when action stops.
    - Crowd/ambience: Medium-low, ducked for SFX.
    - Background music: Supportive, 30–60% of master volume.

- **Stereo Field:**
    - Place footstep/tackle/tag SFX in stereo field relative to raider’s in-game position.
    - Music and crowd: full stereo.
    - UI feedback/menu: Centered stereo.

- **Layered Playback:**
    - Allow up to 8 simultaneous SFX channels (pygame default: 8).
    - Assign priority: tag/tackle > breath > crowd > UI.

### Real-time Balance:

- Use automated ducking for crowd/music when action SFX trigger (sidechain or in code).
- Avoid clipping by keeping overall mix headroom.

### Performance Considerations

- Pre-load all critical SFX into memory before match start.
- Stream background music only.
- Use pooled Sound objects; avoid garbage collection overhead in main loop.
- Limit concurrent SFX on overlapping events (no more than 2 tag sounds same frame).

---

## 7. Performance & Optimization Notes

- **Initialization:**
    - Call `pygame.mixer.pre_init(44100, -16, 2, 512)` before pygame.init() for low latency.
- **Sound Pooling:**
    - Store all commonly used Sound objects in a dict; access without file I/O mid-game.
- **Asynchronous Loading:**
    - Load non-critical ambiences asynchronously/background thread during menus.
- **Memory Use:**
    - Set mixer buffer size to minimize delay; test across hardware.

---

## 8. Audio System Directory / Asset Management

Recommended assets directory:

```
assets/
    sounds/
        bg_menu_theme.ogg
        bg_round_action.ogg
        bg_raid_phase.ogg
        bg_end_round_theme.ogg
        tag_slap.wav
        tackle_grunt.wav
        breath_warning.wav
        raider_chant_loop.wav
        crowd_ambience.wav
        crowd_cheer.wav
        crowd_boo.wav
        game_whistle_start.wav
        game_whistle_end.wav
        point_award.wav
        timer_tick.wav
        substitute_whistle.wav
        ui_menu_select.wav
        ui_pause.wav
        ui_resume.wav
        game_victory.wav
        game_defeat.wav
```
All files named with clear prefixes and stored in respective subfolders for SFX/music.

---

## 9. Finalization Checklist

- [X] SFX library specification for all gameplay and UI events.
- [X] Music themes covering all game states, loop/fade design.
- [X] Feedback mapping and implementation logic (volume ducking, event triggers).
- [X] File format and size/quality recommendations.
- [X] Event mapping for code, performance/mixing notes.
- [X] Directory structure for easy asset management.
- [X] Guidelines for mixing, balancing, and optimization for reliable performance.

---

## 10. Example Summary Flow

1. **Game Start**: bg_menu_theme.ogg plays, UI SFX enabled.
2. **Round Initiates**: Whistle, crowd ambience, bg_round_action.ogg starts.
3. **Raider Raid Phase**: Breath chant loop, tag/tackle SFX, crowd reacts.
4. **Score Update**: Award SFX, crowd cheer overlays, music ducked briefly.
5. **Timer Ending**: Tick SFX intensifies.
6. **Round/Game End**: Whistle, crowd roar, end round music/fanfare.
7. **Menu/Pause/Settings**: All SFX and music routed through master volume/UI controls.

---

This comprehensive audio system blueprint enables the Kabaddi Game’s development team to create rich, responsive, player-focused audio—incorporating detailed event mapping, optimal asset handling, and mixing strategies, fully leveraging pygame’s capabilities for an immersive sports experience.