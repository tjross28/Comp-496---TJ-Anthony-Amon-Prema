import React, { useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ArrowRight, CheckCircle2, FileText, Info, LockKeyhole, Sparkles, Upload, X } from 'lucide-react'
import './styles.css'

const MIN_WORDS = 12
const wordCount = text => text.trim() ? text.trim().split(/\s+/).length : 0

function App() {
  const [policy, setPolicy] = useState('')
  const [result, setResult] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef(null)
  const words = wordCount(policy)

  const updatePolicy = value => {
    setPolicy(value)
    setResult(null)
    setError('')
  }

  const handleFile = file => {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.txt') && file.type !== 'text/plain') {
      setError('Please choose a plain-text .txt file.')
      return
    }
    const reader = new FileReader()
    reader.onload = event => updatePolicy(String(event.target.result || ''))
    reader.onerror = () => setError('The file could not be read. Try opening it and pasting the text instead.')
    reader.readAsText(file)
  }

  const loadSample = async () => {
    try {
      const response = await fetch('/sample_privacy_policy.txt')
      if (!response.ok) throw new Error('The sample policy could not be loaded.')
      updatePolicy(await response.text())
    } catch (requestError) {
      setError(requestError.message || 'The sample policy could not be loaded.')
    }
  }

  const submit = async () => {
    if (words < MIN_WORDS || loading) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const response = await fetch('/api/v1/analyses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: policy }),
      })
      const body = await response.json()
      if (!response.ok) throw new Error(body.error?.message || 'The summary could not be generated.')
      setResult(body)
    } catch (requestError) {
      setError(requestError.message || 'The summary could not be generated.')
    } finally {
      setLoading(false)
    }
  }

  const clear = () => updatePolicy('')

  return <main>
    <nav>
      <a className="brand" href="#top"><span className="brand-mark"><Sparkles size={18}/></span>ClearPolicy</a>
      <div className="nav-links"><a href="#how">How it works</a><a href="#privacy">Privacy</a></div>
      <a className="text-button" href="#about">About this project</a>
    </nav>

    <section className="hero" id="top">
      <div className="eyebrow"><LockKeyhole size={14}/> Privacy policies, in plain language</div>
      <h1>Understand what<br/><em>the policy says.</em></h1>
      <p>Turn a long privacy policy into a clear summary, useful details, and questions you may want to ask.</p>
      <div className="hero-note"><CheckCircle2 size={16}/> The summary is grounded in the text you provide.</div>
    </section>

    <section className="workspace" aria-label="Privacy policy summary">
      <div className="input-card">
        <div className="card-heading">
          <div><span className="step">01</span><h2>Add a privacy policy</h2><p>Paste the policy text or upload a plain-text file.</p></div>
          {policy && <button className="clear" onClick={clear}><X size={15}/> Clear</button>}
        </div>
        <textarea value={policy} onChange={event => updatePolicy(event.target.value)} placeholder="Paste privacy policy text here..." aria-label="Privacy policy text" />
        <div
          className="dropzone"
          onClick={() => fileRef.current?.click()}
          onDragOver={event => { event.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={event => { event.preventDefault(); setDragging(false); handleFile(event.dataTransfer.files[0]) }}
          data-dragging={dragging}
        >
          <Upload size={18}/><span>Drop a .txt file here or <b>browse files</b></span>
          <input ref={fileRef} hidden type="file" accept=".txt,text/plain" onChange={event => handleFile(event.target.files[0])}/>
        </div>
        <div className="input-footer">
          <span>{words ? words.toLocaleString() + ' words' : 'At least ' + MIN_WORDS + ' words'}</span>
          <button className="sample" onClick={loadSample}>Try sample policy</button>
          <button className="analyze" disabled={words < MIN_WORDS || loading} onClick={submit}>
            {loading ? 'Writing summary…' : 'Create summary'} <ArrowRight size={17}/>
          </button>
        </div>
        {error && <p className="form-error" role="alert">{error}</p>}
      </div>

      {result
        ? <AnalysisResults result={result}/>
        : <aside className={'preview' + (loading ? ' preview-loading' : '')} aria-live="polite">
            <div className="preview-icon">{loading ? <Sparkles size={23}/> : <FileText size={23}/>}</div>
            <h3>{loading ? 'Reading the policy…' : 'Your summary will appear here'}</h3>
            <p>{loading ? 'The AI is organizing the main details into clear language.' : 'A focused overview will help you find the details that matter to you.'}</p>
            <div className="preview-list"><span>Plain-language overview</span><span>Important policy details</span><span>Questions to consider</span></div>
          </aside>}
    </section>

    <section className="how" id="how">
      <div><span className="eyebrow"><Info size={14}/> A reading aid for everyday decisions</span><h2>Make dense policy language easier to follow.</h2></div>
      <div className="how-cards">
        <article><b>01</b><h3>Paste</h3><p>Add the policy text or upload a plain-text file.</p></article>
        <article><b>02</b><h3>Read</h3><p>Get a straightforward summary with relevant quotes.</p></article>
        <article><b>03</b><h3>Review</h3><p>Use the questions to decide what you want to look into further.</p></article>
      </div>
    </section>

    <footer id="privacy">
      <div id="about"><span>ClearPolicy <small>Prototype</small></span><p>Educational reading aid, not legal advice.</p></div>
      <p>Policy text is sent to OpenAI for analysis. The project backend does not save submitted policy text.</p>
    </footer>
  </main>
}

function EvidenceSection({ title, items, emptyMessage }) {
  if (!items?.length && !emptyMessage) return null
  return <section className="summary-section">
    <h3>{title}</h3>
    {items?.length
      ? <div className="evidence-list">{items.map((item, index) =>
          <article className="evidence-item" key={item.evidence_excerpt + index}>
            <p>{item.explanation}</p>
            <blockquote>“{item.evidence_excerpt}”</blockquote>
          </article>)}</div>
      : <p className="empty-note">{emptyMessage}</p>}
  </section>
}

function AnalysisResults({ result }) {
  return <aside className="results" aria-live="polite">
    <div className="result-top">
      <div><span className="step">02</span><h2>Plain-language summary</h2></div>
      <span className="model-badge"><Sparkles size={13}/>{result.model}</span>
    </div>
    <p className="summary-copy">{result.summary}</p>
    <EvidenceSection title="Important details" items={result.key_points} emptyMessage="The policy text did not provide clear details to highlight."/>
    <EvidenceSection title="Wording to review" items={result.things_to_review} emptyMessage="No specific wording was flagged for closer review."/>
    {result.reader_questions?.length > 0 && <section className="summary-section questions">
      <h3>Questions you may want to ask</h3>
      <ul>{result.reader_questions.map((question, index) => <li key={question + index}>{question}</li>)}</ul>
    </section>}
    <p className="disclaimer">{result.disclaimer}</p>
  </aside>
}

createRoot(document.getElementById('root')).render(<App />)
