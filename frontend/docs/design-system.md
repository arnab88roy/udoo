# Udoo Design System

## Color Tokens

Defined in `frontend/app/globals.css` as CSS variables.

| Token | Value | Description |
|-------|-------|-------------|
| `--color-bg-base` | `#F8F7F4` | Warm off-white background |
| `--color-bg-surface` | `#FFFFFF` | Primary surface/card color |
| `--color-bg-sidebar` | `#F1F0EC` | Left navigation background |
| `--color-bg-veda` | `#1C1C1E` | VEDA AI sidebar background |
| `--color-accent-primary` | `#1A73E8` | Google Blue |
| `--color-accent-veda` | `#34C759` | VEDA Green (AI status) |
| `--color-text-primary` | `#202124` | Primary body text |
| `--color-text-secondary` | `#5F6368` | Secondary/metadata text |

## Typography

- **UI Font**: DM Sans (fallback for Google Sans)
- **VEDA Font**: JetBrains Mono

## Layout Rules

- **Top Bar**: 48px height, sticky
- **Left Nav**: 220px width
- **VEDA Sidebar**: 340px width (open), 48px (collapsed)
- **Spacing**: 4px base unit
- **Radius**: 8px (cards), 4px (inputs), 24px (EDA chat bubbles)
