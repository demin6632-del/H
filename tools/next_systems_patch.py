from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]


def remove_function(src,name):
    marker='function '+name+'('
    while True:
        p=src.find(marker)
        if p<0:return src
        brace=src.find('{',p)
        if brace<0:raise SystemExit(f'function {name}: opening brace not found')
        depth=1;i=brace+1
        while i<len(src) and depth:
            if src[i]=='{':depth+=1
            elif src[i]=='}':depth-=1
            i+=1
        if depth:raise SystemExit(f'function {name}: unbalanced braces')
        src=src[:p]+src[i:]


def replace_function(src,name,new):
    marker='function '+name+'('
    p=src.find(marker)
    if p<0:raise SystemExit(f'function {name} not found')
    brace=src.find('{',p)
    if brace<0:raise SystemExit(f'function {name}: opening brace not found')
    depth=1;i=brace+1
    while i<len(src) and depth:
        if src[i]=='{':depth+=1
        elif src[i]=='}':depth-=1
        i+=1
    if depth:raise SystemExit(f'function {name}: unbalanced braces')
    return src[:p]+new+src[i:]


SKILL_FUNCS=r'''function upgradeSkill(){hero.skillLevel=Math.max(1,Number(hero.skillLevel||1));hero.skillPoints=Math.max(0,Number(hero.skillPoints||0));if(hero.skillLevel>=5){if(el('out'))el('out').innerHTML='<span class="muted">Навык уже достиг максимального уровня.</span>';return}if(hero.skillPoints<1){if(el('out'))el('out').innerHTML='<span class="red">Нет очков навыка.</span>';return}hero.skillPoints--;hero.skillLevel++;sfx('buy');logEvent('НАВЫК','Улучшен навык «'+((classStats[hero.class]||{}).skill||'Навык')+'» до уровня '+hero.skillLevel+'.');save();renderSkills();renderStats();if(el('out'))el('out').innerHTML='<span class="green">Навык улучшен до уровня '+hero.skillLevel+'.</span>'}
function renderSkills(){const s=classStats[hero.class]||{};const sk=skillStats[hero.class]||{};const level=Math.max(1,Number(hero.skillLevel||1));const points=Math.max(0,Number(hero.skillPoints||0));const bonus=(level-1)*4;const damage=Number(sk.damage||0)+bonus;const can=level<5&&points>0;if(el('skillsContent'))el('skillsContent').innerHTML='<div class="info-card"><h3>'+((s.skill)||'Навык не выбран')+'</h3><div class="sep"></div><div class="info-row"><span>Класс</span><b>'+((hero.class)||'—')+'</b></div><div class="info-row"><span>Уровень навыка</span><b>'+level+'/5</b></div><div class="info-row"><span>Очки навыка</span><b>'+points+'</b></div><div class="info-row"><span>Стоимость энергии</span><b>'+((sk.cost)||'—')+'</b></div><div class="info-row"><span>Урон навыка</span><b>'+damage+'</b></div><p class="muted" style="text-align:center;line-height:1.5">Каждое улучшение навыка даёт +4 к его базовому урону. Очко навыка выдаётся за каждый новый уровень героя.</p><button onclick="upgradeSkill()" '+(can?'':'disabled')+'>'+(level>=5?'Максимальный уровень':can?'Улучшить навык · 1 очко':'Нужно очко навыка')+'</button></div>'}
'''

INFINITE_MARK='INFINITE-ABYSS-PERSISTENT-RPG-V1'
INFINITE_WRAPPER=r'''<script id="infinite-abyss-persistent-rpg-v1">
/* INFINITE-ABYSS-PERSISTENT-RPG-V1 — бесконечная Бездна без рогалика.
   Первые 7 этажей сохраняются; с 8-го начинается постоянная бесконечная глубина.
   Персонаж, уровень, предметы, золото и прогресс не сбрасываются после смерти. */
(function(){
  const BEST_KEY='chronicles_abyss_infinite_best_v1';
  const OLD_MAX_FLOOR=7;
  function readBest(){return Math.max(1,Number(localStorage.getItem(BEST_KEY)||1));}
  function writeBest(){if(typeof abyssFloor==='number'&&abyssFloor>readBest())localStorage.setItem(BEST_KEY,String(Math.floor(abyssFloor)));}
  function restoreBest(){if(typeof abyssFloor!=='number')return;const best=readBest();if(best>abyssFloor)abyssFloor=best;}
  window.addEventListener('load',function(){try{restoreBest()}catch(e){}});
  if(typeof save==='function'){
    const __save=save;
    save=function(){try{writeBest()}catch(e){}return __save.apply(this,arguments)};
  }
  if(typeof updateAbyss==='function'){
    const __updateAbyss=updateAbyss;
    updateAbyss=function(){
      try{restoreBest()}catch(e){}
      const r=__updateAbyss.apply(this,arguments);
      try{
        const depth=Math.max(1,Number(abyssFloor||1));
        const best=Math.max(depth,readBest());
        let host=el('abyss');
        if(host){
          let box=el('infiniteDepthPanel');
          if(!box){box=document.createElement('div');box.id='infiniteDepthPanel';box.className='panel';host.insertBefore(box,host.firstChild)}
          if(depth>=8){
            box.style.display='block';
            box.innerHTML='<div style="text-align:center"><b style="color:#e22">🌑 ГЛУБИНЫ БЕЗДНЫ</b><div class="sep"></div><div class="info-row"><span>Текущая глубина</span><b>'+depth+'</b></div><div class="info-row"><span>Достигнуто</span><b>'+best+'</b></div><div class="muted" style="text-align:center;margin-top:6px">Бесконечный режим. Прогресс персонажа и достигнутая глубина сохраняются.</div></div>';
          }else box.style.display='none';
        }
      }catch(e){}
      return r;
    };
  }
  if(typeof victory==='function'){
    const __victory=victory;
    victory=function(){const r=__victory.apply(this,arguments);try{writeBest();}catch(e){}return r};
  }
  if(typeof die==='function'){
    const __die=die;
    die=function(){const best=readBest();const r=__die.apply(this,arguments);try{if(best>=8)abyssFloor=best;writeBest();save();}catch(e){}return r};
  }
})();
</script>'''

for path in FILES:
    s=path.read_text(encoding='utf-8')
    original=s

    old_key="function buyKey(){const price=75;if(getGold()<price){sfx('error');if(el('out'))el('out').innerHTML='<span class=\"red\">Недостаточно золота.</span>';return}hero.gold-=price;hero.items.push({name:'Таинственный ключ',type:'other',icon:'🔑'});save();logEvent('МАГАЗИН','Куплен Таинственный ключ.');shopTab('other')}"
    new_key="function buyKey(){const price=75;if(!inventoryHasSpace()){sfx('error');if(el('out'))el('out').innerHTML='<span class=\"red\">Инвентарь заполнен (24/24).</span>';return}if(getGold()<price){sfx('error');if(el('out'))el('out').innerHTML='<span class=\"red\">Недостаточно золота.</span>';return}hero.gold-=price;hero.items.push({name:'Таинственный ключ',type:'other',icon:'🔑'});save();logEvent('МАГАЗИН','Куплен Таинственный ключ.');shopTab('other')}"
    if old_key not in s:raise SystemExit(f'{path}: buyKey exact source not found')
    s=s.replace(old_key,new_key,1)

    needle="hero.crit=Math.max(0,Math.min(1,Number(hero.crit||0)));hero.weapon=hero.weapon||'Нет';"
    repl="hero.crit=Math.max(0,Math.min(1,Number(hero.crit||0)));hero.skillLevel=Math.max(1,Math.min(5,Number(hero.skillLevel||1)));hero.skillPoints=Math.max(0,Number(hero.skillPoints||0));hero.weapon=hero.weapon||'Нет';"
    if needle not in s:raise SystemExit(f'{path}: normalizeHero skill insertion point not found')
    s=s.replace(needle,repl,1)

    start_old="hero={name:'Странник',class:className,hp:st.hp,maxHp:st.maxHp,energy:st.energy,maxEnergy:st.maxEnergy,attack:st.attack,def:st.def,level:1,xp:0,items:[],weapon:'Нет',armor:'Нет',gold:100,allies:[],crit:0};"
    start_new="hero={name:'Странник',class:className,hp:st.hp,maxHp:st.maxHp,energy:st.energy,maxEnergy:st.maxEnergy,attack:st.attack,def:st.def,level:1,xp:0,items:[],weapon:'Нет',armor:'Нет',gold:100,allies:[],crit:0,skillLevel:1,skillPoints:0};"
    if start_old not in s:raise SystemExit(f'{path}: start hero source not found')
    s=s.replace(start_old,start_new,1)

    s=remove_function(s,'upgradeSkill')
    s=remove_function(s,'renderSkills')
    marker='function showSkills(){'
    if marker not in s:raise SystemExit(f'{path}: showSkills marker missing')
    s=s.replace(marker,SKILL_FUNCS+marker,1)
    skill_old="let dmg=sk.damage;if(hero.class==='Разбойник'&&Math.random()<.35)dmg*=2;"
    skill_new="let skillLevel=Math.max(1,Math.min(5,Number(hero.skillLevel||1)));let dmg=Number(sk.damage||25)+(skillLevel-1)*4;if(hero.class==='Разбойник'&&Math.random()<.35)dmg*=2;"
    if skill_old not in s:raise SystemExit(f'{path}: skill damage source not found')
    s=s.replace(skill_old,skill_new,1)

    level_old="hero.attack+=3;hero.maxHp+=20;hero.maxEnergy+=5;levels++"
    level_new="hero.attack+=3;hero.maxHp+=20;hero.maxEnergy+=5;hero.skillPoints=(Number(hero.skillPoints)||0)+1;levels++"
    if level_old not in s:raise SystemExit(f'{path}: level-up source not found')
    s=s.replace(level_old,level_new,1)

    explore_old="const names=['Теневой зверь','Заражённый охотник','Мутант пустоши','Пожиратель костей'];const roomNumber=abyssRoom+1;const boss=abyssFloor===MAX_FLOOR&&roomNumber===ROOMS_PER_FLOOR;const elite=!boss&&roomNumber===ROOMS_PER_FLOOR;"
    explore_new="const names=['Теневой зверь','Заражённый охотник','Мутант пустоши','Пожиратель костей'];const roomNumber=abyssRoom+1;const boss=(abyssFloor===7||(abyssFloor>=8&&abyssFloor%5===0))&&roomNumber===ROOMS_PER_FLOOR;const elite=!boss&&roomNumber===ROOMS_PER_FLOOR;if(!boss&&!elite&&Math.random()<0.18){const events=[{name:'Кровавый алтарь',apply:()=>{const heal=Math.max(1,Math.round(hero.maxHp*.25));hero.hp=Math.min(hero.maxHp,hero.hp+heal);return'Восстановлено '+heal+' HP.'}},{name:'Забытый тайник',apply:()=>{const gold=30+abyssFloor*5;hero.gold+=gold;return'Найдено '+gold+' золота.'}},{name:'Источник Бездны',apply:()=>{const energy=Math.max(1,Math.round(hero.maxEnergy*.35));hero.energy=Math.min(hero.maxEnergy,hero.energy+energy);return'Восстановлено '+energy+' энергии.'}}];const event=events[Math.floor(Math.random()*events.length)];const result=event.apply();abyssRoom++;save();logEvent('СОБЫТИЕ',event.name+': '+result);update();screenHistory=['menu','main','abyss'];history.replaceState({screen:'abyss'},'','#abyss');setScreen('abyss',false);updateAbyss();if(el('out'))el('out').innerHTML='<span class=\"green\">'+event.name+': '+result+'</span>';return}if(!boss&&!elite&&Math.random()<0.40){abyssRoom++;save();logEvent('БЕЗ БОЯ','Путь в Бездне продолжается без столкновения.');update();screenHistory=['menu','main','abyss'];history.replaceState({screen:'abyss'},'','#abyss');setScreen('abyss',false);updateAbyss();if(el('out'))el('out').innerHTML='<span class=\"muted\">В этот раз путь прошёл без боя.</span>';return}"
    if explore_old not in s:raise SystemExit(f'{path}: explore source not found')
    s=s.replace(explore_old,explore_new,1)

    update_old="el('enemyName').innerHTML=(enemy.isBoss?'👑 Владыка Бездны':enemy.isElite?'👿 Элитный ':'Проклятый ')+enemy.name;"
    update_new="if(enemy.isBoss&&enemy.phase===2)el('enemyName').innerHTML='👑 Владыка Бездны · Фаза II';else el('enemyName').innerHTML=(enemy.isBoss?'👑 Владыка Бездны':enemy.isElite?'👿 Элитный ':'Проклятый ')+enemy.name;"
    if update_old not in s:raise SystemExit(f'{path}: updateBattle source not found')
    s=s.replace(update_old,update_new,1)

    enemy_old="enemy={name:boss?'Владыка Бездны':names[Math.floor(Math.random()*names.length)],hp:Math.round(hp),max:Math.round(hp),attack:boss?24:elite?16+abyssFloor:8+abyssFloor*2,def:boss?8:elite?4:Math.floor(abyssFloor/2),xp:boss?150:elite?90:50+abyssFloor*5,gold:boss?150:elite?70:20+abyssFloor*5,isElite:elite,isBoss:boss,icon:boss?'👑':elite?'👿':'👹'};"
    enemy_new="enemy={name:boss?'Владыка Бездны':names[Math.floor(Math.random()*names.length)],hp:Math.round(hp),max:Math.round(hp),attack:boss?24:elite?16+abyssFloor:8+abyssFloor*2,def:boss?8:elite?4:Math.floor(abyssFloor/2),xp:boss?150:elite?90:50+abyssFloor*5,gold:boss?150:elite?70:20+abyssFloor*5,isElite:elite,isBoss:boss,phase:1,icon:boss?'👑':elite?'👿':'👹'};"
    if enemy_old not in s:raise SystemExit(f'{path}: enemy source not found')
    s=s.replace(enemy_old,enemy_new,1)

    enemy_turn_old="function enemyTurn(){if(!enemy||hero.hp<=0)return;sfx('hit');const incoming=Math.max(1,(enemy.attack||10)-Math.floor(hero.def*.35));hero.hp-=guard?Math.ceil(incoming*.5):incoming;guard=false;if(hero.hp<=0){hero.hp=0;update();die();return}save();update();updateBattle()}"
    enemy_turn_new="function enemyTurn(){if(!enemy||hero.hp<=0)return;if(enemy.isBoss&&enemy.phase===1&&enemy.hp<=enemy.max*.5){enemy.phase=2;enemy.attack+=6;enemy.def+=2;logEvent('БОСС','Владыка Бездны переходит во вторую фазу.');if(el('battleLog'))el('battleLog').innerHTML='<span class=\"red\">⚠️ Владыка Бездны входит в Фазу II!</span>'}sfx('hit');let incoming=Math.max(1,(enemy.attack||10)-Math.floor(hero.def*.35));if(enemy.isBoss&&enemy.phase===2&&Math.random()<.25){incoming=Math.round(incoming*1.5);logEvent('БОСС','Особая атака: Удар Бездны.');}hero.hp-=guard?Math.ceil(incoming*.5):incoming;guard=false;if(hero.hp<=0){hero.hp=0;update();die();return}save();update();updateBattle()}"
    if enemy_turn_old not in s:raise SystemExit(f'{path}: enemyTurn source not found')
    s=s.replace(enemy_turn_old,enemy_turn_new,1)

    update_old="updateHud();renderHero();renderEquipment();renderTavern()}"
    update_new="updateHud();renderHero();renderEquipment();renderTavern();if(el('statsContent'))renderStats();if(el('skillsContent'))renderSkills()}"
    if update_old not in s:raise SystemExit(f'{path}: update source not found')
    s=s.replace(update_old,update_new,1)

    # Бесконечная глубина начинается после завершения 7-го этажа.
    # Внутренний лимит делаем технически недостижимым, сохраняя первые 7 этажей без изменений.
    s=re.sub(r'const MAX_FLOOR=\d+;', 'const MAX_FLOOR=999999;', s, count=1)

    # Обновляем ранее установленный best-depth только после фактического прохождения.
    if INFINITE_MARK not in s:
        pos=s.rfind('</script>')
        if pos<0:raise SystemExit(f'{path}: closing script tag not found')
        s=s[:pos]+INFINITE_WRAPPER+s[pos:]

    if s==original:raise SystemExit(f'{path}: no changes made')
    path.write_text(s,encoding='utf-8')
    print('Patched',path)
