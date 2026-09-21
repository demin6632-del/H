/* ART-ATLAS-V5 — crisp scalable dark-fantasy visual layer. Gameplay/UI untouched. */
(function(){
if(window.__ART_ATLAS_V5)return;
window.__ART_ATLAS_V5=true;

const names=['shadow','hunter','mutant','bones','elite','boss','start','ordinary','treasure','shop','forge','tavern','sanctuary','cursed','library','altar','trap','labyrinth','portal','bossroom','eliteroom','event'];
const idx={}; names.forEach((n,i)=>idx[n]=i);

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function tile(key,x,y){
const g=[];
const grad='g'+key;
g.push('<g transform="translate('+x+' '+y+')">');
g.push('<defs><linearGradient id="'+grad+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#07111c"/><stop offset=".55" stop-color="#101018"/><stop offset="1" stop-color="#050507"/></linearGradient><radialGradient id="glow'+key+'"><stop stop-color="#ff6840" stop-opacity=".9"/><stop offset="1" stop-color="#7d1018" stop-opacity="0"/></radialGradient><filter id="soft'+key+'"><feGaussianBlur stdDeviation="8"/></filter></defs>');
g.push('<rect width="512" height="512" fill="url(#'+grad+')"/>');
g.push('<path d="M0 355 Q130 315 256 350 T512 345 V512 H0Z" fill="#07080d"/>');
for(let i=0;i<7;i++)g.push('<path d="M'+(70+i*62)+' 355 L'+(15+i*82)+' 512" stroke="#252532" stroke-width="3" opacity=".65"/>');
for(let i=0;i<5;i++)g.push('<path d="M0 '+(385+i*25)+' Q256 '+(360+i*30)+' 512 '+(385+i*25)+'" fill="none" stroke="#3a2930" stroke-width="2" opacity=".6"/>');
g.push('<ellipse cx="256" cy="250" rx="170" ry="150" fill="url(#glow'+key+')" opacity=".22"/>');

if(['shadow','hunter','mutant','bones','elite','boss'].includes(key)){
let body='#11151b', hi='#46515b', glow='#d83a32', eye='#ffb24a';
let scale=1;
if(key==='shadow'){body='#090d14';hi='#33475b';glow='#513bff';eye='#a8e8ff';}
if(key==='hunter'){body='#17161a';hi='#655b56';glow='#8b2020';eye='#e5d19a';}
if(key==='mutant'){body='#17221e';hi='#64745b';glow='#b52d25';eye='#f0d46a';}
if(key==='bones'){body='#171414';hi='#b8a88e';glow='#7d1c24';eye='#ff6a4a';}
if(key==='elite'){body='#111820';hi='#657f8c';glow='#b9272e';eye='#c9f3ff';scale=1.08;}
if(key==='boss'){body='#0c0a10';hi='#8a2e35';glow='#ff3828';eye='#ffdf9b';scale=1.18;}
g.push('<g transform="translate(256 330) scale('+scale+')">');
g.push('<ellipse cx="0" cy="120" rx="125" ry="28" fill="#000" opacity=".8"/>');
g.push('<path d="M-112 105 Q-96 5 -70 -55 Q-50 -105 0 -120 Q50 -105 70 -55 Q96 5 112 105 Q55 145 0 140 Q-55 145 -112 105Z" fill="'+body+'" stroke="'+hi+'" stroke-width="7"/>');
g.push('<path d="M-58 -72 L-104 -138 L-74 -128 L-38 -92 M58 -72 L104 -138 L74 -128 L38 -92" fill="'+body+'" stroke="'+hi+'" stroke-width="7" stroke-linejoin="round"/>');
g.push('<path d="M-62 -12 Q0 34 62 -12 L45 55 Q0 86 -45 55Z" fill="'+hi+'" opacity=".42"/>');
g.push('<ellipse cx="-35" cy="-50" rx="13" ry="8" fill="'+eye+'"/><ellipse cx="35" cy="-50" rx="13" ry="8" fill="'+eye+'"/>');
g.push('<path d="M-30 -5 Q0 12 30 -5" fill="none" stroke="'+glow+'" stroke-width="6"/>');
g.push('<path d="M-88 35 L-150 75 M88 35 L150 75" stroke="'+hi+'" stroke-width="18" stroke-linecap="round"/>');
if(key==='bones'||key==='boss')g.push('<path d="M-70 80 Q0 115 70 80" fill="none" stroke="#d5c9aa" stroke-width="12" opacity=".75"/>');
g.push('</g>');
for(let i=0;i<18;i++){const px=(i*71)%470+20,py=(i*47)%290+35;g.push('<circle cx="'+px+'" cy="'+py+'" r="'+(i%3+1)+'" fill="'+glow+'" opacity=".55"/>');}
}else{
let accent='#b52828';
if(key==='treasure')accent='#d8a83d';
if(key==='portal'||key==='altar')accent='#a62cff';
if(key==='shop'||key==='tavern')accent='#b85a2b';
if(key==='sanctuary')accent='#55b8b0';
if(key==='library')accent='#7587b8';
if(key==='trap')accent='#d53b2e';
g.push('<path d="M60 350 L60 170 L150 100 L220 170 L292 95 L380 170 L452 120 L452 350Z" fill="#12141a" stroke="#414957" stroke-width="6"/>');
g.push('<path d="M60 350 L452 350" stroke="#5b3b3f" stroke-width="9"/>');
for(let i=0;i<8;i++)g.push('<path d="M'+(75+i*50)+' 350 L'+(115+i*38)+' 512" stroke="#29303a" stroke-width="4" opacity=".8"/>');
g.push('<ellipse cx="256" cy="235" rx="90" ry="70" fill="'+accent+'" opacity=".18" filter="url(#soft'+key+')"/>');
if(key==='treasure'){g.push('<path d="M165 335 L347 335 L332 250 L180 250Z" fill="#6c431d" stroke="#d7b55c" stroke-width="7"/><path d="M180 250 Q256 190 332 250 L320 180 Q256 145 192 180Z" fill="#9a6224" stroke="#e0bd63" stroke-width="7"/><circle cx="256" cy="292" r="11" fill="#ffe18a"/>');}
else if(key==='portal'||key==='altar'){g.push('<ellipse cx="256" cy="260" rx="86" ry="118" fill="none" stroke="'+accent+'" stroke-width="18"/><ellipse cx="256" cy="260" rx="58" ry="88" fill="none" stroke="#e4a4ff" stroke-width="6"/><path d="M256 142 L256 378 M178 260 H334" stroke="'+accent+'" stroke-width="4" opacity=".75"/>');}
else if(key==='trap'){g.push('<path d="M120 340 L200 220 L230 340 L290 205 L330 340 L410 220" fill="none" stroke="#d53b2e" stroke-width="12"/><circle cx="256" cy="285" r="42" fill="#1b0d10" stroke="#f04a36" stroke-width="6"/>');}
else if(key==='library'){for(let i=0;i<5;i++)g.push('<rect x="'+(105+i*62)+'" y="165" width="42" height="175" fill="#242d45" stroke="#7688b5" stroke-width="4"/><path d="M'+(112+i*62)+' 190 H'+(140+i*62)+' M'+(112+i*62)+' 220 H'+(140+i*62)+'" stroke="#aebbe0" stroke-width="3"/>');}
else if(key==='forge'){g.push('<path d="M165 340 Q256 300 347 340 L325 210 Q256 175 187 210Z" fill="#2b2424" stroke="#a05a43" stroke-width="7"/><path d="M215 310 Q256 350 297 310 L284 225 Q256 205 228 225Z" fill="#ff6b31" opacity=".8"/>');}
else if(key==='tavern'||key==='shop'){g.push('<rect x="115" y="175" width="282" height="175" rx="12" fill="#241916" stroke="#9a543d" stroke-width="7"/><rect x="150" y="215" width="70" height="95" fill="#38221c"/><rect x="292" y="215" width="70" height="95" fill="#38221c"/><path d="M180 165 H332" stroke="'+accent+'" stroke-width="12"/>');}
else if(key==='sanctuary'){g.push('<path d="M256 120 L330 220 H295 V355 H217 V220 H182Z" fill="#1a2a2d" stroke="#71d6ce" stroke-width="7"/><circle cx="256" cy="205" r="28" fill="#9ff7ef" opacity=".55"/>');}
else if(key==='cursed'){g.push('<path d="M130 360 Q150 180 256 140 Q362 180 382 360" fill="#0b0b10" stroke="#8d3035" stroke-width="8"/><path d="M170 335 Q190 240 256 210 Q322 240 342 335" fill="#020205"/><circle cx="220" cy="280" r="8" fill="#ff4035"/><circle cx="292" cy="280" r="8" fill="#ff4035"/>');}
else if(key==='labyrinth'||key==='ordinary'||key==='event'||key==='start'||key==='bossroom'||key==='eliteroom'){g.push('<path d="M150 350 V235 L215 175 V350 M297 350 V175 L362 235 V350 M215 260 H297 M180 310 H332" fill="none" stroke="#67717d" stroke-width="10"/><path d="M256 170 V350" stroke="'+accent+'" stroke-width="6" opacity=".8"/>');}
}
g.push('</g>'); return g.join('');
}

let sheet='<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="3072" viewBox="0 0 2048 3072">';
for(let i=0;i<24;i++){const key=names[i]||'event';sheet+=tile(key,(i%4)*512,Math.floor(i/4)*512);}
sheet+='</svg>';
const SHEET='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(sheet);

const V4_STYLE=document.createElement('style');
V4_STYLE.textContent='.scene.art-v5-scene:before,.scene.art-v5-scene:after{display:none!important}.scene.art-v5-scene{background-repeat:no-repeat!important}.atlas-creature-v4{display:block;background-image:url("'+SHEET+'");background-size:400% 600%;background-repeat:no-repeat;}';
document.head.appendChild(V4_STYLE);

const V4_TILE_CACHE={};
let V4_SHEET_IMG=null;
function loadV4Sheet(){if(V4_SHEET_IMG)return V4_SHEET_IMG;const img=new Image();img.decoding='async';img.src=SHEET;V4_SHEET_IMG=img;return img;}
function v4Tile(n){const i=idx[n];if(i==null)return '';return 'background-size:400% 600%;background-position:'+((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%;background-repeat:no-repeat;';}
function v4QualityData(key,w,h){
const width=Math.max(1,Math.min(1024,Math.round(w||256))),height=Math.max(1,Math.min(1024,Math.round(h||256)));
const k=key+'@'+width+'x'+height;if(V4_TILE_CACHE[k])return V4_TILE_CACHE[k];
const img=loadV4Sheet();
const make=function(){try{
const dpr=Math.min(2,Math.max(1,window.devicePixelRatio||1));const cw=Math.max(1,Math.round(width*dpr)),ch=Math.max(1,Math.round(height*dpr));
const c=document.createElement('canvas');c.width=cw;c.height=ch;const ctx=c.getContext('2d',{alpha:true});if(!ctx)return null;
ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';const i=idx[key];if(i==null)return null;
const sx=(i%4)*512,sy=Math.floor(i/4)*512;const targetRatio=width/height;let sw=512,sh=512,ox=0,oy=0;
if(targetRatio>1){sh=512/targetRatio;oy=(512-sh)/2}else if(targetRatio<1){sw=512*targetRatio;ox=(512-sw)/2}
ctx.filter='contrast(1.08) saturate(1.08)';ctx.drawImage(img,sx+ox,sy+oy,sw,sh,0,0,cw,ch);ctx.filter='none';
const data=c.toDataURL('image/png');V4_TILE_CACHE[k]=data;return data;
}catch(e){return null;}};
if(img.complete&&img.naturalWidth)return make();img.addEventListener('load',make,{once:true});return null;
}
function renderV4Tile(el,key,w,h){if(!el)return;const width=Math.max(1,Math.min(1024,Math.round(w||el.clientWidth||256))),height=Math.max(1,Math.min(1024,Math.round(h||el.clientHeight||256)));
const data=v4QualityData(key,width,height);if(data){el.style.setProperty('background-image','url("'+data+'")','important');el.style.setProperty('background-size','100% 100%','important');el.style.setProperty('background-position','center center','important');el.style.setProperty('background-repeat','no-repeat','important');el.style.setProperty('image-rendering','auto','important');el.dataset.v4QualityKey=key+'@'+width+'x'+height;return true;}
const img=loadV4Sheet();const apply=function(){if(!el.isConnected)return;el.style.setProperty('background-image','url("'+SHEET+'")','important');el.style.setProperty('background-size','400% auto','important');el.style.setProperty('background-position',v4Tile(key).match(/background-position:[^;]+;/)?.[0]?.replace('background-position:','').replace(';','')||'center center','important');el.style.setProperty('background-repeat','no-repeat','important');el.dataset.v4QualityKey=key+'@raw';setTimeout(function(){renderV4Tile(el,key,width,height)},0);};if(img.complete&&img.naturalWidth)apply();else img.addEventListener('load',apply,{once:true});return false;}
window.renderV4Tile=renderV4Tile;
function setScene(id,key){const s=document.querySelector('#'+id+' .scene');if(!s)return;const i=idx[key];if(i==null)return;s.classList.add('art-v5-scene');s.style.setProperty('background-repeat','no-repeat','important');s.style.setProperty('background-position','center center','important');s.style.setProperty('background-size','cover','important');renderV4Tile(s,key,s.clientWidth||700,s.clientHeight||390);}
function roomKeyV4(){const c=String(typeof abyssRoomContent!=='undefined'?abyssRoomContent:'');if(c.includes('Кровавый алтарь'))return'altar';if(c.includes('Забытый тайник'))return'treasure';if(c.includes('Источник Бездны'))return'portal';if(c.includes('Босс:'))return'bossroom';if(c.includes('Элитный враг:'))return'eliteroom';if(c.includes('Пустой проход')||c.includes('Побеждён'))return'ordinary';return'labyrinth';}
function updateScenesV4(){setScene('main','start');setScene('shop','shop');setScene('tavern','tavern');setScene('equipment','forge');setScene('stats','library');setScene('journal','ordinary');setScene('death','cursed');const a=document.getElementById('abyss');if(a&&!a.classList.contains('hidden'))setScene('abyss',roomKeyV4());}
function installBattleV4(){const old=window.updateBattle;if(typeof old!=='function'||old.__artV4)return false;function wrapped(){old.apply(this,arguments);const b=document.getElementById('enemyArt');if(!b)return;let k='shadow';if(typeof enemy!=='undefined'&&enemy){if(enemy.isBoss)k='boss';else if(enemy.isElite)k='elite';else k=({'Теневой зверь':'shadow','Заражённый охотник':'hunter','Мутант пустоши':'mutant','Пожиратель костей':'bones'})[enemy.name]||'shadow';}b.innerHTML='<span class="atlas-creature-v4" style="'+v4Tile(k)+'"></span>';const e=b.firstElementChild;if(e){e.style.width='min(86vw,360px)';e.style.height='min(86vw,300px)';e.style.margin='auto';e.style.setProperty('background-size','400% 600%','important');e.style.setProperty('background-position',((idx[k]%4)*100/3)+'% '+(Math.floor(idx[k]/4)*100/5)+'%','important');e.style.border='1px solid rgba(45,125,170,.65)';e.style.boxShadow='0 0 22px rgba(0,70,110,.28)';}}wrapped.__artV4=true;wrapped.__battleArtRuntimeFix=true;window.updateBattle=wrapped;return true;}
function installAbyssV4(){const old=window.updateAbyss;if(typeof old!=='function'||old.__artV4)return false;function wrapped(){old.apply(this,arguments);setTimeout(updateScenesV4,0);}wrapped.__artV4=true;window.updateAbyss=wrapped;return true;}
function installScreenV4(){const old=window.setScreen;if(typeof old!=='function'||old.__artV4)return false;function wrapped(){old.apply(this,arguments);setTimeout(updateScenesV4,0);}wrapped.__artV4=true;window.setScreen=wrapped;return true;}
function bootV4(){installBattleV4();installAbyssV4();installScreenV4();updateScenesV4();}
bootV4();document.addEventListener('DOMContentLoaded',bootV4);setTimeout(bootV4,250);
})();