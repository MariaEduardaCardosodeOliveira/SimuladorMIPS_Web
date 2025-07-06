let sessaoId = null;
let executando = false;

function carregarCodigo() {
  const codigo = document.getElementById("codigo").value;
  fetch("http://localhost:8000/carregar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo })
  })
    .then(res => res.json())
    .then(data => {
      sessaoId = data.sessao_id;
      document.getElementById("saida").textContent = "Código carregado!";
    });
}

function executarPasso() {
  if (!sessaoId) return;
  fetch(`http://localhost:8000/passo?sessao_id=${sessaoId}`)
    .then(res => res.json())
    .then(data => atualizarEstado(data));
}

function executarTudo() {
  const codigo = document.getElementById("codigo").value;
  fetch("http://localhost:8000/executar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo })
  })
    .then(res => res.json())
    .then(data => {
      sessaoId = data.sessao_id;
      atualizarEstado(data);
    });
}

function executarDevagar() {
  if (!sessaoId || executando) return;
  executando = true;
  const executarLoop = () => {
    fetch(`http://localhost:8000/passo?sessao_id=${sessaoId}`)
      .then(res => res.json())
      .then(data => {
        atualizarEstado(data);
        if (!data.finalizado) {
          setTimeout(executarLoop, 1000);
        } else {
          executando = false;
        }
      });
  };
  executarLoop();
}

function mostrarRelatorio() {
  if (!sessaoId) return;
  fetch(`http://localhost:8000/relatorio?sessao_id=${sessaoId}`)
    .then(res => {
      if (!res.ok) throw new Error("Erro na resposta do servidor.");
      return res.json();
    })
    .then(data => {
      if (!data || !data.registradores) {
        alert("Relatório indisponível ou sessão inválida.");
        return;
      }

      let relatorio = "📌 REGISTRADORES:\n";
      for (const [reg, val] of Object.entries(data.registradores)) {
        relatorio += `${reg} = ${val}\n`;
      }

      relatorio += "\n📌 MEMÓRIA:\n";
      if (!data.memoria || Object.keys(data.memoria).length === 0) {
        relatorio += "Nenhum valor armazenado.\n";
      } else {
        for (const [addr, val] of Object.entries(data.memoria)) {
          relatorio += `${addr} = ${val}\n`;
        }
      }

      relatorio += `\n📌 PC Final: ${data.pc ?? "indefinido"}\n`;
      relatorio += `\n📌 SAÍDA:\n${data.saida ?? "(sem saída)"}`;

      if (data.binarios && data.binarios.length > 0) {
        relatorio += "\n\n📌 BINÁRIOS:\n" + data.binarios.join("\n");
      }

      alert(relatorio);
    })
    .catch(error => {
      console.error("Erro ao obter relatório:", error);
      alert("Erro ao carregar relatório.");
    });
}

function atualizarEstado(data) {
  document.getElementById("saida").textContent = data.saida;
  document.getElementById("registradores").textContent = JSON.stringify(data.registradores, null, 2);
  document.getElementById("memoria").textContent = JSON.stringify(data.memoria, null, 2);
  document.getElementById("pc").textContent = data.pc;

  if (data.binarios) {
    const binSec = document.getElementById("binarios");
    if (binSec) {
      binSec.textContent = data.binarios.join("\n");
    }
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const btnRelatorio = document.getElementById("btnRelatorio");
  if (btnRelatorio) {
    btnRelatorio.addEventListener("click", mostrarRelatorio);
  }
});
