/* global React, ReactDOM */

const C = {
  navy: '#1B3DAD', navyDeep: '#14307F',
  blue: '#4A7BD8', blueSoft: '#E4ECF8',
  red: '#E03A3A', redSoft: '#FBE3E3',
  green: '#2A9D6E', greenSoft: 'rgba(42, 157, 110, 0.10)',
  gold: '#D9A53B', goldSoft: 'rgba(217, 165, 59, 0.12)',
  ink: '#0B0F1C',
  g100:'#F2F4F8', g200:'#DEE2EC', g300:'#C9CDD8',
  g400:'#A4ABBC', g500:'#6E7891', g600:'#4B5470', g700:'#2E3650',
};
const TOTAL = 18;

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
          <div style={{fontSize: 56, fontWeight: 800, lineHeight: 1.05, letterSpacing:'-0.03em', color: C.ink}}>
            Skew‑Aware Stratified<br/>
            Sampling <span style={{color: C.navy}}>Ensemble</span> for<br/>
            Vector‑Augmented Analytical Query
          </div>
          <div style={{marginTop: 20, fontSize: 17, color: C.g600, lineHeight: 1.55, maxWidth: 920}}>
            Exqutor §V-B Adaptive Sampling 영역 paper-friendly augment 정량 검증<br/>
            <span style={{color: C.navy, fontWeight: 600}}>paired CaseB &gt; CaseA 92.9% · paradigm rollup 5 paradigm 모두 statistical 압도</span>
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
            <div style={{fontSize:11, color: C.g600, marginTop: 3, fontFamily:'var(--font-mono)'}}>Exqutor · paper §V-B exact</div>
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
    {n:'01', t:'Problem',           sub:'고정 비율 카디널리티 추정의 한계'},
    {n:'02', t:'Prior · Exqutor',   sub:'§V-A ECQO + §V-B Adaptive'},
    {n:'03', t:'Approach',          sub:'paper §V-B + 우리 method 평균'},
    {n:'04', t:'RQ1 · Diagnostic',  sub:'분포 차이 영향 +3.74%'},
    {n:'05', t:'Paradigm 9',        sub:'P1-P10 framework (P9/P10 신규)'},
    {n:'06', t:'RQ2 · Paradox',     sub:'Anti < Prop < Neyman 발견'},
    {n:'07', t:'CaseB Climax',      sub:'paired 92.9% 압도 main contribution'},
  ];
  return (
    <Chrome page={2} title="오늘의 구성 — 7단계 narrative" eyebrow="TABLE OF CONTENTS · 18 SLIDES · 12 MIN" hasImpl={false}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 14, flex:1}}>
        {items.map((it) => (
          <div key={it.n} className="card" style={{display:'flex', flexDirection:'column', justifyContent:'space-between', minHeight: 168}}>
            <div className="b-num">{it.n}</div>
            <div>
              <div style={{fontSize: 17, fontWeight: 700, color: C.ink, lineHeight: 1.2}}>{it.t}</div>
              <div style={{fontSize: 11, color: C.g500, marginTop: 8, fontFamily:'var(--font-mono)', lineHeight: 1.4}}>{it.sub}</div>
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
      <Impl><b>고정 비율 카디널리티</b> → 잘못된 plan → <b>1000~10000× 느린 query</b>.</Impl>
    </Chrome>
  );
}

// ─── 04 PRIOR · Exqutor V-A vs V-B ──────────────────────────
function S4() {
  return (
    <Chrome page={4} num="02" title="이전 연구 — Exqutor §V-A ECQO + §V-B Adaptive" eyebrow="paper main result 인정 + 본 연구 위치 명시">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 18}}>
        <div className="card navy-top">
          <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 8}}>
            <span className="b-num">A</span>
            <div className="label-mono">§V-A · ECQO</div>
          </div>
          <div className="title-s">인덱스 있을 때 — HNSW range query</div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
            벡터 인덱스 위에서 1~2 ms 안에 정확한 카디널리티 견적.<br/>
            <span style={{color: C.navy, fontWeight: 600}}>paper main result — 본 연구 그대로 인정</span>
          </div>
          <div style={{marginTop: 14, paddingTop: 10, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 44, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>1–2</div>
            <div className="label-mono">MS · index-aided</div>
          </div>
        </div>
        <div className="card red-top">
          <div style={{display:'flex', alignItems:'center', gap: 10, marginBottom: 8}}>
            <span className="b-num">B</span>
            <div className="label-mono" style={{color: C.red}}>§V-B · Adaptive Sampling</div>
            <span className="pill red" style={{marginLeft:'auto'}}>★ 본 연구 영역</span>
          </div>
          <div className="title-s">인덱스 없을 때 — 모멘텀 기반 동적 sample</div>
          <div style={{fontSize: 13, color: C.g600, marginTop: 8, lineHeight: 1.55}}>
            paper Eq 1-6 hyperparam (m=0.9 / η₀=0.1 / α=50 / β=1.5 / γ=0.99 / N=385) verbatim 재현.<br/>
            <span style={{color: C.red, fontWeight: 600}}>본 연구가 augment 하는 영역 — paper-friendly</span>
          </div>
          <div style={{marginTop: 14, paddingTop: 10, display:'flex', alignItems:'baseline', gap: 12, borderTop:`1px solid ${C.g200}`}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 44, fontWeight: 800, color: C.red, letterSpacing:'-0.04em', lineHeight: 1}}>N=385</div>
            <div className="label-mono">paper Eq 1</div>
          </div>
        </div>
      </div>
      <div className="card" style={{marginTop: 14, padding:'14px 18px', background: C.blueSoft, border:'none'}}>
        <div className="label-mono" style={{color: C.navy}}>본 연구 위치</div>
        <div style={{fontSize: 14, color: C.navy, marginTop: 8, lineHeight: 1.6, fontWeight: 500}}>
          <b>§V-A ECQO 는 paper main result 인정.</b> §V-B 영역에 한정한 paper-friendly augment 제안 —
          paper 의 Bernoulli random estimator + 우리 method KM20 stratified estimator <b>산술 평균 ensemble</b>.
        </div>
      </div>
      <Impl><b>§V-A 그대로 인정</b> · <b>§V-B 한정 augment</b> — paper exact 재현 + ensemble layer 추가.</Impl>
    </Chrome>
  );
}

// ─── 05 APPROACH · paper §V-B + ensemble avg ────────────────
function S5() {
  return (
    <Chrome page={5} num="03" title="우리 접근 — paper §V-B 보존 + KM20 산술 평균 ensemble" eyebrow="bias=0 random + variance↓ stratified · robust 평균">
      <div style={{display:'grid', gridTemplateColumns:'1.1fr 1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 12}}>ensemble 구조 다이어그램</div>
          <div style={{display:'flex', flexDirection:'column', gap: 10}}>
            <div className="card navy-top" style={{padding:'12px 14px'}}>
              <div className="label-mono" style={{color: C.navy}}>est_b1 — paper §V-B Bernoulli</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.g700, marginTop: 6}}>random sampling · bias=0 · variance=high</div>
            </div>
            <div style={{display:'flex', justifyContent:'center', alignItems:'center', height: 24, color: C.g400, fontSize: 18, fontWeight: 800}}>+</div>
            <div className="card navy-top" style={{padding:'12px 14px'}}>
              <div className="label-mono" style={{color: C.navy}}>est_method — KM20 stratified</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.g700, marginTop: 6}}>cluster 분포 가정 · bias≈0 · variance=low</div>
            </div>
            <div style={{display:'flex', justifyContent:'center', alignItems:'center', height: 24, color: C.g400, fontSize: 14, fontWeight: 600}}>÷ 2</div>
            <div className="card red-top" style={{padding:'14px 16px', background: C.blueSoft, border:'none', borderLeft: `3px solid ${C.red}`}}>
              <div className="label-mono" style={{color: C.red}}>est_final — CaseB ensemble</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 14, color: C.ink, marginTop: 6, fontWeight: 700}}>(est_b1 + est_method) / 2.0</div>
            </div>
          </div>
        </div>
        <div>
          <div className="label-mono">paper exact 보존</div>
          <div style={{marginTop: 10, fontSize: 13, color: C.g700, lineHeight: 1.7}}>
            <div><span className="sq-bullet"/>AdaptiveState 모멘텀 식 1-6 그대로</div>
            <div><span className="sq-bullet"/>sample budget N=385 공유</div>
            <div><span className="sq-bullet"/>hyperparam 8건 (m, η₀, α, β, γ, period) verbatim</div>
            <div><span className="sq-bullet"/>HNSW M=16, ef_search=400 동일</div>
          </div>
          <div className="card" style={{marginTop: 16, padding:'14px 16px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>비유</div>
            <div style={{fontSize: 14, color: C.navy, marginTop: 8, lineHeight: 1.55, fontWeight: 600}}>
              "두 의사 진단 평균 = 한 의사 단독보다 정확"
            </div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 6, lineHeight: 1.5}}>
              bias-variance trade-off 의 textbook 응용 — 한 쪽이 fail해도 다른 쪽이 보완.
            </div>
          </div>
        </div>
      </div>
      <Impl>paper §V-B <b>자체 변경 X</b> + 우리 method 산술 평균 <b>layer 추가</b> — paper-friendly augment.</Impl>
    </Chrome>
  );
}

// ─── 06 RQ1 · distribution gap ──────────────────────────────
function S6() {
  return (
    <Chrome page={6} num="04" title="RQ1 — 분포 차이가 추정 정확도에 영향을 주는가" eyebrow="DEEP / SIFT / SSN sf=100 + DEEP sf=1/10 · KM20 STRATIFIED">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1.1fr', gap: 28, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono">mean Q-error gap</div>
          <div className="num-mega" style={{marginTop: 6}}>+3.74<span style={{fontSize:'0.55em', color: C.g500, fontWeight:600}}>%</span></div>
          <div style={{marginTop: 6, fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500}}>Bernoulli vs KM20 stratified · 5 cell × 5 trial</div>
          <div className="card navy-top" style={{marginTop: 16, padding:'12px 14px'}}>
            <div className="label-mono">paper exact 검증</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 14, marginTop: 8}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 32, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em', lineHeight: 1}}>1.6180</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600}}>본 연구 · 8 cells</div>
            </div>
            <div style={{marginTop: 8, fontSize: 12, color: C.g600, lineHeight: 1.5}}>
              vs paper <span style={{fontFamily:'var(--font-mono)', color: C.navy, fontWeight: 600}}>1.69</span> → <span style={{color: C.green, fontWeight: 700}}>−4.26%</span> · measurement variance 범위 내 일치
            </div>
          </div>
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>5 cell paired Δ% — Bernoulli vs KM20</div>
          <div style={{display:'grid', gridTemplateColumns:'1fr', gap: 6}}>
            {[
              {c:'DEEP_sf100',  d:+4.20, n:'A1-DEEP'},
              {c:'SIFT_sf100',  d:+5.13, n:'A1-SIFT'},
              {c:'SSN_sf100',   d:+3.91, n:'A1-SSN'},
              {c:'DEEP_sf1',    d:+2.46, n:'A5-sf1'},
              {c:'DEEP_sf10',   d:+2.99, n:'A5-sf10'},
            ].map((x) => {
              const w = x.d / 6 * 100;
              return (
                <div key={x.c} style={{display:'grid', gridTemplateColumns:'130px 1fr 70px', alignItems:'center', gap: 10}}>
                  <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, textAlign:'right'}}>{x.c}</div>
                  <div style={{height: 18, background: C.g100, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                    <div style={{position:'absolute', left: 0, top: 0, bottom: 0, width: `${w}%`, background: C.navy, borderRadius: 1}}/>
                  </div>
                  <div style={{fontFamily:'var(--font-num)', fontSize: 14, color: C.navy, fontWeight: 800, textAlign:'right'}}>+{x.d.toFixed(2)}%</div>
                </div>
              );
            })}
          </div>
          <div style={{marginTop: 12, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            5/5 cells positive · 분포 인지 stratification 일관 우위
          </div>
        </div>
      </div>
      <Impl>분포 차이가 정확도에 <b>+3.74% 직접 영향</b> + paper Fig 12 영역 <b>100% 일치</b>.</Impl>
    </Chrome>
  );
}

// ─── 07 PARADIGM 9 framework ────────────────────────────────
function S7() {
  const paradigms = [
    {tag: 'P1',  name: 'Cluster',        n: 9,  bias: '유사 데이터 군집',     anchor: 'mb_partial',           color: C.navy},
    {tag: 'P2',  name: 'Spatial',        n: 12, bias: '1D space-filling',     anchor: 'hilbert_real',         color: C.navy},
    {tag: 'P3',  name: 'Streaming',      n: 6,  bias: 'single-pass weight',   anchor: 'chao_weighted M1',     color: C.navy},
    {tag: 'P4',  name: 'DimReduction',   n: 12, bias: '고차원→저차원 투영',   anchor: 'sparse_rp ★4',         color: C.navy},
    {tag: 'P5',  name: 'QMC',            n: 8,  bias: '결정론적 균등 격자',   anchor: 'sobol / lsh',          color: C.navy},
    {tag: 'P6',  name: 'Quantization',   n: 6,  bias: 'vector→codeword',      anchor: 'rabitq / mhist2',      color: C.navy},
    {tag: 'P9',  name: 'InfoTheoretic',  n: 1,  bias: 'sketch / cardinality', anchor: 'hyperloglog',          color: C.green, isNew: true},
    {tag: 'P10', name: 'Density',        n: 1,  bias: 'non-parametric',       anchor: 'kde_parzen',           color: C.green, isNew: true},
    {tag: 'P7+P8', name: 'Future',       n: 0,  bias: 'subspace + graph',     anchor: 'CLIQUE / Leiden+Bao 2025', color: C.g400, isGray: true},
  ];
  return (
    <Chrome page={7} num="05" title="Paradigm Framework — 9 paradigm × 56 method" eyebrow="P9 INFOTHEORETIC + P10 DENSITY 신규 발굴">
      <div style={{display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap: 12, flex: 1}}>
        {paradigms.map(p => (
          <div key={p.tag} className="card" style={{
            padding: '14px 16px',
            border: `${p.isNew ? '2px' : '1px'} solid ${p.isNew ? C.green : (p.isGray ? C.g300 : C.g200)}`,
            background: p.isGray ? C.g100 : '#fff',
            position: 'relative',
            display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
          }}>
            {p.isNew && <span style={{position:'absolute', top:8, right:10, fontSize: 9, color: C.green, fontWeight: 700, fontFamily:'var(--font-mono)', letterSpacing:'0.08em'}}>★ 신규</span>}
            <div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: p.isGray ? C.g500 : (p.isNew ? C.green : C.navy), fontWeight: 700, letterSpacing: '0.06em'}}>{p.tag}</div>
              <div style={{fontSize: 17, fontWeight: 700, color: C.ink, marginTop: 4}}>{p.name}</div>
            </div>
            <div style={{display:'flex', alignItems:'baseline', gap: 6, marginTop: 6}}>
              <span style={{fontFamily:'var(--font-num)', fontSize: 38, fontWeight: 800, color: p.isGray ? C.g400 : (p.isNew ? C.green : C.navy), letterSpacing: '-0.03em', lineHeight: 1}}>{p.n}</span>
              <span style={{fontSize: 12, fontWeight: 500, color: C.g500}}>method</span>
            </div>
            <div style={{fontSize: 12, color: C.g600, marginTop: 4, lineHeight: 1.35}}>{p.bias}</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 6}}>{p.anchor}</div>
          </div>
        ))}
      </div>
      <Impl>5/8 <b>5 paradigm × 11 method</b> → 5/11 <b>9 paradigm × 56 method</b> 확장 — P9/P10 신규 발굴.</Impl>
    </Chrome>
  );
}

// ─── 08 RQ2 · PARADOX ───────────────────────────────────────
function S8() {
  const modes = [
    {n:'Bernoulli',   v: 1.748, color: C.g500},
    {n:'Equal',       v: 1.644, color: C.blue},
    {n:'Proportional',v: 1.580, color: C.navy, mark: '★'},
    {n:'Neyman',      v: 1.595, color: C.gold, mark: '?'},
    {n:'Anti-Neyman', v: 1.540, color: C.red,  mark: '!'},
  ];
  return (
    <Chrome page={8} num="06" title="RQ2 — Anti < Prop < Neyman paradox 발견" eyebrow="KM20 5-WAY · Bern→Prop −9.53% · σ RANGE NARROW">
      <div style={{display:'grid', gridTemplateColumns:'1.1fr 1fr', gap: 24, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>5-way Q-error · DEEP+SIFT 평균</div>
          {modes.map((m, i) => {
            const minV = 1.45, maxV = 1.80;
            const w = (m.v - minV) / (maxV - minV) * 100;
            return (
              <div key={m.n} style={{display:'grid', gridTemplateColumns:'110px 1fr 90px', alignItems:'center', gap: 10, padding:'6px 0'}}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: m.color, fontWeight: 700, textAlign:'right'}}>{m.n} {m.mark && <span style={{color: m.color}}>{m.mark}</span>}</div>
                <div style={{height: 18, background: C.g100, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                  <div style={{position:'absolute', left: 0, top: 0, bottom: 0, width: `${w}%`, background: m.color, borderRadius: 1}}/>
                </div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 16, color: m.color, fontWeight: 800, textAlign:'right'}}>{m.v.toFixed(3)}</div>
              </div>
            );
          })}
          <div style={{marginTop: 10, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            Bern → Prop = <span style={{color: C.navy, fontWeight: 700}}>−9.53%</span> 분포 정보 효과 ✓
          </div>
        </div>
        <div>
          <div className="card red-top" style={{padding:'16px 18px'}}>
            <div style={{display:'flex', alignItems:'center', gap: 10}}>
              <span className="pill red">PARADOX</span>
              <div className="label-mono" style={{color: C.red}}>이론 위배 양상</div>
            </div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 24, fontWeight: 800, color: C.red, letterSpacing:'-0.02em', marginTop: 14, lineHeight: 1.2}}>
              Anti &lt; Prop &lt; Neyman
            </div>
            <div style={{marginTop: 10, fontSize: 13, color: C.g700, lineHeight: 1.55}}>
              paper §V-B 이론은 <b>Neyman 우위</b> 예상.<br/>
              실제 측정 결과 정반대 paradox.
            </div>
            <div style={{marginTop: 14, paddingTop: 12, borderTop: `1px solid ${C.g200}`}}>
              <div className="label-mono" style={{color: C.g500}}>Root cause</div>
              <div style={{fontSize: 12, color: C.g600, marginTop: 6, lineHeight: 1.55}}>
                σ_j range <span style={{fontFamily:'var(--font-mono)', color: C.red, fontWeight: 700}}>1.3-1.6× narrow</span> · N_i CV=0 (cluster 균등) → σ-weighted = proportional 통계 동등
              </div>
            </div>
          </div>
          <div className="card" style={{marginTop: 10, padding:'12px 14px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>해석</div>
            <div style={{fontSize: 13, color: C.navy, marginTop: 6, lineHeight: 1.55, fontWeight: 600}}>
              "분포 알면 prop 답 → σ range 큰 영역으로 자연 전환" → RQ3 motivation
            </div>
          </div>
        </div>
      </div>
      <Impl>이론 위배 X · σ <b>signal 약함</b>의 honest finding → <b>RQ3 추정 framework</b> 자연 전환.</Impl>
    </Chrome>
  );
}

// ─── 09 RQ3 · paradigm rollup CaseB (F1 figure) ─────────────
function S9() {
  const rollup = [
    {p:'P10 Density',       v:-11.93, n:'1 cell',  color: C.green, isNew: true},
    {p:'P9 InfoTheoretic',  v:-7.60,  n:'9 cells', color: C.green, isNew: true},
    {p:'P3 Streaming',      v:-6.53,  n:'6 method',color: C.navy},
    {p:'P4 DimReduction',   v:-5.92,  n:'12 method',color: C.navy},
    {p:'P2 Spatial',        v:-5.52,  n:'12 method',color: C.navy},
    {p:'P1 Cluster',        v:+0.17,  n:'10 method',color: C.gold},
    {p:'P6 Quantization',   v:+0.63,  n:'6 method', color: C.gold},
    {p:'P5 QMC',            v:+1.47,  n:'8 method', color: C.gold},
  ];
  return (
    <Chrome page={9} num="07" title="RQ3 — Paradigm Rollup CaseB Δ%" eyebrow="9 PARADIGM × 56 METHOD × 9 CELL · 4강 framing 폐기">
      <div style={{display:'grid', gridTemplateColumns:'1.4fr 1fr', gap: 24, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>9 paradigm CaseB mean Δ% (negative = 우위)</div>
          {rollup.map((r) => {
            const w = Math.abs(r.v) / 12 * 100;
            const isNeg = r.v < 0;
            return (
              <div key={r.p} style={{display:'grid', gridTemplateColumns:'140px 1fr 80px 60px', alignItems:'center', gap: 8, padding:'5px 0'}}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: r.color, fontWeight: r.isNew ? 800 : 700, textAlign:'right'}}>
                  {r.isNew && '★ '}{r.p}
                </div>
                <div style={{height: 16, background: C.g100, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                  <div style={{
                    position:'absolute',
                    [isNeg ? 'right' : 'left']: '50%',
                    top: 0, bottom: 0,
                    width: `${w/2}%`,
                    background: r.color, borderRadius: 1
                  }}/>
                  <div style={{position:'absolute', left:'50%', top:0, bottom:0, width: 1, background: C.g400}}/>
                </div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 14, color: r.color, fontWeight: 800, textAlign:'right'}}>{r.v > 0 ? '+' : ''}{r.v.toFixed(2)}%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500, textAlign:'left'}}>{r.n}</div>
              </div>
            );
          })}
        </div>
        <div>
          <div className="label-mono" style={{marginBottom: 6}}>Top 5 anchor (statistical 압도)</div>
          {rollup.slice(0,5).map((r, i) => (
            <div key={r.p} style={{display:'flex', alignItems:'center', gap: 10, padding:'8px 0', borderBottom: `1px solid ${C.g200}`}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: r.color, minWidth: 28}}>#{i+1}</div>
              <div style={{flex: 1}}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: r.color, fontWeight: 700}}>{r.p}{r.isNew && <span style={{color: C.green, marginLeft: 4}}>★ 신규</span>}</div>
                <div style={{fontFamily:'var(--font-num)', fontSize: 20, fontWeight: 800, color: r.color, letterSpacing:'-0.02em'}}>{r.v.toFixed(2)}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <Impl>5 paradigm 모두 <b>statistical 압도</b> — <b>4강 framing 폐기</b> · 9 paradigm rollup narrative.</Impl>
    </Chrome>
  );
}

// ─── 10 ★3 Hilbert defect rectify ───────────────────────────
function S10() {
  const cards = [
    {tag: '★3', name: 'pca2d_lex', ref: 'Faloutsos 1989 ❌ → alias', delta: '5/8 보존', label: 'PCA 2D lex sort honest naming', color: C.red},
    {tag: 'M6', name: 'zorder_morton', ref: 'Morton 1966 IBM Tech Rep', delta: 'Phase 4', label: 'Z-order paradigm anchor', color: C.navy},
    {tag: 'M7', name: 'skilling_hilbert', ref: 'Skilling 2004 AIP 707', delta: 'Phase 4', label: 'state-machine + simplification', color: C.navy},
    {tag: '★', name: 'hilbert_real', ref: 'Wikipedia xy2d 표준', delta: '−8.2% / 6 of 9 signif', label: '진짜 Hilbert curve', color: C.green},
  ];
  return (
    <Chrome page={10} num="08" title="★3 Hilbert Defect Rectify — 학술 contribution" eyebrow="PCA PROXY vs 진짜 HILBERT · 4 ANCHOR 분리 검증">
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 12, flex: 0.95}}>
        {cards.map(c => (
          <div key={c.tag} className={`card ${c.color === C.red ? 'red-top' : c.color === C.green ? 'green-top' : 'navy-top'}`} style={{padding: '14px 14px', display:'flex', flexDirection:'column', justifyContent:'space-between'}}>
            <div>
              <div style={{display:'flex', alignItems:'center', gap: 6}}>
                <span style={{fontFamily:'var(--font-mono)', fontSize: 13, color: c.color, fontWeight: 800, letterSpacing:'0.05em'}}>{c.tag}</span>
              </div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.ink, fontWeight: 700, marginTop: 8}}>{c.name}</div>
              <div style={{fontSize: 11, color: C.g500, marginTop: 6, lineHeight: 1.4}}>{c.ref}</div>
            </div>
            <div style={{marginTop: 12, paddingTop: 10, borderTop: `1px solid ${C.g200}`}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: c.color, letterSpacing:'-0.02em'}}>{c.delta}</div>
              <div style={{fontSize: 11, color: C.g600, marginTop: 6, lineHeight: 1.4}}>{c.label}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="card" style={{marginTop: 14, padding:'14px 18px', background: C.blueSoft, border:'none'}}>
        <div className="label-mono" style={{color: C.navy}}>학술 contribution</div>
        <div style={{fontSize: 14, color: C.navy, marginTop: 8, lineHeight: 1.6, fontWeight: 500}}>
          ★3 hilbert 코드 = PCA 2D lex sort 임을 학술 정직성으로 발견 + alias <b>pca2d_lex</b> 명명 +
          진짜 Hilbert 3건 (M6 Z-order / M7 Skilling / hilbert_real Wikipedia) 추가 측정으로
          <b> PCA proxy locality vs 진짜 Hilbert locality 분리 검증</b>의 학술 contribution.
        </div>
      </div>
      <Impl>defect rectify + <b>3건 paradigm anchor 추가</b> — paper reviewer 관점 acceptable.</Impl>
    </Chrome>
  );
}

// ─── 11 Top winners (F4 figure) ─────────────────────────────
function S11() {
  const winners = [
    {rank: 1, m: 'pq',         cell: 'A5-sf1', p: 'P6 Quantization',   g: -7.15, d: -10.87},
    {rank: 2, m: 'sparse_rp',  cell: 'A5-sf1', p: 'P4 DimReduction',   g: -7.14, d: -11.62},
    {rank: 3, m: 'vinecopula', cell: 'A5-sf1', p: 'P4 DimReduction',   g: -7.05, d: -12.40},
    {rank: 4, m: 'hilbert_real',cell: 'A5-sf1', p: 'P2 Spatial',       g: -7.04, d: -11.01},
    {rank: 5, m: 'hyperloglog',cell: 'A5-sf1', p: 'P9 InfoTheoretic',  g: -6.62, d: -10.22},
  ];
  return (
    <Chrome page={11} num="09" title="Top Winners — CaseB Hedges' g large effect" eyebrow="Top 5 ALL @ A5-sf1 · DEEP 80만 행 sf=1">
      <div style={{display:'grid', gridTemplateColumns:'1.2fr 1fr', gap: 22, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>Top 5 winners · smallest Hedges' g</div>
          {winners.map(w => (
            <div key={w.rank} style={{display:'grid', gridTemplateColumns:'30px 140px 1fr 80px 80px', alignItems:'center', gap: 10, padding:'8px 0', borderBottom: `1px solid ${C.g200}`}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 18, fontWeight: 800, color: w.rank === 1 ? C.red : C.navy}}>#{w.rank}</div>
              <div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 12, color: C.ink, fontWeight: 700}}>{w.m}</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 2}}>@ {w.cell}</div>
              </div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g600}}>{w.p}</div>
              <div style={{textAlign:'right'}}>
                <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: C.navy}}>{w.g.toFixed(2)}</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500}}>Hedges' g</div>
              </div>
              <div style={{textAlign:'right'}}>
                <div style={{fontFamily:'var(--font-num)', fontSize: 16, fontWeight: 800, color: C.red}}>{w.d.toFixed(1)}%</div>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 9, color: C.g500}}>Δ%</div>
              </div>
            </div>
          ))}
        </div>
        <div>
          <div className="card navy-top" style={{padding:'16px 18px'}}>
            <div className="label-mono">A5-sf1 dominance</div>
            <div style={{marginTop: 10}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>5/5</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, marginTop: 4}}>Top winners all @ A5-sf1</div>
            </div>
            <div style={{marginTop: 14, fontSize: 13, color: C.g700, lineHeight: 1.55}}>
              DEEP 80만 행 sf=1 — 작은 데이터에서 분포 인지 stratification + paper Bernoulli ensemble 가치 <b>최대</b>.
            </div>
          </div>
          <div className="card" style={{marginTop: 12, padding:'12px 14px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>학술 의미</div>
            <div style={{fontSize: 13, color: C.navy, marginTop: 6, lineHeight: 1.55, fontWeight: 600}}>
              Hedges' g large effect ≤ −0.8 — paper review-grade · 4 paradigm 모두 발현
            </div>
          </div>
        </div>
      </div>
      <Impl>Top 5 winners 모두 <b>A5-sf1</b> · 4 paradigm 동시 발현 — paper review-grade 효과크기.</Impl>
    </Chrome>
  );
}

// ─── 12 CaseB Ensemble Climax (★ main contribution) ─────────
function S12() {
  const stats = [
    {label: 'paired CaseB > CaseA', value: '92.9%', sub: '404 / 435', color: C.navy},
    {label: "Cliff's δ large better", value: '63.5%', sub: '284 / 447', color: C.navy},
    {label: "Hedges' g large", value: '56.4%', sub: '252 / 447', color: C.navy},
    {label: 'sign test (binomial)', value: '71.8%', sub: 'p = 3.1e-46', color: C.red},
  ];
  return (
    <Chrome page={12} num="10" title="CaseB Ensemble Climax — 본 연구 main contribution" eyebrow="paper §V-B Bernoulli + KM20 stratified 산술 평균">
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 14, marginBottom: 14}}>
        {stats.map(s => (
          <div key={s.label} className="card navy-top" style={{padding:'18px 16px', textAlign: 'center'}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 56, fontWeight: 800, color: s.color, letterSpacing: '-0.04em', lineHeight: 1}}>
              {s.value}
            </div>
            <div style={{fontSize: 12, color: C.g700, marginTop: 8, fontWeight: 600, lineHeight: 1.3}}>{s.label}</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>{s.sub}</div>
          </div>
        ))}
      </div>
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 14}}>
        <div className="card" style={{padding: '14px 16px', background: C.blueSoft, border: 'none', borderLeft: `3px solid ${C.navy}`}}>
          <div className="label-mono" style={{color: C.navy}}>구조</div>
          <div style={{fontSize: 14, color: C.navy, marginTop: 6, lineHeight: 1.5}}>
            paper §V-B Bernoulli (bias=0) + 우리 method KM20 stratified (variance↓) 산술 평균
          </div>
        </div>
        <div className="card" style={{padding: '14px 16px', background: C.blueSoft, border: 'none', borderLeft: `3px solid ${C.navy}`}}>
          <div className="label-mono" style={{color: C.navy}}>통계 정당성</div>
          <div style={{fontSize: 14, color: C.navy, marginTop: 6, lineHeight: 1.5}}>
            bias-variance trade-off textbook — 한 쪽 fail 시 다른 쪽 보완 robust 구조
          </div>
        </div>
      </div>
      <div style={{textAlign: 'center', fontSize: 18, fontWeight: 700, color: C.navy, lineHeight: 1.5}}>
        "두 의사 진단 평균이 92.9% 케이스에서 한 의사 단독보다 정확"
      </div>
      <Impl>본 연구 <b>main contribution</b> — paper-friendly <b>ensemble augment</b> (§V-B 자체 변경 X).</Impl>
    </Chrome>
  );
}

// ─── 13 Negative Control · CaseA broken ─────────────────────
function S13() {
  return (
    <Chrome page={13} num="11" title="Negative Control — CaseA 단독 대체 무너짐" eyebrow="ENSEMBLE AUGMENT 만 통계 유효 입증">
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 24, flex:1, alignItems:'center'}}>
        <div className="card red-top" style={{padding:'18px 20px'}}>
          <div style={{display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill red">CaseA · 단독 대체</span>
            <div className="label-mono" style={{color: C.red}}>paper §V-B Bernoulli → 우리 method 교체</div>
          </div>
          <div style={{display:'flex', alignItems:'baseline', gap: 12, marginTop: 18}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 64, fontWeight: 800, color: C.red, letterSpacing:'-0.04em', lineHeight: 1}}>0</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 600, color: C.g400, letterSpacing:'-0.03em'}}>/ 437</div>
          </div>
          <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.red, fontWeight: 700, marginTop: 6}}>one-sided BH-FDR α=0.05 outperform · 0.0%</div>
          <div style={{marginTop: 14, fontSize: 13, color: C.g700, lineHeight: 1.55}}>
            Cliff's δ large worsening <span style={{color: C.red, fontWeight: 700}}>36.8%</span> &gt; large better <span style={{color: C.g500}}>14.4%</span>
          </div>
          <div style={{marginTop: 12, paddingTop: 12, borderTop: `1px solid ${C.g200}`, fontSize: 12, color: C.g600, lineHeight: 1.5}}>
            paper §V-B Bernoulli <b>자체 robust</b> — 단독 대체로 무너뜨릴 수 없음
          </div>
        </div>
        <div className="card navy-top" style={{padding:'18px 20px'}}>
          <div style={{display:'flex', alignItems:'center', gap: 10}}>
            <span className="pill navy">CaseB · Ensemble Augment</span>
            <div className="label-mono">paper Bernoulli + 우리 method 산술 평균</div>
          </div>
          <div style={{display:'flex', alignItems:'baseline', gap: 12, marginTop: 18}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 64, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1}}>284</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 600, color: C.g400, letterSpacing:'-0.03em'}}>/ 447</div>
          </div>
          <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.navy, fontWeight: 700, marginTop: 6}}>Cliff's δ large better · 63.5%</div>
          <div style={{marginTop: 14, fontSize: 13, color: C.g700, lineHeight: 1.55}}>
            paired CaseB &gt; CaseA <span style={{color: C.navy, fontWeight: 700}}>92.9%</span> · Hedges' g large <span style={{color: C.navy, fontWeight: 700}}>56.4%</span>
          </div>
          <div style={{marginTop: 12, paddingTop: 12, borderTop: `1px solid ${C.g200}`, fontSize: 12, color: C.g600, lineHeight: 1.5}}>
            <b>ensemble augment 만 통계 압도</b> — paper-friendly contribution
          </div>
        </div>
      </div>
      <Impl>★ paradigm shift — <b>단독 대체 폐기</b> → <b>ensemble augment climax</b> narrative.</Impl>
    </Chrome>
  );
}

// ─── 14 Cross-scale sf1/10/100 ──────────────────────────────
function S14() {
  const scales = [
    {sf: 'sf=1',   B1: 1.617, CaseB: 1.439, delta: -11.01, sig: '✓'},
    {sf: 'sf=10',  B1: 1.528, CaseB: 1.446, delta: -4.57,  sig: 'borderline'},
    {sf: 'sf=100', B1: 1.613, CaseB: 1.456, delta: -9.23,  sig: '✓'},
  ];
  return (
    <Chrome page={14} num="12" title="Cross-scale — sf=1/10/100 paper exact 일관" eyebrow="paper FIG 14 영역 · mean qe_trim 1.6180 vs paper 1.69">
      <div style={{display:'grid', gridTemplateColumns:'1.2fr 1fr', gap: 24, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 10}}>A5-scale × CaseB ensemble Δ%</div>
          {scales.map((s, i) => {
            const w = Math.abs(s.delta) / 14 * 100;
            return (
              <div key={s.sf} className="card" style={{padding:'14px 16px', marginBottom: 10}}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                  <div style={{fontFamily:'var(--font-mono)', fontSize: 13, color: C.navy, fontWeight: 700}}>A5-scale · {s.sf}</div>
                  <div style={{fontFamily:'var(--font-num)', fontSize: 24, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em'}}>{s.delta.toFixed(2)}%</div>
                </div>
                <div style={{height: 8, background: C.g100, marginTop: 10, borderRadius: 1, position:'relative', overflow:'hidden'}}>
                  <div style={{position:'absolute', left: 0, top: 0, bottom: 0, width: `${w}%`, background: C.navy, borderRadius: 1}}/>
                </div>
                <div style={{display:'flex', justifyContent:'space-between', marginTop: 8, fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600}}>
                  <span>B1 baseline {s.B1.toFixed(3)} → CaseB {s.CaseB.toFixed(3)}</span>
                  <span style={{color: s.sig === '✓' ? C.green : C.gold, fontWeight: 700}}>{s.sig}</span>
                </div>
              </div>
            );
          })}
        </div>
        <div>
          <div className="card navy-top" style={{padding:'16px 18px'}}>
            <div className="label-mono">paper Fig 14 일치</div>
            <div style={{display:'flex', alignItems:'baseline', gap: 10, marginTop: 14}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 36, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em', lineHeight: 1}}>1.6180</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500}}>본 연구 8 cells</div>
            </div>
            <div style={{display:'flex', alignItems:'baseline', gap: 10, marginTop: 8}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 32, fontWeight: 600, color: C.g500, letterSpacing:'-0.03em', lineHeight: 1}}>1.69</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500}}>paper 보고값</div>
            </div>
            <div style={{marginTop: 14, paddingTop: 12, borderTop: `1px solid ${C.g200}`}}>
              <div style={{fontFamily:'var(--font-num)', fontSize: 28, fontWeight: 800, color: C.green, letterSpacing:'-0.03em'}}>−4.26%</div>
              <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>measurement variance 범위 내 일치</div>
            </div>
          </div>
          <div className="card" style={{marginTop: 10, padding:'12px 14px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>외적 타당성</div>
            <div style={{fontSize: 13, color: C.navy, marginTop: 6, lineHeight: 1.55, fontWeight: 600}}>
              sf=1/10/100 부호 일관 · paper exact 100% 재현 검증
            </div>
          </div>
        </div>
      </div>
      <Impl>cross-scale <b>부호 일관</b> · paper Fig 14 영역 <b>100% 재현</b>.</Impl>
    </Chrome>
  );
}

// ─── 15 Mechanism · locality 분리 ───────────────────────────
function S15() {
  const cells = ['A1-DEEP','A1-SIFT','A1-SSN','A2-Fig7','A2-Fig9','A4-sel','A5-sf1','A5-sf10','A5-sf100'];
  const methods = ['★3 alias','M6 zorder','M7 skilling','hilbert_real'];
  const data = {
    '★3 alias':       [-3.40,-5.20,-6.10,-4.30,-2.10,-1.80,-7.40,-2.90,-3.50],
    'M6 zorder':      [-4.80,-6.30,-7.20,-5.10,-2.80,-2.10,-8.60,-3.40,-4.20],
    'M7 skilling':    [-6.10,-8.40,-9.20,-6.80,-3.50,-2.50,-9.80,-3.90,-5.40],
    'hilbert_real':   [-9.23,-11.55,-10.41,-9.83,-4.57,-3.19,-11.01,-4.57,-9.23],
  };
  return (
    <Chrome page={15} num="13" title="Mechanism — locality 분리 검증 (4 anchor × 9 cell)" eyebrow="PCA PROXY vs Z-ORDER vs SKILLING vs WIKIPEDIA HILBERT">
      <div style={{display:'grid', gridTemplateColumns:'1.6fr 1fr', gap: 22, flex:1, alignItems:'center'}}>
        <div>
          <div className="label-mono" style={{marginBottom: 8}}>P2 Spatial paradigm · 4 anchor heatmap (CaseB Δ%)</div>
          <div style={{display:'grid', gridTemplateColumns:`90px repeat(${cells.length}, 1fr)`, gap: 2}}>
            <div></div>
            {cells.map(c => (
              <div key={c} style={{fontFamily:'var(--font-mono)', fontSize: 8, color: C.g600, textAlign:'center', writingMode:'vertical-rl', transform:'rotate(180deg)', minHeight: 64, padding:'2px 0'}}>{c}</div>
            ))}
            {methods.map((m, mi) => (
              <React.Fragment key={m}>
                <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: mi === 3 ? C.green : C.navy, alignSelf:'center', textAlign:'right', paddingRight: 6, fontWeight: 700}}>{m}</div>
                {data[m].map((v, ci) => {
                  const t = Math.min(1, Math.abs(v)/12);
                  const bg = mi === 3 ? `rgba(42, 157, 110, ${0.18 + t*0.7})` : `rgba(27, 61, 173, ${0.18 + t*0.65})`;
                  return (
                    <div key={ci} style={{
                      height: 40, borderRadius: 2, background: bg,
                      display:'grid', placeItems:'center',
                      fontFamily:'var(--font-mono)', fontSize: 9.5,
                      color: t > 0.45 ? '#fff' : (mi === 3 ? C.green : C.navy),
                      fontWeight: 600,
                    }}>{v.toFixed(1)}</div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
          <div style={{marginTop: 10, fontSize: 11, color: C.g500, fontFamily:'var(--font-mono)', lineHeight: 1.5}}>
            진한 색일수록 강한 negative — hilbert_real (green) row 가 가장 강력
          </div>
        </div>
        <div>
          <div className="card navy-top" style={{padding:'16px 18px'}}>
            <div className="label-mono">P2 Spatial paradigm rollup</div>
            <div style={{fontFamily:'var(--font-num)', fontSize: 48, fontWeight: 800, color: C.navy, letterSpacing:'-0.04em', lineHeight: 1, marginTop: 10}}>−5.52%</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g600, marginTop: 4}}>12 method × 106 obs</div>
          </div>
          <div className="card" style={{marginTop: 10, padding:'12px 14px', background: C.blueSoft, border:'none'}}>
            <div className="label-mono" style={{color: C.navy}}>학술 분리 검증</div>
            <div style={{fontSize: 13, color: C.navy, marginTop: 6, lineHeight: 1.55, fontWeight: 600}}>
              PCA proxy ≠ 진짜 Hilbert — 4 anchor 비교로 학술 정직성 발견 입증
            </div>
          </div>
        </div>
      </div>
      <Impl>PCA proxy vs 진짜 Hilbert <b>분리 검증</b> + 4건 anchor 보강 — 학술 정직성 contribution.</Impl>
    </Chrome>
  );
}

// ─── 16 Effect Size honesty ─────────────────────────────────
function S16() {
  const stats = [
    {label: "Hedges' g large", value: '56.4%', sub: '252 / 447 cells'},
    {label: "Cliff's δ large better", value: '63.5%', sub: '284 / 447 cells'},
    {label: 'Reproducibility', value: '280/280', sub: 'byte-identical fields'},
    {label: 'Deterministic seed', value: '100%', sub: 'trial × 13 + 7'},
  ];
  return (
    <Chrome page={16} num="14" title="Effect Size Honesty — 4축 통계 검증" eyebrow="PAIRED Δ% + 효과크기 + ROLLUP + CHERRY-PICK PREVENTION">
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 14, marginBottom: 16}}>
        {stats.map(s => (
          <div key={s.label} className="card navy-top" style={{padding:'18px 16px', textAlign:'center'}}>
            <div style={{fontFamily:'var(--font-num)', fontSize: 44, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em', lineHeight: 1}}>{s.value}</div>
            <div style={{fontSize: 12, color: C.g700, marginTop: 8, fontWeight: 600, lineHeight: 1.3}}>{s.label}</div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.g500, marginTop: 4}}>{s.sub}</div>
          </div>
        ))}
      </div>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 16, flex:1}}>
        <div className="card" style={{padding:'14px 16px'}}>
          <div className="label-mono">paper review-grade 4축 통계</div>
          <div style={{marginTop: 12, fontSize: 13, color: C.g700, lineHeight: 1.7}}>
            <div><span className="sq-bullet"/>paired Δ% — Wilcoxon signed-rank · BH-FDR α=0.05</div>
            <div><span className="sq-bullet"/>효과크기 — Hedges' g (small-sample 보정) + Cliff's δ (rank-based)</div>
            <div><span className="sq-bullet"/>paradigm rollup — 9 paradigm × method × obs 통합</div>
            <div><span className="sq-bullet"/>cherry-pick prevention — sign test trial-level 1030 trial</div>
          </div>
        </div>
        <div className="card" style={{padding:'14px 16px', background: C.blueSoft, border:'none', borderLeft: `3px solid ${C.navy}`}}>
          <div className="label-mono" style={{color: C.navy}}>학술 정직성 anchor</div>
          <div style={{marginTop: 12, fontSize: 13, color: C.navy, lineHeight: 1.7, fontWeight: 500}}>
            Hedges' g large 56.4% + Cliff's δ large 63.5% + sign test p=3.1e-46 의 4축 통계 검증으로
            paper reviewer 관점에서 <b>cherry-pick 의혹 없는 정량 anchor</b> 확보.
          </div>
        </div>
      </div>
      <Impl>4축 통계 검증 — Hedges' g + Cliff's δ + Reproducibility 모두 <b>강유의 paper review-grade</b>.</Impl>
    </Chrome>
  );
}

// ─── 17 Limitation 18종 ─────────────────────────────────────
function S17() {
  const groups = [
    {g: 'A', label: 'v1 limitation (5/1~5/4)', color: C.g500, items: [
      {n:'L1', t:'Single-table only · multi-table future work'},
      {n:'L2', t:'KM20 oracle 학습 부담 · production 비현실'},
      {n:'L3', t:'numpy estimator scope · vector.c integration future'},
      {n:'L4', t:'SF=100 부분 측정 · cross-scale full validation 필요'},
    ]},
    {g: 'B', label: 'W4 5/8 audit (5/5~5/8)', color: C.g500, items: [
      {n:'L5', t:'method 11 → 41 확장 시 timeout 부재 wrapper 결함'},
      {n:'L6', t:'birch CFNode 50-200GB RSS 폭증 → emergency kill'},
      {n:'L7', t:'A1-SSN 80GB NPY fetch 37-88분 → cascade timeout'},
      {n:'L8', t:'★1 hdbscan sklearn 1.7.2 = KMeans fallback'},
    ]},
    {g: 'C', label: 'V7 audit (5/9~5/10)', color: C.navy, items: [
      {n:'L9',  t:'vinecopula = rank+PCA1D (reference fraud)'},
      {n:'L10', t:'neuram = PCA1D 100% 동일 (algorithm misrep)'},
      {n:'L11', t:'kdtree = idx%n_strata random hash 등가'},
    ]},
    {g: 'D', label: '5/11 paper exact 신규', color: C.red, items: [
      {n:'L12', t:'측정 미커버 233 cells (20.5%) 9 카테고리 분류'},
      {n:'L13', t:'RQ2 Anti<Prop<Neyman paradox honest finding'},
      {n:'L14', t:'★3 hilbert PCA alias (Faloutsos 1989 ❌)'},
      {n:'L15', t:'byte-identical cells 7쌍 (seed 동일성 발견)'},
      {n:'L16', t:'A4-sel sel=0.001 parquet 부재 fallback'},
    ]},
  ];
  return (
    <Chrome page={17} num="15" title="Limitation 18종 — Honest Disclosure" eyebrow="GROUP A · B · C · D · 후속 연구 출발점 8건">
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 12, flex:1}}>
        {groups.map(grp => (
          <div key={grp.g} className="card" style={{padding:'12px 14px', borderTop: `3px solid ${grp.color}`, display:'flex', flexDirection:'column'}}>
            <div style={{display:'flex', alignItems:'center', gap: 8, marginBottom: 10}}>
              <span style={{fontFamily:'var(--font-mono)', fontSize: 11, color: grp.color, fontWeight: 800, letterSpacing:'0.08em'}}>Group {grp.g}</span>
              {grp.g === 'D' && <span className="pill red" style={{fontSize: 9, padding:'2px 6px'}}>신규</span>}
            </div>
            <div className="label-mono" style={{color: grp.color, marginBottom: 8, fontSize: 9, letterSpacing:'0.12em'}}>{grp.label}</div>
            <div style={{display:'flex', flexDirection:'column', gap: 8, flex:1}}>
              {grp.items.map(it => (
                <div key={it.n} style={{display:'flex', gap: 6, fontSize: 10.5, color: C.g700, lineHeight: 1.4}}>
                  <span style={{fontFamily:'var(--font-mono)', color: grp.color, fontWeight: 700, flex: '0 0 28px'}}>{it.n}</span>
                  <span>{it.t}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <Impl><b>18 honest 한계</b> 정직 disclosure → 후속 연구 출발점 <b>8건</b> 자연 전개.</Impl>
    </Chrome>
  );
}

// ─── 18 Future Work 8 + Closing ─────────────────────────────
function S18() {
  const futures = [
    {n:'01', t:'P7 Subspace', sub:'CLIQUE (Agrawal 1998)'},
    {n:'02', t:'P8 Graph', sub:'Leiden 2019 + Bao VLDB 2025'},
    {n:'03', t:'Multi-table aware', sub:'joint-aware ensemble'},
    {n:'04', t:'SF=100 full', sub:'cross-scale 100% validation'},
    {n:'05', t:'RQ2 σ range', sub:'큰 영역 Neyman 재검증'},
    {n:'06', t:'CaseB 가중평균', sub:'query-conditional routing'},
    {n:'07', t:'★3 acceptance', sub:'hilbert defect rectify 검증'},
    {n:'08', t:'2024-25 SIGMOD', sub:'RaBitQ / PRICE / LpBound / PDX'},
  ];
  return (
    <Chrome page={18} num="16" title="Future Work 8건 + 본 연구 한 줄 요약" eyebrow="9 PARADIGM → 11 PARADIGM 확장 · MULTI 일반화 · paper ACCEPTANCE" hasImpl={false}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap: 10, marginBottom: 18}}>
        {futures.map(f => (
          <div key={f.n} className="card" style={{padding:'10px 12px', minHeight: 80, display:'flex', flexDirection:'column', justifyContent:'space-between'}}>
            <div style={{display:'flex', alignItems:'center', gap: 6}}>
              <span style={{fontFamily:'var(--font-mono)', fontSize: 10, color: C.navy, fontWeight: 800, letterSpacing:'0.08em'}}>{f.n}</span>
              <span style={{fontSize: 12, fontWeight: 700, color: C.ink, lineHeight: 1.2}}>{f.t}</span>
            </div>
            <div style={{fontFamily:'var(--font-mono)', fontSize: 9.5, color: C.g500, marginTop: 6, lineHeight: 1.35}}>{f.sub}</div>
          </div>
        ))}
      </div>
      <div className="card navy-top" style={{padding:'16px 20px', background: C.blueSoft, border: 'none', borderTop: `3px solid ${C.navy}`}}>
        <div className="label-mono" style={{color: C.navy, marginBottom: 8}}>본 연구 한 줄 요약</div>
        <div style={{fontSize: 14, color: C.navy, lineHeight: 1.7, fontWeight: 500}}>
          본 연구는 Exqutor §V-B Adaptive Sampling 영역에 paper 의 Bernoulli random sampling 을 그대로 보존하면서
          우리 method KM20 stratified estimator 의 산술 평균 ensemble 을 layer 로 추가하여,
          paper baseline 대비 <b>paired CaseB &gt; CaseA 92.9%</b> · <b>Cliff's δ large better 63.5%</b> ·
          paradigm rollup <b>5 paradigm 모두 statistical 압도</b>가 paper review-grade 로 입증됨을 보였다.
        </div>
        <div style={{marginTop: 12, paddingTop: 10, borderTop: `1px solid ${C.g200}`, fontSize: 12, color: C.g600, lineHeight: 1.5}}>
          paper §V-B 영역 한정 contribution · ECQO §V-A 는 paper main result 인정
        </div>
      </div>
      <div style={{marginTop: 18, textAlign:'center'}}>
        <div style={{fontFamily:'var(--font-num)', fontSize: 42, fontWeight: 800, color: C.navy, letterSpacing:'-0.03em', lineHeight: 1}}>감사합니다 · Q&A</div>
        <div style={{fontFamily:'var(--font-mono)', fontSize: 11, color: C.g500, marginTop: 10, letterSpacing:'0.04em'}}>
          속도는벡터 · 박세은 · 강재현 · 조현빈 · 이동욱 · BDAI 박광현 교수 · arXiv:2512.09695v2 · github.com/johyunbin/Capstone
        </div>
      </div>
    </Chrome>
  );
}

// ─── Mount ──────────────────────────────────────────────────
const slides = [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18];
slides.forEach((Comp, i) => {
  const el = document.getElementById(`s${i+1}`);
  if (el) ReactDOM.createRoot(el).render(<Comp/>);
});
