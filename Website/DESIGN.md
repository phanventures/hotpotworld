# Hot Pot World Rotary — design system

The visual world, and the rules that keep it coherent. Everything here is
implemented in `assets/css/style.css`; that file is the source of truth and this
document explains why it looks the way it does.

## The read

A local restaurant landing site for Seattle-area diners choosing tonight's
dinner. Mode is **Persuade**: the visitor decides and acts. The differentiator
is the conveyor belt, so the belt leads.

Dials: `DESIGN_VARIANCE 7 / MOTION_INTENSITY 5 / VISUAL_DENSITY 4`.
The site this replaced read roughly 3 / 1 / 4.

## Theme

**Bands alternate dark and light, strictly, from the first section after the
fact strip to the last.** Hero, fact strip, header and footer stay dark. This
replaced the all-dark lock on 2026-08-20: one theme top to bottom read as heavy.

A light band is `.section--light`, and it works by **re-declaring the tokens**
(`--void`, `--surface-2`, `--bone`, `--bone-dim`, `--red-ink`, the lines) on
the band, so every component inside inverts with no rules of its own. Do not
write component-level light overrides; if something looks wrong on a light band
it is a literal colour that should have been a token. Light bands also set
`color-scheme: light` so form controls follow.

Light palette: page `#F6F2EC`, panels `#FFFFFF`, ink `#141210` (16.76:1),
dim ink `#5C544E` (6.65:1), small red `#B3212A` (5.94:1). Brand red fills are
unchanged and read 5.29:1 on the light page.

## Colour

| Token | Value | Use |
|---|---|---|
| `--void` | `#0E0D0C` | Page. Warm-tinted off-black, never pure black. |
| `--surface` | `#171413` | Raised bands, header, footer. |
| `--surface-2` | `#221D1B` | Panels sitting on a band. |
| `--line` | `#2E2825` | Hairlines. |
| `--bone` | `#F2EDE7` | Body text. 16.68:1 on void. |
| `--bone-dim` | `#B3AAA3` | Secondary text. 8.50:1 on void. |
| `--red` | `#C0262E` | The one accent. Fills and large type only. |
| `--red-deep` | `#96181F` | Pressed and hover states. |
| `--red-ink` | `#F0565C` | Small type on dark. 5.72:1 on void, 4.91:1 on panels. |

**One accent, locked.** Brand red is sampled from the logo artwork, not chosen,
and it is the only colour on the site. Nothing else is tinted.

The red splits into two tokens for a reason worth remembering: `#C0262E` on the
page background is **3.29:1**, which passes AA for large text and UI fills but
fails for body copy. Anything small and red uses `--red-ink` instead. Do not
collapse these back into one value.

Every pair above was measured, not eyeballed. Ratios live in comments beside the
declarations so the next edit can see what it is about to break.

## Type

**Be Vietnam Pro**, self-hosted, weights 400 / 600 / 800. SIL Open Font
License, copy at `assets/fonts/OFL.txt`.

Chosen because the menu names carry Vietnamese diacritics (Thực Đơn, Nước Lẩu,
Lẩu Tứ Xuyên) and most display faces render them badly or not at all. It is
drawn by a Vietnamese foundry for exactly this. Latin, latin-ext and Vietnamese
subsets are split into separate files by unicode-range, so a visitor who never
hits a Vietnamese glyph never downloads that file. The whole family is 104 KB.

Self-hosting is not a preference, it is the site's architecture: no page makes
an external request on load.

Emphasis inside a headline uses weight or italic of this same family. Never a
second family.

- Display: 800, `letter-spacing: -.022em`, `line-height: 1.08`.
- Body: 400 at 17px, `line-height: 1.65`.
- The `.vn` Vietnamese line under an English name: italic, `--red-ink`, sized
  `max(1rem, .34em)`. The floor matters: a bare `.34em` of a fluid heading falls
  to about 10px on a phone, under the legibility floor. These are menu names.

## Shape

Buttons are full pill. Everything else is 14px, 10px for small media. That is
the whole rule, and it is applied everywhere.

## Layout

**The site is one page.** The nav scrolls to sections rather than loading
documents, which suits a restaurant: the visitor's whole decision (what is it,
is it hard, what does it cost, where is it) fits in one scroll.

Two consequences the code has to honour. Anchor targets carry
`scroll-margin-top: 84px` so a jump clears the 68px sticky header. And the nav
marks the section you are in via `aria-current`, set by an IntersectionObserver
watching a thin band across the upper middle of the viewport. Both live in
`main.js` and the `[id]` rule; see README for the ids they depend on.

Sections alternate dark (`--void`) and light (`.section--light`) bands. Each band is a full-width
element containing a `.shell` (max 1220px) which carries the horizontal padding.

**No layout family repeats back to back, and no image-and-text split runs three
times in a row.** The page runs through full-bleed hero, utility fact strip,
moving belt strip, asymmetric split, numbered editorial rows, notice panel,
grouped typographic columns, mixed-size gallery grid, full-width media,
a row of the four real Restaurant Guru badges with a press list and unboxed two-column quotes, panel trio, form split, and a directions
band. Splits are always broken up by a different family within two.

Two specific bans that the old site tripped:

- **No three equal feature cards.** The three steps are rows on hairlines with
  large outlined numerals, not boxes.
- **Long lists get a different component.** Nine broths are grouped into three
  named clusters, not a nine-cell grid.

Eyebrows (the small tracked-caps label above a heading) are rationed to **one
per three sections per page**, and never above an `h1`. The old site had one
above nearly every section, which is the single most recognisable tell of a
templated page.

## Motion

One piece of ambient motion on the whole site: `.beltstrip`, a strip of plate
photographs sliding horizontally under the hero.

It earns its place because it is a picture of the product. Plates move past you
on a belt in the room, so plates move past you on the page. It pauses on hover
and on focus-within, stops entirely under `prefers-reduced-motion`, and is
`aria-hidden` because the same photographs appear with real alt text in the
gallery below.

Everything else is sequencing: `[data-reveal]` fades and lifts section content
as it enters the viewport, driven by `IntersectionObserver`. Never a scroll
listener. The hidden state is gated behind a `.js` class added by the script
itself, so with JavaScript off nothing is ever hidden, and it is gated again
behind `prefers-reduced-motion: no-preference`.

Hover and press states are `transform` and `opacity` only.

## Accessibility floor

- Every text pair meets WCAG AA. Large display type may sit at the 3:1 large
  text threshold; body copy never does.
- The ghost button's border is `#756761`, 3.58:1 on the page, because a button
  boundary is a UI component and needs 3:1.
- `.nav a` is a two-part selector and outranks `.btn--primary`. The nav CTA
  restates its own colour at matching specificity. Without that the site's main
  call to action renders at 2.58:1. If you restructure the nav, re-check this.
- Skip link, visible focus rings, heading levels that never skip, and a mobile
  nav that reports `aria-expanded` and closes on Escape.

## What must not drift

- `assets/` stays lowercase. It was `Assets` once, which works on macOS and
  404s every stylesheet and image on Linux.
- `img { height: auto }` in the base reset is load-bearing. Without it the
  width and height attributes on every image win as presentational hints and
  photos stretch in any column narrower than their attribute width.
- No external requests on page load. No CDN, no web fonts over the wire, no
  analytics, no map iframe. The YouTube player is a click-to-load facade and
  the map is a link.
