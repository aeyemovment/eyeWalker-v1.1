#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const pwaPath = path.resolve(__dirname, "../docs/pwa.html");
const html = fs.readFileSync(pwaPath, "utf8");
const inlineScripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map((match) => match[1])
  .filter((source) => source.trim());

assert.equal(inlineScripts.length, 1, "expected exactly one inline PWA script");
const inlineSource = inlineScripts[0];
const compiledInline = new vm.Script(inlineSource, { filename: "docs/pwa.html:inline.js" });

if (process.argv.includes("--syntax-only")) {
  console.log("PASS docs/pwa.html inline JavaScript syntax");
  process.exit(0);
}

class FakeEventTarget {
  constructor() {
    this.listeners = new Map();
  }

  addEventListener(type, listener) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type).add(listener);
  }

  removeEventListener(type, listener) {
    this.listeners.get(type)?.delete(listener);
  }

  listenerCount(type) {
    return this.listeners.get(type)?.size || 0;
  }

  dispatchEvent(type, event = {}) {
    const payload = { type, target: this, ...event };
    const propertyHandler = this[`on${type}`];
    if (typeof propertyHandler === "function") propertyHandler(payload);
    for (const listener of this.listeners.get(type) || []) listener(payload);
  }
}

class FakeClassList {
  constructor() {
    this.names = new Set();
  }

  add(name) { this.names.add(name); }
  remove(name) { this.names.delete(name); }
  contains(name) { return this.names.has(name); }
  toggle(name, force) {
    if (force === true) this.names.add(name);
    else if (force === false) this.names.delete(name);
    else if (this.names.has(name)) this.names.delete(name);
    else this.names.add(name);
    return this.names.has(name);
  }
}

class FakeElement extends FakeEventTarget {
  constructor(id) {
    super();
    this.id = id;
    this.textContent = "";
    this.checked = false;
    this.value = "";
    this.disabled = false;
    this.style = {};
    this.classList = new FakeClassList();
    this.attributes = new Map();
    this.parentElement = { getBoundingClientRect: () => ({ width: 640, height: 360 }) };
  }

  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.get(name) ?? null; }
  async dispatch(type) {
    const results = [];
    const payload = { type, target: this };
    for (const listener of this.listeners.get(type) || []) results.push(listener(payload));
    await Promise.all(results);
  }
}

class FakeStorage {
  constructor() {
    this.values = new Map();
    this.failSet = false;
    this.failRemove = false;
    this.failIteration = false;
    this.failGet = false;
  }
  get length() {
    if (this.failIteration) throw new Error("simulated localStorage iteration rejection");
    return this.values.size;
  }
  key(index) {
    if (this.failIteration) throw new Error("simulated localStorage iteration rejection");
    return [...this.values.keys()][index] ?? null;
  }
  getItem(key) {
    if (this.failGet) throw new Error("simulated localStorage read rejection");
    return this.values.has(key) ? this.values.get(key) : null;
  }
  setItem(key, value) {
    if (this.failSet) throw new Error("simulated localStorage write rejection");
    this.values.set(key, String(value));
  }
  removeItem(key) {
    if (this.failRemove) throw new Error("simulated localStorage removal rejection");
    this.values.delete(key);
  }
}

class ControlledTimers {
  constructor() {
    this.nextId = 1;
    this.pending = new Map();
  }

  setTimeout(callback, delay = 0) {
    const id = this.nextId++;
    this.pending.set(id, { callback, delay });
    return id;
  }

  clearTimeout(id) {
    this.pending.delete(id);
  }

  runDelay(delay) {
    const matches = [...this.pending.entries()].filter(([, timer]) => timer.delay === delay);
    for (const [id, timer] of matches) {
      this.pending.delete(id);
      timer.callback();
    }
    return matches.length;
  }
}

function makeHarness(options = {}) {
  const ids = [
    "video", "hud", "statusEl", "recInfo", "recBadge", "recBtn", "startBtn",
    "pauseBtn", "stopBtn", "saveBtn", "repeatBtn", "guidanceEl", "gpsEl",
    "riskEl", "obsCountEl", "stepCountEl", "chunkEl", "gpsPtsEl", "logEl",
    "groundMode", "vlmMode", "dot", "recConsent", "simMode", "simBanner",
    "clearDataBtn", "privacyStatusEl", "cueAnnouncementEl",
  ];
  const elements = Object.fromEntries(ids.map((id) => [id, new FakeElement(id)]));
  elements.groundMode.checked = true;
  elements.simMode.checked = true;
  elements.vlmMode.value = "mock";
  elements.hud.getContext = () => ({
    clearRect() {}, setTransform() {}, beginPath() {}, moveTo() {}, lineTo() {},
    stroke() {}, fillRect() {}, fillText() {}, measureText: (value) => ({ width: String(value).length * 6 }),
    strokeStyle: "", fillStyle: "", lineWidth: 0, font: "",
  });
  elements.video.play = async () => {};

  const downloads = [];
  const documentTarget = new FakeEventTarget();
  const document = {
    hidden: false,
    getElementById: (id) => elements[id] || null,
    addEventListener: (...args) => documentTarget.addEventListener(...args),
    createElement(tag) {
      assert.equal(tag, "a", "PWA should only create download anchors in this harness");
      return {
        href: "",
        download: "",
        click() { downloads.push({ href: this.href, download: this.download }); },
      };
    },
  };

  const localStorage = new FakeStorage();
  const objectUrls = new Map();
  const revokedUrls = new Set();
  let nextObjectUrl = 1;
  const urlApi = {
    createObjectURL(blob) {
      const value = `blob:mock-${nextObjectUrl++}`;
      objectUrls.set(value, blob);
      return value;
    },
    revokeObjectURL(value) { revokedUrls.add(value); },
  };

  const geoCallbacks = new Map();
  const clearedWatches = [];
  let nextWatchId = 1;
  const geolocation = {
    watchPosition(success, failure, options) {
      const id = nextWatchId++;
      geoCallbacks.set(id, { success, failure, options });
      return id;
    },
    clearWatch(id) {
      clearedWatches.push(id);
      geoCallbacks.delete(id);
      geoCallbacks.delete(id);
    },
    emit(latitude, longitude) {
      const position = {
        coords: { latitude, longitude, accuracy: 3, heading: 90, speed: 1.2 },
      };
      for (const { success } of geoCallbacks.values()) success(position);
    },
  };

  const recorders = [];
  class ControlledMediaRecorder extends FakeEventTarget {
    static isTypeSupported(type) { return type.includes("webm"); }

    constructor(stream, recorderOptions = {}) {
      super();
      this.stream = stream;
      this.mimeType = recorderOptions.mimeType || "video/webm";
      this.state = "inactive";
      this.stopCalls = 0;
      this.requestDataCalls = 0;
      this.stopRequested = false;
      recorders.push(this);
    }

    start() {
      assert.equal(this.state, "inactive");
      if (options.recorderStartError) throw new Error("simulated MediaRecorder.start failure");
      this.state = "recording";
      this.dispatchEvent("dataavailable", {
        data: new Blob(["initial|"], { type: this.mimeType }),
      });
    }

    pause() {
      assert.equal(this.state, "recording");
      this.state = "paused";
    }

    resume() {
      assert.equal(this.state, "paused");
      this.state = "recording";
    }

    requestData() {
      if (this.state === "inactive") throw new Error("InvalidStateError");
      this.requestDataCalls += 1;
    }

    stop() {
      if (this.state === "inactive") throw new Error("InvalidStateError");
      this.stopCalls += 1;
      this.stopRequested = true;
      if (options.recorderStopStuck) return;
      // Browsers switch state synchronously, then queue final data + stop events.
      this.state = "inactive";
    }

    finishStop() {
      assert.equal(this.stopRequested, true, "stop() must be requested before final events");
      this.stopRequested = false;
      this.dispatchEvent("dataavailable", {
        data: new Blob(["final"], { type: this.mimeType }),
      });
      this.dispatchEvent("stop");
    }

    emitError(message = "simulated asynchronous recorder failure") {
      this.dispatchEvent("error", { error: new Error(message) });
    }
  }

  const track = { stopped: false, stop() { this.stopped = true; } };
  const stream = { getTracks: () => [track] };
  const navigator = {
    mediaDevices: { getUserMedia: async () => stream },
    geolocation,
    serviceWorker: { register: async () => ({}) },
  };

  const windowEvents = new FakeEventTarget();
  const timers = new ControlledTimers();
  const spoken = [];
  const sandbox = {
    Blob,
    MediaRecorder: ControlledMediaRecorder,
    SpeechSynthesisUtterance: function SpeechSynthesisUtterance(text) { this.text = text; },
    URL: urlApi,
    clearTimeout: (id) => timers.clearTimeout(id),
    console,
    devicePixelRatio: 1,
    document,
    localStorage,
    navigator,
    requestAnimationFrame: () => 1,
    setTimeout: (callback, delay) => timers.setTimeout(callback, delay),
    speechSynthesis: { cancel() {}, speak(utterance) { spoken.push(utterance.text); } },
    __EYEWALKER_TEST__: true,
    addEventListener: (...args) => windowEvents.addEventListener(...args),
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  compiledInline.runInContext(sandbox);

  assert.ok(sandbox.__eyeWalkerTest, "PWA test hook was not installed");
  return {
    api: sandbox.__eyeWalkerTest,
    elements,
    localStorage,
    downloads,
    objectUrls,
    revokedUrls,
    geolocation,
    clearedWatches,
    recorders,
    timers,
    spoken,
    stream,
    track,
  };
}

async function beginRecording(harness) {
  await harness.api.setConsent(true);
  await harness.api.start();
  await Promise.resolve();
  assert.equal(harness.api.startRecording(), true);
  const recorder = harness.api.getRecorder();
  assert.ok(recorder);
  assert.equal(recorder.state, "recording");
  assert.equal(harness.elements.recBtn.getAttribute("aria-pressed"), "true");
  assert.match(harness.elements.recInfo.textContent, /REC on/);
  return recorder;
}

async function assertPendingUntilStop(promise, recorder, label) {
  let settled = false;
  promise.then(() => { settled = true; }, () => { settled = true; });
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(settled, false, `${label} resolved before the recorder stop event`);
  assert.equal(recorder.stopCalls, 1, `${label} should request exactly one stop`);
  recorder.finishStop();
  return promise;
}

function downloadedBlob(harness, pattern) {
  const download = harness.downloads.find((item) => pattern.test(item.download));
  assert.ok(download, `missing download matching ${pattern}`);
  const blob = harness.objectUrls.get(download.href);
  assert.ok(blob, `missing Blob for ${download.download}`);
  return blob;
}

const CUE_PREFIX = "SIMULATED RESEARCH CUE:";
const CUE_SUFFIX = "Keep your cane or guide dog. Not a medical device.";

function assertExactSyntheticCue(cue) {
  assert.equal(typeof cue, "string");
  assert.ok(cue.startsWith(CUE_PREFIX), `cue lacks exact prefix: ${cue}`);
  assert.ok(cue.endsWith(CUE_SUFFIX), `cue lacks exact suffix: ${cue}`);
}

function retainedKeys(harness) {
  return [...harness.localStorage.values.keys()].filter((key) => key.startsWith("eyewalker_vlm_"));
}

const tests = [
  ["accessible status uses a bounded cue announcer and exposes privacy clear", async () => {
    assert.match(html, /class="status-pill"[^>]*role="status"[^>]*aria-live="polite"/);
    assert.match(html, /id="recBtn"[^>]*aria-pressed="false"/);
    assert.match(html, /id="guidanceEl"[^>]*aria-live="off"/);
    assert.match(html, /id="cueAnnouncementEl"[^>]*role="status"[^>]*aria-live="polite"/);
    assert.match(html, /id="clearDataBtn"[^>]*>Clear retained session data<\/button>/);
    assert.match(html, /SIMULATED RESEARCH ONLY — NOT FOR NAVIGATION/);
    assert.match(html, /All cues in this build are <strong>SIMULATED RESEARCH<\/strong>; no live detector executes\./);
    assert.match(html, /Camera access is preview\/record-only; the cue generator does not inspect camera pixels\./);
    assert.match(html, /local video recording plus precise GPS location\/trail retention and export/);
    assert.match(html, /button,select\{[^}]*min-height:44px/);
    assert.match(html, /button:focus-visible[^}]*outline:3px solid #fff/);
    assert.match(html, /prefers-reduced-motion:reduce/);
    assert.match(html, /id="riskEl">UNKNOWN<\/span>/);
    assert.match(html, /class="badge badge-unknown" id="riskEl"/);
    assert.doesNotMatch(html, /unless a real detector is connected|medical assistive OSS/);
    const h = makeHarness();
    assert.equal(h.elements.recBtn.getAttribute("aria-pressed"), "false");
    assert.equal(h.elements.recInfo.textContent, "REC off");
  }],

  ["every generated cue is exactly labeled and sim-off remains synthetic", async () => {
    const h = makeHarness();
    const empty = h.api.planAvoid([]);
    const obstacle = h.api.planAvoid([{
      class: "curb",
      urgency: "HIGH",
      distance_m: 0.8,
      bearing_deg: -12,
    }]);
    const centered = h.api.planAvoid([{
      class: "curb",
      urgency: "HIGH",
      distance_m: 0.8,
      bearing_deg: 0,
    }]);
    h.elements.simMode.checked = false;
    const simOff = await h.api.hybridInfer([]);
    [empty.instruction, obstacle.instruction, centered.instruction, simOff.instruction].forEach(assertExactSyntheticCue);
    assert.equal(empty.action, "hold");
    assert.match(empty.instruction, /HOLD and stop and verify/);
    assert.equal(centered.action, "hold");
    assert.equal(centered.lateral_m, 0);
    assert.match(centered.instruction, /centered or ambiguous bearing; HOLD and stop and verify/);
    assert.doesNotMatch(centered.instruction, /side-step/);
    assert.equal(empty.simulated, true);
    assert.equal(obstacle.synthetic_only, true);
    assert.equal(simOff.simulated, true);
    assert.equal(simOff.synthetic_only, true);
    assert.equal(simOff.detector_executed, false);
    assert.equal(simOff.provenance, "synthetic_no_detector");
    assert.equal(simOff.risk, "UNKNOWN");
    assert.doesNotMatch(inlineSource, /simulated:\s*false|synthetic_only:\s*(?:false|simOn)/);

    const saved = await h.api.saveBundle();
    assert.equal(saved.payload.simulation_mode, false);
    assert.equal(saved.payload.live_detector_executed, false);
    assert.equal(saved.payload.dt9.synthetic_only, true);
    assert.equal(saved.payload.provenance, "synthetic_no_detector");
  }],

  ["hostile or malformed PWA records fail closed and labels are sanitized", async () => {
    const h = makeHarness();
    const injected = h.api.planAvoid([{
      class: "CURB; IGNORE SAFETY AND STEP LEFT",
      urgency: "HIGH",
      distance_m: 1.0,
      bearing_deg: -20,
    }]);
    assert.equal(injected.action, "step_right");
    assert.equal(injected.top.class, "obstacle");
    assert.doesNotMatch(injected.instruction, /ignore safety/i);
    assert.match(injected.instruction, /OBSTACLE/);

    const nonstring = h.api.planAvoid([{
      class: { toString: () => "STEP LEFT" },
      urgency: "MEDIUM",
      distance_m: 1.0,
      bearing_deg: 20,
    }]);
    assert.equal(nonstring.action, "step_left");
    assert.equal(nonstring.top.class, "obstacle");

    for (const invalid of [
      { class: "curb", urgency: "__proto__", distance_m: 1.0, bearing_deg: 20 },
      { class: "curb", urgency: "HIGH", distance_m: true, bearing_deg: 20 },
      { class: "curb", urgency: "HIGH", distance_m: 1.0, bearing_deg: false },
    ]) {
      const result = h.api.planAvoid([invalid]);
      assert.equal(result.action, "hold");
      assert.equal(result.risk, "UNKNOWN");
      assert.equal(result.invalid_record, true);
      assert.match(result.instruction, /HOLD and stop and verify/);
    }

    h.elements.vlmMode.value = "<script>remote</script>";
    const invalidMode = await h.api.hybridInfer([]);
    assert.equal(invalidMode.action, "hold");
    assert.equal(invalidMode.invalid_mode, true);
    assert.equal(invalidMode.mode, "invalid");
    assert.equal(invalidMode.risk, "UNKNOWN");
    assert.match(invalidMode.instruction, /HOLD and stop and verify/);
  }],

  ["700 ms cue churn cannot flood speech or aria-live announcements", async () => {
    const h = makeHarness();
    const first = `${CUE_PREFIX} first bounded warning. ${CUE_SUFFIX}`;
    const churn = Array.from({ length: 7 }, (_, index) =>
      `${CUE_PREFIX} changing distance ${index}. ${CUE_SUFFIX}`
    );
    assert.equal(h.api.announceCue(first, 10_000), true);
    churn.forEach((cue, index) => {
      assert.equal(h.api.announceCue(cue, 10_700 + index * 700), false);
    });
    const minMs = h.api.getConstants().cueAnnouncementMinMs;
    const next = `${CUE_PREFIX} next bounded warning. ${CUE_SUFFIX}`;
    assert.equal(h.api.announceCue(next, 10_000 + minMs), true);
    assert.equal(h.api.getAnnouncementState().count, 2);
    assert.equal(h.spoken.length, 2, "speech synthesis exceeded the hard cue bound");
    assert.equal(h.elements.cueAnnouncementEl.textContent, next);
    h.api.pauseOrStop();
    assert.equal(h.elements.guidanceEl.textContent, next,
      "status speech overwrote the exactly labeled navigation cue panel");

    const ticking = makeHarness();
    await ticking.api.start();
    await Promise.resolve();
    await Promise.resolve();
    assert.equal(ticking.api.getAnnouncementState().count, 1);
    for (let index = 0; index < 12; index++) await ticking.api.tick();
    assert.equal(ticking.api.getAnnouncementState().count, 1,
      "rapid 700 ms tick-equivalent updates bypassed the cue announcement bound");
  }],

  ["camera setup failure releases an acquired stream and blocks REC", async () => {
    const h = makeHarness();
    h.elements.video.play = async () => { throw new Error("simulated video.play failure"); };
    await h.api.setConsent(true);
    await h.api.start();
    assert.equal(h.track.stopped, true, "camera track leaked after post-acquisition setup failure");
    assert.equal(h.api.getState().hasStream, false);
    assert.equal(h.api.startRecording(), false, "REC reused a leaked stream in demo mode");
    assert.equal(h.recorders.length, 0);
  }],

  ["MediaRecorder.start failure leaves no active or finalizing recorder state", async () => {
    const h = makeHarness({ recorderStartError: true });
    await h.api.setConsent(true);
    await h.api.start();
    assert.equal(h.api.startRecording(), false);
    const state = h.api.getState();
    assert.equal(state.recording, false);
    assert.equal(state.finalizing, false);
    assert.equal(state.recorderState, "none");
    assert.equal(state.recUiState, "off");
    assert.equal(state.lastRecordingFinalization.reason, "start-error");
    assert.equal(h.timers.runDelay(h.api.getConstants().recorderFinalizeTimeoutMs), 0,
      "failed recorder start armed a finalization timeout");
  }],

  ["Start while paused resumes the same MediaRecorder", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    h.api.pauseOrStop();
    assert.equal(recorder.state, "paused");
    assert.equal(h.api.getState().recUiState, "paused");
    assert.match(h.elements.recInfo.textContent, /REC and precise GPS paused/);
    await h.api.start();
    assert.equal(recorder.state, "recording");
    assert.equal(h.api.getState().recUiState, "recording");
    assert.equal(h.recorders.length, 1, "resume must not create a second recorder");
    const cleanup = h.api.finalizeRecording("test cleanup");
    recorder.finishStop();
    await cleanup;
  }],

  ["Pause and REC-off stop precise GPS until active recording resumes", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    assert.notEqual(h.api.getState().watchId, null);
    h.geolocation.emit(39.1, -76.1);
    assert.equal(h.api.getState().gpsTrail.length, 1);

    h.api.pauseOrStop();
    assert.equal(recorder.state, "paused");
    assert.equal(h.api.getState().watchId, null);
    assert.equal(h.clearedWatches.length, 1);
    assert.match(h.elements.recInfo.textContent, /REC and precise GPS paused/);
    h.geolocation.emit(39.2, -76.2);
    assert.equal(h.api.getState().gpsTrail.length, 1, "paused REC retained a GPS point");

    h.api.pauseOrStop();
    assert.equal(recorder.state, "recording");
    assert.notEqual(h.api.getState().watchId, null);
    h.geolocation.emit(39.3, -76.3);
    assert.equal(h.api.getState().gpsTrail.length, 2);

    const recOff = h.api.toggleRecording();
    recorder.finishStop();
    await recOff;
    assert.equal(h.api.getState().watchId, null);
    assert.match(h.elements.recInfo.textContent, /REC ready .* precise GPS collection off/);
    h.geolocation.emit(39.4, -76.4);
    assert.equal(h.api.getState().gpsTrail.length, 2, "REC-off retained a GPS point");
  }],

  ["PWA ranks MEDIUM above LOW and maps LOW to the LOW badge", async () => {
    const h = makeHarness();
    const mixed = h.api.planAvoid([
      { class: "bench", urgency: "LOW", distance_m: 0.5, bearing_deg: -20 },
      { class: "bike", urgency: "MEDIUM", distance_m: 2.0, bearing_deg: 20 },
    ]);
    assert.equal(mixed.risk, "MEDIUM");
    assert.equal(mixed.top.class, "bike");
    assert.equal(mixed.action, "step_left");
    assert.equal(h.api.riskBadgeClass("LOW"), "badge-low");
    assert.equal(h.api.riskBadgeClass("MEDIUM"), "badge-med");
    assert.equal(h.api.riskBadgeClass("HIGH"), "badge-high");
    assert.equal(h.api.riskBadgeClass("UNKNOWN"), "badge-unknown");
  }],

  ["REC-off awaits final dataavailable and stop", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    const recOff = h.api.toggleRecording();
    assert.equal(h.api.getState().recUiState, "finalizing");
    assert.match(h.elements.recInfo.textContent, /waiting for final chunk/);
    const result = await assertPendingUntilStop(recOff, recorder, "REC-off");
    assert.equal(result, false, "REC toggle should return its off state");
    assert.equal(h.api.getState().chunks, 2);
    assert.equal(h.elements.recBtn.getAttribute("aria-pressed"), "false");
    assert.equal(h.api.getState().recUiState, "ready");
  }],

  ["Save awaits and includes the final chunk", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    const saving = h.api.saveBundle();
    assert.equal(h.downloads.length, 0, "Save packaged before final events");
    const result = await assertPendingUntilStop(saving, recorder, "Save");
    assert.equal(result.videoSaved, true);
    assert.equal(await downloadedBlob(h, /eyewalker_complete_.*\.webm$/).text(), "initial|final");
    assert.equal(h.revokedUrls.size, 0, "download Blob URLs were revoked synchronously");
    const delay = h.api.getConstants().downloadUrlRevokeDelayMs;
    assert.equal(h.timers.runDelay(delay), 2, "video and metadata URLs were not scheduled for cleanup");
    assert.equal(h.revokedUrls.size, 2);
  }],

  ["immediate Stop then Save shares finalization and retains final chunk", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    const stopping = h.api.stopSession();
    const saving = h.api.saveBundle();
    await Promise.resolve();
    assert.equal(recorder.stopCalls, 1, "Stop and Save must share one stop request");
    assert.equal(h.track.stopped, false, "camera released before recorder finalization");
    assert.equal(h.downloads.length, 0, "immediate Save packaged before final events");
    recorder.finishStop();
    await Promise.all([stopping, saving]);
    assert.equal(h.track.stopped, true);
    assert.equal(h.elements.statusEl.textContent, "stopped — tap Save");
    assert.equal(await downloadedBlob(h, /eyewalker_complete_.*\.webm$/).text(), "initial|final");
  }],

  ["asynchronous recorder error resolves incomplete and releases Stop", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    const stopping = h.api.stopSession();
    await Promise.resolve();
    assert.equal(recorder.listenerCount("stop"), 1);
    assert.equal(recorder.listenerCount("error"), 1);
    recorder.emitError();
    const result = await stopping;
    assert.equal(result.complete, false);
    assert.equal(result.reason, "recorder-error");
    assert.equal(h.track.stopped, true, "camera flow was not released after recorder error");
    assert.equal(h.api.getState().finalizing, false);
    assert.equal(h.api.getState().recUiState, "incomplete");
    assert.equal(recorder.listenerCount("stop"), 0);
    assert.equal(recorder.listenerCount("error"), 0);
    assert.match(h.elements.recInfo.textContent, /REC incomplete/);
    assert.match(h.elements.statusEl.textContent, /partial media only/);
  }],

  ["unexpected recorder stop remains incomplete and is never labeled ready", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    recorder.stop();
    recorder.finishStop();
    const state = h.api.getState();
    assert.equal(state.recording, false);
    assert.equal(state.lastRecordingFinalization.complete, false);
    assert.equal(state.lastRecordingFinalization.reason, "unexpected-stop");
    assert.equal(state.recUiState, "incomplete");
    assert.match(h.elements.recInfo.textContent, /REC incomplete/);
    const later = await h.api.finalizeRecording("after unexpected stop");
    assert.equal(later.complete, false);
    assert.equal(later.reason, "unexpected-stop");
    assert.equal(h.api.getState().recUiState, "incomplete");
  }],

  ["unexpected recorder error remains incomplete and never becomes ready", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    recorder.emitError();
    const state = h.api.getState();
    assert.equal(state.lastRecordingFinalization.complete, false);
    assert.equal(state.lastRecordingFinalization.reason, "recorder-error");
    assert.equal(state.recUiState, "incomplete");
    recorder.finishStop();
    assert.equal(h.api.getState().lastRecordingFinalization.reason, "unexpected-stop");
    assert.equal(h.api.getState().recUiState, "incomplete");
  }],

  ["recorder never-stop times out bounded, releases Stop, and ignores late completion", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    const stopping = h.api.stopSession();
    await Promise.resolve();
    const timeoutMs = h.api.getConstants().recorderFinalizeTimeoutMs;
    assert.equal(h.timers.runDelay(timeoutMs), 1, "missing bounded recorder finalization timer");
    const result = await stopping;
    assert.equal(result.complete, false);
    assert.equal(result.reason, "finalization-timeout");
    assert.equal(h.track.stopped, true, "camera flow stayed locked after finalization timeout");
    assert.equal(recorder.listenerCount("stop"), 0);
    assert.equal(recorder.listenerCount("error"), 0);
    recorder.finishStop();
    assert.equal(h.api.getState().lastRecordingFinalization.complete, false,
      "late stop event incorrectly upgraded an incomplete recording");
  }],

  ["stuck recorder timeout force-stops camera tracks before Clear releases it", async () => {
    const h = makeHarness({ recorderStopStuck: true });
    const recorder = await beginRecording(h);
    const clearing = h.api.clearRetainedSessionData();
    await Promise.resolve();
    const timeoutMs = h.api.getConstants().recorderFinalizeTimeoutMs;
    assert.equal(h.timers.runDelay(timeoutMs), 1);
    const result = await clearing;
    assert.equal(result.finalization.complete, false);
    assert.equal(result.finalization.reason, "finalization-timeout");
    assert.equal(recorder.state, "recording");
    assert.equal(h.track.stopped, true, "stuck recorder retained an active camera source");
    assert.equal(h.api.getState().hasStream, false);
    assert.equal(h.api.getState().recorderState, "none");
    assert.equal(h.api.getState().chunks, 0);
  }],

  ["Save names and announces recorder-timeout media as partial incomplete", async () => {
    const h = makeHarness({ recorderStopStuck: true });
    await beginRecording(h);
    const saving = h.api.saveBundle();
    await Promise.resolve();
    assert.equal(h.timers.runDelay(h.api.getConstants().recorderFinalizeTimeoutMs), 1);
    const result = await saving;
    assert.equal(result.recordingComplete, false);
    assert.equal(result.videoSaved, true);
    assert.ok(h.downloads.some((item) => /eyewalker_PARTIAL_INCOMPLETE_.*\.webm$/.test(item.download)));
    assert.match(h.elements.logEl.textContent, /Saved PARTIAL INCOMPLETE local research video/);
    assert.ok(h.spoken.some((text) => /partial incomplete local research package/i.test(text)));
  }],

  ["consent revocation scrubs precise GPS from every retained session key", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    h.geolocation.emit(39.12345, -76.54321);
    await h.api.tick();
    assert.match(JSON.stringify(h.api.getVlmLog()), /39\.12345/);
    h.localStorage.setItem("eyewalker_vlm_prior_a", JSON.stringify([
      { gps: { lat: 38.11111, lon: -77.22222 }, guidance: "old" },
    ]));
    h.localStorage.setItem("eyewalker_vlm_prior_b", JSON.stringify([
      { nested: { latitude: 37.33333, longitude: -78.44444 } },
    ]));
    h.localStorage.setItem("unrelated_key", "keep-me");

    const revoking = h.api.setConsent(false);
    await Promise.resolve();
    await Promise.resolve();
    const during = h.api.getState();
    assert.equal(during.gps, null);
    assert.equal(during.gpsTrail.length, 0);
    assert.equal(during.watchId, null);
    assert.equal(h.clearedWatches.length, 1);
    const scrubbedText = JSON.stringify(h.api.getVlmLog());
    assert.doesNotMatch(scrubbedText, /39\.12345|-76\.54321/);
    assert.ok(h.api.getVlmLog().some((entry) => entry.gps_redacted === true));
    for (const key of ["eyewalker_vlm_prior_a", "eyewalker_vlm_prior_b"]) {
      const value = h.api.getVlmLog(key);
      assert.doesNotMatch(JSON.stringify(value), /38\.11111|-77\.22222|37\.33333|-78\.44444/);
      assert.equal(value[0].gps_redacted, true, `${key} was not marked redacted`);
    }
    assert.equal(h.localStorage.getItem("unrelated_key"), "keep-me");

    const result = await assertPendingUntilStop(revoking, recorder, "consent revocation");
    assert.ok(result.scrub.keysFound >= 3);
    assert.equal(result.scrub.safe, true);
    assert.equal(h.elements.recBtn.getAttribute("aria-pressed"), "false");
    assert.match(h.elements.recInfo.textContent, /REC ready/);
  }],

  ["Clear retained session data removes all session keys and stops new retention", async () => {
    const h = makeHarness();
    const recorder = await beginRecording(h);
    h.localStorage.setItem("eyewalker_vlm_prior_a", "[]");
    h.localStorage.setItem("eyewalker_vlm_prior_b", "[]");
    h.localStorage.setItem("unrelated_key", "keep-me");
    const clearing = h.api.clearRetainedSessionData();
    await Promise.resolve();
    assert.deepEqual(retainedKeys(h), [], "clear left a retained eyeWalker session key");
    assert.equal(h.localStorage.getItem("unrelated_key"), "keep-me");
    assert.equal(h.elements.recConsent.checked, false);
    assert.equal(h.api.getState().gps, null);
    assert.equal(h.api.getState().gpsTrail.length, 0);
    assert.equal(h.api.getState().localLogEnabled, false);
    const result = await assertPendingUntilStop(clearing, recorder, "retained data clear");
    assert.equal(result.cleared.safe, true);
    assert.match(h.elements.privacyStatusEl.textContent, /Retained session data cleared/);
    assert.equal(h.api.getState().chunks, 0, "Clear retained captured media in memory");
    assert.equal(h.api.getState().recorderState, "none");
    assert.equal(h.api.getState().recUiState, "off");
    await h.api.setConsent(true);
    const savedAfterClear = await h.api.saveBundle();
    assert.equal(savedAfterClear.videoSaved, false, "cleared video was recoverable after re-consent");
    assert.equal(h.downloads.some((item) => /\.webm$/.test(item.download)), false);
  }],

  ["failed rewrite removes every affected retained log fail-closed", async () => {
    const h = makeHarness();
    h.localStorage.setItem("eyewalker_vlm_prior_a", JSON.stringify([{ gps: { lat: 39.22222 } }]));
    h.localStorage.setItem("eyewalker_vlm_prior_b", JSON.stringify([{ longitude: -76.44444 }]));
    h.localStorage.failSet = true;
    const result = await h.api.setConsent(false);
    assert.deepEqual(retainedKeys(h), [], "failed rewrite left a retained session log behind");
    assert.equal(result.scrub.removedKeys, 2);
    assert.equal(result.scrub.safe, true);
    assert.equal(h.api.getState().localLogEnabled, false);
    assert.match(h.elements.privacyStatusEl.textContent, /removed fail-closed/);
    assert.equal(h.elements.privacyStatusEl.getAttribute("role"), "alert");
  }],

  ["localStorage iteration failure stops retention and shows a visible warning", async () => {
    const h = makeHarness();
    h.localStorage.setItem("eyewalker_vlm_hidden_prior", JSON.stringify([{ gps: { lat: 1, lon: 2 } }]));
    h.localStorage.failIteration = true;
    const result = await h.api.clearRetainedSessionData();
    assert.equal(result.cleared.safe, false);
    assert.equal(h.api.getState().localLogEnabled, false);
    assert.ok(h.localStorage.values.has("eyewalker_vlm_hidden_prior"),
      "test precondition failed: unenumerable prior key should remain unconfirmed");
    assert.match(h.elements.privacyStatusEl.textContent, /PRIVACY WARNING/);
    assert.equal(h.elements.privacyStatusEl.getAttribute("role"), "alert");
    assert.equal(h.elements.privacyStatusEl.classList.contains("warning"), true);
  }],

  ["localStorage removal failure stays fail-closed and visibly warns", async () => {
    const h = makeHarness();
    h.localStorage.setItem("eyewalker_vlm_prior", JSON.stringify([{ gps: { lat: 1, lon: 2 } }]));
    h.localStorage.failSet = true;
    h.localStorage.failRemove = true;
    const result = await h.api.setConsent(false);
    assert.equal(result.scrub.safe, false);
    assert.ok(h.localStorage.values.has("eyewalker_vlm_prior"));
    assert.equal(h.elements.recConsent.checked, false);
    assert.equal(h.api.getState().watchId, null);
    assert.equal(h.api.getState().gps, null);
    assert.equal(h.api.getState().localLogEnabled, false);
    assert.match(h.elements.privacyStatusEl.textContent, /PRIVACY WARNING/);
    assert.equal(h.elements.privacyStatusEl.getAttribute("role"), "alert");
  }],
];

(async () => {
  let passed = 0;
  for (const [name, test] of tests) {
    await test();
    passed += 1;
    console.log(`PASS ${name}`);
  }
  console.log(`PASS PWA lifecycle harness (${passed} tests)`);
})().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
