import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "C:\\Users\\taylo\\Desktop\\Comp-496---TJ-Anthony-Amon-Prema";
const skillDir = "C:\\Users\\taylo\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.1007.11041\\skills\\presentations";
const tmpDir = path.join(workspaceDir, "tmp", "presentation-build");
const outputDir = path.join(workspaceDir, "output", "presentation");
const draftPath = path.join(tmpDir, "clearpolicy-presentation-draft.pptx");
const finalPath = path.join(outputDir, "ClearPolicy_Project_Presentation.pptx");
const scriptPath = path.join(outputDir, "ClearPolicy_Presentation_Script.md");

const { finalizePresentation, resolvePresentationFont } = await import(
  pathToFileURL(path.join(skillDir, "container_tools", "artifact_tool_utils.mjs")).href
);
const font = resolvePresentationFont();

const C = {
  ink: "#16333C",
  muted: "#52666B",
  paper: "#F7F5EF",
  white: "#FFFFFF",
  teal: "#087F72",
  tealPale: "#E1EFE9",
  grayPale: "#E9ECE6",
  coral: "#C96F50",
  mint: "#B6E1D2",
  cream: "#E9E5D8",
};

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function text(slide, name, x, y, w, h, value, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: font,
    fontSize: options.size ?? 24,
    color: options.color ?? C.ink,
    bold: options.bold ?? false,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    wrap: "wrap",
    autoFit: "none",
    insets: 0,
  };
  return shape;
}

function block(slide, name, x, y, w, h, fill) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: "none", width: 0 },
  });
}

function addSlide(title, bg = C.paper) {
  const slide = presentation.slides.add();
  slide.background.fill = bg;
  if (title) text(slide, "slide-title", 72, 54, 1136, 58, title, { size: 44, bold: true });
  return slide;
}

const script = [
  {
    title: "Opening",
    speaker: "Anthony",
    time: "0:20",
    action: "Introduce the three presenters and the purpose of the project.",
    words: "Hi, we’re TJ, Anthony, and Amon. We built ClearPolicy, a class prototype that helps readers find privacy policy language worth reviewing. Amon will show how the app handles a policy, I’ll explain the rule engine, and TJ will cover the clause tagger and run the live demo.",
  },
  {
    title: "Analysis flow",
    speaker: "Amon",
    time: "0:40",
    action: "Point to the interface, API, and the two analysis paths.",
    words: "A reader can paste policy text or load the sample. The React interface splits the text into clauses and sends them to our Flask API. The API runs two separate analyses: the versioned rules engine returns findings and the weighted Trust Score, while the learned classifier suggests topics for clauses. The interface brings those results together so a reader can compare them with the policy wording. Submitted text is processed in memory and is not saved by the service.",
  },
  {
    title: "Rules and Trust Score",
    speaker: "Anthony",
    time: "0:45",
    action: "Walk through the category weights and explain what one rule finding contains.",
    words: "Our rule engine uses versioned phrase rules and returns evidence with each finding: the matched wording, a plain-language explanation, and a suggested next step. The Trust Score weights data sharing at 25 percent, readability at 20, data collection at 20, legal language at 20, and user agency at 15. If the policy text does not provide enough evidence for a category, the app marks it as needing evidence and excludes it from the normalized score rather than treating it as favorable. The score summarizes transparency signals in the supplied text; it is not a legal compliance result.",
  },
  {
    title: "OPP-115 clause tagger",
    speaker: "TJ",
    time: "0:45",
    action: "Explain the training set, policy-level holdout, and baseline results.",
    words: "The clause tagger is a multi-label Naive Bayes model trained on consolidated OPP-115 annotations: 3,790 segments from 115 policies. We held out whole policies, using 92 for training and 23 for evaluation, which gave us 862 held-out segments. On that baseline, micro F1 was 0.7119, macro F1 was 0.6150, and exact label-set match was 0.3805. The final model artifact was then fit on all 115 policies. These topic tags are experimental, their scores are not calibrated probabilities, and they do not affect the Trust Score. The corpus is historical and limited to English website policies; this artifact is for non-commercial academic use under the OPP-115 terms.",
  },
  {
    title: "Live demo",
    speaker: "TJ",
    time: "2:30",
    action: "Take browser control. Load the fictional sample, analyze it, then trace rule findings and any displayed clause tag back to the source text.",
    words: "I’ll run the sample policy through the app. It is fictional and was written for this classroom demonstration, not taken from a real company.",
    demo: [
      ["Load", "Select Try sample policy. Briefly show the input text."],
      ["Analyze", "Select Analyze policy and wait for the results."],
      ["Trace", "Show the score and category coverage. Point to the advertising-sharing and open-ended-retention findings, then compare each with its source sentence. Note the access and deletion language. If a clause tag appears, read its topic and check the original clause."],
    ],
    extra: "The rules help me find language to review. A topic tag is only a model suggestion, and a missing tag does not mean a clause is unimportant. I’ll use the original policy text to interpret every signal. The app does not tell us whether the policy complies with a law.",
  },
  {
    title: "Project workstreams and close",
    speaker: "Anthony",
    time: "0:20",
    action: "Recap the three project workstreams and thank the audience.",
    words: "Today, we’ve shown three connected areas: TJ’s clause model and demo, Amon’s API and interface integration, and my rule engine and scoring. Together, they make policy language easier to inspect while keeping evidence visible. This is an educational aid, not legal advice or proof of compliance. Thank you.",
  },
];

// Slide 1: cover
{
  const slide = addSlide(null, C.ink);
  text(slide, "course", 80, 64, 600, 32, "COMP 496  ·  FALL 2026", { size: 19, bold: true, color: C.mint });
  text(slide, "product-name", 80, 170, 950, 96, "ClearPolicy", { size: 76, bold: true, color: C.white });
  text(slide, "presentation-subject", 84, 274, 900, 55, "Privacy Policy Analyzer", { size: 34, color: C.mint });
  text(slide, "cover-summary", 84, 374, 780, 76, "A classroom prototype for finding policy language worth reviewing.", { size: 27, color: C.white });
  text(slide, "presenters", 84, 608, 900, 38, "TJ  ·  Anthony  ·  Amon", { size: 23, color: C.mint });
}

// Slide 2: architecture and Amon's interface/API workstream
{
  const slide = addSlide("Analysis flow");
  text(slide, "flow-subtitle", 74, 120, 1110, 54, "The interface packages policy text into clauses before the API runs both analyzers.", { size: 23, color: C.muted });
  const nodes = [
    { x: 72, label: "POLICY TEXT", body: "Paste text or load the sample", fill: C.tealPale, fg: C.ink },
    { x: 437, label: "REACT INTERFACE", body: "Splits text into clauses", fill: C.grayPale, fg: C.ink },
    { x: 802, label: "FLASK API", body: "POST /api/v1/analyses", fill: C.teal, fg: C.white },
  ];
  for (const [index, node] of nodes.entries()) {
    block(slide, `flow-node-${index + 1}`, node.x, 215, 282, 124, node.fill);
    text(slide, `flow-label-${index + 1}`, node.x + 20, 235, 244, 31, node.label, { size: 20, bold: true, color: node.fg });
    text(slide, `flow-body-${index + 1}`, node.x + 20, 278, 244, 45, node.body, { size: 21, color: node.fg });
  }
  text(slide, "flow-arrow-one", 365, 250, 54, 48, "→", { size: 40, bold: true, color: C.coral, align: "center" });
  text(slide, "flow-arrow-two", 730, 250, 54, 48, "→", { size: 40, bold: true, color: C.coral, align: "center" });
  text(slide, "rules-heading", 75, 402, 520, 37, "VERSIONED RULE ENGINE", { size: 22, bold: true, color: C.teal });
  text(slide, "rules-body", 75, 452, 520, 111, "Evidence-backed findings, category assessments, and the weighted Trust Score.", { size: 24 });
  text(slide, "model-heading", 660, 402, 520, 37, "LEARNED CLAUSE TAGGER", { size: 22, bold: true, color: C.coral });
  text(slide, "model-body", 660, 452, 520, 111, "Experimental topic suggestions returned separately from rule findings and scoring.", { size: 24 });
  text(slide, "privacy-note", 75, 620, 1100, 42, "The API returns both paths to the interface. Submitted policy text is processed in memory, not saved.", { size: 20, color: C.muted });
}

// Slide 3: rule engine and weighted score
{
  const slide = addSlide("Rules and the Trust Score");
  text(slide, "rules-subtitle", 74, 120, 1110, 43, "Anthony’s workstream: versioned rules, evidence-backed findings, and weighted scoring.", { size: 22, color: C.muted });
  const weights = [
    ["25%", "Data sharing"],
    ["20%", "Readability"],
    ["20%", "Data collection"],
    ["20%", "Legal language"],
    ["15%", "User agency"],
  ];
  weights.forEach(([weight, category], index) => {
    const y = 202 + index * 74;
    text(slide, `weight-${index}`, 78, y, 112, 44, weight, { size: 34, bold: true, color: C.teal });
    text(slide, `category-${index}`, 205, y + 5, 400, 42, category, { size: 26 });
  });
  text(slide, "finding-heading", 694, 211, 470, 42, "Each finding includes", { size: 30, bold: true });
  text(slide, "finding-details", 696, 273, 462, 161, "Matched policy wording\nPlain-language explanation\nSuggested next step\nSelected rules link to GDPR and CCPA/CPRA references.", { size: 22 });
  text(slide, "coverage-heading", 696, 461, 462, 40, "Coverage stays visible", { size: 24, bold: true, color: C.coral });
  text(slide, "coverage-body", 696, 511, 468, 76, "Insufficient text is marked “Needs evidence” and excluded from the normalized score.", { size: 22 });
  text(slide, "score-meaning", 78, 610, 1100, 40, "A higher score means stronger transparency and user-protective signals in the text; it is not a legal compliance result.", { size: 19, color: C.muted });
}

// Slide 4: model method and evaluation
{
  const slide = addSlide("OPP-115 clause tagger");
  text(slide, "model-subtitle", 74, 120, 1110, 43, "TJ’s workstream: multi-label topic suggestions attached to policy clauses.", { size: 22, color: C.muted });
  text(slide, "model-method", 76, 186, 1120, 38, "Multinomial Naive Bayes  ·  binary word and adjacent-word-pair features", { size: 22, bold: true, color: C.teal });
  text(slide, "data-count", 78, 257, 1120, 48, "115 policies     ·     3,790 labeled segments     ·     92 train / 23 holdout policies", { size: 25 });
  text(slide, "holdout-detail", 78, 310, 1120, 35, "The held-out evaluation used 862 segments from policies the model had not seen.", { size: 20, color: C.muted });
  const metrics = [
    { x: 78, value: "0.7119", label: "micro F1" },
    { x: 444, value: "0.6150", label: "macro F1" },
    { x: 810, value: "0.3805", label: "exact label-set match" },
  ];
  for (const [index, metric] of metrics.entries()) {
    text(slide, `metric-value-${index}`, metric.x, 390, 330, 66, metric.value, { size: 52, bold: true, color: C.ink });
    text(slide, `metric-label-${index}`, metric.x + 2, 461, 330, 36, metric.label, { size: 22, color: C.teal });
  }
  text(slide, "model-limitations", 78, 548, 1125, 97, "The released model was fit on all 115 policies after evaluation. OPP-115 is a small, historical English website-policy corpus; tag scores are not calibrated probabilities, and the artifact is for non-commercial academic use under the corpus terms.", { size: 20, color: C.muted });
}

// Slide 5: live browser demo, led by TJ
{
  const slide = addSlide("Live demo");
  text(slide, "demo-speaker", 76, 120, 300, 34, "TJ  ·  ABOUT 2:30", { size: 20, bold: true, color: C.teal });
  const steps = [
    ["01", "Load the sample", "Select Try sample policy."],
    ["02", "Run the analysis", "Show the Trust Score and category coverage."],
    ["03", "Trace the signals", "Compare a finding and any visible topic tag with the source wording."],
  ];
  steps.forEach(([num, heading, description], index) => {
    const y = 210 + index * 117;
    text(slide, `demo-number-${index}`, 80, y, 78, 58, num, { size: 34, bold: true, color: C.coral });
    text(slide, `demo-heading-${index}`, 174, y + 1, 445, 40, heading, { size: 27, bold: true });
    text(slide, `demo-description-${index}`, 174, y + 47, 445, 57, description, { size: 20, color: C.muted });
  });
  block(slide, "sample-excerpt-background", 682, 218, 526, 324, C.tealPale);
  text(slide, "sample-label", 710, 246, 465, 30, "FICTIONAL CLASSROOM POLICY", { size: 18, bold: true, color: C.teal });
  text(slide, "sample-excerpt-sharing", 710, 302, 456, 77, "“We may share personal information with advertising partners...”", { size: 23, bold: true });
  text(slide, "sample-excerpt-retention", 710, 410, 456, 80, "“We retain information for as long as necessary for business purposes.”", { size: 22 });
  text(slide, "demo-disclaimer", 78, 608, 1125, 44, "The sample is fictional. Use the source text to interpret every signal; the app does not determine legal compliance.", { size: 19, color: C.muted });
}

// Slide 6: roles and close
{
  const slide = addSlide("Project workstreams");
  text(slide, "workstream-subtitle", 74, 120, 1120, 43, "This overview highlights three connected areas of work.", { size: 22, color: C.muted });
  const people = [
    { x: 78, name: "TJ", area: "CLAUSE MODEL + DEMO", body: "Built the OPP-115 topic tagger and leads the live browser demonstration." },
    { x: 456, name: "Anthony", area: "RULES + SCORING", body: "Owns the versioned policy rules, evaluator, and evidence-backed Trust Score." },
    { x: 834, name: "Amon", area: "API + INTERFACE", body: "Owns the API/UI integration and how analysis results appear in the app." },
  ];
  for (const [index, person] of people.entries()) {
    text(slide, `person-name-${index}`, person.x, 236, 335, 56, person.name, { size: 37, bold: true });
    text(slide, `person-area-${index}`, person.x, 310, 335, 31, person.area, { size: 17, bold: true, color: index === 1 ? C.coral : C.teal });
    text(slide, `person-body-${index}`, person.x, 363, 325, 148, person.body, { size: 23 });
  }
  text(slide, "project-takeaway", 78, 566, 1110, 68, "Educational review signals only. The prototype is not legal advice or proof of compliance.", { size: 25, bold: true, color: C.ink });
}

const notesText = (section) => {
  const parts = [`${section.speaker} · ${section.time}`, `ACTION: ${section.action}`, `${section.speaker}: “${section.words}”`];
  if (section.demo) {
    parts.push("DEMO ACTIONS:");
    section.demo.forEach(([label, instruction]) => parts.push(`${label}: ${instruction}`));
    parts.push(`TJ: “${section.extra}”`);
  }
  return parts.join("\n\n");
};
presentation.slides.items.forEach((slide, index) => {
  slide.speakerNotes.text = notesText(script[index]);
  slide.speakerNotes.setVisible(true);
});

function scriptMarkdown() {
  const lines = [
    "# ClearPolicy presentation script",
    "",
    "**Estimated run time:** about 5 minutes 30 seconds, including a 2 minute 30 second live demo.",
    "",
    "## Before presenting",
    "",
    "1. Start the backend in one terminal: `.\\.venv\\Scripts\\python.exe backend\\app.py`. If dependencies are not installed, follow the one-time Windows setup in the project README.",
    "2. Start the interface in a second terminal: `pnpm dev`.",
    "3. Open the local URL printed by Vite and leave the policy field blank. Keep the browser with TJ for the demo.",
    "4. Use the fictional sample policy included in the project.",
    "",
    "## Slide-by-slide script",
    "",
  ];
  for (const [index, section] of script.entries()) {
    lines.push(`### Slide ${index + 1}: ${section.title} — ${section.speaker} (${section.time})`, "");
    lines.push(`**Cue:** ${section.action}`, "");
    lines.push(`**${section.speaker}:** “${section.words}”`, "");
    if (section.demo) {
      lines.push("**Browser actions:**", "");
      for (const [label, instruction] of section.demo) lines.push(`- **${label}:** ${instruction}`);
      lines.push("", `**TJ:** “${section.extra}”`, "");
    }
  }
  lines.push("## Timing", "", "Opening and project explanation: about 2 minutes 50 seconds. Live demo: about 2 minutes 30 seconds. Closing and transitions bring the total to roughly 5 minutes 30 seconds.", "");
  return lines.join("\n");
}

await fs.mkdir(tmpDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(scriptPath, scriptMarkdown(), "utf8");

for (const [index, slide] of presentation.slides.items.entries()) {
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  const previewPath = path.join(tmpDir, `slide-${String(index + 1).padStart(2, "0")}.png`);
  await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
}
const montage = await presentation.export({ format: "webp", montage: true });
await fs.writeFile(path.join(tmpDir, "deck-montage.webp"), new Uint8Array(await montage.arrayBuffer()));

const draft = await PresentationFile.exportPptx(presentation);
await draft.save(draftPath);

const validation = await finalizePresentation({
  workspaceDir,
  candidatePath: draftPath,
  finalPath,
  pythonExecutable: "C:\\Users\\taylo\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe",
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
  explicitTotalSlideCount: 6,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(tmpDir, "validation-report-v3.json"),
});

console.log(JSON.stringify({ font, finalPath, scriptPath, validation }, null, 2));
