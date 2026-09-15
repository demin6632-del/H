from pathlib import Path
p=Path('NEW_DARK_RPG/index.html')
s=p.read_text(encoding='utf-8')
# Снижаем только вероятность обычного боевого столкновения в генерации комнаты.
old='Math.random()<0.65'
new='Math.random()<0.40'
if old not in s:
    raise SystemExit('Не найдено текущее значение вероятности обычного боя 0.65')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Вероятность обычного боя изменена с 65% до 40%.')
