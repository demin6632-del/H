// Chronicles of the Abyss V5 — original enemy families
const FAMILIES = [
  { id:"hollow", name:"Пустотник", base:{hp:38,power:8,defense:2,speed:7}, depths:[1,3] },
  { id:"grave_hound", name:"Могильный гончий", base:{hp:52,power:11,defense:3,speed:11}, depths:[1,4] },
  { id:"ash_witch", name:"Пепельная ведьма", base:{hp:70,power:14,defense:4,speed:9}, depths:[2,6] },
  { id:"iron_revenant", name:"Железный ревенант", base:{hp:105,power:17,defense:9,speed:5}, depths:[3,7] },
  { id:"abyssal_stalker", name:"Охотник Бездны", base:{hp:88,power:21,defense:6,speed:14}, depths:[5,7] }
];

export function createEnemy(depth = 1, random = Math.random, elite = false) {
  const candidates = FAMILIES.filter(x => depth >= x.depths[0] && depth <= x.depths[1]);
  const family = candidates[Math.floor(random() * candidates.length)] || FAMILIES[0];
  const scale = 1 + Math.max(0, depth - 1) * 0.22;
  const eliteScale = elite ? 1.65 : 1;
  return {
    id:family.id + (elite ? "_elite" : ""),
    name:(elite ? "Элитный " : "") + family.name,
    stats:{
      hp:Math.round(family.base.hp * scale * eliteScale),
      power:Math.round(family.base.power * scale * eliteScale),
      defense:Math.round(family.base.defense * scale),
      speed:Math.round(family.base.speed * (elite ? 1.08 : 1))
    },
    elite,
    depth
  };
}

export function createBoss(depth) {
  const bosses = [
    {id:"warden_of_ashes",name:"Хранитель Пепла"},
    {id:"mouth_of_depth",name:"Уста Глубины"},
    {id:"black_colossus",name:"Чёрный Колосс"}
  ];
  const b = bosses[(Math.max(1,depth)-1) % bosses.length];
  return {
    id:b.id + "_" + depth,
    name:b.name,
    elite:true,
    boss:true,
    depth,
    stats:{hp:220 + depth*55,power:22 + depth*4,defense:10 + depth*2,speed:8 + depth}
  };
}
