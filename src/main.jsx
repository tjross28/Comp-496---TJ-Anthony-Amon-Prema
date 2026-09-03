import React, { useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, FileText, Info, LockKeyhole, ShieldCheck, Upload, X } from 'lucide-react'
import './styles.css'

const samplePolicy = `We collect information you provide, including your name, email address, and account activity. We automatically collect device identifiers, IP address, location information, and browsing behavior. We may share your personal information with advertising partners, analytics providers, affiliates, and other third parties. We retain information for as long as necessary for our business purposes. You may opt out of promotional emails, but some data collection is required to use the service. By using our service, you agree to binding arbitration and waive your right to participate in a class action lawsuit.`

const checks = [
  { id: 'collection', label: 'Data collection', terms: ['collect', 'device', 'location', 'identifier', 'browsing', 'personal information'], description: 'What information the service says it gathers.' },
  { id: 'sharing', label: 'Data sharing', terms: ['share', 'third party', 'advertising', 'affiliate', 'analytics', 'partner'], description: 'Who may receive or use your data.' },
  { id: 'legal', label: 'Legal language', terms: ['arbitration', 'class action', 'waive', 'liability', 'indemnif'], description: 'Terms that may limit choices or legal remedies.' },
  { id: 'agency', label: 'Your control', terms: ['opt out', 'delete', 'access', 'choice', 'control', 'consent'], description: 'Controls offered for your data.' },
]

const wordCount = text => text.trim() ? text.trim().split(/\s+/).length : 0
const sentenceCount = text => (text.match(/[.!?]+/g) || []).length || 1
const readability = text => {
  const words = wordCount(text); if (!words) return null
  const avg = words / sentenceCount(text)
  return avg < 15 ? { label: 'Easy to scan', score: 82, tone: 'good', note: 'Sentences are generally short.' } : avg < 25 ? { label: 'Moderate complexity', score: 61, tone: 'warn', note: 'Some sentences may need a second read.' } : { label: 'Dense legal language', score: 37, tone: 'risk', note: 'Long sentences can hide important details.' }
}

function analyze(text) {
  const normalized = text.toLowerCase()
  const findings = checks.map(check => {
    const matched = check.terms.filter(term => normalized.includes(term))
    return { ...check, matched, score: Math.min(92, matched.length * 19 + (check.id === 'agency' ? 10 : 0)) }
  })
  const concerns = [
    ['Shares data with advertising or analytics providers', /advertising|analytics|third party/],
    ['Collects precise or approximate location information', /location/],
    ['Includes binding arbitration or class-action waiver language', /arbitration|class action/],
    ['Uses open-ended data retention language', /as long as necessary|business purposes/],
  ].filter(([, pattern]) => pattern.test(normalized)).map(([label]) => label)
  const positive = [
    ['Mentions a way to opt out', /opt out/], ['Mentions access or deletion controls', /delete|access/], ['References consent or choices', /consent|choice/],
  ].filter(([, pattern]) => pattern.test(normalized)).map(([label]) => label)
  const risk = Math.min(98, 20 + concerns.length * 16 + (findings.find(x => x.id === 'sharing').matched.length * 4))
  return { findings, concerns, positive, risk, readability: readability(text) }
}

function App() {
  const [policy, setPolicy] = useState('')
  const [result, setResult] = useState(null)
  const [dragging, setDragging] = useState(false)
  const fileRef = useRef()
  const words = wordCount(policy)
  const handleFile = file => { if (file && file.type.startsWith('text/')) { const reader = new FileReader(); reader.onload = e => setPolicy(e.target.result); reader.readAsText(file) } }
  const submit = () => { if (words >= 12) setResult(analyze(policy)) }
  const riskLabel = useMemo(() => result ? result.risk >= 65 ? 'High caution' : result.risk >= 40 ? 'Review closely' : 'Lower concern' : '', [result])

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

function Results({ result, label }) { return <aside className="results"><div className="result-top"><div><span className="step">02</span><h2>Analysis summary</h2></div><div className={`risk ${result.risk >= 65 ? 'high' : result.risk >= 40 ? 'medium' : 'low'}`}><strong>{result.risk}</strong><span>/100</span><small>{label}</small></div></div><div className="meter"><i style={{width:`${result.risk}%`}}/></div><p className="risk-note">This is a draft signal based on language found in the text. Review the full policy for context.</p><div className="findings">{result.findings.map(item => <article key={item.id}><div><h3>{item.label}</h3><p>{item.matched.length ? `Found: ${item.matched.slice(0,3).join(', ')}` : 'No common signals found'}</p></div><span className={item.matched.length ? 'tag concern' : 'tag'}>{item.matched.length ? `${item.matched.length} signals` : 'Clear'}</span></article>)}</div><div className="readability"><div><h3>Readability</h3><p>{result.readability.note}</p></div><span className={`tag ${result.readability.tone}`}>{result.readability.label}</span></div><div className="takeaways"><h3>Key takeaways</h3>{result.concerns.length ? result.concerns.map(x => <p key={x}><AlertTriangle size={15}/>{x}</p>) : <p><CheckCircle2 size={15}/>No high-risk common phrases were detected.</p>}{result.positive.map(x => <p className="positive" key={x}><CheckCircle2 size={15}/>{x}</p>)}</div></aside> }

createRoot(document.getElementById('root')).render(<App />)
