from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]

# Финальная версия: после 7-го этажа исследование Бездны продолжается бесконечно.
for path in FILES:
    s=path.read_text(encoding='utf-8')
    original=s

    # После завершения пяти комнат всегда открываем следующий этаж/глубину.
    old="if(abyssRoom>=ROOMS_PER_FLOOR){if(abyssFloor<MAX_FLOOR){abyssFloor++;abyssRoom=0;save();updateAbyss();logEvent('ЭТАЖ','Открыт этаж '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">Этаж '+abyssFloor+' открыт.</span>';return}"
    new="if(abyssRoom>=ROOMS_PER_FLOOR){abyssFloor++;abyssRoom=0;abyssRoomContent='Новая комната ещё не исследована.';save();updateAbyss();logEvent('ЭТАЖ',abyssFloor<=MAX_FLOOR?'Открыт этаж '+abyssFloor+'.':'Открыта новая глубина Бездны: '+abyssFloor+'.');if(el('out'))el('out').innerHTML='<span class=\"green\">'+(abyssFloor<=MAX_FLOOR?'Этаж '+abyssFloor+' открыт.':'Глубина '+abyssFloor+' открыта.')+'</span>';return}"
    if old not in s: raise SystemExit(f'{path}: finite floor transition not found')
    s=s.replace(old,new,1)

    # Полностью удаляем старое конечное завершение вместе с его закрывающей скобкой.
    old="abyssBossDefeated=true;save();logEvent('БЕЗДНА','Вершина Бездны достигнута.');if(el('out'))el('out').innerHTML='<span class=\"gold\">Ты достиг вершины Бездны.</span>';screenHistory=['menu','main'];history.replaceState({screen:'main'},'','#main');setScreen('main',false);return}"
    if old not in s: raise SystemExit(f'{path}: finite Abyss ending not found')
    s=s.replace(old,'',1)

    # Смерть больше не сбрасывает глубину. После смерти герой возвращается в город с сохранённой глубиной.
    old="logEvent('СМЕРТЬ','Герой пал на этаже '+abyssFloor+', комната '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Забег завершён.');resetAbyss();hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    new="logEvent('СМЕРТЬ','Герой пал на глубине '+abyssFloor+', комнате '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'. Глубина сохранена.');abyssRoom=0;abyssRoomContent='Новая комната ещё не исследована.';abyssBossDefeated=false;hero.hp=hero.maxHp;hero.energy=hero.maxEnergy;save();"
    if old not in s: raise SystemExit(f'{path}: death reset block not found')
    s=s.replace(old,new,1)

    # После 7-го этажа индикатор показывает бесконечные Глубины.
    old="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+'/'+MAX_FLOOR;"
    new="if(el('abyssFloor'))el('abyssFloor').textContent=abyssFloor+(abyssFloor>=8?' · Глубины':'/'+MAX_FLOOR);if(el('abyssRoomInfo'))el('abyssRoomInfo').innerHTML='<b>Комната '+Math.min(ROOMS_PER_FLOOR,abyssRoom+1)+'/'+ROOMS_PER_FLOOR+'</b><br><span class=\"muted\">'+abyssRoomContent+'</span>';"
    if old not in s: raise SystemExit(f'{path}: abyss floor display not found')
    s=s.replace(old,new,1)

    # Кнопка после пятой комнаты всегда ведёт дальше.
    old="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?(abyssFloor<MAX_FLOOR?'Следующий этаж':'Завершить Бездну'):'Войти в комнату'"
    new="el('exploreBtn').textContent=abyssRoom>=ROOMS_PER_FLOOR?'Следующая глубина':'Войти в комнату'"
    if old not in s: raise SystemExit(f'{path}: explore button text not found')
    s=s.replace(old,new,1)

    # Храним описание последней исследуемой комнаты отдельно от прогресса, чтобы показывать его в Бездна.
    if "let abyssRoomContent='Новая комната ещё не исследована.';" not in s:
        old="let abyssFloor=1,abyssRoom=0,enemy=null,guard=false,abyssBossDefeated=false;"
        new="let abyssFloor=1,abyssRoom=0,enemy=null,guard=false,abyssBossDefeated=false;let abyssRoomContent='Новая комната ещё не исследована.';"
        if old not in s: raise SystemExit(f'{path}: abyss state declaration not found')
        s=s.replace(old,new,1)

    # Восстанавливаем описание комнаты из сохранения, не меняя остальные данные сохранения.
    old="abyssBossDefeated=!!data.abyssBossDefeated;journalEntries=Array.isArray(data.journal)?data.journal:[];"
    new="abyssBossDefeated=!!data.abyssBossDefeated;abyssRoomContent=String(data.abyssRoomContent||'Новая комната ещё не исследована.');journalEntries=Array.isArray(data.journal)?data.journal:[];"
    if old in s:
        s=s.replace(old,new,1)

    # Добавляем описание комнаты в сохранение.
    old="function save(){localStorage.setItem(saveKey,JSON.stringify({hero,abyssFloor,abyssRoom,abyssBossDefeated,journal:journalEntries,allies}));}"
    new="function save(){localStorage.setItem(saveKey,JSON.stringify({hero,abyssFloor,abyssRoom,abyssBossDefeated,abyssRoomContent,journal:journalEntries,allies}));}"
    if old in s:
        s=s.replace(old,new,1)

    # Очищаем описание при новом начале Бездны.
    old="function resetAbyss(){abyssFloor=1;abyssRoom=0;abyssBossDefeated=false;updateAbyss()}"
    new="function resetAbyss(){abyssFloor=1;abyssRoom=0;abyssBossDefeated=false;abyssRoomContent='Новая комната ещё не исследована.';updateAbyss()}"
    if old not in s: raise SystemExit(f'{path}: resetAbyss not found')
    s=s.replace(old,new,1)

    # Показываем найденное содержимое события.
    old="const result=event.apply();abyssRoom++;save();logEvent('СОБЫТИЕ',event.name+': '+result);"
    new="const result=event.apply();abyssRoomContent='Событие: '+event.name+' — '+result;abyssRoom++;save();logEvent('СОБЫТИЕ',event.name+': '+result);"
    if old not in s: raise SystemExit(f'{path}: event room block not found')
    s=s.replace(old,new,1)

    # Показываем пустой/спокойный проход без боя.
    old="if(!boss&&!elite&&Math.random()<0.40){abyssRoom++;save();logEvent('БЕЗ БОЯ','Путь в Бездне продолжается без столкновения.');"
    new="if(!boss&&!elite&&Math.random()<0.40){abyssRoomContent='Пустой проход — врагов и событий не обнаружено.';abyssRoom++;save();logEvent('БЕЗ БОЯ','Путь в Бездне продолжается без столкновения.');"
    if old not in s: raise SystemExit(f'{path}: no-battle room block not found')
    s=s.replace(old,new,1)

    # Показываем врага, который находится в комнате.
    old="enemy={name:boss?'Владыка Бездны':names[Math.floor(Math.random()*names.length)],hp:Math.round(hp),max:Math.round(hp),attack:boss?24:elite?16+abyssFloor:8+abyssFloor*2,def:boss?8:elite?4:Math.floor(abyssFloor/2),xp:boss?150:elite?90:50+abyssFloor*5,gold:boss?150:elite?70:20+abyssFloor*5,isElite:elite,isBoss:boss,phase:1,icon:boss?'👑':elite?'👿':'👹'};logEvent"
    new="enemy={name:boss?'Владыка Бездны':names[Math.floor(Math.random()*names.length)],hp:Math.round(hp),max:Math.round(hp),attack:boss?24:elite?16+abyssFloor:8+abyssFloor*2,def:boss?8:elite?4:Math.floor(abyssFloor/2),xp:boss?150:elite?90:50+abyssFloor*5,gold:boss?150:elite?70:20+abyssFloor*5,isElite:elite,isBoss:boss,phase:1,icon:boss?'👑':elite?'👿':'👹'};abyssRoomContent=(boss?'Босс: ':elite?'Элитный враг: ':'Враг: ')+enemy.name;logEvent"
    if old not in s: raise SystemExit(f'{path}: enemy room block not found')
    s=s.replace(old,new,1)

    # При победе оставляем описание побеждённого противника на экране Бездны.
    if "abyssRoomContent=abyssRoomContent+' · Побеждён';" not in s:
        old="const loot=generateLoot();const lootAdded=addItemToInventory(loot);abyssRoom++;"
        new="const loot=generateLoot();const lootAdded=addItemToInventory(loot);abyssRoomContent=abyssRoomContent+' · Побеждён';abyssRoom++;"
        if old not in s: raise SystemExit(f'{path}: victory room block not found')
        s=s.replace(old,new,1)

    # В интерфейсе Бездны показываем отдельную карточку комнаты.
    old='<div class=\"info-row\"><span>Комнаты</span><b id=\"abyssRooms\">0/5</b></div></div><button id=\"exploreBtn\"'
    new='<div class=\"info-row\"><span>Комнаты</span><b id=\"abyssRooms\">0/5</b></div></div><div class=\"info-card\" id=\"abyssRoomInfo\" style=\"margin-top:7px;line-height:1.55\">Комната 1/5<br><span class=\"muted\">Новая комната ещё не исследована.</span></div><button id=\"exploreBtn\"'
    if old not in s: raise SystemExit(f'{path}: Abyss room UI location not found')
    s=s.replace(old,new,1)

    # CSS только для читаемости новой карточки; существующий интерфейс не меняется.
    css_marker='<style id="abyss-room-info-v1">'
    if css_marker not in s:
        s=s.replace('</head>', '<style id="abyss-room-info-v1">#abyssRoomInfo b{color:#e22;font-size:13px}#abyssRoomInfo .muted{display:inline-block;margin-top:2px}</style></head>', 1)

    marker="const INFINITE_PERSISTENCE_FIX_V2='"
    if marker not in s:
        s=s.replace('</script>',"const INFINITE_PERSISTENCE_FIX_V2='persistent-infinite-abyss';\n</script>",1)

    if s==original: raise SystemExit(f'{path}: no changes made')
    path.write_text(s,encoding='utf-8')
    print(f'Updated {path}')
