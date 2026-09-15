from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')

    # Громкая музыка по умолчанию: 100% ползунка = усиление 1.8x.
    for old in ['0.28','0.48','0.58','0.72','0.82','0.90','0.96']:
        s=s.replace(f'value="{old}" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')

    # ВАЖНО: никаких минимальных 0.96/0.90 — они ломали регулировку после перезапуска.
    for old in ['0.48','0.58','0.70','0.72','0.82','0.90','0.96']:
        s=s.replace(f"musicVolume=Number(localStorage.getItem('abyss_music_volume')||{old})", "musicVolume=Math.max(0,Math.min(1,Number(localStorage.getItem('abyss_music_volume')||1)))")
    s=re.sub(r"musicVolume=Math\.max\((?:0\.48|0\.58|0\.72|0\.82|0\.90|0\.96),Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|(?:0\.48|0\.58|0\.72|0\.82|0\.90|0\.96)\)\)", "musicVolume=Math.max(0,Math.min(1,Number(localStorage.getItem('abyss_music_volume')||1)))", s)

    # Реальное управление GainNode: 0% = тишина, 100% = усиление 1.8x.
    s=s.replace('musicGain.gain.value=musicVolume','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0.90,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')

    # Убираем возможную лишнюю закрывающую скобку в обработчике ползунка.
    s=re.sub(
        r"function setMusicVolume\(v\)\{.*?\}\}\}?",
        "function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem('abyss_music_volume',musicVolume);if(musicGain){const t=audioCtx?audioCtx.currentTime:0;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(Math.min(1.8,musicVolume*1.8),t,.025)}}",
        s,
        count=1
    )

    p.write_text(s,encoding='utf-8')
print('Music slider fixed: 0-100%, persistent, 1.8x maximum, JS syntax repaired.')
