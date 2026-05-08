/* global React, ReactDOM */

const C = {
  navy: '#1B3DAD', navyDeep: '#14307F',
  blue: '#4A7BD8', blueSoft: '#E4ECF8',
  red: '#E03A3A', redSoft: '#FBE3E3',
  green: '#2A9D6E', gold: '#D9A53B',
  ink: '#0B0F1C',
  g100:'#F2F4F8', g200:'#DEE2EC', g300:'#C9CDD8',
  g400:'#A4ABBC', g500:'#6E7891', g600:'#4B5470', g700:'#2E3650',
};
const TOTAL = 16;

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
            벡터 카디널리티 추정에서 distribution-aware stratified sampling 의 정량적 가치<br/>
            <span style={{color: C.navy, fontWeight: 600}}>Single → Multi-vector: 25.4× magnitude shrinkage</span>
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
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>Exqutor · PDX (SIGMOD'25)</div>
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
    {n:'02', t:'Prior Work',        sub:'Exqutor + PDX'},
    {n:'03', t:'Approach',          sub:'Skew-Aware Sampling'},
    {n:'04', t:'RQ1 · Diagnostic',  sub:'12-cell ρ<0 일관'},
    {n:'05', t:'RQ2 · Aware',       sub:'51/52 CI 0 제외'},
    {n:'06', t:'RQ3 · 4강',         sub:'10-cell paired Δ%'},
    {n:'07', t:'Cross-Scale',       sub:'sf1 → sf10'},
    {n:'08', t:'Mechanism',         sub:'multi 25.4× shrinkage'},
    {n:'09', t:'Effect Honesty',    sub:'SSN++ ceiling'},
    {n:'10', t:'Limitation',        sub:'8 open questions'},
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

// ─── 04 PRIOR WORK + PDX ────────────────────────────────────
function S4() {
  return (
    <Chrome page={4} num="02" title="이전 연구 — Exqutor + PDX 학술 confirmation" eyebrow="ECQO · ADAPTIVE · PDX (SIGMOD 2025)">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 18}}>
        <div className="card navy-top">
          <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 8}}>
            <span className="b-num">A</span>
            <div className="label-mono">ECQO</div>
          </div>
          <div className="title-s">빠른 카디널리티 견적</div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
            HNSW 보조 인덱스로 1~2 ms 안에 견적 — 옵티마이저 비용 추정 시점에 사용 가능.
          </div>
          <div style={{marginTop: 14, paddingTop: 10, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 44, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1–2</div>
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
          <div style={{marginTop: 14, paddingTop: 10, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 44, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1000</div>
            <div className="label-mono">×</div>
          </div>
        </div>
      </div>
      <div className="card red-top" style={{marginTop: 14, padding:'14px 18px'}}>
        <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 6}}>
          <span className="pill red">PDX · SIGMOD 2025</span>
          <span style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500}}>CWI Amsterdam · arXiv:2503.04422</span>
        </div>
        <div style={{display:'grid', gridTemplateColumns:'1.4fr 1fr', gap: 22, marginTop: 8}}>
          <div style={{fontSize: 13, color: C.g600, lineHeight: 1.55}}>
            <span style={{color: C.ink, fontWeight: 700}}>"intrinsic_dim + skewness 가 algorithm selection 결정"</span> — 우리 thesis 와 정확 일치 → 학술적 정당성 확보.
          </div>
          <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 10}}>
            <div style={{padding:'10px 12px', background: C.g100, borderRadius: 2}}>
              <div className="label-mono" style={{color: C.g500}}>PDX</div>
              <div style={{fontSize: 11, color: C.g600, marginTop: 4, fontWeight: 600}}>compute layer<br/><span style={{fontFamily:'var(--font-mono)', color: C.g500, fontWeight: 400}}>fast similarity</span></div>
            </div>
            <div style={{padding:'10px 12px', background: C.blueSoft, borderRadius: 2}}>
              <div className="label-mono" style={{color: C.navy}}>본 연구</div>
              <div style={{fontSize: 11, color: C.navy, marginTop: 4, fontWeight: 600}}>pre-process layer<br/><span style={{fontFamily:'var(--font-mono)', color: C.g500, fontWeight: 400}}>accurate cardinality</span></div>
            </div>
          </div>
        </div>
      </div>
      <Impl><b>비용 절감 + PDX compute layer</b> 위에 — <b>분포 인지의 가치</b>를 pre-process layer 로 보완.</Impl>
    </Chrome>
  );
}

// ─── 05 APPROACH ────────────────────────────────────────────
function S5() {
  const items = [
    {n:'RQ1', t:'Diagnostic', desc:'Skew가 추정 오차에 영향을 주는가?', tag:'12-cell ρ<0 100% 일관', color: C.navy},
    {n:'RQ2', t:'Aware',      desc:'분포를 알 때 어떤 분할이 최적인가?', tag:'51 / 52 (sel=0.10) CI ex', color: C.blue},
    {n:'RQ3', t:'Agnostic',   desc:'분포를 모를 때 채택 가능한 방법은?', tag:'4강 method × 10 cell paired', color: C.red},
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
  // 12 cells × 5 selectivity bins, ρ ∈ [-0.609, -0.366]
  const cellRhos = [
    {c:'DEEP_sf1·KM20',    r:-0.680},
    {c:'DEEP_sf10·KM20',   r:-0.609},
    {c:'SIFT_sf1·KM20',    r:-0.520},
    {c:'SIFT_sf10·KM20',   r:-0.488},
    {c:'WIKI_sf1·KM20',    r:-0.471},
    {c:'WIKI_sf10·KM20',   r:-0.452},
    {c:'YFCC_sf1·KM20',    r:-0.428},
    {c:'YFCC_sf10·KM20',   r:-0.410},
    {c:'SSN_sf1·KM20',     r:-0.392},
    {c:'SSN_sf10·KM20',    r:-0.376},
    {c:'DEEP_sf1·HDBSCAN', r:-0.371},
    {c:'SIFT_sf1·Hilbert', r:-0.366},
  ];
  return (
    <Chrome page={6} num="04" title="RQ1 — Selectivity Gradient 단조성 100% 일관" eyebrow="12 SINGLE CELL · ρ < 0 SIGN 100%">
      <div style={{display:'grid', gridTemplateColumns:'0.9fr 1.2fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">DEEP_sf1 · KM20 (W1-A)</div>
          <div className="num-mega" style={{marginTop: 6}}>−0.680</div>
          <div style={{marginTop: 6, fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500, letterSpacing:'0.04em'}}>
            95% CI [−0.800, −0.440] · 0 제외 ✓
          </div>
          <div className="card navy-top" style={{marginTop: 16, padding:'12px 14px'}}>
            <div className="label-mono">12 cell sign 일관성</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 14, marginTop: 8}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight:1}}>12<span style={{color: C.g300, fontWeight: 300}}>/</span>12</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.green, fontWeight: 600}}>ρ &lt; 0 ✓</div>
            </div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 8, lineHeight: 1.5}}>
              range <span style={{fontFamily:'var(--font-mono)', color: C.navy}}>−0.609 ~ −0.366</span> — 5 dataset × 2 sf × 1~2 method.
            </div>
          </div>
          <div style={{marginTop: 10, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            n = 5 seeds × 5 selectivity bins · paired Spearman
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>12-cell ρ ranking · 모두 음수</div>
          <div style={{display:'grid', gridTemplateColumns:'1fr', gap: 4}}>
            {cellRhos.map((x, i) => {
              const w = Math.abs(x.r) / 0.7 * 100;
              return (
                <div key={x.c} style={{display:'grid', gridTemplateColumns:'140px 1fr 60px', alignItems:'center', gap: 10}}>
                  <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g600, textAlign:'right'}}>{x.c}</div>
                  <div style={{height: 14, background: C.g100, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                    <div style={{position:'absolute', right: 0, top: 0, bottom: 0, width: `${w}%`, background: i===0 ? C.navy : C.blue, borderRadius: 1}}/>
                  </div>
                  <div style={{fontFamily:'var(--font-num)', fontSize: 12, color: i===0 ? C.navy : C.g600, fontWeight: i===0?800:600, textAlign:'right'}}>{x.r.toFixed(3)}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      <Impl>12개 cell 전부 ρ&lt;0 — <b>단조성은 dataset-method 공통 현상</b>.</Impl>
    </Chrome>
  );
}

// ─── 07 RQ2 ─────────────────────────────────────────────────
function S7() {
  return (
    <Chrome page={7} num="05" title="RQ2 — Distribution-aware (51/52 CI 0 제외)" eyebrow="12 CELL × 4 MODE = 48 + ANTI-NEYMAN">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 130, fontWeight: 800, color: C.navy, letterSpacing:'-0.06em', lineHeight: 0.85}}>
            51<span style={{color: C.g300, fontWeight: 300}}>/</span>52
          </div>
          <div style={{fontSize: 18, fontWeight: 700, color: C.ink, marginTop: 12}}>(sel = 0.10) <span style={{color: C.navy}}>CI excludes 0</span></div>
          <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500, marginTop: 4}}>분포 정보 활용 효과 강력 · 12 cell × 4 mode = 48 + anti-Neyman 4</div>

          <div className="card red-top" style={{marginTop: 16, padding:'12px 14px'}}>
            <div className="label-mono" style={{color: C.red}}>Anti-Neyman counterfactual</div>
            <div style={{display:'flex', gap: 22, marginTop: 8}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.red, lineHeight: 1}}>+5.21%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>DEEP [+1.36, +9.16]</div>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 700, color: C.red, lineHeight: 1}}>+9.49%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>SIFT [+4.66, +11.75]</div>
              </div>
            </div>
          </div>
        </div>
        <div>
          <div className="card navy-top" style={{padding:'14px 16px'}}>
            <div className="label-mono">σ-allocation (Neyman vs Anti-Neyman)</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 14, marginTop: 10}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 50, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight:1}}>7<span style={{color: C.g300, fontWeight: 300}}>/</span>12</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600}}>cells with gap &lt; 1%</div>
            </div>
            <div style={{marginTop: 10, fontSize: 12, color: C.g600, lineHeight: 1.55}}>
              σ 격차가 7/12 cell 에서 1% 이내 — <b>단순 균등 stratification 충분</b>.
            </div>
          </div>
          <div className="card" style={{marginTop: 12, padding:'14px 16px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>핵심 함의</div>
            <div style={{fontSize: 13, color: C.navy, marginTop: 8, lineHeight: 1.55, fontWeight: 600}}>
              σᵢ 신호 약함을 honest 입증 → <b>RQ3 distribution-agnostic</b> 추구의 정직 motivation.
            </div>
          </div>
        </div>
      </div>
      <Impl>분포 정보 활용은 <b>강력</b>, σ 신호는 <b>약함</b> — agnostic 추구의 motivation.</Impl>
    </Chrome>
  );
}

// ─── 08 RQ3 4강 ranking + 10-cell heatmap ───────────────────
function S8() {
  const ranks = [
    {n:'HDBSCAN',  d:-8.04, neg:'8/10', ci:'8/10'},
    {n:'MB_partial', d:-7.63, neg:'8/10', ci:'9/10'},
    {n:'Hilbert',  d:-7.54, neg:'8/10', ci:'9/10'},
    {n:'Hybrid',   d:-7.13, neg:'8/10', ci:'8/10'},
  ];
  // 10-cell heatmap data
  const cells = ['DEEP_sf1','DEEP_sf10','SIFT_sf1','SIFT_sf10','SSN_sf1','SSN_sf10','WIKI_sf1','WIKI_sf10','YFCC_sf1','YFCC_sf10'];
  const methods = ['HDBSCAN','MB_p','Hilbert','Hybrid'];
  const data = {
    'HDBSCAN': [-1.84,-1.77,-32.63,-10.47,+1.56,+1.39,-9.96,-4.30,-7.23,-5.77],
    'MB_p':    [-1.36,-2.07,-31.58,-10.22,+1.73,+2.04,-9.86,-2.58,-7.15,-5.62],
    'Hilbert': [-0.43,-1.20,-32.08,-10.72,+2.34,+2.06,-9.61,-4.48,-6.88,-5.21],
    'Hybrid':  [-1.06,-1.91,-28.95,-10.20,+1.35,+1.25,-7.69,-4.21,-5.71,-4.78],
  };
  return (
    <Chrome page={8} num="06" title="RQ3 — 4강 method × 10 cell paired Δ% (sel=0.10)" eyebrow="TIER 4 WINNER · CI 0 제외 ROBUST">
      <div style={{display:'grid', gridTemplateColumns:'0.85fr 1.3fr', gap: 22, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>4강 ranking (avg Δ%)</div>
          {ranks.map((r, i) => (
            <div key={r.n} style={{display:'grid', gridTemplateColumns:'24px 90px 1fr 80px', alignItems:'center', gap: 10, padding:'8px 0', borderBottom:`1px solid ${C.g200}`}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: i===0?C.red:C.navy}}>★{i+1}</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.ink, fontWeight: 700}}>{r.n}</div>
              <div style={{fontFamily:'var(--font-num)', fontSize: 22, fontWeight: 800, color: i===0?C.red:C.navy, letterSpacing:'-0.03em'}}>{r.d.toFixed(2)}%</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500, lineHeight: 1.4, textAlign:'right'}}>neg {r.neg}<br/>CI ex {r.ci}</div>
            </div>
          ))}
          <div style={{marginTop: 10, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            <span style={{color: C.navy}}>★1</span> HDBSCAN density-based · <span style={{color: C.navy}}>★2</span> MB_partial OLTP friendly 유일 · <span style={{color: C.navy}}>★3</span> Hilbert production sweet spot
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>10 cell × 4 method · paired Δ%</div>
          <div style={{display:'grid', gridTemplateColumns:`70px repeat(${cells.length}, 1fr)`, gap: 2}}>
            <div></div>
            {cells.map(c => (
              <div key={c} style={{fontFamily:'var(--font-mono)', fontSize: 8, color: C.g600, textAlign:'center', writingMode:'vertical-rl', transform:'rotate(180deg)', minHeight: 56, padding:'2px 0'}}>{c}</div>
            ))}
            {methods.map(m => (
              <React.Fragment key={m}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.navy, alignSelf:'center', textAlign:'right', paddingRight: 6, fontWeight: 700}}>{m}</div>
                {data[m].map((v, ci) => {
                  const isBad = v > 0;
                  const t = Math.min(1, Math.abs(v)/35);
                  const bg = isBad ? `rgba(217, 165, 59, ${0.20 + t*0.55})` : `rgba(27, 61, 173, ${0.18 + t*0.7})`;
                  return (
                    <div key={ci} style={{
                      height: 38, borderRadius: 2, background: bg,
                      display:'grid', placeItems:'center',
                      fontFamily:'var(--font-mono)', fontSize: 9,
                      color: t > 0.45 ? '#fff' : (isBad ? C.gold : C.navy),
                      fontWeight: 600,
                    }}>{v > 0 ? '+' : ''}{v.toFixed(1)}</div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
          <div style={{marginTop: 10, display:'flex', gap: 14, fontSize: 10, color: C.g600, fontFamily:'var(--font-mono)'}}>
            <span><span style={{display:'inline-block', width:8, height:8, background: C.navy, marginRight: 4}}/>negative (improve)</span>
            <span><span style={{display:'inline-block', width:8, height:8, background: C.gold, marginRight: 4}}/>SSN++ ceiling (+1~+2%)</span>
          </div>
        </div>
      </div>
      <Impl>4강 모두 paired Δ% <b>−7~−8% avg</b> · SIFT_sf1 <b>−32%</b> · SSN++ ceiling +1~+2%로 outer boundary 정의.</Impl>
    </Chrome>
  );
}

// ─── 09 ★ Hilbert + Tier 1 spread ───────────────────────────
function S9() {
  const tier1 = [
    {n:'HDBSCAN',  d:-8.04},
    {n:'MB_p',     d:-7.63},
    {n:'Hilbert',  d:-7.54},
    {n:'Hybrid',   d:-7.13},
    {n:'kdtree',   d:-6.83},
  ];
  return (
    <Chrome page={9} num="★" title="Contribution 1 — Hilbert · production sweet spot" eyebrow="LEARNING-FREE · TIER 1 SPREAD 1.21%p">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Hilbert avg Δ% · 4강 #3</div>
          <div className="num-mega" style={{marginTop: 6}}>−7.54<span style={{fontSize:'0.55em', color: C.g500, fontWeight:600}}>%</span></div>
          <div style={{marginTop: 6, fontFamily:'var(--font-mono)', fontSize: 11, color: C.green}}>neg 8/10 · CI ex 9/10 · SIFT_sf1 −33.53%</div>
          <div style={{marginTop: 14, display:'flex', alignItems:'center', gap: 8, flexWrap:'wrap'}}>
            <span className="pill navy">★ learning-free 1위</span>
            <span className="pill red">deployment cost 0</span>
          </div>
          <div className="card navy-top" style={{marginTop: 16, padding:'10px 12px'}}>
            <div className="label-mono">inverse Manhattan</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 14, marginTop: 6}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1.000</div>
                <div className="label-mono" style={{marginTop: 2}}>HILBERT</div>
              </div>
              <div style={{color: C.g400, fontSize: 14}}>vs</div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 800, color: C.g500, letterSpacing:'-0.04em', lineHeight: 1}}>1.992</div>
                <div className="label-mono" style={{marginTop: 2}}>Z-ORDER</div>
              </div>
            </div>
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>Tier 1 (살아남기 17종) — spread 1.21%p</div>
          {tier1.map((t, i) => {
            const w = Math.abs(t.d) / 8.04 * 100;
            return (
              <div key={t.n} style={{display:'grid', gridTemplateColumns:'90px 1fr 60px', alignItems:'center', gap: 10, padding:'5px 0'}}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: t.n==='Hilbert'?C.navy:C.g600, fontWeight: t.n==='Hilbert'?700:500}}>{t.n}</div>
                <div style={{height: 14, background: C.g100, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                  <div style={{position:'absolute', right:0, top:0, bottom:0, width: `${w}%`, background: t.n==='Hilbert'?C.navy:C.blue, borderRadius: 1}}/>
                </div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 12, color: t.n==='Hilbert'?C.navy:C.g600, fontWeight: 700, textAlign:'right'}}>{t.d.toFixed(2)}%</div>
              </div>
            );
          })}
          <div className="card red-top" style={{marginTop: 12, padding:'12px 14px'}}>
            <div className="label-mono" style={{color: C.red}}>Spread = 1.21%p (HDBSCAN ↔ kdtree)</div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 6, lineHeight: 1.5}}>
              method choice <b>부차</b> — <b>"분포 인지 vs 미인지" boundary</b>가 결정적.
            </div>
          </div>
        </div>
      </div>
      <Impl><b>Hilbert</b>는 학습 비용 0 · 17종 spread 1.21%p — 분포 인지 boundary 가 결정적.</Impl>
    </Chrome>
  );
}

// ─── 10 ★ MiniBatch · OLTP friendly ─────────────────────────
function S10() {
  const data = [
    {name:'full K-means', t: 1189, fill: C.g500},
    {name:'MiniBatch',    t: 1,    fill: C.navy},
  ];
  return (
    <Chrome page={10} num="★" title="Contribution 2 — MiniBatch K-means · OLTP friendly" eyebrow="PRODUCTION-READY · 4강 #2 · CI EX 9/10">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">MB_partial avg Δ% · 4강 #2</div>
          <div className="num-mega" style={{marginTop: 6}}>−7.63<span style={{fontSize:'0.55em', color: C.g500, fontWeight: 600}}>%</span></div>
          <div style={{marginTop: 6, fontFamily:'var(--font-mono)', fontSize: 11, color: C.green}}>neg 8/10 · CI ex <b style={{color: C.green}}>9/10</b> 강력 · SIFT_sf1 −33.13%</div>
          <div style={{marginTop: 14, display:'flex', alignItems:'center', gap: 8}}>
            <span className="pill navy">★ OLTP friendly 유일</span>
            <span className="pill red">partial_fit · 1,189× speedup</span>
          </div>
          <div style={{marginTop: 18, fontSize: 14, color: C.g600, lineHeight: 1.55}}>
            <span className="sq-bullet"/>partial_fit ARI = <b style={{color: C.green}}>1.000</b> (full K-means 동일)<br/>
            <span className="sq-bullet" style={{marginTop:6}}/>OLTP streaming 환경 drop-in 가능
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>Training time · log scale</div>
          {(() => {
            const W = 540, H = 200, M = {top: 14, right: 80, bottom: 36, left: 110};
            const PW = W - M.left - M.right, PH = H - M.top - M.bottom;
            const xMin = 0.5, xMax = 2000;
            const xScale = v => M.left + PW * (Math.log10(v) - Math.log10(xMin)) / (Math.log10(xMax) - Math.log10(xMin));
            const ticks = [1, 10, 100, 1000];
            const rowH = PH / data.length * 0.55;
            return (
              <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{display:'block'}} preserveAspectRatio="xMidYMid meet">
                {ticks.map(t => (
                  <g key={t}>
                    <line x1={xScale(t)} x2={xScale(t)} y1={M.top} y2={M.top + PH} stroke={C.g200} strokeDasharray="3 3" />
                    <text x={xScale(t)} y={M.top + PH + 16} fontFamily="var(--font-mono)" fontSize="11" fill={C.g500} textAnchor="middle">{t}</text>
                  </g>
                ))}
                {data.map((d, i) => {
                  const cy = M.top + PH * (i + 0.5) / data.length;
                  const x0 = xScale(xMin);
                  const x1 = xScale(d.t);
                  return (
                    <g key={d.name}>
                      <text x={M.left - 8} y={cy + 4} fontFamily="var(--font-sans)" fontSize="13" fill={C.g600} textAnchor="end">{d.name}</text>
                      <rect x={x0} y={cy - rowH/2} width={Math.max(2, x1 - x0)} height={rowH} fill={d.fill} />
                      <text x={x1 + 6} y={cy + 4} fontFamily="var(--font-mono)" fontSize="12" fill={C.g600}>{d.t.toLocaleString()}s</text>
                    </g>
                  );
                })}
              </svg>
            );
          })()}
          <div className="card" style={{background: 'rgba(42,157,110,0.08)', border:'1px solid rgba(42,157,110,0.3)', marginTop: 8, padding:'10px 14px'}}>
            <div className="label-mono" style={{color: C.green}}>SAME ACCURACY · 1000× CHEAPER · OLTP-READY</div>
          </div>
        </div>
      </div>
      <Impl><b>OLTP friendly 유일 4강</b> · 정확도 동일 + 1000× cheaper — production drop-in.</Impl>
    </Chrome>
  );
}

// ─── 11 ★ Sweet Spot 정량 boundary ──────────────────────────
function S11() {
  return (
    <Chrome page={11} num="★" title="Contribution 3 — Distribution Sweet Spot 정량 boundary" eyebrow="CLUSTER_RATIO × INTRINSIC_DIM">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 22, flex:1, alignItems:'center'}}>
        <div className="card navy-top" style={{padding:'18px 20px'}}>
          <div style={{display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill navy">SWEET</span>
            <div className="label-mono">강력 improve 영역</div>
          </div>
          <div style={{marginTop: 16}}>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.navy, fontWeight: 700}}>cluster_ratio &gt; 1.4</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.navy, fontWeight: 700, marginTop: 4}}>intrinsic_dim &lt; 0.85</div>
          </div>
          <div style={{marginTop: 14, paddingTop: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>−7 ~ −32%</div>
            <div className="label-mono" style={{marginTop: 6}}>SIFT · WIKI · YFCC</div>
          </div>
          <div style={{marginTop: 12, fontSize: 11, color: C.g600, lineHeight: 1.5, fontFamily:'var(--font-mono)'}}>
            cluster 구조 명확 + dim manifold 압축 → 분할이 분산을 직접 줄임.
          </div>
        </div>
        <div className="card red-top" style={{padding:'18px 20px'}}>
          <div style={{display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill red">CEILING</span>
            <div className="label-mono" style={{color: C.red}}>effect 약함 boundary</div>
          </div>
          <div style={{marginTop: 16}}>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.red, fontWeight: 700}}>cluster_ratio &lt; 1.4</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.red, fontWeight: 700, marginTop: 4}}>intrinsic_dim &gt; 0.85</div>
          </div>
          <div style={{marginTop: 14, paddingTop: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: C.red, letterSpacing:'-0.04em', lineHeight: 1}}>+1 ~ +2%</div>
            <div className="label-mono" style={{marginTop: 6, color: C.red}}>SSN++ ceiling</div>
          </div>
          <div style={{marginTop: 12, fontSize: 11, color: C.g600, lineHeight: 1.5, fontFamily:'var(--font-mono)'}}>
            cluster_ratio 1.29 · intrinsic_dim 0.88 → BERN 자체 ceiling.
          </div>
        </div>
      </div>
      <div style={{marginTop: 10, display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 12}}>
        <div className="card" style={{padding:'10px 14px'}}>
          <div className="label-mono">SIFT_sf1 (sweet)</div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 18, fontWeight: 800, color: C.navy, marginTop: 4}}>−32.63%</div>
        </div>
        <div className="card" style={{padding:'10px 14px'}}>
          <div className="label-mono">DEEP_sf1 (mid)</div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 18, fontWeight: 800, color: C.navy, marginTop: 4}}>−1.84%</div>
        </div>
        <div className="card" style={{padding:'10px 14px'}}>
          <div className="label-mono" style={{color: C.red}}>SSN_sf1 (ceiling)</div>
          <div style={{fontFamily:'var(--font-num)', fontSize: 18, fontWeight: 800, color: C.red, marginTop: 4}}>+1.56%</div>
        </div>
      </div>
      <Impl><b>cluster_ratio × intrinsic_dim</b> 두 축이 distribution sweet spot 의 정량 boundary 를 정의.</Impl>
    </Chrome>
  );
}

// ─── 12 CROSS-SCALE sf1 → sf10 ──────────────────────────────
function S12() {
  const cells = ['DEEP','SIFT','SSN','WIKI','YFCC'];
  const sf1  = {'DEEP':-1.84,'SIFT':-32.63,'SSN':+1.56,'WIKI':-9.96,'YFCC':-7.23};
  const sf10 = {'DEEP':-1.77,'SIFT':-10.47,'SSN':+1.39,'WIKI':-4.30,'YFCC':-5.77};
  return (
    <Chrome page={12} num="07" title="Cross-scale Sensitivity — sf1 → sf10 4강 일관성" eyebrow="HDBSCAN · 5 DATASETS · sf100 자문 진행 중">
      <div style={{display:'grid', gridTemplateColumns:'1.2fr 1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>HDBSCAN paired Δ% · sf1 vs sf10</div>
          <div style={{display:'grid', gridTemplateColumns:`80px repeat(${cells.length}, 1fr)`, gap: 4}}>
            <div></div>
            {cells.map(c => <div key={c} style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, textAlign:'center', fontWeight: 600}}>{c}</div>)}
            {['sf1','sf10'].map(sf => (
              <React.Fragment key={sf}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.navy, alignSelf:'center', paddingRight: 8, textAlign:'right', fontWeight: 700}}>{sf}</div>
                {cells.map(c => {
                  const v = (sf==='sf1'?sf1:sf10)[c];
                  const isBad = v > 0;
                  const t = Math.min(1, Math.abs(v)/33);
                  const bg = isBad ? `rgba(217, 165, 59, ${0.20 + t*0.55})` : `rgba(27, 61, 173, ${0.18 + t*0.7})`;
                  return (
                    <div key={c} style={{
                      height: 56, borderRadius: 2, background: bg,
                      display:'grid', placeItems:'center',
                      fontFamily:'var(--font-mono)', fontSize: 12,
                      color: t > 0.45 ? '#fff' : (isBad ? C.gold : C.navy),
                      fontWeight: 700,
                    }}>{v > 0 ? '+' : ''}{v.toFixed(2)}%</div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
          <div style={{marginTop: 12, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)'}}>
            * SIFT_sf1 −32.63% → sf10 −10.47% (magnitude 약화, 부호 일관)
          </div>
        </div>
        <div style={{display:'grid', gap: 12}}>
          <div className="card navy-top" style={{padding:'12px 14px'}}>
            <div className="label-mono">4강 ranking 일관성</div>
            <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
              HDBSCAN · MB_partial · Hilbert · Hybrid — sf1 / sf10 모두 상위 4 유지.
            </div>
          </div>
          <div className="card red-top" style={{padding:'12px 14px'}}>
            <div className="label-mono" style={{color: C.red}}>SSN++ ceiling 부호 유지</div>
            <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
              sf1 +1.56 / sf10 +1.39 — outer boundary scale 무관.
            </div>
          </div>
          <div className="card" style={{padding:'12px 14px', background: C.g100, border:'none'}}>
            <div className="label-mono">sf100 측정</div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 6, fontFamily:'var(--font-mono)'}}>
              채림 석사 자문 후 보강 (5/15) · multi-table join STAGE 3 진행 중
            </div>
          </div>
        </div>
      </div>
      <Impl><b>4강 ranking + SSN++ ceiling 부호</b> 모두 scale invariant — 외적 타당성 확보.</Impl>
    </Chrome>
  );
}

// ─── 13 MECHANISM + multi 25.4× shrinkage ───────────────────
function S13() {
  const multi = [
    {n:'deep_sift_10',  hdbs:-1.02, hilb:-0.48, hyb:+0.31, mb:-1.30},
    {n:'deep_wiki_10',  hdbs:+1.15, hilb:+0.06, hyb:+0.08, mb:+0.99},
  ];
  return (
    <Chrome page={13} num="08" title="Mechanism — locality + multi-vector shrinkage" eyebrow="SINGLE × 25.4 → MULTI · NECESSARY ≠ SUFFICIENT">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.2fr', gap: 24, flex:1, alignItems:'center'}}>
        <div>
          <div className="card navy-top" style={{padding:'12px 14px'}}>
            <div className="label-mono">Locality (inverse Manhattan)</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 16, marginTop: 8}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1.000</div>
                <div className="label-mono" style={{marginTop: 4}}>HILBERT</div>
              </div>
              <div style={{color: C.g400, fontSize: 14}}>vs</div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 800, color: C.g500, letterSpacing:'-0.04em', lineHeight: 1}}>1.992</div>
                <div className="label-mono" style={{marginTop: 4}}>Z-ORDER</div>
              </div>
            </div>
          </div>
          <div className="card red-top" style={{marginTop: 12, padding:'14px 16px'}}>
            <div className="label-mono" style={{color: C.red}}>Single → Multi shrinkage</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 14, marginTop: 8}}>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 26, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em'}}>17.13%</div>
                <div className="label-mono" style={{marginTop: 4}}>SINGLE avg |Δ%|</div>
              </div>
              <div style={{color: C.g400, fontSize: 14}}>→</div>
              <div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 26, fontWeight: 800, color: C.red, letterSpacing:'-0.03em'}}>0.67%</div>
                <div className="label-mono" style={{marginTop: 4, color: C.red}}>MULTI avg |Δ%|</div>
              </div>
            </div>
            <div style={{marginTop: 10, fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 800, color: C.red, letterSpacing:'-0.03em'}}>25.4× 약화</div>
            <div style={{fontSize: 11, color: C.g500, marginTop: 4, fontFamily:'var(--font-mono)'}}>3/8 negative · 5/8 positive · |Δ| &lt; 1.5%</div>
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>Multi-vector cell × 4강 (sel=0.10)</div>
          <div style={{display:'grid', gridTemplateColumns:`130px repeat(4, 1fr)`, gap: 4}}>
            <div></div>
            {['HDBSCAN','Hilbert','Hybrid','MB_p'].map(m => (
              <div key={m} style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g600, textAlign:'center', fontWeight: 600}}>{m}</div>
            ))}
            {multi.map(row => (
              <React.Fragment key={row.n}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.navy, alignSelf:'center', textAlign:'right', paddingRight: 8, fontWeight: 700}}>{row.n}</div>
                {[row.hdbs, row.hilb, row.hyb, row.mb].map((v, ci) => {
                  const isBad = v > 0;
                  const t = Math.min(1, Math.abs(v)/1.5);
                  const bg = isBad ? `rgba(217, 165, 59, ${0.20 + t*0.55})` : `rgba(27, 61, 173, ${0.18 + t*0.7})`;
                  return (
                    <div key={ci} style={{
                      height: 44, borderRadius: 2, background: bg,
                      display:'grid', placeItems:'center',
                      fontFamily:'var(--font-mono)', fontSize: 11,
                      color: t > 0.45 ? '#fff' : (isBad ? C.gold : C.navy),
                      fontWeight: 700,
                    }}>{v > 0 ? '+' : ''}{v.toFixed(2)}%</div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
          <div className="card" style={{marginTop: 12, padding:'10px 14px', background: C.blueSoft, border:'none'}}>
            <div style={{fontSize: 12, color: C.navy, lineHeight: 1.5, fontWeight: 600}}>
              해석: 단일 정확성은 multi 정확성의 <b>필요조건만 성립</b> — 충분조건 ✗. joint-aware clustering / multi-vector decomposition 별도 설계 future work.
            </div>
          </div>
        </div>
      </div>
      <Impl>locality 이득은 단일에서 강력, multi에선 25.4× 약화 — <b>multi-relation 일반화는 별도 design 필요</b>.</Impl>
    </Chrome>
  );
}

// ─── 14 EFFECT HONESTY + SSN++ ceiling ──────────────────────
function S14() {
  return (
    <Chrome page={14} num="09" title="Effect Size Honesty — DEFF · ESS · SSN++ ceiling" eyebrow="STANDARD METRICS · OUTER BOUNDARY">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.05fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">Hilbert · ESS / SRS-equivalent</div>
          <div className="num-mega" style={{marginTop: 6}}>6×</div>
          <div style={{fontSize: 18, fontWeight: 700, color: C.ink, marginTop: 8}}>SRS effective sample</div>
          <div style={{marginTop: 18, display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 12}}>
            <div className="stat-w">
              <div className="label">DEFF</div>
              <div className="v" style={{fontSize: 26}}>0.338</div>
            </div>
            <div className="stat-w">
              <div className="label">ESS</div>
              <div className="v" style={{fontSize: 26}}>2,325</div>
            </div>
            <div className="stat-w">
              <div className="label">mean d</div>
              <div className="v" style={{fontSize: 26, color: C.g500}}>≈ 0.3</div>
            </div>
          </div>
          <div className="card red-top" style={{marginTop: 14, padding:'10px 14px'}}>
            <div className="label-mono" style={{color: C.red}}>Q4_hard spread vs difficulty</div>
            <div style={{display:'flex', alignItems:'center', gap: 14, marginTop: 6}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 800, color: C.red, letterSpacing:'-0.03em', lineHeight:1}}>ρ = 0.78</div>
              <div style={{fontSize: 11, color: C.g600, lineHeight: 1.45}}>per-query routing 가치 — 어려운 query 강한 양의 상관</div>
            </div>
          </div>
        </div>
        <div className="card navy-top" style={{padding:'16px 18px'}}>
          <div style={{display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill red">SSN++ CEILING</span>
            <div className="label-mono">honest reporting</div>
          </div>
          <div style={{marginTop: 14, fontSize: 14, color: C.g600, lineHeight: 1.6}}>
            <span className="sq-bullet"/>cluster_ratio <b style={{color:C.ink}}>1.29</b> + intrinsic_dim <b style={{color:C.ink}}>0.88</b> = 분포 균형 dataset<br/>
            <span className="sq-bullet" style={{marginTop:6}}/>BERN baseline 자체가 ceiling — improve room 없음<br/>
            <span className="sq-bullet" style={{marginTop:6}}/>4강 모두 +1 ~ +2% 미세 후퇴 (positive direction)
          </div>
          <div style={{marginTop: 14, paddingTop: 12, borderTop:`1px solid ${C.g200}`, display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap: 8}}>
            {[
              {n:'HDBS', v:'+1.56'},
              {n:'MB_p', v:'+1.73'},
              {n:'Hilb', v:'+2.34'},
              {n:'Hyb',  v:'+1.35'},
            ].map(s => (
              <div key={s.n} style={{padding:'8px 10px', background: 'rgba(217,165,59,0.12)', borderRadius: 2, textAlign:'center'}}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.gold, fontWeight: 700, letterSpacing:'0.06em'}}>{s.n}</div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: C.gold, marginTop: 2}}>{s.v}%</div>
              </div>
            ))}
          </div>
          <div style={{marginTop: 10, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.4}}>
            본 연구 outer boundary 정의 — sweet spot 의 반대 극.
          </div>
        </div>
      </div>
      <Impl>effect는 <b>practical small</b>이지만 honest — SSN++ ceiling 이 outer boundary 정의.</Impl>
    </Chrome>
  );
}

// ─── 15 LIMITATION 8-card ───────────────────────────────────
function S15() {
  const items = [
    { tag:'L1', cat:'PARTIAL', t:'Single-table only',
      d:'multi-table은 Exqutor main scope. 단일 정확성이 multi 필요조건 (3 STAGE 측정 진행).' },
    { tag:'L2', cat:'FUTURE',  t:'Multi-vector 일반화',
      d:'25.4× shrinkage — joint-aware clustering / multi-vector decomposition 별도 설계 필요.' },
    { tag:'L3', cat:'FUTURE',  t:'sf100 cross-scale',
      d:'sf1 → sf10 일관성 확정. sf100 측정 채림 석사 자문 후 (5/15 보강).' },
    { tag:'L4', cat:'PARTIAL', t:'KM20 oracle 학습 부담',
      d:'full K-means ~30분. partial_fit (OLTP) + Hilbert (learning-free) 가 production replacement.' },
    { tag:'L5', cat:'HONEST',  t:'SSN++ ceiling honest',
      d:'cluster_ratio 1.29 + intrinsic_dim 0.88 → BERN ceiling. boundary 정의로 활용.' },
    { tag:'L6', cat:'HONEST',  t:'Effect size practical small',
      d:'모든 RQ3 |d|<0.8. 어려운 query routing 가치 (Q4 spread ρ=0.78).' },
    { tag:'L7', cat:'PARTIAL', t:'numpy estimator scope',
      d:'≤10K row 캐시 + HT weight만 N=1M. 절대 q-error 인용 시 명시, 상대 비교 보존.' },
    { tag:'L8', cat:'FUTURE',  t:'vector.c integration',
      d:'5/6 시도 → memory leak. Python 시뮬 본질 검증 + 5/15 채림 자문 후 진입.' },
  ];
  const catColor = c => c==='HONEST'?C.red : c==='FUTURE'?C.gold : C.navy;
  return (
    <Chrome page={15} num="10" title="Limitation · Future Work" eyebrow="8 OPEN QUESTIONS · PARTIAL / FUTURE / HONEST">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gridTemplateRows:'1fr 1fr', gap: 10, flex:1}}>
        {items.map(it => (
          <div key={it.tag} className="card" style={{display:'flex', flexDirection:'column', padding:'12px 14px', borderTop: `3px solid ${catColor(it.cat)}`}}>
            <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', gap: 6}}>
              <span className="b-num">{it.tag}</span>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 8, color: catColor(it.cat), fontWeight: 700, letterSpacing:'0.1em'}}>{it.cat}</div>
            </div>
            <div style={{marginTop: 8, color: C.ink, fontSize: 13, fontWeight: 700, letterSpacing:'-0.01em', lineHeight: 1.2}}>{it.t}</div>
            <div style={{fontSize: 11, color: C.g600, marginTop: 6, lineHeight: 1.45}}>{it.d}</div>
          </div>
        ))}
      </div>
      <Impl>8가지 모두 자연스러운 후속 연구 출발점 — PARTIAL · FUTURE · HONEST 분류.</Impl>
    </Chrome>
  );
}

// ─── 16 CLOSING ─────────────────────────────────────────────
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
            <div className="pn" style={{marginTop:6}}>16 <span className="total">/ 16</span></div>
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
          <div style={{marginTop: 36, display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap: 18, maxWidth: 1080}}>
            <div className="card navy-top">
              <div className="label-mono">GitHub</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 14, color: C.navy, marginTop: 8, fontWeight: 600}}>github.com/johyunbin/Capstone</div>
            </div>
            <div className="card navy-top">
              <div className="label-mono">Reference</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 14, color: C.navy, marginTop: 8, fontWeight: 600}}>arXiv:2512.09695v2</div>
              <div style={{fontSize: 11, color: C.g500, marginTop: 4, fontFamily:'var(--font-mono)'}}>Exqutor · PDX (SIGMOD'25)</div>
            </div>
            <div className="card red-top">
              <div className="label-mono" style={{color: C.red}}>STAGE 3 보강 예정</div>
              <div style={{fontSize: 12, color: C.g600, marginTop: 8, lineHeight: 1.5, fontFamily:'var(--font-mono)'}}>multi-table join (deep⨝wiki) 측정 결과 회의 후 추가 보고</div>
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
  ['s9', S9], ['s10', S10], ['s11', S11], ['s12', S12],
  ['s13', S13], ['s14', S14], ['s15', S15], ['s16', S16],
];
for (const [id, Comp] of slides) {
  const el = document.getElementById(id);
  if (el) ReactDOM.createRoot(el).render(<Comp />);
}
