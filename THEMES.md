# Theme Guide

## Built-in Themes

### Flat
Classic flat design with solid background.

### Minimal
Clean minimal design with subtle styling.

### Neon
Bright neon colors with glowing effects.

### Cyberpunk
Dark cyberpunk theme with gradients.

### Glass
Frosted glass effect with transparency.

### Pixel
Retro pixel art style.

## Custom Themes

Themes are defined in `src/themes/__init__.py`. Each theme includes:

- `template`: SVG template string
- `text_template`: Text rendering template
- `bg_color`: Background color
- `text_color`: Text color
- `height`: Badge height

## Installing Themes

POST `/themes/install?url=<theme_url>`

Download and install custom themes from URLs.

## Theme Variables

- `{width}`: Calculated badge width
- `{height}`: Badge height
- `{bg_color}`: Background color
- `{text_color}`: Text color
- `{label}`: Badge label
- `{value}`: Badge value
- `{icon}`: Icon SVG
- `{animation}`: Animation CSS