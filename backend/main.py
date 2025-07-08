from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from uuid import uuid4

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodigoMIPS(BaseModel):
    codigo: str

sessoes: Dict[str, "Simulador"] = {}

class Simulador:
    def __init__(self, codigo: str):
        # Remove comentários ("#" ou "//") e linhas vazias
        self.instrucoes = []
        for linha in codigo.splitlines():
            # tira tudo após '#' e '//'
            sem_hash = linha.split('#', 1)[0]
            sem_comments = sem_hash.split('//', 1)[0]
            instr = sem_comments.strip()
            if instr:
                self.instrucoes.append(instr)

        self.pc = 0
        self.saida: list[str] = []
        self.regs = {f"$t{i}": 0 for i in range(10)}
        self.memoria: Dict[str, int] = {}
        self.binarios: list[str] = []

    def reg_to_bin(self, reg: str) -> str:
        if reg.startswith("$t") and reg[2:].isdigit():
            return format(int(reg[2:]), '05b')
        print(f"Aviso: registrador {reg} não reconhecido, usando 00000")
        return "00000"
        
    def passo(self) -> bool:
        if self.pc >= len(self.instrucoes):
            return True

        instr = self.instrucoes[self.pc]
        partes = instr.replace(",", " ").split()
        if not partes:
            self.pc += 1
            return self.pc >= len(self.instrucoes)

        op = partes[0].lower()
        try:
            if op == "li":
                _, reg, val = partes
                self.regs[reg] = int(val)
                self.saida.append(f"{reg} = {val}")

            elif op == "add":
                _, rd, rs, rt = partes
                self.regs[rd] = self.regs[rs] + self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100000"
                )

            elif op == "addi":
                _, rd, rs, imm = partes
                self.regs[rd] = self.regs[rs] + int(imm)
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"001000 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(imm), '016b')}"
                )

            elif op == "sub":
                _, rd, rs, rt = partes
                self.regs[rd] = self.regs[rs] - self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100010"
                )

            elif op == "mult":
                _, rd, rs, rt = partes
                self.regs[rd] = self.regs[rs] * self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 011000"
                )

            elif op == "and":
                _, rd, rs, rt = partes
                self.regs[rd] = self.regs[rs] & self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100100"
                )

            elif op == "or":
                _, rd, rs, rt = partes
                self.regs[rd] = self.regs[rs] | self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100101"
                )

            elif op == "sll":
                _, rd, rs, shamt = partes
                self.regs[rd] = self.regs[rs] << int(shamt)
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 00000 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(shamt), '05b')} 000000"
                )

            elif op == "slt":
                _, rd, rs, rt = partes
                self.regs[rd] = int(self.regs[rs] < self.regs[rt])
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 101010"
                )

            elif op == "slti":
                _, rd, rs, imm = partes
                self.regs[rd] = int(self.regs[rs] < int(imm))
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"001010 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(imm), '016b')}"
                )

            elif op == "lui":
                _, rd, val = partes
                self.regs[rd] = int(val) << 16
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(
                    f"001111 00000 {self.reg_to_bin(rd)} {format(int(val), '016b')}"
                )

            elif op == "lw":
                _, rd, endereco = partes
                addr = endereco.strip('()')
                self.regs[rd] = self.memoria.get(addr, 0)
                self.saida.append(f"{rd} carregado de {addr} = {self.regs[rd]}")
                self.binarios.append(
                    f"100011 {self.reg_to_bin('$t0')} {self.reg_to_bin(rd)} {format(int(addr), '016b')}"
                )

            elif op == "sw":
                _, rs, endereco = partes
                addr = endereco.strip('()')
                self.memoria[addr] = self.regs[rs]
                self.saida.append(f"endereço {addr} armazenado = {self.memoria[addr]}")
                self.binarios.append(
                    f"101011 {self.reg_to_bin('$t0')} {self.reg_to_bin(rs)} {format(int(addr), '016b')}"
                )

            elif op == "imprimir":
                tipo = partes[1].lower() if len(partes) > 1 else ''
                if tipo == "inteiro":
                    if len(partes) >= 3:
                        reg = partes[2]
                        valor = self.regs.get(reg, 0)
                        self.saida.append(f"[IMPRIMIR] {reg} = {valor}")
                    else:
                        self.saida.append(
                            "[IMPRIMIR] Inteiros: " +
                            ", ".join(f"{k} = {v}" for k, v in self.regs.items())
                        )
                elif tipo == "string":
                    if '"' in instr:
                        texto = instr[instr.find('"')+1 : instr.rfind('"')]
                        self.saida.append(texto)
                    else:
                        self.saida.append("[IMPRIMIR] Texto inválido")

            elif op in ["sair", "exit"]:
                self.saida.append("[ENCERRADO PELO USUÁRIO]")
                self.pc = len(self.instrucoes)
                return True

            else:
                self.saida.append(f"[ERRO] Instrução não reconhecida: {instr}")

        except Exception as e:
            self.saida.append(f"[ERRO] Falha ao executar '{instr}': {e}")

        self.pc += 1
        return self.pc >= len(self.instrucoes)

    def estado(self) -> Dict:
        return {
            "registradores": self.regs,
            "memoria": self.memoria,
            "saida": "\n".join(self.saida),
            "pc": self.pc,
            "finalizado": self.pc >= len(self.instrucoes),
            "binarios": self.binarios
        }

@app.post("/carregar")
def carregar(codigo: CodigoMIPS):
    id_sessao = str(uuid4())
    sessoes[id_sessao] = Simulador(codigo.codigo)
    return {"sessao_id": id_sessao}

@app.get("/passo")
def passo(sessao_id: str = Query(...)):
    sim = sessoes[sessao_id]
    sim.passo()
    return sim.estado()

@app.get("/relatorio")
def relatorio(sessao_id: str = Query(...)):
    sim = sessoes[sessao_id]
    return sim.estado()

@app.post("/executar")
def executar(codigo: CodigoMIPS):
    id_sessao = str(uuid4())
    sim = Simulador(codigo.codigo)
    while not sim.passo():
        pass
    sessoes[id_sessao] = sim
    estado = sim.estado()
    estado["sessao_id"] = id_sessao
    return estado
