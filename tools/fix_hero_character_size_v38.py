from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

for rel in ('NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    if 'hero-character-v37' not in text:
        raise RuntimeError(f'Не найден блок hero-character-v37 в {rel}')

    # Увеличиваем самого героя, не меняя сетку карточек и игровую механику.
    text = re.sub(
        r'(\.hero-character-image\{.*?height:)100%(.*?object-fit:contain!important;)',
        r'\g<1>155%\g<2>',
        text,
        count=1,
        flags=re.S,
    )
    # На узких экранах оставляем увеличенный масштаб, но чуть меньше.
    text = re.sub(
        r'(@media\(max-width:360px\)\{\s*\.hero-figure\{height:260px!important;min-height:260px!important\}\s*\})',
        r'@media(max-width:360px){.hero-figure{height:260px!important;min-height:260px!important}.hero-character-image{height:145%!important}}',
        text,
        count=1,
        flags=re.S,
    )
    path.write_text(text, encoding='utf-8')
    print(f'Увеличен персонаж в {rel}')
