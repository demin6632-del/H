from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')
    # Музыка должна быть отчётливо слышна уже на средней системной громкости.
    s=s.replace("Math.min(1,Math.max(0.90,musicVolume))","Math.min(1,Math.max(0.96,musicVolume))")
    s=s.replace("Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))","Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicGain.gain.value=musicVolume","musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))")
    # Если старое сохранение пользователя содержит слишком низкую громкость, поднимаем только музыку.
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.48)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.58)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.72)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.82)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    # Усиливаем музыкальные осцилляторы, не меняя звуки кнопок/боевых действий.
    for a,b in [('0.07','0.095'),('0.055','0.085'),('0.035','0.055'),('0.024','0.042'),('0.014','0.024'),('0.009','0.018')]:
        s=s.replace(f'g.gain.exponentialRampToValueAtTime({a}',f'g.gain.exponentialRampToValueAtTime({b}')
    p.write_text(s,encoding='utf-8')
print('Music v3 amplification applied.')
