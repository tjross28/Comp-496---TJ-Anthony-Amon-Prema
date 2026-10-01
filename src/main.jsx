import React, { useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, FileText, Info, LockKeyhole, ShieldCheck, Upload, X } from 'lucide-react'
import './styles.css'

const samplePolicy = `We collect information you provide, including your name, email address, and account activity. We automatically collect device identifiers, IP address, location information, and browsing behavior. We may share your personal information with advertising partners, analytics providers, affiliates, and other third parties. We retain information for as long as necessary for our business purposes. You may opt out of promotional emails, but some data collection is required to use the service. By using our service, you agree to binding arbitration and waive your right to participate in a class action lawsuit.`

const wordCount = text => text.trim() ? text.trim().split(/\s+/).length : 0
const buildAnalysisRequest = text => {
  const clauses = text.split(/(?<=[.!?])\s+/).filter(Boolean); let offset = 0
  return { document_id: `browser-${crypto.randomUUID()}`, source_type: 'text', text, clauses: clauses.map((clause, index) => { const start_offset = text.indexOf(clause, offset); offset = start_offset + clause.length; return { clause_id: `browser-clause-${index + 1}`, text: clause, section_heading: null, start_offset, end_offset: offset, tags: [], confidence: null } }) }
}

function App() {
  const [policy, setPolicy] = useState('')
  const [result, setResult] = useState(null)
  const [dragging, setDragging] = useState(false); const [loading, setLoading] = useState(false); const [error, setError] = useState('')
  const fileRef = useRef()
  const words = wordCount(policy)
  const handleFile = file => { if (file && file.type.startsWith('text/')) { const reader = new FileReader(); reader.onload = e => setPolicy(e.target.result); reader.readAsText(file) } }
  const submit = async () => { if (words < 12) return; setLoading(true); setError(''); try { const response = await fetch('/api/v1/analyses', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(buildAnalysisRequest(policy)) }); const body = await response.json(); if (!response.ok) throw new Error(body.error?.message || 'Analysis could not be completed.'); setResult(body) } catch (requestError) { setError(requestError.message || 'Analysis could not be completed.') } finally { setLoading(false) } }
  const riskLabel = useMemo(() => result ? ({ high: 'High risk signal', moderate: 'Review closely', low: 'Lower risk signal', unknown: 'Insufficient evidence' }[result.risk_level]) : '', [result])

  return <main>
    <nav><a className="brand" href="#top"><span className="brand-mark"><ShieldCheck size={20}/></span>ClearPolicy</a><div className="nav-links"><a href="#how">How it works</a><a href="#privacy">Privacy</a></div><button className="text-button">About the project</button></nav>
    <section className="hero" id="top"><div className="eyebrow"><LockKeyhole size={14}/> Privacy policy clarity, without the jargon</div><h1>Know what you’re<br/><em>agreeing to.</em></h1><p>Paste a policy to uncover data practices, concerning clauses, and the controls you have - before you click “agree.”</p><div className="trust-row"><span><CheckCircle2 size={16}/> No account required</span><span><CheckCircle2 size={16}/> Your text stays in this browser</span></div></section>
    <section className="workspace" aria-label="Policy analyzer"><div className="input-card"><div className="card-heading"><div><span className="step">01</span><h2>Add a privacy policy</h2><p>Paste the text or upload a plain-text file.</p></div>{policy && <button className="clear" onClick={() => {setPolicy('');setResult(null)}}><X size={15}/> Clear</button>}</div><textarea value={policy} onChange={e => setPolicy(e.target.value)} placeholder="Paste privacy policy text here..." aria-label="Privacy policy text" />
      <div className="dropzone" onClick={() => fileRef.current.click()} onDragOver={e => {e.preventDefault();setDragging(true)}} onDragLeave={() => setDragging(false)} onDrop={e => {e.preventDefault();setDragging(false);handleFile(e.dataTransfer.files[0])}} data-dragging={dragging}><Upload size={18}/><span>Drop a .txt file here or <b>browse files</b></span><input ref={fileRef} hidden type="file" accept=".txt,text/plain" onChange={e => handleFile(e.target.files[0])}/></div>
      <div className="input-footer"><span>{words ? `${words.toLocaleString()} words` : 'Minimum 12 words'}</span><button className="sample" onClick={() => setPolicy(samplePolicy)}>Try sample policy</button><button className="analyze" disabled={words < 12} onClick={submit}>Analyze policy <ArrowRight size={17}/></button></div></div>
      {result ? <Results result={result} label={riskLabel} /> : <aside className="preview"><div className="preview-icon"><FileText size={24}/></div><h3>Your analysis will appear here</h3><p>We’ll organize the important details into clear, readable takeaways.</p><div className="preview-list"><span>Data collection</span><span>Sharing practices</span><span>Legal terms</span><span>Your choices</span></div></aside>}</section>
    <section className="how" id="how"><div><span className="eyebrow"><Info size={14}/> Built for everyday decisions</span><h2>Privacy policies shouldn’t require a law degree.</h2></div><div className="how-cards"><article><b>01</b><h3>Submit</h3><p>Add policy text from a website or document.</p></article><article><b>02</b><h3>Understand</h3><p>See plain-language signals across key privacy areas.</p></article><article><b>03</b><h3>Decide</h3><p>Use the findings to ask better questions before agreeing.</p></article></div></section>
    <footer id="privacy"><span>ClearPolicy <small>Prototype</small></span><p>This draft provides educational signals, not legal advice.</p></footer>
  </main>
}

function Results({ result, label }) { return <aside className="results"><div className="result-top"><div><span className="step">02</span><h2>Analysis summary</h2></div><div className={`risk ${result.risk_level === 'high' ? 'high' : result.risk_level === 'moderate' ? 'medium' : 'low'}`}><strong>{result.trust_score}</strong><span>/100</span><small>{label}</small></div></div><div className="meter"><i style={{width:`${result.trust_score}%`}}/></div><p className="risk-note">Higher Trust Scores indicate stronger transparency signals. {result.disclaimer}</p><div className="findings">{result.categories.map(item => <article key={item.id}><div><h3>{item.label}</h3><p>{item.rationale}</p></div><span className="tag">{item.status === 'assessed' ? `${item.score}/100` : 'Needs evidence'}</span></article>)}</div><div className="takeaways"><h3>Rule findings</h3>{result.findings.length ? result.findings.map(item => <p key={item.finding_id}><AlertTriangle size={15}/>{item.title}</p>) : <p><CheckCircle2 size={15}/>No configured concern rules matched.</p>}{result.positive_signals.map(item => <p className="positive" key={item.signal_id}><CheckCircle2 size={15}/>{item.title}</p>)}</div></aside> }

createRoot(document.getElementById('root')).render(<App />)
