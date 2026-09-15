from pathlib import Path

p=Path('NEW_DARK_RPG/index.html')
s=p.read_text(encoding='utf-8')

# Уменьшаем частоту обычных боёв, не меняя остальные механики.
old='Math.random()<0.18'
new='Math.random()<0.10'
if old not in s:
    raise SystemExit('Не найдено текущее значение частоты событий 0.18')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('Частота случайных событий изменена с 18% до 10%.')
