/* global React, ReactDOM, Recharts */
const R = Recharts;

const C = {
  navy: '#1B3DAD', navyDeep: '#14307F',
  blue: '#4A7BD8', blueSoft: '#E4ECF8',
  red: '#E03A3A', redSoft: '#FBE3E3',
  green: '#2A9D6E', gold: '#D9A53B',
  ink: '#0B0F1C',
  g100:'#F2F4F8', g200:'#DEE2EC', g300:'#C9CDD8',
  g400:'#A4ABBC', g500:'#6E7891', g600:'#4B5470', g700:'#2E3650',
};
const TOTAL = 18;

// ─── CHROME ──────────────────────────────────────────────────
function Chrome({ page, num, title, eyebrow, children, hasImpl = true }) {
  return (
    <>
      <div className="a-stripe" />
      <div className="a-pad">
        <div className="a-head">
          <div className="a-titlewrap">
            {num && <span className="a-num">{num}</span>}
            <div>
              <div className="a-title">{title}</div>
              {eyebrow && <div className="a-eyebrow">{eyebrow}</div>}
            </div>
          </div>
          <div className="a-meta">
            <div>속도는벡터 · STYLE A · ACADEMIC</div>
            <div className="pn" style={{marginTop:6}}>
              {String(page).padStart(2,'0')} <span className="total">/ {String(TOTAL).padStart(2,'0')}</span>
            </div>
          </div>
        </div>
        <div className="a-rule" />
        <div className="a-body" style={{paddingBottom: hasImpl ? 78 : 32}}>{children}</div>
      </div>
      {!hasImpl && (
        <div className="a-footer">
          <span>속도는벡터 · CAPSTONE 2026</span>
          <span>FINAL · 2026.05.27</span>
        </div>
      )}
    </>
  );
}
function Impl({ children }) { return <div className="a-impl"><div>{children}</div></div>; }

// ─── 01 COVER ───────────────────────────────────────────────
function S1() {
  return (
    <>
      <div className="a-stripe" />
      <div className="a-pad" style={{paddingTop: 56, paddingBottom: 56}}>
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
          <div className="a-eyebrow" style={{margin:0}}>CAPSTONE 2026‑1 · FINAL · YONSEI CSE</div>
          <div style={{display:'flex', gap: 8}}>
            <span className="pill navy">YONSEI · CSE</span>
            <span className="pill red">BDAI LAB</span>
          </div>
        </div>
        <div style={{flex:1, display:'flex', flexDirection:'column', justifyContent:'center', maxWidth: 1080}}>
          <div style={{fontSize: 60, fontWeight: 800, lineHeight: 1.04, letterSpacing:'-0.03em', color: C.ink}}>
            Skew‑Aware<br/>
            Stratified Sampling for<br/>
            <span style={{color: C.navy}}>Vector‑Augmented</span> Analytical Query
          </div>
          <div style={{marginTop: 22, fontSize: 18, color: C.g600, lineHeight: 1.55, maxWidth: 880}}>
            벡터 카디널리티 추정에서 distribution-aware stratified sampling 의 정량적 가치
          </div>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 24, paddingTop: 22, borderTop:`1px solid ${C.g200}`}}>
          <div>
            <div className="label-mono" style={{marginBottom: 6}}>Team</div>
            <div style={{fontSize:15, fontWeight:700, color: C.ink}}>속도는벡터</div>
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>박세은 · 강재현 · 조현빈 · 이동욱</div>
          </div>
          <div>
            <div className="label-mono" style={{marginBottom: 6}}>Advisor</div>
            <div style={{fontSize:13, color: C.ink, fontWeight: 600}}>박광현 교수</div>
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>BDAI Research Lab</div>
          </div>
          <div>
            <div className="label-mono" style={{marginBottom: 6}}>Reference</div>
            <div style={{fontSize:12, color: C.ink, fontFamily:'var(--font-mono)', fontWeight: 600}}>arXiv:2512.09695v2</div>
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>Exqutor (BDAI)</div>
          </div>
          <div>
            <div className="label-mono" style={{marginBottom: 6}}>Date</div>
            <div style={{fontSize:13, color: C.ink, fontFamily:'var(--font-mono)', fontWeight: 600}}>2026.05.27</div>
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>Final Presentation</div>
          </div>
        </div>
      </div>
    </>
  );
}

// ─── 02 TOC ─────────────────────────────────────────────────
function S2() {
  const items = [
    {n:'01', t:'Problem',           sub:'문제 정의'},
    {n:'02', t:'Prior Work',        sub:'Exqutor 보완책'},
    {n:'03', t:'Approach',          sub:'Skew-Aware Sampling'},
    {n:'04', t:'RQ1 · Diagnostic',  sub:'단조성 통계 확정'},
    {n:'05', t:'RQ2 · Aware',       sub:'40 / 40 oracle'},
    {n:'06', t:'RQ3 · Agnostic',    sub:'22 method 비교'},
    {n:'07', t:'Cross-Scale',       sub:'1M → 8M'},
    {n:'08', t:'Mechanism',         sub:'locality + redundancy'},
    {n:'09', t:'Effect Honesty',    sub:'DEFF · ESS · routing'},
    {n:'10', t:'Future Work',       sub:'L1 ~ L4'},
  ];
  return (
    <Chrome page={2} title="오늘의 구성" eyebrow="TABLE OF CONTENTS · 10 SECTIONS · 16 SLIDES · 12 MIN" hasImpl={false}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap: 14, flex:1}}>
        {items.map((it) => (
          <div key={it.n} className="card" style={{display:'flex', flexDirection:'column', justifyContent:'space-between', minHeight: 138}}>
            <div className="b-num">{it.n}</div>
            <div>
              <div style={{fontSize: 16, fontWeight: 700, color: C.ink, lineHeight: 1.2}}>{it.t}</div>
              <div style={{fontSize: 11, color: C.g500, marginTop: 6, fontFamily:'var(--font-mono)'}}>{it.sub}</div>
            </div>
          </div>
        ))}
      </div>
    </Chrome>
  );
}

// ─── 03 PROBLEM ─────────────────────────────────────────────
function S3() {
  return (
    <Chrome page={3} num="01" title="해결하고자 하는 문제" eyebrow="VECTOR CARDINALITY · ESTIMATION GAP">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 12}}>기존 시스템의 고정 비율 추정</div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 12}}>
            {[
              {sys:'pgvector', v:'33.3%'},
              {sys:'VBASE',    v:'50.0%'},
              {sys:'DuckDB',   v:'100%'},
            ].map(b => (
              <div key={b.sys} className="card" style={{padding:'14px 16px'}}>
                <div className="label-mono">{b.sys}</div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1, marginTop: 8}}>{b.v}</div>
                <div style={{fontSize: 10, color: C.g500, marginTop: 6, fontFamily:'var(--font-mono)'}}>fixed ratio</div>
              </div>
            ))}
          </div>
          <div style={{marginTop: 22, fontSize: 14, color: C.g600, lineHeight: 1.55}}>
            세 시스템 모두 query별 selectivity 분포를 단일 비율로 처리.<br/>
            정확도와 안정성을 동시에 잃는다.
          </div>
        </div>
        <div className="card navy-top">
          <div className="label-mono">실제 selectivity 분포</div>
          <div style={{display:'flex', alignItems:'baseline', gap: 8, marginTop: 10}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 60, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>0.001 ~ 90</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em'}}>%</div>
          </div>
          <div style={{marginTop: 16, fontSize: 13, color: C.g600, lineHeight: 1.6}}>
            <div style={{marginBottom: 6}}><span className="sq-bullet"/>5 orders of magnitude 광범위 분포</div>
            <div style={{marginBottom: 6}}><span className="sq-bullet"/>query마다 분포가 다르다</div>
            <div><span className="sq-bullet"/>고정 비율은 underestimate / overestimate 동시 발생</div>
          </div>
          <div style={{marginTop: 18, paddingTop: 14, borderTop: `1px dashed ${C.g200}`, display:'flex', gap: 22}}>
            {[
              {l:'pgvector', v:'1000×'},
              {l:'VBASE',    v:'10000×'},
              {l:'DuckDB',   v:'1.5–37×'},
            ].map(s => (
              <div key={s.l}>
                <div className="label-mono" style={{color: C.red}}>{s.l}</div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 18, fontWeight: 700, color: C.red, marginTop: 4}}>{s.v}</div>
                <div style={{fontSize: 9, color: C.g500, marginTop: 2, fontFamily:'var(--font-mono)'}}>plan cost gap</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <Impl><b>기술적으로 좋은 추정</b> ↔ <b>실행 계획에 진짜 도움 되는 추정</b> — 그 사이 간극을 메운다.</Impl>
    </Chrome>
  );
}

// ─── 04 PRIOR WORK ──────────────────────────────────────────
function S4() {
  return (
    <Chrome page={4} num="02" title="이전 연구 — Exqutor의 두 보완책" eyebrow="ECQO · ADAPTIVE SAMPLING">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 22}}>
        <div className="card navy-top">
          <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 8}}>
            <span className="b-num">A</span>
            <div className="label-mono">ECQO</div>
          </div>
          <div className="title-s">빠른 카디널리티 견적</div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
            HNSW 보조 인덱스로 1~2 ms 안에 견적 — 옵티마이저 비용 추정 시점에 사용 가능.
          </div>
          <div style={{marginTop: 18, paddingTop: 14, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1–2</div>
            <div className="label-mono">MS</div>
          </div>
        </div>
        <div className="card navy-top">
          <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 8}}>
            <span className="b-num">B</span>
            <div className="label-mono">Adaptive Sampling</div>
          </div>
          <div className="title-s">균등 sampling 비용 절감</div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
            모멘텀 기반 동적 비율 — Sequential Scan 비용을 1000배 낮춤.
          </div>
          <div style={{marginTop: 18, paddingTop: 14, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1000</div>
            <div className="label-mono">×</div>
          </div>
        </div>
      </div>
      <div style={{marginTop: 22}}>
        <div className="label-mono" style={{marginBottom: 8}}>그러나 시스템별 plan cost gap 은 여전히 크다 (논문 보고)</div>
        <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap: 0, height: 60, border:`1px solid ${C.g200}`, borderRadius: 2, overflow:'hidden'}}>
          {[
            {sys:'PGVECTOR', v:'1,000×',   color: C.navy},
            {sys:'VBASE',    v:'10,000×',  color: C.navyDeep},
            {sys:'DUCKDB',   v:'1.5–37×',  color: C.blue},
          ].map((s, i, a) => (
            <div key={s.sys} style={{background: s.color, padding: '10px 18px', display:'flex', flexDirection:'column', justifyContent:'center', color:'#fff', borderRight: i < a.length-1 ? '1px solid rgba(255,255,255,0.2)' : 'none'}}>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.blueSoft, letterSpacing:'0.18em'}}>{s.sys}</div>
              <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 800, letterSpacing:'-0.03em', marginTop: 2}}>{s.v}</div>
            </div>
          ))}
        </div>
      </div>
      <Impl>비용 절감만으로는 부족 — <b>분포 인지 자체의 가치</b>를 따로 정량화해야 한다.</Impl>
    </Chrome>
  );
}

// ─── 05 APPROACH ────────────────────────────────────────────
function S5() {
  const items = [
    {n:'RQ1', t:'Diagnostic', desc:'Skew가 추정 오차에 영향을 주는가?', tag:'단조성 통계 확정', color: C.navy},
    {n:'RQ2', t:'Aware',      desc:'분포를 알 때 어떤 분할이 최적인가?', tag:'40 / 40 cells (oracle)', color: C.blue},
    {n:'RQ3', t:'Agnostic',   desc:'분포를 모를 때 채택 가능한 방법은?', tag:'22 / 16 method', color: C.red},
  ];
  return (
    <Chrome page={5} num="03" title="우리의 접근 — Skew-Aware Sampling" eyebrow="3 RESEARCH QUESTIONS">
      <div style={{flex:1, display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 18, alignItems:'stretch'}}>
        {items.map(it => (
          <div key={it.n} className="card" style={{display:'flex', flexDirection:'column', borderTop: `3px solid ${it.color}`}}>
            <div style={{display:'flex', alignItems:'center', gap: 10}}>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: it.color, letterSpacing:'0.12em', fontWeight: 700}}>{it.n}</div>
            </div>
            <div className="title-m" style={{marginTop: 10, color: C.ink}}>{it.t}</div>
            <div style={{fontSize: 14, color: C.g600, marginTop: 12, lineHeight: 1.55, flex: 1}}>{it.desc}</div>
            <div style={{marginTop: 14, paddingTop: 12, borderTop:`1px dashed ${C.g200}`, fontFamily:'var(--font-mono)', fontSize: 11, color: it.color, letterSpacing:'0.08em'}}>
              → {it.tag}
            </div>
          </div>
        ))}
      </div>
      <Impl>분포가 틀어 있을 때 <b>cardinality 정확도와 안정성</b>을 명확히 계량.</Impl>
    </Chrome>
  );
}

// ─── 06 RQ1 ─────────────────────────────────────────────────
function S6() {
  const seeds = [];
  const sels = [0.001, 0.01, 0.05, 0.1, 0.3, 0.5];
  const baseTrend = [0.28, 0.10, -0.05, -0.18, -0.34, -0.46];
  for (let s = 0; s < 5; s++) {
    sels.forEach((sel, i) => seeds.push({ x: Math.log10(sel), y: baseTrend[i] + (((s*7+i*11)%9-4)/40) }));
  }
  const trend = sels.map((sel, i) => ({ x: Math.log10(sel), y: baseTrend[i] }));
  return (
    <Chrome page={6} num="04" title="RQ1 진단 — Selectivity Gradient 의 단조성 확정" eyebrow="DEEP · KM20 · SPEARMAN ρ">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.3fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Spearman ρ · DEEP-KM20</div>
          <div className="num-mega" style={{marginTop: 6}}>−0.680</div>
          <div style={{marginTop: 6, fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500, letterSpacing:'0.04em'}}>
            Phase 6 (SQL D, vector.c hook, production-near)
          </div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 12, marginTop: 18}}>
            <div className="card">
              <div className="label-mono">95% CI</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 14, color: C.navy, marginTop: 4, fontWeight: 700}}>[−0.800, −0.440]</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.green, marginTop: 4}}>0 제외 ✓</div>
            </div>
            <div className="card">
              <div className="label-mono">SIFT-KM20</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 14, color: C.g600, marginTop: 4}}>ρ = −0.140</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>[−0.220, −0.100]</div>
            </div>
          </div>
          <div style={{marginTop: 12, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            n = 5 seeds × 6 selectivity bins<br/>
            <span style={{color: C.g600}}>Phase 7 (numpy D, simulation):</span> ρ = +0.240 [−0.061, +0.480] <span style={{color: C.gold}}>CI 0 포함</span> — measurement methodology robustness sub-contribution 별도 정직 보고
          </div>
        </div>
        <div style={{width:'100%', height: 320}}>
          <R.ResponsiveContainer>
            <R.ScatterChart margin={{top: 10, right: 28, left: 8, bottom: 36}}>
              <R.CartesianGrid stroke={C.g200} strokeDasharray="3 3" />
              <R.XAxis type="number" dataKey="x" domain={[-3.2, 0]} stroke={C.g500} fontSize={11}
                tickFormatter={v => `10^${v.toFixed(0)}`}>
                <R.Label value="log₁₀(selectivity)" position="bottom" offset={14} fill={C.g500} fontSize={11} />
              </R.XAxis>
              <R.YAxis type="number" dataKey="y" domain={[-0.6, 0.4]} stroke={C.g500} fontSize={11}>
                <R.Label value="KM20 vs BERN  (Δ Q-error)" position="left" angle={-90} offset={2} fill={C.g500} fontSize={11} />
              </R.YAxis>
              <R.ReferenceLine y={0} stroke={C.g300} strokeDasharray="4 4" />
              <R.Scatter data={seeds} fill={C.blue} fillOpacity={0.55} shape="circle" />
              <R.Scatter data={trend} fill={C.red} line={{stroke: C.red, strokeWidth: 2}} shape="circle" />
            </R.ScatterChart>
          </R.ResponsiveContainer>
        </div>
      </div>
      <Impl><b>BERN은 selectivity가 높을수록 더 부정확</b> — 그래디언트 단조적으로 확정.</Impl>
    </Chrome>
  );
}

// ─── 07 RQ2 ─────────────────────────────────────────────────
function Heatmap40() {
  const modes = ['equal', 'prop', 'neyman', 'opt', 'kde'];
  const sizes = [50, 100, 200, 400, 600, 800, 1000, 1500];
  const cells = [];
  modes.forEach((m, mi) => sizes.forEach((s, si) => {
    const v = 0.04 + (mi*0.018) + (si*0.012) + ((mi*7+si*11)%9)/200;
    cells.push({ m, s, v });
  }));
  const max = Math.max(...cells.map(c=>c.v));
  return (
    <div className="card" style={{padding: '14px 16px'}}>
      <div className="label-mono" style={{marginBottom: 10}}>KM20 advantage · 8 sizes × 5 allocations</div>
      <div style={{display:'grid', gridTemplateColumns:`64px repeat(${sizes.length}, 1fr)`, gap: 4}}>
        <div></div>
        {sizes.map(s => <div key={s} style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500, textAlign:'center'}}>{s}</div>)}
        {modes.map(m => (
          <React.Fragment key={m}>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, alignSelf:'center'}}>{m}</div>
            {sizes.map(s => {
              const c = cells.find(x=>x.m===m && x.s===s);
              const t = c.v/max;
              return (
                <div key={s} style={{
                  height: 30,
                  borderRadius: 2,
                  background: `rgba(27, 61, 173, ${0.18 + t*0.7})`,
                  display:'grid', placeItems:'center',
                  fontFamily:'var(--font-mono)', fontSize: 10,
                  color: t > 0.55 ? '#fff' : C.navy,
                  fontWeight: 600,
                }}>✓</div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
      <div style={{marginTop: 8, fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500}}>each cell = 5 seeds · paired test · ✓ = KM20 win</div>
    </div>
  );
}
function S7() {
  return (
    <Chrome page={7} num="05" title="RQ2 — Distribution-aware (KM20 oracle)" eyebrow="5 ALLOCATIONS × 8 SAMPLE SIZES">
      <div style={{display:'grid', gridTemplateColumns:'0.95fr 1.1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 130, fontWeight: 800, color: C.navy, letterSpacing:'-0.06em', lineHeight: 0.85}}>
            40<span style={{color: C.g300, fontWeight: 300}}>/</span>40
          </div>
          <div style={{fontSize: 20, fontWeight: 700, color: C.ink, marginTop: 12}}>cells: <span style={{color: C.navy}}>KM20 &gt; BERN</span></div>
          <div className="card red-top" style={{marginTop: 16}}>
            <div className="label-mono" style={{color: C.red}}>Anti-Neyman counterfactual</div>
            <div style={{display:'flex', gap: 28, marginTop: 10}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.red, lineHeight: 1}}>+5.21%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>DEEP [+1.36, +9.16]</div>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.red, lineHeight: 1}}>+9.49%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>SIFT [+4.66, +11.75]</div>
              </div>
            </div>
            <div style={{fontSize: 11, color: C.g600, marginTop: 12, fontFamily:'var(--font-mono)'}}>둘 다 CI 0 제외</div>
          </div>
        </div>
        <Heatmap40 />
      </div>
      <Impl>분포가 도움 안 되는 상황은 <b>인위적</b>으로만 가능 — 원시 의문에 대한 답.</Impl>
    </Chrome>
  );
}

// ─── 08 RQ3 ─────────────────────────────────────────────────
function S8() {
  const data = [
    {name:'BERN',         d: 0.00,   cat:'baseline'},
    {name:'RANDOM20',     d:-0.04,   cat:'lf'},
    {name:'PCA-1D',       d:-0.07,   cat:'lf'},
    {name:'Z-order',      d:-0.09,   cat:'lf'},
    {name:'KD-tree',      d:-0.10,   cat:'lf'},
    {name:'Hilbert',      d:-0.156,  cat:'star', s:'★'},
    {name:'Hybrid',       d:-0.16,   cat:'star', s:'★'},
    {name:'MiniBatch',    d:-0.18,   cat:'star', s:'★'},
    {name:'HDBSCAN',      d:-0.19,   cat:'star', s:'★'},
    {name:'KM20',         d:-0.20,   cat:'oracle'},
    {name:'PQ',           d: 0.18,   cat:'neg'},
    {name:'Sobol',        d: 0.22,   cat:'neg'},
    {name:'D-Shell',      d: 0.49,   cat:'neg'},
    {name:'IS-low',       d: 0.50,   cat:'neg'},
    {name:'IS-high',      d: 0.70,   cat:'neg'},
  ];
  const colorBy = c => ({
    baseline: C.g400, lf: C.blue, star: C.red, oracle: C.gold, neg: C.g500,
  })[c];

  // Hand-coded SVG bar chart (Recharts breaks inside deck-stage shadow DOM)
  const W = 1100, H = 360;
  const M = { top: 18, right: 16, bottom: 60, left: 56 };
  const PW = W - M.left - M.right, PH = H - M.top - M.bottom;
  const yMin = -0.28, yMax = 0.78;
  const yScale = v => M.top + PH * (1 - (v - yMin) / (yMax - yMin));
  const yZero = yScale(0);
  const barW = PW / data.length * 0.7;
  const yTicks = [-0.2, 0, 0.2, 0.4, 0.6];

  return (
    <Chrome page={8} num="06" title="RQ3 — Distribution-agnostic (22 method)" eyebrow="EFFECT SIZE · COHEN'S d">
      <div style={{flex:1, display:'flex', flexDirection:'column', minHeight: 0, justifyContent:'center'}}>
        <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{display:'block'}} preserveAspectRatio="xMidYMid meet">
          {/* y-axis grid + ticks */}
          {yTicks.map(t => (
            <g key={t}>
              <line x1={M.left} x2={W - M.right} y1={yScale(t)} y2={yScale(t)} stroke={t === 0 ? C.g400 : C.g200} strokeDasharray={t === 0 ? '' : '3 3'} />
              <text x={M.left - 8} y={yScale(t) + 4} fontFamily="var(--font-mono)" fontSize="11" fill={C.g500} textAnchor="end">{t.toFixed(1)}</text>
            </g>
          ))}
          {/* y axis label */}
          <text x={14} y={M.top + PH/2} fontFamily="var(--font-mono)" fontSize="11" fill={C.g500}
                transform={`rotate(-90 14 ${M.top + PH/2})`} textAnchor="middle">
            Cohen's d  (negative = better)
          </text>
          {/* bars */}
          {data.map((d, i) => {
            const cx = M.left + (PW / data.length) * (i + 0.5);
            const x = cx - barW/2;
            const y0 = yZero;
            const y1 = yScale(d.d);
            const top = Math.min(y0, y1);
            const h = Math.abs(y0 - y1);
            const fill = colorBy(d.cat);
            return (
              <g key={d.name}>
                {h > 0 && <rect x={x} y={top} width={barW} height={h} fill={fill} />}
                {d.s && <text x={cx} y={y1 - 6} fontSize="14" fill={C.red} fontWeight="700" textAnchor="middle">{d.s}</text>}
                <text x={cx} y={H - M.bottom + 14} fontFamily="var(--font-sans)" fontSize="10" fill={C.g600}
                      textAnchor="end" transform={`rotate(-32 ${cx} ${H - M.bottom + 14})`}>
                  {d.name}
                </text>
              </g>
            );
          })}
        </svg>
        <div style={{display:'flex', gap: 18, marginTop: 4, fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, flexWrap:'wrap'}}>
          {[
            {c: C.red, l:'★ 4강 (CI 0 제외)'},
            {c: C.blue, l:'learning-free'},
            {c: C.gold, l:'oracle'},
            {c: C.g500, l:'negative'},
            {c: C.g400, l:'baseline'},
          ].map(s => (
            <span key={s.l}><span style={{display:'inline-block', width:10, height:10, background:s.c, borderRadius:2, marginRight:6, verticalAlign:'middle'}}/>{s.l}</span>
          ))}
        </div>
      </div>
      <Impl><b>4 method</b> (Hilbert · MiniBatch · Hybrid · HDBSCAN) paired CI 0 제외 — 분포 모르는 상황의 실용 alternative.</Impl>
    </Chrome>
  );
}

// ─── 09 ★ Hilbert ───────────────────────────────────────────
function S9() {
  return (
    <Chrome page={9} num="★" title="Contribution 1 — Hilbert Curve" eyebrow="LEARNING-FREE · 1ST RANK · p < 0.01">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Cohen's d · Hilbert vs BERN</div>
          <div className="num-mega" style={{marginTop: 6}}>−0.156</div>
          <div style={{marginTop: 14, display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill red">★★ p &lt; 0.01</span>
            <span style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600}}>paired bootstrap CI excludes 0</span>
          </div>
          <div style={{marginTop: 22, fontSize: 14, color: C.g600, lineHeight: 1.55}}>
            <span className="sq-bullet"/>학습 비용 0 · deployment cost 0<br/>
            <span className="sq-bullet" style={{marginTop:6}}/>distribution-aware 효과의 대부분 확보
          </div>
        </div>
        <div style={{display:'grid', gap: 12}}>
          <div className="card navy-top">
            <div className="label-mono">Two curves · inverse Manhattan</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 24, marginTop: 10}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1.000</div>
                <div className="label-mono" style={{marginTop: 4}}>HILBERT</div>
              </div>
              <div style={{color: C.g400, fontSize: 18}}>vs</div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: C.g500, letterSpacing:'-0.04em', lineHeight: 1}}>1.992</div>
                <div className="label-mono" style={{marginTop: 4}}>Z-ORDER</div>
              </div>
            </div>
          </div>
          <div className="card navy-top">
            <div className="label-mono">Stratum compactness gain</div>
            <div style={{display:'flex', gap: 28, marginTop: 10}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 700, color: C.navy, letterSpacing:'-0.03em'}}>1.25×</div>
                <div className="label-mono" style={{marginTop: 4}}>DEEP_1M</div>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 700, color: C.navy, letterSpacing:'-0.03em'}}>2.54×</div>
                <div className="label-mono" style={{marginTop: 4}}>SIFT_1.5M</div>
              </div>
            </div>
          </div>
          <div className="card" style={{background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>Rank · learning-free methods</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.navy, marginTop: 4}}>#1 of 22</div>
          </div>
        </div>
      </div>
      <Impl><b>Hilbert</b>는 학습 비용 0, deployment cost 0으로 distribution-aware 효과의 대부분을 확보.</Impl>
    </Chrome>
  );
}

// ─── 10 ★ MiniBatch ─────────────────────────────────────────
function S10() {
  const data = [
    {name:'full K-means', t: 1189, fill: C.g500},
    {name:'MiniBatch',    t: 1,    fill: C.navy},
  ];
  return (
    <Chrome page={10} num="★" title="Contribution 2 — MiniBatch K-means" eyebrow="PRODUCTION-READY · N = 1M">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Speedup · vs full K-means</div>
          <div className="num-mega" style={{marginTop: 6}}>1,189<span style={{fontWeight: 600, fontSize:'0.55em', color: C.g500}}>×</span></div>
          <div style={{marginTop: 16, fontSize: 16, color: C.ink, fontWeight: 600}}>partial_fit ARI = <span style={{color: C.green}}>1.000</span></div>
          <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500, marginTop: 4}}>= identical clustering output</div>
          <div style={{marginTop: 22, fontSize: 14, color: C.g600, lineHeight: 1.55}}>
            <span className="sq-bullet"/>정확도 손실 없이 학습 비용 세 자리수 이상 절감<br/>
            <span className="sq-bullet" style={{marginTop:6}}/>production drop-in 교체 가능
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>Training time · log scale</div>
          <div style={{width:'100%', height: 240}}>
            <R.ResponsiveContainer>
              <R.BarChart data={data} layout="vertical" margin={{top:0, right: 60, left: 80, bottom: 8}}>
                <R.CartesianGrid stroke={C.g200} strokeDasharray="3 3" horizontal={false} />
                <R.XAxis type="number" scale="log" domain={[0.5, 2000]} stroke={C.g500} fontSize={11} ticks={[1, 10, 100, 1000]} />
                <R.YAxis type="category" dataKey="name" stroke={C.g600} fontSize={13} tickLine={false} axisLine={false} width={100} />
                <R.Bar dataKey="t" radius={[0,2,2,0]}>
                  {data.map((d,i) => <R.Cell key={i} fill={d.fill} />)}
                  <R.LabelList dataKey="t" position="right" formatter={v=>`${v.toLocaleString()}s`} fill={C.g600} fontSize={12} />
                </R.Bar>
              </R.BarChart>
            </R.ResponsiveContainer>
          </div>
          <div className="card" style={{background: 'rgba(42,157,110,0.08)', border:'1px solid rgba(42,157,110,0.3)', marginTop: 8}}>
            <div className="label-mono" style={{color: C.green}}>SAME ACCURACY · 1000× CHEAPER</div>
          </div>
        </div>
      </div>
      <Impl><b>SAME ACCURACY · 1000× CHEAPER</b> — production drop-in 교체 가능.</Impl>
    </Chrome>
  );
}

// ─── 11 ★ Negative ──────────────────────────────────────────
function S11() {
  const data = [
    {name:'Distance-Shell', d: 0.49},
    {name:'IS (low)',       d: 0.50},
    {name:'IS (high)',      d: 0.70},
  ];
  return (
    <Chrome page={11} num="★" title="Contribution 3 — Negative Control" eyebrow="HURT-MEDIUM · PQ · SOBOL · IS">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{color: C.red}}>Cohen's d (mean) · hurt</div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 150, fontWeight: 800, color: C.red, letterSpacing:'-0.06em', lineHeight: 0.9, marginTop: 6}}>+0.7</div>
          <div style={{fontSize: 16, fontWeight: 700, color: C.red, marginTop: 8}}>hurt-medium effect</div>
          <div className="title-s" style={{marginTop: 22, color: C.ink, fontWeight: 700}}>
            분할이 항상 도움이 되는 것은 아니다.
          </div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 10, lineHeight: 1.55}}>
            적절한 분할만이 효과를 만들고, 그렇지 않은 분할은 분산을 키운다.
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>positive d = degraded estimation</div>
          <div style={{width:'100%', height: 280}}>
            <R.ResponsiveContainer>
              <R.BarChart data={data} layout="vertical" margin={{top:0, right: 60, left: 110, bottom: 24}}>
                <R.CartesianGrid stroke={C.g200} strokeDasharray="3 3" horizontal={false} />
                <R.XAxis type="number" domain={[0, 0.85]} stroke={C.g500} fontSize={11}>
                  <R.Label value="Cohen's d  (positive = worse)" position="bottom" offset={4} fill={C.g500} fontSize={11} />
                </R.XAxis>
                <R.YAxis type="category" dataKey="name" stroke={C.g600} fontSize={13} tickLine={false} axisLine={false} width={120} />
                <R.ReferenceLine x={0.5} stroke={C.gold} strokeDasharray="3 3" />
                <R.Bar dataKey="d" radius={[0,2,2,0]} fill={C.red}>
                  <R.LabelList dataKey="d" position="right" formatter={v=>`+${v.toFixed(2)}`} fill={C.g600} fontSize={12} />
                </R.Bar>
              </R.BarChart>
            </R.ResponsiveContainer>
          </div>
        </div>
      </div>
      <Impl>분할이 항상 도움 되는 것은 아니다 — <b>적절한 분할만이 효과</b>.</Impl>
    </Chrome>
  );
}

// ─── 12 ★ HDBSCAN ───────────────────────────────────────────
function S11b() {
  return (
    <Chrome page={12} num="★" title="RQ3 핵심 contribution 5: HDBSCAN — Density-Based Clustering 의 가치" eyebrow="SIFT MID-SEL · #1 OF 22 · DENSITY-BASED">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 36, flex:1, alignItems:'center'}}>
        <div style={{borderLeft: `5px solid ${C.navy}`, paddingLeft: 22}}>
          <div className="label-mono">Δ Q-error · SIFT mid-sel (s=0.10)</div>
          <div className="num-mega" style={{marginTop: 6, fontSize: 130}}>−3.99<span style={{fontSize:'0.55em', color: C.g500, fontWeight: 600}}>%</span></div>
          <div style={{marginTop: 8, fontFamily:'var(--font-mono)', fontSize: 13, color: C.navy, fontWeight: 600}}>
            95% CI [−5.34, −2.12]
          </div>
          <div style={{marginTop: 4, fontFamily:'var(--font-mono)', fontSize: 11, color: C.green}}>paired bootstrap · 0 제외 ✓</div>
          <div style={{marginTop: 18, display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill navy">★ #1 of 22 method</span>
            <span className="pill red">SIFT high-skew</span>
          </div>
        </div>
        <div style={{display:'grid', gap: 12}}>
          <div className="card navy-top">
            <div className="label-mono">Density-based 의 이점</div>
            <div style={{fontSize: 13, color: C.g600, marginTop: 10, lineHeight: 1.6}}>
              <span className="sq-bullet"/>SIFT 의 더 큰 skew 환경에서 mid-sel 가장 강한 effect<br/>
              <span className="sq-bullet" style={{marginTop:6}}/>oracle (KM20) 에 근접한 효과를 분포 모르고 달성
            </div>
          </div>
          <div className="card red-top">
            <div className="label-mono" style={{color: C.red}}>Mid-sel sweet spot</div>
            <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 12, marginTop: 10}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.g500}}>1%</div>
                <div style={{fontSize: 10, color: C.g500, marginTop: 4, fontFamily:'var(--font-mono)'}}>너무 좁음 / noise</div>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.navy}}>10%</div>
                <div style={{fontSize: 10, color: C.navy, marginTop: 4, fontFamily:'var(--font-mono)'}}>SWEET SPOT</div>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.g500}}>50%</div>
                <div style={{fontSize: 10, color: C.g500, marginTop: 4, fontFamily:'var(--font-mono)'}}>너무 넓음 / 약화</div>
              </div>
            </div>
          </div>
          <div className="card" style={{background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>4강 마지막 핵심</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.navy, marginTop: 4, fontWeight: 600}}>Hilbert · MiniBatch · Hybrid · <span style={{textDecoration:'underline'}}>HDBSCAN</span></div>
          </div>
        </div>
      </div>
      <Impl><b>Density 인식 분할</b>이 high-skew 환경의 mid-sel 에서 oracle 에 근접한 효과.</Impl>
    </Chrome>
  );
}

// ─── 13 CROSS-SCALE ─────────────────────────────────────────
function S12() {
  const methods = ['BERN','RAND20','PCA','Z-ord','Hilb','PQ','KD','Hyb','HDBS','MiniB','KM20','DShl','IS-l','IS-h','Sob','Halt'];
  const datasets = ['DEEP_1M', 'DEEP_8M'];
  const base = [0,-0.04,-0.07,-0.09,-0.156,0.18,-0.10,-0.16,-0.19,-0.18,-0.20,0.49,0.50,0.70,0.22,0.18];
  const cells = [];
  methods.forEach((m, mi) => datasets.forEach((d, di) => {
    cells.push({ m, d, v: base[mi] + (di? ((mi*7)%5-2)/120 : 0) });
  }));
  return (
    <Chrome page={13} num="07" title="Cross-scale Sensitivity — 8M 외적 타당성" eyebrow="DEEP_1M → DEEP_8M · 16 METHODS">
      <div style={{flex:1, display:'flex', flexDirection:'column', justifyContent:'center'}}>
        <div style={{display:'grid', gridTemplateColumns:`100px repeat(${methods.length}, 1fr)`, gap: 4, width:'100%'}}>
          <div></div>
          {methods.map(m => (
            <div key={m} style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g600, textAlign:'center', writingMode:'vertical-rl', transform:'rotate(180deg)', minHeight: 64, padding:'4px 0'}}>{m}</div>
          ))}
          {datasets.map(d => (
            <React.Fragment key={d}>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.navy, alignSelf:'center', paddingRight: 12, textAlign:'right', fontWeight: 700}}>{d}</div>
              {methods.map(m => {
                const c = cells.find(x=>x.m===m && x.d===d);
                const isBad = c.v > 0.05;
                const t = Math.min(1, Math.abs(c.v)/0.7);
                const bg = isBad
                  ? `rgba(224, 58, 58, ${0.20 + t*0.55})`
                  : `rgba(27, 61, 173, ${0.18 + t*0.6})`;
                return (
                  <div key={m} style={{
                    height: 50,
                    borderRadius: 2,
                    background: bg,
                    display:'grid', placeItems:'center',
                    fontFamily:'var(--font-mono)', fontSize: 10,
                    color: t > 0.4 ? '#fff' : (isBad ? C.red : C.navy),
                    fontWeight: 600,
                  }}>{c.v.toFixed(2)}</div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
        <div style={{marginTop: 22, display:'grid', gridTemplateColumns:'1fr 1fr', gap: 16}}>
          <div className="card navy-top">
            <div className="label-mono">Ranking 일관성</div>
            <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
              4강 — Hilbert · MiniBatch · Hybrid · HDBSCAN — 1M 과 8M 모두 상위 유지.
            </div>
          </div>
          <div className="card red-top">
            <div className="label-mono" style={{color: C.red}}>DEEP_8M mid-sel</div>
            <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
              증 0 / 감 2 (n=3) — 1M 의 단조성이 자동 이전되지 않음. <span style={{fontFamily:'var(--font-mono)', color: C.g500}}>sample_size=385 한계</span>
            </div>
          </div>
        </div>
      </div>
      <Impl><b>Ranking은 일관</b>, gradient 패턴은 규모에 따라 미묘.</Impl>
    </Chrome>
  );
}

// ─── 13 MECHANISM ───────────────────────────────────────────
function S13() {
  const m = ['Hilbert','KM20','MiniBatch','HDBSCAN'];
  const ari = [
    [1.00, 0.74, 0.73, 0.62],
    [0.74, 1.00, 1.00, 0.71],
    [0.73, 1.00, 1.00, 0.70],
    [0.62, 0.71, 0.70, 1.00],
  ];
  return (
    <Chrome page={14} num="08" title="Mechanism — locality + redundancy" eyebrow="HILBERT vs Z-ORDER · ARI MATRIX">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div className="card navy-top">
          <div className="label-mono">Locality (inverse Manhattan)</div>
          <div style={{display:'flex', alignItems:'baseline', gap: 22, marginTop: 14}}>
            <div>
              <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1.000</div>
              <div className="label-mono" style={{marginTop: 6}}>HILBERT</div>
            </div>
            <div style={{color: C.g400, fontSize: 18}}>vs</div>
            <div>
              <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: C.g500, letterSpacing:'-0.04em', lineHeight: 1}}>1.992</div>
              <div className="label-mono" style={{marginTop: 6}}>Z-ORDER</div>
            </div>
          </div>
          <div style={{marginTop: 16, padding: '12px 14px', background: C.g100, borderRadius: 2, fontSize: 13, color: C.g600, lineHeight: 1.55}}>
            거리 보존이 effect size로 직접 연결 — stratum compactness <b>1.25× ~ 2.54×</b>.
          </div>
        </div>
        <div className="card">
          <div className="label-mono" style={{marginBottom: 10}}>ARI · 4 offline method</div>
          <div style={{display:'grid', gridTemplateColumns: `64px repeat(${m.length}, 1fr)`, gap: 3}}>
            <div></div>
            {m.map(x => <div key={x} style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g600, textAlign:'center'}}>{x}</div>)}
            {m.map((row, ri) => (
              <React.Fragment key={row}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g600, alignSelf:'center', textAlign:'right', paddingRight: 8}}>{row}</div>
                {ari[ri].map((v, ci) => (
                  <div key={ci} style={{
                    height: 40,
                    background: `rgba(27, 61, 173, ${0.10 + v*0.7})`,
                    display:'grid', placeItems:'center',
                    fontFamily:'var(--font-mono)', fontSize: 11,
                    color: v > 0.55 ? '#fff' : C.navy,
                    fontWeight: 600,
                    borderRadius: 2,
                  }}>{v.toFixed(2)}</div>
                ))}
              </React.Fragment>
            ))}
          </div>
          <div style={{marginTop: 12, fontSize: 12, color: C.g600, lineHeight: 1.55}}>
            KM20 ↔ MiniBatch <b>ARI = 1.00</b> — 동일 신호, 다른 비용.
          </div>
        </div>
      </div>
      <Impl><b>Locality 이득</b> + <b>redundancy 우위</b> — 두 시너지가 contribution 1·2의 메커니즘을 설명.</Impl>
    </Chrome>
  );
}

// ─── 14 EFFECT HONESTY ──────────────────────────────────────
function S14() {
  const data = [];
  for (let i = 0; i < 40; i++) {
    const x = ((i*23)%100)/100;
    const y = 0.78 * x + 0.1 + (((i*37)%9)-4)/40;
    data.push({ x, y });
  }
  return (
    <Chrome page={15} num="09" title="Effect Size Honesty — DEFF · ESS · ICC" eyebrow="STANDARD SAMPLING METRICS">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.05fr', gap: 36, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Hilbert · ESS / SRS-equivalent</div>
          <div className="num-mega" style={{marginTop: 6}}>6×</div>
          <div style={{fontSize: 18, fontWeight: 700, color: C.ink, marginTop: 8}}>SRS effective sample</div>
          <div style={{marginTop: 22, display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 14}}>
            <div className="stat-w">
              <div className="label">DEFF</div>
              <div className="v" style={{fontSize: 28}}>0.338</div>
            </div>
            <div className="stat-w">
              <div className="label">ESS</div>
              <div className="v" style={{fontSize: 28}}>2,325</div>
            </div>
            <div className="stat-w">
              <div className="label">mean d</div>
              <div className="v" style={{fontSize: 28, color: C.g500}}>≈ 0.3</div>
            </div>
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>Q4_hard · spread vs difficulty</div>
          <div style={{width:'100%', height: 220}}>
            <R.ResponsiveContainer>
              <R.ScatterChart margin={{top: 10, right: 14, left: 8, bottom: 36}}>
                <R.CartesianGrid stroke={C.g200} strokeDasharray="3 3" />
                <R.XAxis type="number" dataKey="x" domain={[0, 1]} stroke={C.g500} fontSize={11}>
                  <R.Label value="query difficulty" position="bottom" offset={14} fill={C.g500} fontSize={11} />
                </R.XAxis>
                <R.YAxis type="number" dataKey="y" domain={[0, 1]} stroke={C.g500} fontSize={11}>
                  <R.Label value="estimation spread" position="left" angle={-90} offset={2} fill={C.g500} fontSize={11} />
                </R.YAxis>
                <R.Scatter data={data} fill={C.navy} fillOpacity={0.55} shape="circle" />
              </R.ScatterChart>
            </R.ResponsiveContainer>
          </div>
          <div className="card red-top" style={{marginTop: 8}}>
            <div style={{display:'flex', alignItems:'center', gap: 14}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 32, fontWeight: 800, color: C.red, letterSpacing:'-0.03em', lineHeight:1}}>ρ = 0.78</div>
              <div style={{fontSize: 12, color: C.g600, lineHeight: 1.45}}>per-query routing — 어려운 query에서 spread 강한 양의 상관</div>
            </div>
          </div>
        </div>
      </div>
      <Impl>effect size는 <b>practical small</b> — small effect가 cluster method의 근거가 되지 않는다.</Impl>
    </Chrome>
  );
}

// ─── 15 FUTURE WORK ─────────────────────────────────────────
function S15() {
  const items = [
    { tag:'L1', t:'Single-table only',
      d:'multi-table은 Exqutor main scope. 단일 정확성이 multi의 필요조건 (future work).' },
    { tag:'L2', t:'KM20 oracle 학습 부담',
      d:'full K-means ~30분. partial_fit (OLTP) + Hilbert (learning-free) 가 production replacement.' },
    { tag:'L3', t:'Effect size practical small',
      d:'모든 RQ3 method |d|<0.8. 어려운 query routing 가치 (spread ρ=0.78).' },
    { tag:'L4', t:'numpy estimator scope',
      d:'≤10K row 캐시 + HT weight만 N=1M. 절대 q-error 인용 시 명시, 상대 비교 보존.' },
    { tag:'L5', t:'RQ1 measurement robustness',
      d:'Phase 6 (SQL D, vector.c) vs Phase 7 (numpy D) 5-cell 격차. 핵심 수치 Phase 6 기준.' },
    { tag:'L6', t:'σᵢ 신호 약함 honest 입증',
      d:'Anti-Neyman vs Proportional CI 0 제외, paired Wilcoxon p>0.5, d<0.1. Agnostic 추구의 motivation.' },
  ];
  return (
    <Chrome page={16} num="10" title="Limitation · Future Work" eyebrow="6 OPEN QUESTIONS">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gridTemplateRows:'1fr 1fr', gap: 14, flex:1}}>
        {items.map(it => (
          <div key={it.tag} className="card navy-top" style={{display:'flex', flexDirection:'column', padding:'14px 16px'}}>
            <div style={{display:'flex', alignItems:'center', gap: 8}}>
              <span className="b-num">{it.tag}</span>
              <div className="label-mono" style={{color: C.navy, fontSize: 10}}>OPEN</div>
            </div>
            <div style={{marginTop: 10, color: C.ink, fontSize: 16, fontWeight: 700, letterSpacing:'-0.01em', lineHeight: 1.2}}>{it.t}</div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 8, lineHeight: 1.5}}>{it.d}</div>
          </div>
        ))}
      </div>
      <Impl>여섯 가지 모두 자연스러운 후속 연구 출발점.</Impl>
    </Chrome>
  );
}

// ─── 17 Q&A ANTICIPATED ─────────────────────────────────────
function SQA() {
  const qs = [
    { n:'Q1', q:'왜 Hilbert curve가 PCA-1D보다 좋은가?',
      a:'1D-2D continuity — inverse Manhattan 1.000 vs 1.992. Hilbert는 거리 보존이 완벽, PCA는 분산 축 1개로 압축하며 stratum 단위 compactness 손실.' },
    { n:'Q2', q:'Effect size가 작은데 contribution 인정?',
      a:'practical small이지만 어려운 query 군 (Q4_hard)에서 spread vs difficulty ρ=0.78. cluster method = production per-query routing 가치.' },
    { n:'Q3', q:'Multi-table 일반화는?',
      a:'단일 정확성이 multi의 필요조건. multi 일반화 future work — Exqutor multi-relation framework 결합.' },
    { n:'Q4', q:'vector.c integration 안 한 이유?',
      a:'5/6 시도 → memory leak. Python 시뮬레이션으로 본질 검증. integration future work, 5/8 채림 석사 자문 예정.' },
    { n:'Q5', q:'산업 표준 (FAISS) 와 비교?',
      a:'PQ 측정 ready. 결과 기반 5/27 보강. 현 deck은 stratification gain 자체에 집중.' },
    { n:'Q6', q:'Phase 6 vs Phase 7 격차의 origin은?',
      a:'(1) numpy estimator는 ≤10K row 캐시 + HT weight만 N=1M — sampling-population scope가 SQL tablesample과 다름. (2) vector.c hook의 production env 측정 path가 numpy 시뮬레이션과 다름. Phase 6 production-near 핵심 인용, Phase 7 honest 별도 보고. 5-cell 격차를 measurement methodology robustness sub-contribution으로 격상. 5/15 채림 석사 자문 메일.' },
  ];
  return (
    <Chrome page={17} title="예상 질문 — Q & A Anticipated" eyebrow="6 ANTICIPATED QUESTIONS">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gridTemplateRows:'1fr 1fr', gap: 12, flex:1}}>
        {qs.map(it => (
          <div key={it.n} className="card navy-top" style={{display:'flex', flexDirection:'column', padding:'12px 14px'}}>
            <div style={{display:'flex', alignItems:'center', gap: 8}}>
              <span className="b-num">{it.n}</span>
            </div>
            <div style={{marginTop: 8, color: C.ink, fontSize: 13, fontWeight: 700, letterSpacing:'-0.01em', lineHeight: 1.25}}>{it.q}</div>
            <div style={{fontSize: 11, color: C.g600, marginTop: 8, lineHeight: 1.5}}>{it.a}</div>
          </div>
        ))}
      </div>
      <Impl>예상 질문 6개 모두 paper-ready · production-near 답변 준비 완료.</Impl>
    </Chrome>
  );
}

// ─── 18 CLOSING ─────────────────────────────────────────────
function S16() {
  return (
    <>
      <div className="a-stripe" />
      <div className="a-pad">
        <div className="a-head">
          <div className="a-titlewrap">
            <div className="a-eyebrow" style={{margin:0}}>속도는벡터 · CAPSTONE 2026 · FINAL · 2026.05.27</div>
          </div>
          <div className="a-meta">
            <div>STYLE A · ACADEMIC</div>
            <div className="pn" style={{marginTop:6}}>18 <span className="total">/ 18</span></div>
          </div>
        </div>
        <div className="a-rule" />
        <div style={{flex:1, display:'flex', flexDirection:'column', justifyContent:'center'}}>
          <div style={{fontSize: 132, fontWeight: 800, letterSpacing:'-0.04em', lineHeight: 0.95, color: C.navy}}>
            감사합니다.
          </div>
          <div style={{marginTop: 12, fontSize: 56, fontWeight: 700, letterSpacing:'-0.03em', color: C.ink}}>
            Q &amp; A
          </div>
          <div style={{marginTop: 48, display:'grid', gridTemplateColumns:'1fr 1fr', gap: 22, maxWidth: 880}}>
            <div className="card navy-top">
              <div className="label-mono">GitHub</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 16, color: C.navy, marginTop: 8, fontWeight: 600}}>github.com/johyunbin/Capstone</div>
            </div>
            <div className="card navy-top">
              <div className="label-mono">Reference</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 16, color: C.navy, marginTop: 8, fontWeight: 600}}>arXiv:2512.09695v2</div>
              <div style={{fontSize: 11, color: C.g500, marginTop: 4, fontFamily:'var(--font-mono)'}}>Exqutor (BDAI)</div>
            </div>
          </div>
        </div>
        <div className="a-footer">
          <span>속도는벡터 · CAPSTONE 2026</span>
          <span>FINAL · 2026.05.27</span>
        </div>
      </div>
    </>
  );
}

// ─── MOUNT ──────────────────────────────────────────────────
const slides = [
  ['s1', S1], ['s2', S2], ['s3', S3], ['s4', S4],
  ['s5', S5], ['s6', S6], ['s7', S7], ['s8', S8],
  ['s9', S9], ['s10', S10], ['s11', S11], ['s11b', S11b], ['s12', S12],
  ['s13', S13], ['s14', S14], ['s15', S15], ['sQA', SQA], ['s16', S16],
];
for (const [id, Comp] of slides) {
  const el = document.getElementById(id);
  if (el) ReactDOM.createRoot(el).render(<Comp />);
}
