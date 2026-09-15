from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')
    # Музыка должна быть заметно громче, при этом ползунок должен реально управлять громкостью.
    s=s.replace('value="0.28" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.96" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace("Math.max(0.90,Number(localStorage.getItem('abyss_music_volume')||0.90))","Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))","Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicGain.gain.value=musicVolume","musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))")
    s=s.replace("musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))","musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.48)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.58)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.72)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    s=s.replace("musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.82)","musicVolume=Math.max(0.96,Number(localStorage.getItem('abyss_music_volume')||0.96))")
    # Усиливаем саму музыкальную огибающую примерно на 35–70%.
    for a,b in [('0.07','0.14'),('0.055','0.115'),('0.035','0.075'),('0.024','0.052'),('0.014','0.032'),('0.009','0.022'),('0.095','0.16'),('0.085','0.14'),('0.055','0.09'),('0.042','0.065'),('0.024','0.04'),('0.018','0.028')]:
        s=s.replace(f'g.gain.exponentialRampToValueAtTime({a}',f'g.gain.exponentialRampToValueAtTime({b}')
    # Добавляем динамический компрессор только на музыкальную ветку: он делает тихие части плотнее и помогает избежать резкого клиппинга.
    s=s.replace('let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicTimer=null,musicStep=0;', 'let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicCompressor=null,musicTimer=null,musicStep=0;')
    s=s.replace('musicGain.connect(audioMaster);sfxGain.connect(audioMaster);audioMaster.connect(audioCtx.destination);', 'musicCompressor=audioCtx.createDynamicsCompressor();musicCompressor.threshold.value=-18;musicCompressor.knee.value=24;musicCompressor.ratio.value=4;musicCompressor.attack.value=0.003;musicCompressor.release.value=0.22;musicGain.connect(musicCompressor);musicCompressor.connect(audioMaster);sfxGain.connect(audioMaster);audioMaster.connect(audioCtx.destination);')
    old='function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem(\'abyss_music_volume\',musicVolume);if(musicGain){const t=audioCtx?audioCtx.currentTime:0;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(musicVolume,t,.025)}}'
    new='function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem(\'abyss_music_volume\',musicVolume);if(musicGain){const t=audioCtx?audioCtx.currentTime:0;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(Math.min(1.8,musicVolume*1.8),t,.025)}}'
    s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
print('Background music amplified: 1.8x gain plus dynamic compression; slider remains functional.')
