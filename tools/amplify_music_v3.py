from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
for p in FILES:
    s=p.read_text(encoding='utf-8')

    # Громкая музыка по умолчанию: 100% ползунка = усиление 1.8x.
    s=s.replace('value="0.28" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.48" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.58" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.72" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.82" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.90" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')
    s=s.replace('value="0.96" oninput="setMusicVolume(this.value)"','value="1" oninput="setMusicVolume(this.value)"')

    # ВАЖНО: никаких минимальных 0.96/0.90 — они ломали регулировку после перезапуска.
    s=re.sub(r"musicVolume=Math\.max\(0\.96,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.96\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.90,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.90\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.82,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.82\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.72,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.72\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.58,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.58\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.48,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.48\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)
    s=re.sub(r"musicVolume=Math\.max\(0\.90,Number\(localStorage\.getItem\('abyss_music_volume'\)\|\|0\.90\)\)", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)", s)

    # На случай старых вариантов инициализации без Math.max.
    for default in ['0.48','0.58','0.72','0.82','0.90','0.96']:
        s=s.replace(f"musicVolume=Number(localStorage.getItem('abyss_music_volume')||{default})", "musicVolume=Number(localStorage.getItem('abyss_music_volume')||0.70)")

    # Реальное управление GainNode: диапазон ползунка 0..1 переводится в усиление 0..1.8.
    s=s.replace('musicGain.gain.value=musicVolume','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0.96,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0.90,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')
    s=s.replace('musicGain.gain.value=Math.min(1,Math.max(0,musicVolume))','musicGain.gain.value=Math.min(1.8,Math.max(0,musicVolume*1.8))')

    # Усиливаем огибающие нот, не меняя саму мелодию.
    for a,b in [('0.07','0.14'),('0.055','0.115'),('0.035','0.075'),('0.024','0.052'),('0.014','0.032'),('0.009','0.022'),('0.095','0.16'),('0.085','0.14'),('0.055','0.09'),('0.042','0.065'),('0.024','0.04'),('0.018','0.028')]:
        s=s.replace(f'g.gain.exponentialRampToValueAtTime({a}',f'g.gain.exponentialRampToValueAtTime({b}')

    # Компрессор делает музыку плотнее и громче без постоянного клиппинга.
    if 'musicCompressor=null' not in s:
        s=s.replace('let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicTimer=null,musicStep=0;', 'let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicCompressor=null,musicTimer=null,musicStep=0;')
    if 'musicCompressor=audioCtx.createDynamicsCompressor()' not in s:
        s=s.replace('musicGain.connect(audioMaster);sfxGain.connect(audioMaster);audioMaster.connect(audioCtx.destination);', 'musicCompressor=audioCtx.createDynamicsCompressor();musicCompressor.threshold.value=-18;musicCompressor.knee.value=24;musicCompressor.ratio.value=4;musicCompressor.attack.value=0.003;musicCompressor.release.value=0.22;musicGain.connect(musicCompressor);musicCompressor.connect(audioMaster);sfxGain.connect(audioMaster);audioMaster.connect(audioCtx.destination);')

    # Плавное изменение громкости при движении ползунка.
    s=re.sub(
        r"function setMusicVolume\(v\)\{.*?\}",
        "function setMusicVolume(v){musicVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem('abyss_music_volume',musicVolume);if(musicGain){const t=audioCtx?audioCtx.currentTime:0;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(Math.min(1.8,musicVolume*1.8),t,.025)}}",
        s,
        count=1
    )

    p.write_text(s,encoding='utf-8')
print('Music fixed: loud output, working 0-100% slider, no minimum-volume clamp, compressor enabled.')