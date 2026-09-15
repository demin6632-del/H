from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')
    # Музыка должна быть отчётливо слышна по умолчанию, но ползунок обязан реально менять её громкость.
    s=s.replace('value="0.28" oninput="setMusicVolume(this.value)"','value="0.96" oninput="setMusicVolume(this.value)"')
    s=s.replace("Math.min(1,Math.max(0.90,musicVolume))","Math.min(1,Math.max(0.96,musicVolume))")
    s=s.replace("Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))","Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicGain.gain.value=musicVolume","musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.48)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.58)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.72)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.82)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    # Ползунок теперь напрямую управляет musicGain и сохраняет выбранное значение.
    old="function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem('abyss_music_volume',musicVolume);if(musicGain)musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))}"
    new="function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem('abyss_music_volume',musicVolume);if(musicGain){const t=audioCtx?audioCtx.currentTime:0;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(musicVolume,t,.025)}}"
    s=s.replace(old,new)
    old_show="function showSettings(){syncSettings();setScreen('settings')}"
    new_show="function showSettings(){syncSettings();const m=el('musicVolume'),f=el('sfxVolume');if(m)m.value=String(musicVolume);if(f)f.value=String(sfxVolume);setScreen('settings')}"
    s=s.replace(old_show,new_show)
    # Усиливаем музыкальные осцилляторы, не меняя звуки кнопок/боевых действий.
    for a,b in [('0.07','0.095'),('0.055','0.085'),('0.035','0.055'),('0.024','0.042'),('0.014','0.024'),('0.009','0.018')]:
        s=s.replace(f'g.gain.exponentialRampToValueAtTime({a}',f'g.gain.exponentialRampToValueAtTime({b}')
    p.write_text(s,encoding='utf-8')
print('Music amplification and volume slider fix applied.')
