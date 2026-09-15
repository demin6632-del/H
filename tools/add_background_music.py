from pathlib import Path

FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]
OLD = '''function startMusic(){
  if(!audioCtx||musicTimer)return;
  // Постоянная мрачная фоновая тема: бас + мелодия + редкие аккорды.
  const notes=[55,65.41,73.42,49,55,61.74,73.42,43.65],lead=[220,196,246.94,174.61,220,261.63,196,164.81];
  const chords=[[110,130.81,164.81],[98,116.54,146.83],[110,138.59,164.81],[87.31,110,130.81]];
  musicTimer=setInterval(()=>{
    if(!audioCtx||!audioEnabled)return;
    const i=musicStep++%notes.length,t=audioCtx.currentTime;
    bass(notes[i],.48,t);
    toneMusic(lead[i],.30,t+.08);
    if(i%2===0)toneMusic(lead[(i+2)%lead.length]*.5,.22,t+.22);
    if(i%4===0)padChord(chords[(i/4)%chords.length|0],t+.01,.82);
  },420);
  // Первый такт запускается сразу после разрешённого пользовательского жеста.
  if(audioCtx.state==='running') musicStep=0;
}
function bass(f,d,t){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='triangle';o.frequency.value=f;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.055,t+.035);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(musicGain);o.start(t);o.stop(t+d+.02)}
function toneMusic(f,d,t){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.024,t+.025);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(musicGain);o.start(t);o.stop(t+d+.02)}
function padChord(fs,t,d){if(!audioCtx)return;fs.forEach(f=>{const o=audioCtx.createOscillator(),g=audioCtx.createGain(),filter=audioCtx.createBiquadFilter();o.type='sawtooth';o.frequency.value=f;filter.type='lowpass';filter.frequency.value=700;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.009,t+.18);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(filter).connect(g).connect(musicGain);o.start(t);o.stop(t+d+.03)})}'''
NEW = '''function startMusic(){
  if(!audioCtx||musicTimer)return;
  // Более светлая и заметная тема: тёплый бас + выразительная мелодия + мягкие аккорды.
  const notes=[65.41,73.42,82.41,98,65.41,73.42,87.31,110],lead=[261.63,293.66,329.63,392,329.63,293.66,349.23,392];
  const chords=[[261.63,329.63,392],[293.66,349.23,440],[261.63,329.63,440],[246.94,329.63,392]];
  musicTimer=setInterval(()=>{
    if(!audioCtx||!audioEnabled)return;
    const i=musicStep++%notes.length,t=audioCtx.currentTime;
    bass(notes[i],.43,t);
    toneMusic(lead[i],.32,t+.04);
    if(i%2===0)toneMusic(lead[(i+1)%lead.length]*.5,.24,t+.20);
    if(i%4===0)padChord(chords[(i/4)%chords.length|0],t,.78);
  },380);
  if(audioCtx.state==='running') musicStep=0;
}
function bass(f,d,t){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='triangle';o.frequency.value=f;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.07,t+.03);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(musicGain);o.start(t);o.stop(t+d+.02)}
function toneMusic(f,d,t){if(!audioCtx)return;const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.type='triangle';o.frequency.value=f;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.035,t+.02);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(musicGain);o.start(t);o.stop(t+d+.02)}
function padChord(fs,t,d){if(!audioCtx)return;fs.forEach(f=>{const o=audioCtx.createOscillator(),g=audioCtx.createGain(),filter=audioCtx.createBiquadFilter();o.type='triangle';o.frequency.value=f;filter.type='lowpass';filter.frequency.value=1100;g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(.014,t+.12);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(filter).connect(g).connect(musicGain);o.start(t);o.stop(t+d+.03)})}'''
for path in FILES:
    s=path.read_text(encoding='utf-8')
    if OLD not in s:
        raise SystemExit(f'Не найден текущий блок музыки: {path}')
    s=s.replace(OLD, NEW, 1)
    s=s.replace("Number(localStorage.getItem('abyss_music_volume')||0.28)", "Number(localStorage.getItem('abyss_music_volume')||0.48)", 1)
    path.write_text(s, encoding='utf-8')
print('Brighter and louder background music updated in both HTML copies.')
