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

sessoes = {}

class Simulador:
    def __init__(self, codigo):
        self.instrucoes = [linha.strip() for linha in codigo.splitlines() if linha.strip()]
        self.pc = 0
        self.saida = []
        self.regs = {f"$t{i}": 0 for i in range(10)}
        self.memoria = {}
        self.finalizado = False
        self.binarios = []

    def reg_to_bin(self, reg):
        if reg.startswith("$t"):
            return format(int(reg[2]), '05b')
        return "00000"

    def passo(self):
        if self.pc >= len(self.instrucoes):
            return True

        instr = self.instrucoes[self.pc]
        instr_limpa = instr.replace(",", " ").split()
        if not instr_limpa:
            self.pc += 1
            return self.pc >= len(self.instrucoes)

        try:
            op = instr_limpa[0].lower()

            if op == "li":
                _, reg, val = instr_limpa
                self.regs[reg] = int(val)
                self.saida.append(f"{reg} = {val}")

            elif op == "add":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = self.regs[rs] + self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100000")

            elif op == "addi":
                _, rd, rs, imm = instr_limpa
                self.regs[rd] = self.regs[rs] + int(imm)
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"001000 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(imm), '016b')}")

            elif op == "sub":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = self.regs[rs] - self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100010")

            elif op == "mult":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = self.regs[rs] * self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 011000")

            elif op == "and":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = self.regs[rs] & self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100100")

            elif op == "or":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = self.regs[rs] | self.regs[rt]
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 100101")

            elif op == "sll":
                _, rd, rs, shamt = instr_limpa
                self.regs[rd] = self.regs[rs] << int(shamt)
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 00000 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(shamt), '05b')} 000000")

            elif op == "slt":
                _, rd, rs, rt = instr_limpa
                self.regs[rd] = int(self.regs[rs] < self.regs[rt])
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"000000 {self.reg_to_bin(rs)} {self.reg_to_bin(rt)} {self.reg_to_bin(rd)} 00000 101010")

            elif op == "slti":
                _, rd, rs, imm = instr_limpa
                self.regs[rd] = int(self.regs[rs] < int(imm))
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"001010 {self.reg_to_bin(rs)} {self.reg_to_bin(rd)} {format(int(imm), '016b')}")

            elif op == "lui":
                _, rd, val = instr_limpa
                self.regs[rd] = int(val) << 16
                self.saida.append(f"{rd} = {self.regs[rd]}")
                self.binarios.append(f"001111 00000 {self.reg_to_bin(rd)} {format(int(val), '016b')}")

            elif op == "lw":
                _, rd, endereco = instr_limpa
                addr = endereco.strip("()$t")
                self.regs[rd] = self.memoria.get(addr, 0)
                self.saida.append(f"{rd} carregado de {addr} = {self.regs[rd]}")
                self.binarios.append(f"100011 {self.reg_to_bin('$t0')} {self.reg_to_bin(rd)} {format(int(addr), '016b')}")

            elif op == "sw":
                _, rs, endereco = instr_limpa
                addr = endereco.strip("()$t")
                self.memoria[addr] = self.regs[rs]
                self.saida.append(f"{addr} armazenado = {self.memoria[addr]}")
                self.binarios.append(f"101011 {self.reg_to_bin('$t0')} {self.reg_to_bin(rs)} {format(int(addr), '016b')}")

            elif op == "imprimir":
                if instr_limpa[1].lower() == "inteiro":
                    self.saida.append("[IMPRIMIR] Inteiros: " + ", ".join(f"{k} = {v}" for k, v in self.regs.items()))
                elif instr_limpa[1].lower() == "string":
                    self.saida.append("[IMPRIMIR] Esta é uma string de teste.")

            elif op in ["sair", "exit"]:
                self.saida.append("[ENCERRADO PELO USUÁRIO]")
                self.pc = len(self.instrucoes)

            else:
                self.saida.append(f"[ERRO] Instrução não reconhecida: {instr}")

        except Exception as e:
            self.saida.append(f"[ERRO] Falha ao executar '{instr}': {e}")

        self.pc += 1
        return self.pc >= len(self.instrucoes)

    def estado(self):
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
