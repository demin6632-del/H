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

    # Музыка должна существовать только пока пользователь находится в игре.
    if 'let gameMusicAllowed=false;' not in s:
        s=s.replace('let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicCompressor=null,musicTimer=null,musicStep=0;', 'let audioCtx=null,audioMaster=null,musicGain=null,sfxGain=null,musicCompressor=null,musicTimer=null,musicStep=0;\nlet gameMusicAllowed=false;')

    # Инициализация AudioContext сама по себе не запускает музыку на главном меню.
    s=s.replace('  startMusic();\n}', '}', 1)

    # Таймер музыки не должен работать, когда игра закрыта/запрещена.
    s=s.replace('function startMusic(){\n  if(!audioCtx||musicTimer)return;', 'function startMusic(){\n  if(!audioCtx||!gameMusicAllowed||musicTimer)return;')

    # Останавливаем и возобновляем музыку при смене состояния страницы.
    if 'function stopMusic(){' not in s:
        marker="function setSfxVolume(v){sfxVolume=Math.max(0,Math.min(1,Number(v)));localStorage.setItem('abyss_sfx_volume',sfxVolume);if(sfxGain)sfxGain.gain.value=sfxVolume}\n"
        lifecycle=("function stopMusic(){if(musicTimer){clearInterval(musicTimer);musicTimer=null}musicStep=0;if(musicGain&&audioCtx){const t=audioCtx.currentTime;musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(0,t,.03)}}\n"
                   "function resumeMusic(){if(!audioCtx||!gameMusicAllowed||!audioEnabled)return;if(audioCtx.state==='suspended')audioCtx.resume();const t=audioCtx.currentTime;if(musicGain){musicGain.gain.cancelScheduledValues(t);musicGain.gain.setTargetAtTime(Math.min(1.8,musicVolume*1.8),t,.03)}startMusic()}\n"
                   "document.addEventListener('visibilitychange',()=>{if(document.hidden){stopMusic();if(audioCtx&&audioCtx.state==='running')audioCtx.suspend()}else{resumeMusic()}});\n"
                   "window.addEventListener('pagehide',()=>{stopMusic();if(audioCtx&&audioCtx.state==='running')audioCtx.suspend()});\n")
        if marker in s:
            s=s.replace(marker,marker+lifecycle,1)
        else:
            raise SystemExit(f'Audio SFX marker not found in {p}')

    # При старте новой игры разрешаем музыку и запускаем её.
    s=s.replace("function start(className){let s=classStats[className];", "function start(className){gameMusicAllowed=true;let s=classStats[className];", 1)
    # После выбора класса обязательно возвращаем аудио из suspended-состояния.
    s=s.replace("setScreen('main')}", "resumeAudio();resumeMusic();setScreen('main')}", 1)

    # Кнопка «Да» в окне выхода должна полностью остановить фоновую музыку.
    s=s.replace("function mainMenu(){closeModal();", "function mainMenu(){gameMusicAllowed=false;stopMusic();if(audioCtx&&audioCtx.state==='running')audioCtx.suspend();closeModal();", 1)

    p.write_text(s,encoding='utf-8')

print('Background music lifecycle fixed: stops on exit/hide, resumes only when returning to an active game.')
