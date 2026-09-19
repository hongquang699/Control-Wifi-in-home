/**
 * Module Giám Sát Lưu Lượng Mạng & Biểu Đồ Sóng Waveform Canvas
 */
window.toggleWaveAnimation = function() {
  isWaveAnimationPaused = !isWaveAnimationPaused;
  const icon = document.getElementById("wavePauseIcon");
  const text = document.getElementById("wavePauseText");
  if (icon && text) {
    if (isWaveAnimationPaused) {
      icon.textContent = "▶️";
      text.textContent = "Tiếp tục";
      showToast("Đã tạm dừng đồ thị sóng băng thông");
    } else {
      icon.textContent = "⏸️";
      text.textContent = "Tạm dừng";
      showToast("Đã kích hoạt lại đồ thị sóng băng thông");
    }
  }
};

// ----------------------------------------------------
// TAB 4: TRAFFIC WAVEFORM CANVAS
// ----------------------------------------------------
function initDemoWaveCanvas2() {
  if (wave2Initialized) return;
  const canvas = document.getElementById("demoWaveCanvas2");
  if (!canvas) return;
  wave2Initialized = true;
  const ctx = canvas.getContext("2d");
  let step = 0;

  function draw() {
    if (isWaveAnimationPaused) {
      requestAnimationFrame(draw);
      return;
    }
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Cyan
    ctx.beginPath();
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#38bdf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.sin((x + step) * 0.03) * 25 + Math.sin((x + step * 0.8) * 0.015) * 12;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Purple
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#a855f7";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.cos((x + step * 1.1) * 0.025) * 18;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    step += 2;
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}



// ==================== LIVE WAVEFORM CANVAS ====================
function initDemoWaveCanvas() {
  const canvas = document.getElementById("demoWaveCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let step = 0;

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    // Download Wave (Cyan)
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#38bdf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.sin((x + step) * 0.04) * 16 + Math.sin((x + step * 0.7) * 0.02) * 8;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fillStyle = "rgba(56, 189, 248, 0.08)";
    ctx.fill();

    // Upload Wave (Indigo)
    ctx.beginPath();
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "#818cf8";
    for (let x = 0; x < w; x++) {
      const y = h / 2 + Math.cos((x + step * 1.2) * 0.035) * 12;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    step += 2;
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

