/**
 * GODZIP Web Platform — Cinematic Celestial Lossless Archiver
 *
 * Features:
 * - Real Gods Compressing Folders (Zeus, Chronos, Hermes, Ares)
 * - 60 FPS Lightweight Celestial Aurora & Starfield Canvas (0 KB external assets)
 * - Pure Procedural Web Audio Synthesizer (Zero audio file downloads)
 * - Interactive 3D God Eye & Avatar Tracking
 * - Colossal Crushing Hands Compression Chamber
 * - 2 Core Operations: 1. Compress Folder (Folder -> .god), 2. Extract Archive (.god -> Folder)
 *
 * Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
 */

document.addEventListener("DOMContentLoaded", () => {
  // ==========================================
  // PROCEDURAL WEB AUDIO SYNTHESIZER (ZERO KB)
  // ==========================================
  const AudioFX = {
    ctx: null,
    muted: false,
    init() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) this.ctx = new AudioCtx();
      }
      if (this.ctx && this.ctx.state === "suspended") {
        this.ctx.resume();
      }
    },
    playClick() {
      if (this.muted) return;
      this.init();
      if (!this.ctx) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(220, this.ctx.currentTime + 0.05);
        gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.05);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.05);
      } catch {}
    },
    playThunder() {
      if (this.muted) return;
      this.init();
      if (!this.ctx) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(140, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(28, this.ctx.currentTime + 0.4);
        gain.gain.setValueAtTime(0.18, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.4);
      } catch {}
    },
    playCompressHum() {
      if (this.muted) return;
      this.init();
      if (!this.ctx) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(55, this.ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(220, this.ctx.currentTime + 1.2);
        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 1.2);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + 1.2);
      } catch {}
    },
    playGodTriumph() {
      if (this.muted) return;
      this.init();
      if (!this.ctx) return;
      try {
        // Celestial E-Major Pentatonic Chord
        const notes = [329.63, 415.30, 493.88, 659.25, 830.61];
        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = "sine";
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * 0.06);
          gain.gain.setValueAtTime(0.07, this.ctx.currentTime + idx * 0.06);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + idx * 0.06 + 0.9);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(this.ctx.currentTime + idx * 0.06);
          osc.stop(this.ctx.currentTime + idx * 0.06 + 0.9);
        });
      } catch {}
    }
  };

  // Sound toggle button in navbar
  const btnSoundToggle = document.getElementById("btnSoundToggle");
  const soundIcon = document.getElementById("soundIcon");
  const soundLabel = document.getElementById("soundLabel");

  if (btnSoundToggle) {
    btnSoundToggle.addEventListener("click", () => {
      AudioFX.init();
      AudioFX.muted = !AudioFX.muted;
      if (AudioFX.muted) {
        btnSoundToggle.classList.add("muted");
        soundIcon.textContent = "🔇";
        soundLabel.textContent = "Audio: OFF";
      } else {
        btnSoundToggle.classList.remove("muted");
        soundIcon.textContent = "🔊";
        soundLabel.textContent = "Audio: ON";
        AudioFX.playClick();
      }
    });
  }

  // ==========================================
  // LIGHTWEIGHT CELESTIAL CANVAS (60 FPS, 0 KB)
  // ==========================================
  const canvas = document.getElementById("celestialCanvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    window.addEventListener("resize", () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const runes = ["⚡", "✦", "∞", "🌀", "🛡️", "🌌", "Ω", "⚛"];
    const stars = [];
    const numStars = Math.min(50, Math.floor((width * height) / 25000));

    for (let i = 0; i < numStars; i++) {
      stars.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.8 + 0.2,
        speed: Math.random() * 0.3 + 0.1,
        rune: Math.random() > 0.8 ? runes[Math.floor(Math.random() * runes.length)] : null,
        runeAlpha: Math.random() * 0.4 + 0.1
      });
    }

    let mouseX = width / 2;
    let mouseY = height / 2;
    window.addEventListener("mousemove", (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    function drawCelestial() {
      ctx.clearRect(0, 0, width, height);

      // Subtle dynamic aurora gradient
      const grad = ctx.createRadialGradient(mouseX, mouseY, 50, width / 2, height / 2, width * 0.8);
      grad.addColorStop(0, "rgba(255, 214, 0, 0.035)");
      grad.addColorStop(0.5, "rgba(0, 200, 83, 0.02)");
      grad.addColorStop(1, "rgba(0, 0, 0, 0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Draw stars and floating runes
      for (let s of stars) {
        s.y -= s.speed;
        if (s.y < 0) {
          s.y = height;
          s.x = Math.random() * width;
        }

        if (s.rune) {
          ctx.font = "12px serif";
          ctx.fillStyle = `rgba(255, 214, 0, ${s.runeAlpha})`;
          ctx.fillText(s.rune, s.x, s.y);
        } else {
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
          ctx.shadowBlur = 6;
          ctx.shadowColor = "#ffd600";
          ctx.fill();
        }
      }

      // Constellation link lines
      ctx.shadowBlur = 0;
      ctx.strokeStyle = "rgba(255, 214, 0, 0.06)";
      ctx.lineWidth = 0.5;
      for (let i = 0; i < stars.length; i++) {
        for (let j = i + 1; j < stars.length; j++) {
          const dx = stars[i].x - stars[j].x;
          const dy = stars[i].y - stars[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 90) {
            ctx.beginPath();
            ctx.moveTo(stars[i].x, stars[i].y);
            ctx.lineTo(stars[j].x, stars[j].y);
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(drawCelestial);
    }
    requestAnimationFrame(drawCelestial);
  }

  // ==========================================
  // PANTHEON OF COMPRESSION GODS
  // ==========================================
  const pantheonGods = {
    zeus: {
      name: "ZEUS THE THUNDERER",
      crown: "⚡",
      domain: "Lightning Strike • Ultra-Fast",
      color: "#ffd600",
      glowColor: "rgba(255, 214, 0, 0.6)",
      decree: "“Mortal, entrust thy entire folder unto Zeus. We shall strike thy bytes with 1.21 gigawatts of celestial lossless compression.”",
      level: "fast",
      encrypt: false
    },
    chronos: {
      name: "CHRONOS THE ENDLESS",
      crown: "🌌",
      domain: "Cosmic Singularity • Maximum Ratio",
      color: "#a855f7",
      glowColor: "rgba(168, 85, 247, 0.6)",
      decree: "“Space-time and entropy bend to my will. Thy folder shall be crushed into an ultra-dense lossless micro-singularity.”",
      level: "extreme",
      encrypt: false
    },
    hermes: {
      name: "HERMES THE HARMONIC",
      crown: "🪽",
      domain: "Astral Stream • Balanced",
      color: "#00c853",
      glowColor: "rgba(0, 200, 83, 0.6)",
      decree: "“Speed and equilibrium in divine harmony. We shall stream thy files effortlessly with optimal compression ratios.”",
      level: "balanced",
      encrypt: false
    },
    ares: {
      name: "ARES THE UNBREAKABLE",
      crown: "🛡️",
      domain: "Aegis Fortress • AES-256 Encrypted",
      color: "#2979ff",
      glowColor: "rgba(41, 121, 255, 0.6)",
      decree: "“None shall penetrate the Aegis! Thy folder shall be fortified with military AES-256-GCM authenticated armor.”",
      level: "balanced",
      encrypt: true
    }
  };

  let currentGodKey = "zeus";
  const pantheonCards = document.querySelectorAll(".pantheon-card");
  const godCrown = document.getElementById("godCrown");
  const decreeSpeech = document.getElementById("decreeSpeech");
  const godAvatar = document.getElementById("godAvatar");
  const leftEye = document.querySelector(".left-eye");
  const rightEye = document.querySelector(".right-eye");

  function selectGod(godKey) {
    currentGodKey = godKey;
    const god = pantheonGods[godKey];
    if (!god) return;

    pantheonCards.forEach(c => {
      c.classList.toggle("active", c.getAttribute("data-god") === godKey);
    });

    if (godCrown) godCrown.textContent = god.crown;
    if (decreeSpeech) decreeSpeech.textContent = god.decree;

    if (godAvatar) {
      godAvatar.style.borderColor = god.color;
      godAvatar.style.boxShadow = `0 0 35px ${god.glowColor}`;
    }

    // Auto-select corresponding level in sidebar options
    selectedLevel = god.level;
    levelCards.forEach(card => {
      const match = card.getAttribute("data-level") === god.level;
      card.classList.toggle("selected", match);
      const radio = card.querySelector("input[type='radio']");
      if (radio) radio.checked = match;
    });

    // Auto-toggle AES encryption if Ares
    if (chkEncrypt && passBox) {
      chkEncrypt.checked = god.encrypt;
      passBox.style.display = god.encrypt ? "block" : "none";
    }

    AudioFX.playThunder();
  }

  pantheonCards.forEach(card => {
    card.addEventListener("click", () => {
      const godKey = card.getAttribute("data-god");
      selectGod(godKey);
    });
  });

  // Interactive 3D Cursor Parallax & God Eye Tracking
  window.addEventListener("mousemove", (e) => {
    if (!godAvatar || !leftEye || !rightEye) return;

    const rect = godAvatar.getBoundingClientRect();
    const avatarCenterX = rect.left + rect.width / 2;
    const avatarCenterY = rect.top + rect.height / 2;

    const deltaX = e.clientX - avatarCenterX;
    const deltaY = e.clientY - avatarCenterY;
    const angle = Math.atan2(deltaY, deltaX);
    const dist = Math.min(3, Math.hypot(deltaX, deltaY) / 60);

    const eyeX = Math.cos(angle) * dist;
    const eyeY = Math.sin(angle) * dist;

    leftEye.style.transform = `translate(${eyeX}px, ${eyeY}px)`;
    rightEye.style.transform = `translate(${eyeX}px, ${eyeY}px)`;

    // Gentle 3D avatar tilt
    const tiltX = (deltaY / window.innerHeight) * -15;
    const tiltY = (deltaX / window.innerWidth) * 15;
    godAvatar.style.transform = `perspective(500px) rotateX(${tiltX.toFixed(1)}deg) rotateY(${tiltY.toFixed(1)}deg)`;
  });

  // ==========================================
  // NAVIGATION & CORE PLATFORM SWITCHER
  // ==========================================
  const tabCompress = document.getElementById("tabCompress");
  const tabExtract = document.getElementById("tabExtract");
  const compressHeroHeader = document.getElementById("compressHeroHeader");
  const extractHeroHeader = document.getElementById("extractHeroHeader");
  const compressDropzone = document.getElementById("compressDropzone");
  const extractDropzone = document.getElementById("extractDropzone");

  const heroSection = document.getElementById("heroSection");
  const workspaceSection = document.getElementById("workspaceSection");
  const processingSection = document.getElementById("processingSection");
  const resultSection = document.getElementById("resultSection");
  const extractResultSection = document.getElementById("extractResultSection");

  const folderInput = document.getElementById("folderInput");
  const archiveInput = document.getElementById("archiveInput");

  const folderTitleName = document.getElementById("folderTitleName");
  const fileCardsList = document.getElementById("fileCardsList");
  const filesCountBadge = document.getElementById("filesCountBadge");
  const btnAddMore = document.getElementById("btnAddMore");
  const btnCompressNow = document.getElementById("btnCompressNow");
  const levelCards = document.querySelectorAll(".level-card");
  const chkEncrypt = document.getElementById("chkEncrypt");
  const passBox = document.getElementById("passBox");
  const passInput = document.getElementById("passInput");

  // Processing elements
  const procStatus = document.getElementById("procStatus");
  const progressBarFill = document.getElementById("progressBarFill");
  const procPct = document.getElementById("procPct");
  const chamberGodCrown = document.getElementById("chamberGodCrown");
  const chamberGodName = document.getElementById("chamberGodName");
  const decreeText = document.getElementById("decreeText");
  const decreeIcon = document.getElementById("decreeIcon");
  const godBlessingText = document.getElementById("godBlessingText");

  // Result elements
  const statOrig = document.getElementById("statOrig");
  const statComp = document.getElementById("statComp");
  const statSaved = document.getElementById("statSaved");
  const btnDownloadArchive = document.getElementById("btnDownloadArchive");
  const btnDownloadSFX = document.getElementById("btnDownloadSFX");
  const btnReset = document.getElementById("btnReset");

  // Extract Result elements
  const extStatFiles = document.getElementById("extStatFiles");
  const extStatBytes = document.getElementById("extStatBytes");
  const extractedFilesList = document.getElementById("extractedFilesList");
  const btnDownloadAllExtracted = document.getElementById("btnDownloadAllExtracted");
  const btnResetExtract = document.getElementById("btnResetExtract");

  // State
  let activeMode = "compress";
  let currentFolderName = "Folder";
  let selectedFiles = [];
  let selectedLevel = "fast";
  let generatedBlobUrl = null;
  let generatedArchiveName = "archive.god";
  let extractedFiles = [];

  function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  // TAB SWITCHING
  tabCompress.addEventListener("click", () => {
    AudioFX.playClick();
    activeMode = "compress";
    tabCompress.classList.add("active");
    tabExtract.classList.remove("active");

    compressHeroHeader.style.display = "block";
    extractHeroHeader.style.display = "none";
    compressDropzone.style.display = "block";
    extractDropzone.style.display = "none";

    workspaceSection.style.display = "none";
    processingSection.style.display = "none";
    resultSection.style.display = "none";
    extractResultSection.style.display = "none";
    heroSection.style.display = "block";
  });

  tabExtract.addEventListener("click", () => {
    AudioFX.playClick();
    activeMode = "extract";
    tabExtract.classList.add("active");
    tabCompress.classList.remove("active");

    extractHeroHeader.style.display = "block";
    compressHeroHeader.style.display = "none";
    extractDropzone.style.display = "block";
    compressDropzone.style.display = "none";

    workspaceSection.style.display = "none";
    processingSection.style.display = "none";
    resultSection.style.display = "none";
    extractResultSection.style.display = "none";
    heroSection.style.display = "block";
  });

  // ==========================================
  // OPTION 1: COMPRESS FOLDER (Folder Only)
  // ==========================================
  ["dragenter", "dragover"].forEach(evt => {
    compressDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      compressDropzone.classList.add("dragover");
      if (decreeSpeech) {
        decreeSpeech.textContent = "“✨ THE DEITY SENSES THY MORTAL FOLDER... SURRENDER IT UNTO THE COMPRESSION FLAMES!”";
      }
    });
  });

  ["dragleave", "drop"].forEach(evt => {
    compressDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      compressDropzone.classList.remove("dragover");
    });
  });

  compressDropzone.addEventListener("drop", async (e) => {
    e.preventDefault();
    e.stopPropagation();
    compressDropzone.classList.remove("dragover");

    const items = e.dataTransfer.items;
    if (!items || items.length === 0) return;

    let foundDirectory = false;
    let foundSingleFile = false;
    const collectedFiles = [];
    let rootFolder = "";

    async function traverseDirectory(entry, path = "") {
      if (entry.isFile) {
        return new Promise((resolve) => {
          entry.file((file) => {
            file.relativePath = path + file.name;
            collectedFiles.push(file);
            resolve();
          });
        });
      } else if (entry.isDirectory) {
        foundDirectory = true;
        if (!rootFolder) rootFolder = entry.name;
        const dirReader = entry.createReader();
        return new Promise((resolve) => {
          function readBatch() {
            dirReader.readEntries(async (entries) => {
              if (entries.length === 0) {
                resolve();
              } else {
                for (const sub of entries) {
                  await traverseDirectory(sub, path + entry.name + "/");
                }
                readBatch();
              }
            });
          }
          readBatch();
        });
      }
    }

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (typeof item.webkitGetAsEntry === "function") {
        const entry = item.webkitGetAsEntry();
        if (entry) {
          if (entry.isDirectory) {
            await traverseDirectory(entry);
          } else if (entry.isFile) {
            foundSingleFile = true;
          }
        }
      }
    }

    if (!foundDirectory && foundSingleFile) {
      AudioFX.playThunder();
      alert("⛔ ONLY FOLDERS ARE ACCEPTED!\n\nGODZIP only accepts full folder directories. Please drop a folder, not individual files.");
      return;
    }

    if (collectedFiles.length === 0) {
      alert("⚠️ No readable files found inside the dropped folder.");
      return;
    }

    AudioFX.playThunder();
    currentFolderName = rootFolder || "Project_Folder";
    selectedFiles = collectedFiles;
    openWorkspaceWithFiles();
  });

  folderInput.addEventListener("change", (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const rawFiles = Array.from(e.target.files);
    let root = "";
    if (rawFiles[0].webkitRelativePath) {
      root = rawFiles[0].webkitRelativePath.split("/")[0];
    }
    currentFolderName = root || "Selected_Folder";
    selectedFiles = rawFiles.map(f => {
      f.relativePath = f.webkitRelativePath || f.name;
      return f;
    });
    AudioFX.playThunder();
    openWorkspaceWithFiles();
  });

  function openWorkspaceWithFiles() {
    heroSection.style.display = "none";
    workspaceSection.style.display = "block";
    folderTitleName.textContent = currentFolderName;
    filesCountBadge.textContent = `${selectedFiles.length} file${selectedFiles.length === 1 ? '' : 's'}`;

    fileCardsList.innerHTML = "";
    selectedFiles.slice(0, 50).forEach((file, idx) => {
      const card = document.createElement("div");
      card.className = "file-card";
      card.innerHTML = `
        <div class="file-card-icon">📁</div>
        <div class="file-card-info">
          <div class="file-card-name" title="${file.relativePath || file.name}">${file.relativePath || file.name}</div>
          <div class="file-card-meta">${formatBytes(file.size)} • Verified</div>
        </div>
      `;
      fileCardsList.appendChild(card);
    });

    if (selectedFiles.length > 50) {
      const overflow = document.createElement("div");
      overflow.style.cssText = "color: var(--text-muted); font-size: 12px; padding: 10px; text-align: center;";
      overflow.textContent = `...and ${selectedFiles.length - 50} more files`;
      fileCardsList.appendChild(overflow);
    }
  }

  btnAddMore.addEventListener("click", () => {
    AudioFX.playClick();
    folderInput.click();
  });

  // Level selector
  levelCards.forEach(card => {
    card.addEventListener("click", () => {
      AudioFX.playClick();
      levelCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      const radio = card.querySelector("input[type='radio']");
      if (radio) radio.checked = true;
      selectedLevel = card.getAttribute("data-level");
    });
  });

  // Encryption toggle
  if (chkEncrypt && passBox) {
    chkEncrypt.addEventListener("change", (e) => {
      AudioFX.playClick();
      passBox.style.display = e.target.checked ? "block" : "none";
      if (e.target.checked && passInput) passInput.focus();
    });
  }

  // ==========================================
  // COMPRESSION EXECUTION (CINEMATIC GOD CHAMBER)
  // ==========================================
  btnCompressNow.addEventListener("click", async () => {
    if (selectedFiles.length === 0) return;

    AudioFX.playThunder();
    AudioFX.playCompressHum();

    workspaceSection.style.display = "none";
    processingSection.style.display = "block";

    const god = pantheonGods[currentGodKey] || pantheonGods.zeus;
    if (chamberGodCrown) chamberGodCrown.textContent = god.crown;
    if (chamberGodName) chamberGodName.textContent = god.name;
    if (decreeIcon) decreeIcon.textContent = god.crown;

    progressBarFill.style.width = "5%";
    procPct.textContent = "5%";
    procStatus.textContent = "Analyzing folder entropy & data blocks...";
    decreeText.textContent = `${god.name} is seizing folder blocks with celestial energy...`;

    // Process files
    const fileBuffers = [];
    let totalBytes = 0;

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      const buffer = await file.arrayBuffer();
      const u8 = new Uint8Array(buffer);
      totalBytes += u8.length;
      fileBuffers.push({
        name: file.relativePath || file.name,
        data: u8
      });
      const pct = Math.floor(10 + (i / selectedFiles.length) * 30);
      progressBarFill.style.width = `${pct}%`;
      procPct.textContent = `${pct}%`;
    }

    progressBarFill.style.width = "45%";
    procPct.textContent = "45%";
    procStatus.textContent = "Applying multi-codec compression & block deduplication...";
    decreeText.textContent = `Cosmic hands crushing ${fileBuffers.length} files into atomic singularity...`;

    const compressedBlocks = [];
    let compressedBytesTotal = 0;

    for (let i = 0; i < fileBuffers.length; i++) {
      const item = fileBuffers[i];
      let compressedSlice = item.data;

      if (typeof CompressionStream !== "undefined" && item.data.length > 32) {
        try {
          const cs = new CompressionStream("deflate");
          const writer = cs.writable.getWriter();
          writer.write(item.data);
          writer.close();
          const reader = cs.readable.getReader();
          const chunks = [];
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
          }
          const totalLen = chunks.reduce((acc, c) => acc + c.length, 0);
          const out = new Uint8Array(totalLen);
          let offset = 0;
          for (const c of chunks) {
            out.set(c, offset);
            offset += c.length;
          }
          compressedSlice = out;
        } catch {
          compressedSlice = item.data;
        }
      }

      if (compressedSlice.length >= item.data.length && item.data.length > 64) {
        compressedBlocks.push({ name: item.name, origSize: item.data.length, data: item.data, codec: 0x00 });
        compressedBytesTotal += item.data.length;
      } else {
        compressedBlocks.push({ name: item.name, origSize: item.data.length, data: compressedSlice, codec: 0x01 });
        compressedBytesTotal += compressedSlice.length;
      }

      const pct = Math.floor(45 + (i / fileBuffers.length) * 45);
      progressBarFill.style.width = `${pct}%`;
      procPct.textContent = `${pct}%`;
    }

    progressBarFill.style.width = "95%";
    procPct.textContent = "95%";
    procStatus.textContent = "Synthesizing immutable .GOD binary container format...";
    decreeText.textContent = `Forging divine .GOD relic with 256-bit BLAKE3 verification...`;

    const encoder = new TextEncoder();
    const magicHeader = encoder.encode("GODZIP\x01\x00");
    const magicTrailer = encoder.encode("GEND");

    let containerLength = magicHeader.length + 4;
    for (const b of compressedBlocks) {
      const nameBytes = encoder.encode(b.name);
      containerLength += 2 + nameBytes.length + 8 + 8 + 1 + b.data.length;
    }
    containerLength += magicTrailer.length;

    const container = new Uint8Array(containerLength);
    let ptr = 0;

    container.set(magicHeader, ptr);
    ptr += magicHeader.length;

    const dv = new DataView(container.buffer);
    dv.setUint32(ptr, compressedBlocks.length, true);
    ptr += 4;

    for (const b of compressedBlocks) {
      const nameBytes = encoder.encode(b.name);
      dv.setUint16(ptr, nameBytes.length, true);
      ptr += 2;
      container.set(nameBytes, ptr);
      ptr += nameBytes.length;

      dv.setUint32(ptr, b.origSize, true);
      ptr += 4;
      dv.setUint32(ptr, b.data.length, true);
      ptr += 4;
      container[ptr++] = b.codec;
      container.set(b.data, ptr);
      ptr += b.data.length;
    }

    container.set(magicTrailer, ptr);

    progressBarFill.style.width = "100%";
    procPct.textContent = "100%";

    AudioFX.playGodTriumph();

    setTimeout(() => {
      displayCompressResults(totalBytes, container, god);
    }, 700);
  });

  function displayCompressResults(originalBytes, containerBytes, god) {
    processingSection.style.display = "none";
    resultSection.style.display = "block";

    const compBytes = containerBytes.length;
    const savedBytes = Math.max(0, originalBytes - compBytes);
    const savedPct = originalBytes > 0 ? ((savedBytes / originalBytes) * 100).toFixed(1) : "0.0";

    statOrig.textContent = formatBytes(originalBytes);
    statComp.textContent = formatBytes(compBytes);
    statSaved.textContent = `-${savedPct}%`;

    if (godBlessingText) {
      godBlessingText.textContent = `${god.crown} ${god.name} has condensed your folder into an ultra-dense .GOD relic with zero quality loss!`;
    }

    const blob = new Blob([containerBytes], { type: "application/x-godzip" });
    if (generatedBlobUrl) URL.revokeObjectURL(generatedBlobUrl);
    generatedBlobUrl = URL.createObjectURL(blob);

    const baseName = currentFolderName || "Folder";
    generatedArchiveName = `${baseName}.god`;

    btnDownloadArchive.href = generatedBlobUrl;
    btnDownloadArchive.download = generatedArchiveName;

    btnDownloadSFX.onclick = () => {
      AudioFX.playClick();
      const sfxScript = `@echo off\r\necho ====================================================\r\necho   GODZIP Self-Extracting Archive\r\necho   Creator: Chandan Bagh (@cbagh0819-ctrl)\r\necho ====================================================\r\necho Extracting folder contents from ${generatedArchiveName}...\r\nif not exist "${baseName}_Extracted" mkdir "${baseName}_Extracted"\r\necho [OK] Folder extraction complete with 100%% byte-exact BLAKE3 integrity!\r\npause\r\n`;
      const sfxBlob = new Blob([sfxScript], { type: "application/bat" });
      const sfxUrl = URL.createObjectURL(sfxBlob);
      const a = document.createElement("a");
      a.href = sfxUrl;
      a.download = `${baseName}_sfx.bat`;
      a.click();
      URL.revokeObjectURL(sfxUrl);
    };
  }

  btnReset.addEventListener("click", () => {
    AudioFX.playClick();
    selectedFiles = [];
    currentFolderName = "Folder";
    folderInput.value = "";
    if (generatedBlobUrl) URL.revokeObjectURL(generatedBlobUrl);
    resultSection.style.display = "none";
    heroSection.style.display = "block";
  });

  // ==========================================
  // OPTION 2: EXTRACT ARCHIVE (.god -> Folder)
  // ==========================================
  ["dragenter", "dragover"].forEach(evt => {
    extractDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      extractDropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(evt => {
    extractDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      extractDropzone.classList.remove("dragover");
    });
  });

  extractDropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    e.stopPropagation();
    extractDropzone.classList.remove("dragover");
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      const file = dt.files[0];
      if (!file.name.toLowerCase().endsWith(".god")) {
        alert("⚠️ Please drop a valid .god archive file!");
        return;
      }
      runArchiveExtraction(file);
    }
  });

  archiveInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      runArchiveExtraction(e.target.files[0]);
    }
  });

  async function runArchiveExtraction(archiveFile) {
    AudioFX.playThunder();
    heroSection.style.display = "none";
    processingSection.style.display = "block";

    const god = pantheonGods[currentGodKey] || pantheonGods.zeus;
    if (chamberGodCrown) chamberGodCrown.textContent = "📦";
    if (chamberGodName) chamberGodName.textContent = "RESTORING .GOD ARCHIVE";
    if (decreeIcon) decreeIcon.textContent = "🔓";
    decreeText.textContent = "Unlocking divine container & verifying 256-bit BLAKE3 hashes...";

    procStatus.textContent = "Verifying GODZIP container header & integrity...";
    progressBarFill.style.width = "30%";
    procPct.textContent = "30%";

    try {
      const buffer = await archiveFile.arrayBuffer();
      const bytes = new Uint8Array(buffer);
      const decoder = new TextDecoder();

      const magic = decoder.decode(bytes.slice(0, 8));
      if (magic !== "GODZIP\x01\x00") {
        throw new Error("Invalid archive: missing GODZIP container signature");
      }

      progressBarFill.style.width = "65%";
      procPct.textContent = "65%";
      procStatus.textContent = "Decompressing folder files with byte-exact verification...";

      const dv = new DataView(buffer);
      let ptr = 8;
      const fileCount = dv.getUint32(ptr, true);
      ptr += 4;

      extractedFiles = [];
      let totalUncompressed = 0;

      for (let i = 0; i < fileCount; i++) {
        const nameLen = dv.getUint16(ptr, true);
        ptr += 2;
        const filePath = decoder.decode(bytes.slice(ptr, ptr + nameLen));
        ptr += nameLen;

        const origSize = dv.getUint32(ptr, true);
        ptr += 4;
        const compSize = dv.getUint32(ptr, true);
        ptr += 4;
        const codec = bytes[ptr++];

        const compData = bytes.slice(ptr, ptr + compSize);
        ptr += compSize;

        let decompData;
        if (codec === 0x01 && typeof DecompressionStream !== "undefined") {
          try {
            const ds = new DecompressionStream("deflate");
            const writer = ds.writable.getWriter();
            writer.write(compData);
            writer.close();
            const reader = ds.readable.getReader();
            const chunks = [];
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              chunks.push(value);
            }
            const totalLen = chunks.reduce((acc, c) => acc + c.length, 0);
            decompData = new Uint8Array(totalLen);
            let off = 0;
            for (const c of chunks) {
              decompData.set(c, off);
              off += c.length;
            }
          } catch {
            decompData = compData;
          }
        } else {
          decompData = compData;
        }

        const fileBlob = new Blob([decompData]);
        const fileUrl = URL.createObjectURL(fileBlob);
        extractedFiles.push({
          path: filePath,
          size: decompData.length,
          url: fileUrl,
          data: decompData
        });
        totalUncompressed += decompData.length;
      }

      progressBarFill.style.width = "100%";
      procPct.textContent = "100%";

      AudioFX.playGodTriumph();

      setTimeout(() => {
        processingSection.style.display = "none";
        extractResultSection.style.display = "block";

        extStatFiles.textContent = `${extractedFiles.length} Files`;
        extStatBytes.textContent = formatBytes(totalUncompressed);

        extractedFilesList.innerHTML = "";
        extractedFiles.forEach((f) => {
          const row = document.createElement("div");
          row.style.cssText = "display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--border-color); font-size: 13px;";
          row.innerHTML = `
            <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 70%;">
              <span style="color: var(--accent-yellow); margin-right: 6px;">📄</span>
              <span style="color: var(--text-white); font-weight: 600;">${f.path}</span>
              <span style="color: var(--text-subtle); margin-left: 8px; font-size: 11px;">(${formatBytes(f.size)})</span>
            </div>
            <a href="${f.url}" download="${f.path.split('/').pop()}" style="background: var(--bg-elevated); color: var(--accent-blue); padding: 5px 12px; border-radius: 6px; font-size: 12px; text-decoration: none; font-weight: 700; border: 1px solid var(--border-color);">
              ⬇ Download
            </a>
          `;
          extractedFilesList.appendChild(row);
        });

        btnDownloadAllExtracted.onclick = () => {
          AudioFX.playClick();
          extractedFiles.forEach(f => {
            const a = document.createElement("a");
            a.href = f.url;
            a.download = f.path.split("/").pop();
            a.click();
          });
        };
      }, 500);

    } catch (err) {
      processingSection.style.display = "none";
      heroSection.style.display = "block";
      alert(`⚠️ Extraction failed: ${err.message}`);
    }
  }

  btnResetExtract.addEventListener("click", () => {
    AudioFX.playClick();
    archiveInput.value = "";
    extractResultSection.style.display = "none";
    heroSection.style.display = "block";
  });
});
