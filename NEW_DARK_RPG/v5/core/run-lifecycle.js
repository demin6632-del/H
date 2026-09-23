// Chronicles of the Abyss V5 — death and run lifecycle
import { clearRun } from "../core/run-persistence.js";

export function finishDeath(game) {
  const state=game.state;
  state.meta.deaths=(state.meta.deaths||0)+1;
  state.meta.bestDepth=Math.max(state.meta.bestDepth||1,state.abyss.depth||1);
  state.abyss.active=false;
  state.abyss.room=0;
  state.abyss.pending=null;
  state.abyss.morale=100;
  state.abyss.risk=0;
  state.abyss.awareness=50;
  state.abyss.tempo=50;
  game.combat=null;
  clearRun();
  return {dead:true,depth:state.abyss.depth,deaths:state.meta.deaths};
}

export function newGame(game) {
  game.state={
    version:5,
    meta:{deaths:0,gold:0,bestDepth:1},
    character:{level:1,xp:0,classId:null,stats:{},baseStats:{},skills:[],equipment:{}},
    inventory:[],
    abyss:{active:false,depth:1,room:0,pending:null,morale:100,risk:0,awareness:50,tempo:50},
    economy:{reputation:0,merchants:{}},
    endgame:{arena:{bestWave:0},achievements:{},collections:{},contracts:{}}
  };
  game.combat=null;
  clearRun();
  return game;
}
