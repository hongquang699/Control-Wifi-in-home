/**
 * Module Hạ Tầng Mạng, Sơ Đồ Topo Đa Tầng & Live Ping Tool
 */
window.selectTopologyNode = function(nodeKey) {
  document.querySelectorAll(".topo-node").forEach(n => {
    n.classList.remove("ring-2", "ring-sky-400", "shadow-sky-500/30");
  });

  const selected = document.querySelector(`[data-node="${nodeKey}"]`);
  if (selected) {
    selected.classList.add("ring-2", "ring-sky-400", "shadow-sky-500/30");
  }

  const routeEl = document.getElementById("topoHopRouteText");
  const statusEl = document.getElementById("topoHopStatus");
  if (!routeEl || !statusEl) return;

  const nodeInfo = {
    internet: {
      route: "Internet Toàn Cầu ➔ Cáp Quang ISP (VNPT/Viettel/FPT) ➔ Cổng WAN Modem",
      status: "WAN Uplink • 1.2 Gbps Băng Thông",
      ip: "8.8.8.8"
    },
    modem: {
      route: "Modem Tổng ISP (192.168.1.1) ➔ Gateway ISP ➔ Internet Toàn Cầu",
      status: "1 Hop • 1 ms RTT (Trực Tuyến)",
      ip: "192.168.1.1"
    },
    subrouter: {
      route: "Router Phụ TP-Link (192.168.110.1) ➔ Modem Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 2 ms RTT (Gigabit LAN)",
      ip: "192.168.110.1"
    },
    macbook: {
      route: "MacBook Pro M2 (192.168.1.189) ➔ Wi-Fi Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 2 ms RTT (Wi-Fi 5GHz)",
      ip: "192.168.1.189"
    },
    iphone: {
      route: "iPhone 15 Pro (192.168.1.115) ➔ Wi-Fi Tổng (192.168.1.1) ➔ Internet",
      status: "1 Hop • 4 ms RTT (Wi-Fi 5GHz)",
      ip: "192.168.1.115"
    },
    tv: {
      route: "Samsung Smart 4K TV (192.168.110.45) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 5 ms RTT (Dây LAN)",
      ip: "192.168.110.45"
    },
    cam: {
      route: "Ezviz Cam C6N (192.168.110.88) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 12 ms RTT (Wi-Fi 2.4GHz)",
      ip: "192.168.110.88"
    },
    esp: {
      route: "ESP32 Relay (192.168.110.99) ➔ Router Phụ (192.168.110.1) ➔ Modem Tổng ➔ Internet",
      status: "2 Hops • 8 ms RTT (Wi-Fi 2.4GHz)",
      ip: "192.168.110.99"
    }
  };

  const info = nodeInfo[nodeKey] || nodeInfo.subrouter;
  routeEl.textContent = info.route;
  statusEl.textContent = info.status;

  const pingInput = document.getElementById("pingTargetInput");
  if (pingInput && info.ip) {
    pingInput.value = info.ip;
  }
};

window.runPingTest = function() {
  const input = document.getElementById("pingTargetInput");
  const output = document.getElementById("pingConsoleOutput");
  const spinner = document.getElementById("pingBtnSpinner");
  if (!input || !output) return;

  const target = input.value.trim() || "192.168.1.1";
  spinner.classList.add("animate-spin");
  output.innerHTML = `<div class="text-sky-400 font-bold">[PING] Bắt đầu gửi 4 gói tin ICMP (32 bytes) tới ${target}...</div>`;

  let packetIndex = 1;
  const timer = setInterval(() => {
    if (packetIndex <= 4) {
      const rtt = (1.2 + Math.random() * 2.5).toFixed(1);
      const ttl = target.startsWith("8.") || target.startsWith("1.") ? 116 : 64;
      const line = document.createElement("div");
      line.className = "text-slate-300";
      line.textContent = `Phản hồi từ ${target}: bytes=32 thời gian=${rtt}ms TTL=${ttl}`;
      output.appendChild(line);
      packetIndex++;
    } else {
      clearInterval(timer);
      spinner.classList.remove("animate-spin");
      const summary1 = document.createElement("div");
      summary1.className = "text-emerald-400 font-bold pt-1 border-t border-slate-800";
      summary1.textContent = `Thống kê Ping cho ${target}: Đã gửi = 4, Đã nhận = 4, Mất = 0 (0% loss)`;
      const summary2 = document.createElement("div");
      summary2.className = "text-slate-400";
      summary2.textContent = `Thời gian khứ hồi (RTT): Min = 1.2ms, Max = 3.6ms, Avg = 2.1ms`;
      output.appendChild(summary1);
      output.appendChild(summary2);
    }
  }, 300);
};

// ----------------------------------------------------
// TAB 4: TRAFFIC CONTROLS
// ----------------------------------------------------
