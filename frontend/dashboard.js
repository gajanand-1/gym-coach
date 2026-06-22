/* ═══════════════════════════════════════════════════════════════════
   FitCoach AI — dashboard.js
   All UI logic: state management, macro bars, charts, page routing
═══════════════════════════════════════════════════════════════════ */

// ── App State ────────────────────────────────────────────────────────
const state = {
  profile: {
    name: "Raj", goal: "fat_loss", diet_type: "non_vegetarian",
    weight_kg: 82, target_weight_kg: 75, week: 4,
    calories_target: 2000, protein_target: 140,
    carbs_target: 220, fat_target: 55,
  },
  today: {
    calories: 1050, protein: 62, carbs: 103, fat: 32,
    meals: [
      { name: "Breakfast", items: ["4 Boiled Eggs", "2 Roti", "1 Banana"],
        kcal: 480, protein: 30, carbs: 42, fat: 18 },
      { name: "Lunch",     items: ["200g Chicken Breast", "1 Bowl Rice", "Salad"],
        kcal: 570, protein: 32, carbs: 61, fat: 14 },
    ],
  },
  weights: [
    { date: "Jun 1",  kg: 82.0 }, { date: "Jun 3",  kg: 81.8 },
    { date: "Jun 5",  kg: 81.6 }, { date: "Jun 8",  kg: 81.5 },
    { date: "Jun 10", kg: 81.3 }, { date: "Jun 12", kg: 81.2 },
    { date: "Jun 15", kg: 81.5 }, { date: "Jun 17", kg: 81.0 },
    { date: "Jun 19", kg: 80.8 }, { date: "Jun 22", kg: 81.5 },
  ],
  workoutToday: {
    split: "Push day",
    exercises: [
      { name: "Bench Press",    sets: ["60kg×10", "60kg×10", "60kg×8", "60kg×7"] },
      { name: "Shoulder Press", sets: ["40kg×10", "40kg×10", "40kg×10"] },
      { name: "Incline DB Press", sets: ["30kg×12", "30kg×12", "30kg×10"] },
      { name: "Tricep Pushdown", sets: ["25kg×15", "25kg×15", "25kg×12"] },
    ],
    tip: "You completed +2 reps on Bench Press vs last week. Bump to 62.5kg next session.",
  },
  dietPlan: [],
  workoutPlan: [],
  overloadHistory: [],
  checkinHistory: [],
};


// ── Navigation ───────────────────────────────────────────────────────
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const el = document.getElementById('page-' + page);
  if (el) el.classList.add('active');
  const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
  if (nav) nav.classList.add('active');
  if (page === 'weightlog') renderWeightPage();
  if (page === 'weekdiet')  renderDietPlan();
  if (page === 'workoutplan') renderWorkoutPlan();
  if (page === 'grocery')   renderGrocery();
  if (page === 'overload')  renderOverload();
  if (page === 'foodlog')   renderFoodLogPage();
}

document.querySelectorAll('.nav-item[data-page]').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();
    navigate(item.dataset.page);
  });
});

// ── Greeting ─────────────────────────────────────────────────────────
function initGreeting() {
  const h = new Date().getHours();
  const greet = h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening';
  document.getElementById('greeting-text').textContent = `${greet}, ${state.profile.name}`;
  const day  = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date().getDay()];
  const goal = state.profile.goal.replace('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
  const w1   = state.profile.weight_kg, w2 = state.profile.target_weight_kg;
  document.getElementById('header-sub').textContent =
    `${day}, Week ${state.profile.week} · ${goal} · ${w1}kg → ${w2}kg`;
  document.getElementById('sidebar-username').textContent =
    `${state.profile.name} · ${goal}`;
}

// ── Stat Cards ────────────────────────────────────────────────────────
function updateStatCards() {
  const { calories, protein } = state.today;
  const { calories_target, protein_target, target_weight_kg, weight_kg } = state.profile;
  document.getElementById('cal-consumed').textContent   = calories.toLocaleString();
  document.getElementById('cal-target').textContent     = calories_target.toLocaleString();
  document.getElementById('protein-consumed').textContent = protein;
  document.getElementById('protein-target').textContent   = protein_target;
  const latest = state.weights[state.weights.length - 1];
  document.getElementById('current-weight').textContent = latest ? latest.kg : weight_kg;
  const diff  = (latest ? latest.kg : weight_kg) - target_weight_kg;
  const weeks = Math.round(Math.abs(diff) / 0.5);
  document.getElementById('weeks-left').textContent = weeks || '—';
}


// ── Macro Bars ────────────────────────────────────────────────────────
function updateMacroBars() {
  const { calories, protein, carbs, fat } = state.today;
  const t = state.profile;
  const set = (id, barId, val, max, label) => {
    const pct = Math.min(100, Math.round((val / max) * 100));
    document.getElementById(barId).style.width = pct + '%';
    document.getElementById(id).textContent = label;
  };
  set('num-cal',     'bar-cal',     calories, t.calories_target, `${calories} / ${t.calories_target}`);
  set('num-protein', 'bar-protein', protein,  t.protein_target,  `${protein} / ${t.protein_target}g`);
  set('num-carbs',   'bar-carbs',   carbs,    t.carbs_target,    `${carbs} / ${t.carbs_target}g`);
  set('num-fat',     'bar-fat',     fat,      t.fat_target,      `${fat} / ${t.fat_target}g`);
}

// ── Today's Workout ───────────────────────────────────────────────────
function renderWorkoutToday() {
  const w = state.workoutToday;
  document.getElementById('workout-day-title').textContent = `Today's workout: ${w.split}`;
  const container = document.getElementById('workout-exercises');
  container.innerHTML = w.exercises.map(ex => `
    <div class="exercise-block">
      <div class="exercise-name">${ex.name}</div>
      <div class="set-chips">
        ${ex.sets.map(s => `<span class="set-chip">${s}</span>`).join('')}
      </div>
    </div>
  `).join('');
  if (w.tip) {
    const tip = document.getElementById('coach-tip');
    tip.textContent = `Coach says: ${w.tip}`;
    tip.style.display = 'flex';
  }
}

// ── Food Log ──────────────────────────────────────────────────────────
function renderFoodLogDashboard() {
  const list = document.getElementById('food-log-list');
  list.innerHTML = state.today.meals.map(m => `
    <div class="food-log-entry">
      <div>
        <div class="meal-name">${m.name}</div>
        <div class="meal-macros">${m.items.join(' · ')}</div>
      </div>
      <div class="meal-macros">${m.kcal} kcal · P:${m.protein}g C:${m.carbs}g F:${m.fat}g</div>
    </div>
  `).join('') || '<p class="empty-state">No meals logged yet today.</p>';
}

function logFood() {
  const input = document.getElementById('food-input');
  const text  = input.value.trim();
  if (!text) return;
  const meal = parseFoodInput(text);
  state.today.meals.push(meal);
  state.today.calories += meal.kcal;
  state.today.protein  += meal.protein;
  state.today.carbs    += meal.carbs;
  state.today.fat      += meal.fat;
  input.value = '';
  updateStatCards();
  updateMacroBars();
  renderFoodLogDashboard();
  saveLocal();
}

function logFood2() {
  const input = document.getElementById('food-input-2');
  const text  = input.value.trim();
  if (!text) return;
  const meal = parseFoodInput(text);
  state.today.meals.push(meal);
  state.today.calories += meal.kcal;
  state.today.protein  += meal.protein;
  state.today.carbs    += meal.carbs;
  state.today.fat      += meal.fat;
  input.value = '';
  updateStatCards();
  updateMacroBars();
  renderFoodLogPage();
  saveLocal();
}

function renderFoodLogPage() {
  const list = document.getElementById('food-log-full');
  if (!list) return;
  list.innerHTML = state.today.meals.map(m => `
    <div class="food-log-entry">
      <div>
        <div class="meal-name">${m.name}</div>
        <div class="meal-macros">${m.items.join(' · ')}</div>
      </div>
      <div class="meal-macros">${m.kcal} kcal · P:${m.protein}g C:${m.carbs}g F:${m.fat}g</div>
    </div>
  `).join('') || '<p class="empty-state">No meals logged yet today.</p>';

  const mb = document.getElementById('foodlog-macros');
  if (mb) {
    mb.innerHTML = `
      <div class="macro-row"><span class="macro-label">Calories</span>
        <div class="bar-track"><div class="bar-fill bar-cal" style="width:${pct(state.today.calories,state.profile.calories_target)}%"></div></div>
        <span class="macro-nums">${state.today.calories} / ${state.profile.calories_target}</span></div>
      <div class="macro-row"><span class="macro-label">Protein</span>
        <div class="bar-track"><div class="bar-fill bar-protein" style="width:${pct(state.today.protein,state.profile.protein_target)}%"></div></div>
        <span class="macro-nums">${state.today.protein} / ${state.profile.protein_target}g</span></div>
      <div class="macro-row"><span class="macro-label">Carbs</span>
        <div class="bar-track"><div class="bar-fill bar-carbs" style="width:${pct(state.today.carbs,state.profile.carbs_target)}%"></div></div>
        <span class="macro-nums">${state.today.carbs} / ${state.profile.carbs_target}g</span></div>
      <div class="macro-row"><span class="macro-label">Fat</span>
        <div class="bar-track"><div class="bar-fill bar-fat" style="width:${pct(state.today.fat,state.profile.fat_target)}%"></div></div>
        <span class="macro-nums">${state.today.fat} / ${state.profile.fat_target}g</span></div>`;
  }
}
const pct = (v, max) => Math.min(100, Math.round((v / max) * 100));


// ── Food Parser (client-side nutrient DB) ────────────────────────────
const NUTRIENTS = {
  // Grains
  roti:{k:106,p:3,c:20,f:2}, rice:{k:130,p:3,c:28,f:0}, oats:{k:389,p:17,c:66,f:7},
  bread:{k:265,p:9,c:49,f:3}, paratha:{k:257,p:5,c:35,f:11}, poha:{k:110,p:2,c:24,f:1},
  pasta:{k:131,p:5,c:25,f:1}, "brown rice":{k:123,p:3,c:26,f:1},
  // Dairy
  milk:{k:61,p:3,c:5,f:3}, curd:{k:98,p:11,c:4,f:5}, paneer:{k:265,p:18,c:3,f:20},
  cheese:{k:402,p:25,c:1,f:33}, butter:{k:717,p:1,c:0,f:81}, ghee:{k:900,p:0,c:0,f:99},
  // Fruits
  banana:{k:89,p:1,c:23,f:0}, apple:{k:52,p:0,c:14,f:0},
  orange:{k:47,p:1,c:12,f:0}, mango:{k:60,p:1,c:15,f:0},
  // Veg Protein
  dal:{k:116,p:9,c:20,f:1}, "soy chunks":{k:345,p:52,c:33,f:1},
  tofu:{k:76,p:8,c:2,f:5}, peanuts:{k:567,p:26,c:16,f:49},
  chickpeas:{k:164,p:9,c:27,f:3}, "kidney beans":{k:127,p:9,c:23,f:0},
  // NON-VEG
  "chicken breast":{k:165,p:31,c:0,f:4}, "chicken leg":{k:184,p:26,c:0,f:9},
  "chicken thigh":{k:209,p:26,c:0,f:11}, chicken:{k:165,p:31,c:0,f:4},
  egg:{k:78,p:6,c:0,f:5}, eggs:{k:78,p:6,c:0,f:5},
  "boiled egg":{k:78,p:6,c:0,f:5}, omelette:{k:154,p:11,c:1,f:12},
  fish:{k:136,p:22,c:0,f:5}, "rohu fish":{k:97,p:16,c:0,f:3},
  tuna:{k:116,p:26,c:0,f:1}, salmon:{k:208,p:20,c:0,f:13},
  prawns:{k:99,p:24,c:0,f:1}, mutton:{k:294,p:25,c:0,f:21},
  turkey:{k:189,p:29,c:0,f:7},
  // Nuts
  almonds:{k:579,p:21,c:22,f:50}, walnuts:{k:654,p:15,c:14,f:65},
  cashews:{k:553,p:18,c:30,f:44},
};

function parseFoodInput(text) {
  const mealKeywords = {
    breakfast:['breakfast','morning','subah'],
    lunch:['lunch','afternoon','daal','dal time'],
    dinner:['dinner','night','raat'],
    snack:['snack','evening'],
  };
  let mealName = 'Meal';
  const tl = text.toLowerCase();
  for (const [k, kws] of Object.entries(mealKeywords))
    if (kws.some(w => tl.includes(w))) { mealName = k.charAt(0).toUpperCase()+k.slice(1); break; }

  const items = text.split(/,|and/i).map(s => s.trim()).filter(Boolean);
  let totalK=0, totalP=0, totalC=0, totalF=0;

  items.forEach(item => {
    const qty  = parseFloat(item.match(/(\d+(?:\.\d+)?)/)?.[1] || 1);
    const unit = (item.match(/(\d+(?:\.\d+)?)\s*(g|ml|kg)/i)?.[2]||'').toLowerCase();
    const grams = unit==='g'||unit==='ml' ? qty : unit==='kg' ? qty*1000 : qty*100;
    const name  = item.replace(/\d+(?:\.\d+)?\s*(g|ml|kg|x)?/gi,'').trim().toLowerCase();
    const match = Object.keys(NUTRIENTS).find(k => name.includes(k));
    if (match) {
      const n = NUTRIENTS[match], f = grams/100;
      totalK += n.k*f; totalP += n.p*f; totalC += n.c*f; totalF += n.f*f;
    }
  });

  return {
    name: mealName, items,
    kcal:    Math.round(totalK||Math.random()*300+200),
    protein: Math.round(totalP||Math.random()*20+10),
    carbs:   Math.round(totalC||Math.random()*30+15),
    fat:     Math.round(totalF||Math.random()*10+5),
  };
}


// ── Weight Chart (Canvas) ─────────────────────────────────────────────
function drawWeightChart(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const data = state.weights;
  if (data.length < 2) return;

  ctx.clearRect(0, 0, W, H);
  const pad = { top:12, right:16, bottom:24, left:36 };
  const cw = W - pad.left - pad.right;
  const ch = H - pad.top  - pad.bottom;

  const vals  = data.map(d => d.kg);
  const minV  = Math.min(...vals) - 0.5;
  const maxV  = Math.max(...vals) + 0.5;
  const xStep = cw / (data.length - 1);
  const yScale= ch / (maxV - minV);

  const tx = i  => pad.left + i * xStep;
  const ty = kg => pad.top  + (maxV - kg) * yScale;

  // Grid lines
  ctx.strokeStyle = '#e9ece7';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + (ch / 4) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(W - pad.right, y); ctx.stroke();
  }

  // Gradient fill
  const grad = ctx.createLinearGradient(0, pad.top, 0, H - pad.bottom);
  grad.addColorStop(0, 'rgba(34,165,94,0.18)');
  grad.addColorStop(1, 'rgba(34,165,94,0)');
  ctx.beginPath();
  ctx.moveTo(tx(0), ty(data[0].kg));
  data.forEach((d, i) => { if (i > 0) ctx.lineTo(tx(i), ty(d.kg)); });
  ctx.lineTo(tx(data.length-1), H - pad.bottom);
  ctx.lineTo(tx(0), H - pad.bottom);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.strokeStyle = '#22a55e';
  ctx.lineWidth = 2.5;
  ctx.lineJoin = 'round';
  data.forEach((d, i) => i === 0 ? ctx.moveTo(tx(i), ty(d.kg)) : ctx.lineTo(tx(i), ty(d.kg)));
  ctx.stroke();

  // Dots
  data.forEach((d, i) => {
    ctx.beginPath();
    ctx.arc(tx(i), ty(d.kg), 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    ctx.strokeStyle = '#22a55e';
    ctx.lineWidth = 2;
    ctx.stroke();
  });

  // X labels (every 3rd)
  ctx.fillStyle = '#9ca3af';
  ctx.font = '10px Inter, sans-serif';
  ctx.textAlign = 'center';
  data.forEach((d, i) => {
    if (i % 3 === 0) ctx.fillText(d.date, tx(i), H - 4);
  });

  // Y labels
  ctx.textAlign = 'right';
  for (let i = 0; i <= 4; i++) {
    const kg  = maxV - ((maxV - minV) / 4) * i;
    const y   = pad.top + (ch / 4) * i;
    ctx.fillText(kg.toFixed(1), pad.left - 4, y + 3);
  }
}

function logWeight() {
  const val = parseFloat(document.getElementById('weight-input').value);
  if (!val || val < 30 || val > 300) return;
  const today = new Date();
  const label = `${today.toLocaleString('default',{month:'short'})} ${today.getDate()}`;
  state.weights.push({ date: label, kg: val });
  document.getElementById('weight-input').value = '';
  document.getElementById('weight-current').textContent = val;
  updateStatCards();
  drawWeightChart('weight-canvas');
  saveLocal();
}

function logWeight2() {
  const val = parseFloat(document.getElementById('weight-input-2').value);
  if (!val || val < 30 || val > 300) return;
  const today = new Date();
  const label = `${today.toLocaleString('default',{month:'short'})} ${today.getDate()}`;
  state.weights.push({ date: label, kg: val });
  document.getElementById('weight-input-2').value = '';
  updateStatCards();
  drawWeightChart('weight-canvas');
  renderWeightPage();
  saveLocal();
}

function renderWeightPage() {
  drawWeightChart('weight-canvas-2');
  const tbl = document.getElementById('weight-table');
  if (!tbl) return;
  const rows = [...state.weights].reverse().slice(0, 15);
  tbl.innerHTML = `<table>
    <thead><tr><th>Date</th><th>Weight (kg)</th><th>Change</th></tr></thead>
    <tbody>${rows.map((w, i) => {
      const prev   = rows[i + 1];
      const change = prev ? (w.kg - prev.kg).toFixed(1) : '—';
      const color  = change === '—' ? '' : parseFloat(change) < 0 ? 'color:#22a55e' : 'color:#ef4444';
      return `<tr><td>${w.date}</td><td><b>${w.kg}</b></td>
        <td style="${color}">${change !== '—' ? (parseFloat(change)>0?'+':'')+change+' kg' : '—'}</td></tr>`;
    }).join('')}</tbody></table>`;
  document.getElementById('weight-start').textContent   = state.weights[0]?.kg || '—';
  document.getElementById('weight-current').textContent = state.weights[state.weights.length-1]?.kg || '—';
  document.getElementById('weight-target').textContent  = state.profile.target_weight_kg;
}


// ── Weekly Diet Plan ─────────────────────────────────────────────────
const SAMPLE_NON_VEG_PLAN = [
  { day:"Monday",   daily_cost:160, total_kcal:2010,
    meals:[
      {name:"Breakfast", items:["4 Boiled Eggs","2 Roti (70g)","1 Banana"],       kcal:490, protein_g:32, carbs_g:42, fat_g:18},
      {name:"Lunch",     items:["200g Chicken Breast","1 Bowl Rice","Salad"],      kcal:560, protein_g:48, carbs_g:52, fat_g:10},
      {name:"Snack",     items:["1 Can Tuna (185g)","4 Crackers"],                 kcal:260, protein_g:30, carbs_g:18, fat_g:4},
      {name:"Dinner",    items:["150g Mutton Curry","2 Roti","1 Bowl Dal"],        kcal:700, protein_g:38, carbs_g:55, fat_g:25},
    ]},
  { day:"Tuesday",  daily_cost:145, total_kcal:1980,
    meals:[
      {name:"Breakfast", items:["3-Egg Omelette","2 Roti","1 Glass Milk"],         kcal:480, protein_g:28, carbs_g:38, fat_g:20},
      {name:"Lunch",     items:["150g Rohu Fish Curry","1 Bowl Rice","Curd 100g"], kcal:520, protein_g:36, carbs_g:58, fat_g:12},
      {name:"Snack",     items:["Boiled Eggs x2","1 Apple"],                       kcal:220, protein_g:14, carbs_g:16, fat_g:10},
      {name:"Dinner",    items:["200g Chicken Thigh","2 Roti","Spinach Sabzi"],    kcal:760, protein_g:44, carbs_g:42, fat_g:28},
    ]},
  { day:"Wednesday",daily_cost:155, total_kcal:2020,
    meals:[
      {name:"Breakfast", items:["Oats 80g","Milk 250ml","2 Boiled Eggs"],           kcal:500, protein_g:26, carbs_g:58, fat_g:14},
      {name:"Lunch",     items:["200g Chicken Breast","Brown Rice 150g","Salad"],   kcal:540, protein_g:46, carbs_g:48, fat_g:8},
      {name:"Snack",     items:["100g Paneer","1 Banana"],                          kcal:350, protein_g:20, carbs_g:26, fat_g:18},
      {name:"Dinner",    items:["150g Prawn Curry","2 Roti","Dal"],                 kcal:630, protein_g:40, carbs_g:52, fat_g:16},
    ]},
  { day:"Thursday", daily_cost:150, total_kcal:1990,
    meals:[
      {name:"Breakfast", items:["4 Boiled Eggs","2 Paratha (small)"],              kcal:580, protein_g:30, carbs_g:46, fat_g:26},
      {name:"Lunch",     items:["Tuna Can 185g","1 Bowl Rice","Salad"],            kcal:480, protein_g:42, carbs_g:48, fat_g:6},
      {name:"Snack",     items:["Curd 150g","Almonds 20g"],                        kcal:260, protein_g:14, carbs_g:12, fat_g:16},
      {name:"Dinner",    items:["200g Chicken Leg","2 Roti","Sabzi"],              kcal:670, protein_g:42, carbs_g:40, fat_g:24},
    ]},
  { day:"Friday",   daily_cost:170, total_kcal:2030,
    meals:[
      {name:"Breakfast", items:["3-Egg Scrambled","2 Roti","1 Glass Milk"],        kcal:490, protein_g:28, carbs_g:38, fat_g:20},
      {name:"Lunch",     items:["150g Salmon","Brown Rice 100g","Broccoli"],       kcal:580, protein_g:38, carbs_g:36, fat_g:22},
      {name:"Snack",     items:["Boiled Eggs x2","Peanuts 20g"],                   kcal:280, protein_g:16, carbs_g:6,  fat_g:20},
      {name:"Dinner",    items:["200g Chicken Breast Curry","2 Roti","Dal"],       kcal:680, protein_g:50, carbs_g:52, fat_g:14},
    ]},
  { day:"Saturday", daily_cost:160, total_kcal:2050,
    meals:[
      {name:"Breakfast", items:["Oats 80g","Milk 250ml","4 Egg Whites"],           kcal:440, protein_g:30, carbs_g:56, fat_g:8},
      {name:"Lunch",     items:["200g Mutton Biryani","Raita"],                    kcal:680, protein_g:32, carbs_g:68, fat_g:24},
      {name:"Snack",     items:["1 Can Tuna","4 Rice Cakes"],                      kcal:270, protein_g:30, carbs_g:22, fat_g:4},
      {name:"Dinner",    items:["150g Prawn Masala","2 Roti","Sabzi"],             kcal:660, protein_g:42, carbs_g:44, fat_g:20},
    ]},
  { day:"Sunday",   daily_cost:140, total_kcal:1960,
    meals:[
      {name:"Breakfast", items:["4 Boiled Eggs","Poha 100g"],                      kcal:440, protein_g:28, carbs_g:48, fat_g:14},
      {name:"Lunch",     items:["200g Chicken Breast","1 Bowl Rice","Dal"],        kcal:640, protein_g:52, carbs_g:58, fat_g:12},
      {name:"Snack",     items:["Curd 150g","1 Banana"],                           kcal:235, protein_g:14, carbs_g:30, fat_g:7},
      {name:"Dinner",    items:["150g Fish Curry","2 Roti","Spinach Dal"],         kcal:645, protein_g:38, carbs_g:46, fat_g:18},
    ]},
];

function generateDiet() {
  state.dietPlan = SAMPLE_NON_VEG_PLAN;
  renderDietPlan();
  saveLocal();
}

function renderDietPlan() {
  const grid = document.getElementById('diet-plan-grid');
  if (!grid) return;
  if (!state.dietPlan.length) {
    grid.innerHTML = '<p class="empty-state">Click "Generate Plan" to create your non-veg meal plan.</p>';
    return;
  }
  grid.innerHTML = state.dietPlan.map(day => `
    <div class="diet-day-card">
      <div class="diet-day-title">
        <span>${day.day}</span>
        <span class="diet-day-cost">₹${day.daily_cost} · ${day.total_kcal} kcal</span>
      </div>
      ${day.meals.map(m => `
        <div class="diet-meal">
          <div class="diet-meal-name">${m.name}</div>
          <div class="diet-meal-items">${m.items.join(', ')}</div>
          <div class="diet-meal-macros">${m.kcal} kcal · P:${m.protein_g}g C:${m.carbs_g}g F:${m.fat_g}g</div>
        </div>
      `).join('')}
    </div>
  `).join('');
}


// ── Grocery List ─────────────────────────────────────────────────────
function renderGrocery() {
  const el = document.getElementById('grocery-content');
  if (!el) return;
  const nonVeg = [
    {item:"Chicken Breast",   qty:"1 kg",    cost:300},
    {item:"Eggs (12 pcs)",    qty:"12 pcs",  cost:96},
    {item:"Rohu Fish",        qty:"500 g",   cost:90},
    {item:"Tuna Cans",        qty:"2 cans",  cost:100},
    {item:"Mutton",           qty:"500 g",   cost:275},
    {item:"Prawns",           qty:"250 g",   cost:88},
  ];
  const pantry = [
    {item:"Oats",             qty:"1 kg",    cost:80},
    {item:"Brown Rice",       qty:"2 kg",    cost:160},
    {item:"Roti Atta",        qty:"2 kg",    cost:90},
    {item:"Milk",             qty:"7 litres",cost:336},
    {item:"Curd",             qty:"500 g",   cost:40},
    {item:"Banana",           qty:"1 dozen", cost:60},
    {item:"Spinach",          qty:"500 g",   cost:20},
    {item:"Onion + Tomato",   qty:"1 kg ea", cost:60},
    {item:"Dal (Moong)",      qty:"500 g",   cost:60},
    {item:"Almonds",          qty:"100 g",   cost:70},
  ];
  const all   = [...nonVeg, ...pantry];
  const total = all.reduce((s,i) => s + i.cost, 0);

  el.innerHTML = `
    <div class="card-title">🛒 Weekly Grocery List (Non-Veg)</div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px">
      <thead><tr style="border-bottom:1px solid #e5e7eb">
        <th style="text-align:left;padding:7px 8px;color:#6b7280;font-size:11px">ITEM</th>
        <th style="text-align:left;padding:7px 8px;color:#6b7280;font-size:11px">QTY</th>
        <th style="text-align:right;padding:7px 8px;color:#6b7280;font-size:11px">COST</th>
      </tr></thead>
      <tbody>
        <tr><td colspan="3" style="padding:8px 8px 4px;font-weight:700;font-size:11px;color:#1a7a4a;letter-spacing:.05em">🍗 NON-VEG PROTEINS</td></tr>
        ${nonVeg.map(i=>`<tr style="border-bottom:1px solid #f3f4f2">
          <td style="padding:7px 8px">${i.item}</td>
          <td style="padding:7px 8px;color:#6b7280">${i.qty}</td>
          <td style="padding:7px 8px;text-align:right">₹${i.cost}</td></tr>`).join('')}
        <tr><td colspan="3" style="padding:8px 8px 4px;font-weight:700;font-size:11px;color:#1a7a4a;letter-spacing:.05em">🥦 PANTRY & VEG</td></tr>
        ${pantry.map(i=>`<tr style="border-bottom:1px solid #f3f4f2">
          <td style="padding:7px 8px">${i.item}</td>
          <td style="padding:7px 8px;color:#6b7280">${i.qty}</td>
          <td style="padding:7px 8px;text-align:right">₹${i.cost}</td></tr>`).join('')}
        <tr style="border-top:2px solid #e5e7eb;font-weight:700">
          <td style="padding:9px 8px">TOTAL</td><td></td>
          <td style="padding:9px 8px;text-align:right;color:#1a7a4a">₹${total}</td>
        </tr>
      </tbody>
    </table>
    <div style="font-size:12px;color:#6b7280">Monthly estimate: ₹${total*4} &nbsp;|&nbsp; Daily: ₹${Math.round(total/7)}</div>`;
}

// ── Workout Plan ─────────────────────────────────────────────────────
const SAMPLE_WORKOUT = [
  {day:"Monday",    split:"Push",  cardio:"20 min treadmill incline 5",
   exercises:[{name:"Bench Press",sets:4,reps:"8-10",rest:90},{name:"Incline DB Press",sets:3,reps:"10-12",rest:75},
              {name:"Shoulder Press",sets:3,reps:"10",rest:75},{name:"Tricep Pushdown",sets:3,reps:"12-15",rest:60}]},
  {day:"Tuesday",   split:"Pull",  cardio:"20 min cycling",
   exercises:[{name:"Deadlift",sets:4,reps:"6-8",rest:120},{name:"Barbell Row",sets:3,reps:"10",rest:90},
              {name:"Lat Pulldown",sets:3,reps:"12",rest:75},{name:"Bicep Curl",sets:3,reps:"12-15",rest:60}]},
  {day:"Wednesday", split:"Legs",  cardio:"20 min treadmill",
   exercises:[{name:"Squat",sets:4,reps:"8-10",rest:120},{name:"Leg Press",sets:3,reps:"12",rest:90},
              {name:"Romanian Deadlift",sets:3,reps:"10",rest:90},{name:"Calf Raises",sets:4,reps:"15-20",rest:60}]},
  {day:"Thursday",  split:"Rest",  cardio:"", exercises:[]},
  {day:"Friday",    split:"Push",  cardio:"20 min treadmill",
   exercises:[{name:"Overhead Press",sets:4,reps:"8-10",rest:90},{name:"Cable Fly",sets:3,reps:"12",rest:60},
              {name:"Dips",sets:3,reps:"10-12",rest:75},{name:"Skull Crushers",sets:3,reps:"12",rest:60}]},
  {day:"Saturday",  split:"Pull",  cardio:"20 min cycling",
   exercises:[{name:"Pull-Ups",sets:4,reps:"6-10",rest:90},{name:"Seated Row",sets:3,reps:"12",rest:75},
              {name:"Face Pulls",sets:3,reps:"15",rest:60},{name:"Hammer Curl",sets:3,reps:"12",rest:60}]},
  {day:"Sunday",    split:"Rest",  cardio:"", exercises:[]},
];

function generateWorkout() {
  state.workoutPlan = SAMPLE_WORKOUT;
  renderWorkoutPlan();
  saveLocal();
}

function renderWorkoutPlan() {
  const grid = document.getElementById('workout-plan-grid');
  if (!grid) return;
  if (!state.workoutPlan.length) {
    grid.innerHTML = '<p class="empty-state">Click "Generate Plan" to create your workout programme.</p>';
    return;
  }
  grid.innerHTML = state.workoutPlan.map(day => {
    if (day.split === 'Rest') return `
      <div class="diet-day-card" style="opacity:.6">
        <div class="diet-day-title">${day.day} <span class="diet-day-cost">Rest Day 🛌</span></div>
        <p style="font-size:13px;color:#6b7280">Active recovery, stretching, walking.</p>
      </div>`;
    return `<div class="diet-day-card">
      <div class="diet-day-title">${day.day} <span class="diet-day-cost">${day.split}</span></div>
      ${day.exercises.map(ex=>`
        <div class="diet-meal">
          <div class="diet-meal-name">${ex.name}</div>
          <div class="diet-meal-items">${ex.sets} sets × ${ex.reps} reps · rest ${ex.rest}s</div>
        </div>`).join('')}
      ${day.cardio?`<div style="font-size:12px;color:#22a55e;margin-top:8px">🏃 ${day.cardio}</div>`:''}
    </div>`;
  }).join('');
}


// ── Progressive Overload ─────────────────────────────────────────────
function logWorkout() {
  const input = document.getElementById('workout-input');
  const text  = input.value.trim();
  if (!text) return;

  const lines    = text.split(/,\s*(?=[A-Za-z])/);
  const entries  = [];
  const today    = new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'short'});

  lines.forEach(line => {
    const nameMatch   = line.match(/^([A-Za-z\s]+)/);
    const weightMatch = line.match(/(\d+(?:\.\d+)?)\s*kg/i);
    const repsMatch   = line.match(/kg[^:]*:?\s*([\d,\s]+)/i) || line.match(/\d+kg\s+([\d\s,]+)/i);
    if (!nameMatch) return;
    const name   = nameMatch[1].trim();
    const weight = weightMatch ? parseFloat(weightMatch[1]) : 0;
    const reps   = repsMatch
      ? repsMatch[1].split(/[\s,]+/).map(Number).filter(Boolean)
      : [10, 10, 8];

    // Find prev entry for overload advice
    const prev = state.overloadHistory.find(e => e.exercise.toLowerCase() === name.toLowerCase());
    let advice = '';
    if (!prev) {
      advice = 'First session logged — aim to beat this next week! 💪';
    } else {
      const prevAvg = prev.reps.reduce((a,b)=>a+b,0)/prev.reps.length;
      const curAvg  = reps.reduce((a,b)=>a+b,0)/reps.length;
      if (curAvg >= prevAvg + 1.5) {
        advice = `Reps improved (avg ${prevAvg.toFixed(1)} → ${curAvg.toFixed(1)}). Increase to ${weight + 2.5}kg next week 🔺`;
      } else if (curAvg < prevAvg - 1) {
        advice = `Performance dipped. Prioritise sleep & nutrition. Keep ${weight}kg next week.`;
      } else {
        advice = `Consistent! Try 1 more rep per set next week before bumping weight.`;
      }
    }

    entries.push({ exercise: name, date: today, weight, reps, advice,
      prevWeight: prev?.weight || null, prevReps: prev?.reps || null });

    // Update overload history
    const idx = state.overloadHistory.findIndex(e => e.exercise.toLowerCase() === name.toLowerCase());
    if (idx >= 0) state.overloadHistory[idx] = { exercise: name, weight, reps };
    else          state.overloadHistory.push({ exercise: name, weight, reps });
  });

  input.value = '';
  renderOverloadEntries(entries);
  saveLocal();
}

function renderOverloadEntries(entries) {
  const list = document.getElementById('overload-list');
  if (!list) return;
  list.innerHTML = entries.map(e => `
    <div class="overload-card">
      <div class="overload-exercise">${e.exercise}</div>
      <div class="overload-weeks">
        ${e.prevWeight ? `<span>Last week: <b>${e.prevWeight}kg × [${e.prevReps?.join(', ')}]</b></span>` : ''}
        <span>This week: <b>${e.weight}kg × [${e.reps.join(', ')}]</b></span>
      </div>
      <div class="overload-advice">💡 ${e.advice}</div>
    </div>`).join('');
}

function renderOverload() {
  if (!state.overloadHistory.length) {
    const list = document.getElementById('overload-list');
    if (list) list.innerHTML = '<p class="empty-state">No workouts logged yet. Log a session above.</p>';
  }
}

// ── Weekly Check-In ───────────────────────────────────────────────────
function submitCheckin() {
  const weight = parseFloat(document.getElementById('ci-weight').value) || null;
  const energy = document.getElementById('ci-energy').value;
  const hunger = document.getElementById('ci-hunger').value;
  const sleep  = parseFloat(document.getElementById('ci-sleep').value) || 7;
  const notes  = document.getElementById('ci-notes').value;

  const checkin = { date: new Date().toLocaleDateString(), weight, energy, hunger, sleep, notes };
  state.checkinHistory.push(checkin);

  // Rule-based recommendations
  let cals_adj = 0, cardio_adj = 0, vol = 'Maintain', tip = '';
  if (weight && state.weights.length >= 2) {
    const recent = state.weights.slice(-7);
    const trend  = (recent[recent.length-1].kg - recent[0].kg) / recent.length;
    if (Math.abs(trend) < 0.05)  { cals_adj = -100; tip = 'Weight stalled — small calorie cut.'; }
    if (trend < -0.14)            { cals_adj = +150; tip = 'Losing too fast — add 150 kcal to protect muscle.'; }
    if (trend > 0.1 && state.profile.goal === 'fat_loss') { cals_adj = -150; tip = 'Gaining weight — cut 150 kcal.'; }
  }
  if (energy === 'low' && hunger === 'low') { cals_adj = +100; tip = 'Energy & hunger both low — likely under-eating.'; }
  if (sleep < 6)  { vol = 'Decrease'; tip += ' Sleep under 6h — reduce training volume this week.'; }
  if (cardio_adj === 0 && cals_adj === 0 && !tip) tip = 'Great week! Stay consistent and keep pushing. 💪';

  const result = document.getElementById('checkin-result');
  result.style.display = 'block';
  result.innerHTML = `
    <b>✅ Check-In Recorded — ${checkin.date}</b><br><br>
    Weight: ${weight||'N/A'} kg &nbsp;|&nbsp; Energy: ${energy} &nbsp;|&nbsp; Hunger: ${hunger} &nbsp;|&nbsp; Sleep: ${sleep}h<br><br>
    <b>Coach's Recommendations:</b><br>
    ${cals_adj !== 0 ? `🍽️ Calories: ${cals_adj > 0 ? '+' : ''}${cals_adj} kcal/day<br>` : ''}
    ${cardio_adj !== 0 ? `🏃 Cardio: +${cardio_adj} min/session<br>` : ''}
    💪 Training volume: ${vol}<br><br>
    📝 ${tip}`;

  if (weight) {
    const today = new Date();
    state.weights.push({ date: `${today.toLocaleString('default',{month:'short'})} ${today.getDate()}`, kg: weight });
    updateStatCards();
    drawWeightChart('weight-canvas');
  }
  saveLocal();
}

// ── Ask Coach (simple keyword responses) ─────────────────────────────
const COACH_RESPONSES = {
  protein: "For fat loss at 82kg, aim for ~148g protein/day. Best sources: chicken breast (31g/100g), eggs (6g each), tuna (26g/100g), paneer (18g/100g).",
  chicken: "Chicken breast is your best friend: 165 kcal, 31g protein, 0 carbs per 100g. Grill or boil it — no oil needed!",
  egg:     "Eggs are perfect: whole egg = 78 kcal, 6g protein. Egg whites = 0 fat, pure protein. 4-6 eggs/day is fine for most people.",
  diet:    "Your non-veg diet plan is on the Weekly Diet page. It's built around chicken, eggs, fish, and mutton to hit 140g+ protein daily.",
  workout: "Your PPL split is on the Workout Plan page. Push on Mon/Fri, Pull on Tue/Sat, Legs on Wed. Rest Thu/Sun.",
  overload:"Progressive overload: increase weight by 2.5kg once you can complete all sets with good form. Log in Overload section.",
  sleep:   "Sleep 7-9 hours for optimal muscle recovery and fat loss. Poor sleep raises cortisol and slows fat loss significantly.",
  creatine:"Creatine monohydrate 5g/day is the most researched supplement. Safe, effective, cheap. Take it daily — timing doesn't matter.",
  supplement:"Focus on: Whey protein (if needed), Creatine 5g/day, Vitamin D3 2000IU, Fish Oil 1g. Everything else is optional.",
  cardio:  "For fat loss, 20-30 min low intensity cardio (walking, cycling) after weights 3-4x/week. Don't overdo it — protect muscle.",
  fat:     "Healthy fats from eggs, fish, almonds, olive oil. Fat doesn't make you fat — excess calories do.",
  water:   "Aim for 3-4 litres of water daily. Hydration improves performance, recovery, and fat loss.",
};

function sendChat() {
  const input = document.getElementById('chat-input');
  const text  = input.value.trim();
  if (!text) return;

  const msgs = document.getElementById('chat-messages');
  msgs.innerHTML += `<div class="chat-bubble user">${text}</div>`;
  input.value = '';

  const tl = text.toLowerCase();
  let reply = "I can help with diet, workouts, protein intake, supplements, and more. What would you like to know?";
  for (const [key, resp] of Object.entries(COACH_RESPONSES))
    if (tl.includes(key)) { reply = resp; break; }

  setTimeout(() => {
    msgs.innerHTML += `<div class="chat-bubble coach">🤖 ${reply}</div>`;
    msgs.scrollTop = msgs.scrollHeight;
  }, 400);
  msgs.scrollTop = msgs.scrollHeight;
}

// ── LocalStorage persistence ─────────────────────────────────────────
function saveLocal() {
  try {
    localStorage.setItem('fitcoach_state', JSON.stringify({
      today: state.today, weights: state.weights,
      dietPlan: state.dietPlan, workoutPlan: state.workoutPlan,
      overloadHistory: state.overloadHistory, checkinHistory: state.checkinHistory,
    }));
  } catch(e) {}
}

function loadLocal() {
  try {
    const saved = JSON.parse(localStorage.getItem('fitcoach_state') || '{}');
    if (saved.today)          state.today           = saved.today;
    if (saved.weights?.length) state.weights         = saved.weights;
    if (saved.dietPlan)       state.dietPlan        = saved.dietPlan;
    if (saved.workoutPlan)    state.workoutPlan     = saved.workoutPlan;
    if (saved.overloadHistory) state.overloadHistory = saved.overloadHistory;
    if (saved.checkinHistory)  state.checkinHistory  = saved.checkinHistory;
  } catch(e) {}
}

// ── Boot ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadLocal();
  initGreeting();
  updateStatCards();
  updateMacroBars();
  renderWorkoutToday();
  renderFoodLogDashboard();
  drawWeightChart('weight-canvas');

  document.getElementById('weight-start').textContent   = state.weights[0]?.kg || state.profile.weight_kg;
  document.getElementById('weight-current').textContent = state.weights[state.weights.length-1]?.kg || state.profile.weight_kg;
  document.getElementById('weight-target').textContent  = state.profile.target_weight_kg;
});
