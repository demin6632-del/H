from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')
    # Поднимаем музыкальный мастер до 90% минимум и усиливаем только музыкальные gain-узлы.
    s=s.replace("musicGain.gain.value=musicVolume","musicGain.gain.value=Math.min(1,Math.max(0.90,musicVolume))",1)
    s=s.replace("Math.max(0.72,Number(localStorage.getItem('abyss_music_volume')||0.88))","Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))")
    s=s.replace("Math.max(0.82,Number(localStorage.getItem('abyss_music_volume')||0.82))","Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))")
    s=s.replace("Math.max(0.88,Number(localStorage.getItem('abyss_music_volume')||0.88))","Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))")
    s=s.replace("||0.62)","||0.90)",1)
    for a,b in [('0.11','0.18'),('0.075','0.13'),('0.045','0.085'),('0.025','0.05'),('0.018','0.036')]:
        s=s.replace(f'g.gain.setValueAtTime({a}',f'g.gain.setValueAtTime({b}')
    p.write_text(s,encoding='utf-8')
print('Music amplification applied.')
