/* ART-ATLAS-V4-FIX — точечное исправление боевой картинки. */
(function(){
  if(window.__ART_ATLAS_V4_BATTLE_FIX)return;
  window.__ART_ATLAS_V4_BATTLE_FIX=true;
  const idx={shadow:0,hunter:1,mutant:2,bones:3,elite:4,boss:5};
  function getSheet(){try{const scene=document.querySelector('.scene.art-v4-scene');const bg=scene&&scene.style&&scene.style.backgroundImage||'';const m=bg.match(/^url\(\"?(data:image\/webp;base64,[^\"\)]+)\"?\)$/);return m?m[1]:'';}catch(_){return '';}}
  function render(){
    const b=document.getElementById('enemyArt');
    if(!b)return;
    let k='shadow';
    if(typeof enemy!=='undefined'&&enemy){
      if(enemy.isBoss)k='boss';
      else if(enemy.isElite)k='elite';
      else k=({'Теневой зверь':'shadow','Заражённый охотник':'hunter','Мутант пустоши':'mutant','Пожиратель костей':'bones'})[enemy.name]||'shadow';
    }
    const sheet=getSheet();
    if(!sheet){setTimeout(render,350);return;}
    const i=idx[k];
    b.innerHTML='<span class="atlas-creature-v4"></span>';
    const e=b.firstElementChild;if(!e)return;
    e.style.display='block';e.style.width='min(72vw,256px)';e.style.height='min(72vw,256px)';e.style.margin='auto';
    e.style.backgroundImage='url("'+sheet+'")';e.style.backgroundRepeat='no-repeat';
    e.style.setProperty('background-size','400% 600%','important');
    e.style.setProperty('background-position',((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%','important');
    e.style.border='1px solid rgba(45,125,170,.65)';e.style.boxShadow='0 0 22px rgba(0,70,110,.28)';
  }
  function install(){
    if(typeof window.updateBattle!=='function')return;
    const old=window.updateBattle;if(old.__battleArtFix){render();return;}
    function wrapped(){old.apply(this,arguments);render();}
    wrapped.__battleArtFix=true;window.updateBattle=wrapped;render();
  }
  install();const timer=setInterval(install,250);
  window.addEventListener('beforeunload',()=>clearInterval(timer),{once:true});
})();
