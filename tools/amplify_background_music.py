from pathlib import Path

FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]

for path in FILES:
    text = path.read_text(encoding='utf-8')
    old = "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.62)"
    if old in text:
        text = text.replace(old, "musicVolume=Math.min(1,Math.max(0.72,Number(localStorage.getItem('abyss_music_volume')||0.88)))", 1)
    old2 = "musicGain.gain.value=musicVolume"
    if old2 in text:
        text = text.replace(old2, "musicGain.gain.value=Math.min(1,Math.max(0.72,musicVolume))", 1)
    text = text.replace("g.gain.setValueAtTime(0.11", "g.gain.setValueAtTime(0.18", 1)
    text = text.replace("g.gain.setValueAtTime(0.075", "g.gain.setValueAtTime(0.12", 1)
    text = text.replace("g.gain.setValueAtTime(0.045", "g.gain.setValueAtTime(0.075", 1)
    text = text.replace("g.gain.setValueAtTime(0.025", "g.gain.setValueAtTime(0.045", 1)
    path.write_text(text, encoding='utf-8')

print('Background music amplified: higher default volume and stronger musical layers.')
