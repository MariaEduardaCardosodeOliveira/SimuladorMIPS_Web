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

class InstrucaoR:
    def __init__(self, opcode: int, rd: int, funct3: int, rs1: int, rs2: int, funct7: int):
        self.opcode = opcode
        self.rd = rd
        self.funct3 = funct3
        self.rs1 = rs1
        self.rs2 = rs2
        self.funct7 = funct7
    
    def to_binary(self) -> str:
        funct7_bin = format(self.funct7, '07b')
        rs2_bin = format(self.rs2, '05b')
        rs1_bin = format(self.rs1, '05b')
        funct3_bin = format(self.funct3, '03b')
        rd_bin = format(self.rd, '05b')
        opcode_bin = format(self.opcode, '07b')
        return f"{funct7_bin} {rs2_bin} {rs1_bin} {funct3_bin} {rd_bin} {opcode_bin}"

class InstrucaoI:
    def __init__(self, opcode: int, rd: int, funct3: int, rs1: int, imm: int):
        self.opcode = opcode
        self.rd = rd
        self.funct3 = funct3
        self.rs1 = rs1
        self.imm = imm
    
    def to_binary(self) -> str:
        imm_bin = format(self.imm & 0xFFF, '012b')
        rs1_bin = format(self.rs1, '05b')
        funct3_bin = format(self.funct3, '03b')
        rd_bin = format(self.rd, '05b')
        opcode_bin = format(self.opcode, '07b')
        return f"{imm_bin} {rs1_bin} {funct3_bin} {rd_bin} {opcode_bin}"

class InstrucaoS:
    def __init__(self, opcode: int, funct3: int, rs1: int, rs2: int, imm: int):
        self.opcode = opcode
        self.funct3 = funct3
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
    
    def to_binary(self) -> str:
        imm_11_5 = (self.imm >> 5) & 0x7F
        imm_4_0 = self.imm & 0x1F
        imm_11_5_bin = format(imm_11_5, '07b')
        rs2_bin = format(self.rs2, '05b')
        rs1_bin = format(self.rs1, '05b')
        funct3_bin = format(self.funct3, '03b')
        imm_4_0_bin = format(imm_4_0, '05b')
        opcode_bin = format(self.opcode, '07b')
        return f"{imm_11_5_bin} {rs2_bin} {rs1_bin} {funct3_bin} {imm_4_0_bin} {opcode_bin}"

def sign_extend_12(imm: int) -> int:
    if imm & 0x800:
        return imm | 0xFFFFF000
    return imm & 0xFFF

def parse_add(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x0, rs1=rs1, rs2=rs2, funct7=0x0)

def parse_sub(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x0, rs1=rs1, rs2=rs2, funct7=0x20)

def parse_mult(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x0, rs1=rs1, rs2=rs2, funct7=0x1)

def parse_and(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x7, rs1=rs1, rs2=rs2, funct7=0x0)

def parse_or(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x6, rs1=rs1, rs2=rs2, funct7=0x0)

def parse_sll(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    shamt = int(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x1, rs1=rs1, rs2=shamt, funct7=0x0)

def parse_slt(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    rs2 = reg_to_index_func(partes[3])
    return InstrucaoR(opcode=0x33, rd=rd, funct3=0x2, rs1=rs1, rs2=rs2, funct7=0x0)

def parse_addi(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    imm = int(partes[3])
    imm = sign_extend_12(imm)
    return InstrucaoI(opcode=0x13, rd=rd, funct3=0x0, rs1=rs1, imm=imm)

def parse_slti(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    rs1 = reg_to_index_func(partes[2])
    imm = int(partes[3])
    imm = sign_extend_12(imm)
    return InstrucaoI(opcode=0x13, rd=rd, funct3=0x2, rs1=rs1, imm=imm)

def parse_lw(partes, reg_to_index_func):
    rd = reg_to_index_func(partes[1])
    offset_rs1_str = partes[2]
    if '(' in offset_rs1_str:
        offset_str, rs1_str = offset_rs1_str.split('(')
        offset = int(offset_str) if offset_str else 0
        rs1_str = rs1_str.rstrip(')')
        rs1 = reg_to_index_func(rs1_str)
    else:
        offset = int(offset_rs1_str) if offset_rs1_str.isdigit() else 0
        rs1 = 0
    offset = sign_extend_12(offset)
    return InstrucaoI(opcode=0x03, rd=rd, funct3=0x2, rs1=rs1, imm=offset)

def parse_sw(partes, reg_to_index_func):
    rs2 = reg_to_index_func(partes[1])
    offset_rs1_str = partes[2]
    if '(' in offset_rs1_str:
        offset_str, rs1_str = offset_rs1_str.split('(')
        offset = int(offset_str) if offset_str else 0
        rs1_str = rs1_str.rstrip(')')
        rs1 = reg_to_index_func(rs1_str)
    else:
        offset = int(offset_rs1_str) if offset_rs1_str.isdigit() else 0
        rs1 = 0
    offset = sign_extend_12(offset)
    return InstrucaoS(opcode=0x23, funct3=0x2, rs1=rs1, rs2=rs2, imm=offset)

class InstrucaoEcall:
    def __init__(self):
        self.opcode = 0x73
    
    def to_binary(self) -> str:
        return "000000000000 00000 000 00000 1110011"

def gera_sinais_controle(instr_obj):
    if isinstance(instr_obj, InstrucaoR):
        return {
            "ALUSrc": 0,
            "MemWrite": 0,
            "RegWrite": 1,
            "ResultSrc": 0,
            "ImmSrc": 0
        }
    elif isinstance(instr_obj, InstrucaoI):
        if instr_obj.opcode == 0x03:
            return {
                "ALUSrc": 1,
                "MemWrite": 0,
                "RegWrite": 1,
                "ResultSrc": 1,
                "ImmSrc": 0
            }
        else:
            return {
                "ALUSrc": 1,
                "MemWrite": 0,
                "RegWrite": 1,
                "ResultSrc": 0,
                "ImmSrc": 0
            }
    elif isinstance(instr_obj, InstrucaoS):
        return {
            "ALUSrc": 1,
            "MemWrite": 1,
            "RegWrite": 0,
            "ResultSrc": 0,
            "ImmSrc": 1
        }
    return {
        "ALUSrc": 0,
        "MemWrite": 0,
        "RegWrite": 0,
        "ResultSrc": 0,
        "ImmSrc": 0
    }

def executa_ula(operando1: int, operando2: int, funct3: int, funct7: int) -> int:
    if funct3 == 0x0:
        if funct7 == 0x0:
            return operando1 + operando2
        elif funct7 == 0x20:
            return operando1 - operando2
        elif funct7 == 0x1:
            return operando1 * operando2
    elif funct3 == 0x1:
        return operando1 << operando2
    elif funct3 == 0x2:
        return int(operando1 < operando2)
    elif funct3 == 0x6:
        return operando1 | operando2
    elif funct3 == 0x7:
        return operando1 & operando2
    return 0

def decode_binary(bin_str: str):
    bin_clean = bin_str.replace(" ", "")
    if len(bin_clean) != 32:
        return None
    
    opcode = int(bin_clean[25:32], 2)
    rd = int(bin_clean[20:25], 2)
    funct3 = int(bin_clean[17:20], 2)
    rs1 = int(bin_clean[12:17], 2)
    rs2 = int(bin_clean[7:12], 2)
    funct7 = int(bin_clean[0:7], 2)
    
    if opcode == 0x33:
        return {"tipo": "R", "opcode": opcode, "rd": rd, "funct3": funct3, "rs1": rs1, "rs2": rs2, "funct7": funct7}
    elif opcode == 0x13 or opcode == 0x03:
        imm = int(bin_clean[0:12], 2)
        imm = sign_extend_12(imm)
        return {"tipo": "I", "opcode": opcode, "rd": rd, "funct3": funct3, "rs1": rs1, "imm": imm}
    elif opcode == 0x23:
        imm_11_5 = int(bin_clean[0:7], 2)
        imm_4_0 = int(bin_clean[20:25], 2)
        imm = (imm_11_5 << 5) | imm_4_0
        imm = sign_extend_12(imm)
        return {"tipo": "S", "opcode": opcode, "funct3": funct3, "rs1": rs1, "rs2": rs2, "imm": imm}
    
    return None

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
        
        # Mapeamento de nomes para índices (x0-x31)
        self.reg_map = {f"x{i}": i for i in range(32)}
        # Aliases opcionais
        self.reg_map.update({
            "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4,
            "t0": 5, "t1": 6, "t2": 7,
            "s0": 8, "s1": 9,
            "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17,
            "s2": 18, "s3": 19, "s4": 20, "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25, "s10": 26, "s11": 27,
            "t3": 28, "t4": 29, "t5": 30, "t6": 31
        })
        
        # Inicializa 32 registradores (x0-x31)
        self.regs = [0] * 32
        self.memoria: Dict[str, int] = {}
        self.binarios: list[str] = []

    def reg_to_index(self, reg: str) -> int:
        reg_clean = reg.strip("$,")
        if reg_clean in self.reg_map:
            return self.reg_map[reg_clean]
        if reg_clean.startswith("x") and reg_clean[1:].isdigit():
            idx = int(reg_clean[1:])
            if 0 <= idx < 32:
                return idx
        return 0

    def get_reg(self, reg: str) -> int:
        idx = self.reg_to_index(reg)
        return self.regs[idx]

    def set_reg(self, reg: str, valor: int):
        idx = self.reg_to_index(reg)
        if idx == 0:
            return
        self.regs[idx] = valor

    def reg_to_bin(self, reg: str) -> str:
        idx = self.reg_to_index(reg)
        return format(idx, '05b')
    
    def regs_to_dict(self) -> Dict[str, int]:
        result = {}
        for nome, idx in self.reg_map.items():
            if nome.startswith("x") or nome in ["zero", "ra", "sp", "gp", "tp"]:
                result[nome] = self.regs[idx]
        return result
        
    def passo(self) -> bool:
        # FETCH: buscar instrução
        if self.pc >= len(self.instrucoes):
            return True

        instr = self.instrucoes[self.pc]
        partes = instr.replace(",", " ").split()
        if not partes:
            self.pc += 1
            return self.pc >= len(self.instrucoes)

        op = partes[0].lower()
        try:
            # DECODE: parse da instrução
            if op == "li":
                _, reg, val = partes
                self.set_reg(reg, int(val))
                self.saida.append(f"{reg} = {int(val)}")
                instr_obj = parse_addi(["addi", reg, "x0", val], self.reg_to_index)
                self.binarios.append(instr_obj.to_binary())

            elif op == "add":
                instr_obj = parse_add(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                # EXECUTE: ULA
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                # WRITE BACK: atualizar registrador
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "addi":
                instr_obj = parse_addi(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                resultado = executa_ula(self.regs[rs1_idx], instr_obj.imm, instr_obj.funct3, 0)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "sub":
                instr_obj = parse_sub(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "mult":
                instr_obj = parse_mult(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "and":
                instr_obj = parse_and(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "or":
                instr_obj = parse_or(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "sll":
                instr_obj = parse_sll(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                shamt = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], shamt, instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "slt":
                instr_obj = parse_slt(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                rs2_idx = instr_obj.rs2
                resultado = executa_ula(self.regs[rs1_idx], self.regs[rs2_idx], instr_obj.funct3, instr_obj.funct7)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "slti":
                instr_obj = parse_slti(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                resultado = executa_ula(self.regs[rs1_idx], instr_obj.imm, instr_obj.funct3, 0)
                self.regs[rd_idx] = resultado
                self.saida.append(f"x{rd_idx} = {resultado}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "lw":
                instr_obj = parse_lw(partes, self.reg_to_index)
                rd_idx = instr_obj.rd
                rs1_idx = instr_obj.rs1
                # EXECUTE: calcular endereço
                addr = executa_ula(self.regs[rs1_idx], instr_obj.imm, 0x0, 0x0)
                addr_str = str(addr)
                # MEMORY ACCESS: ler da memória
                valor = self.memoria.get(addr_str, 0)
                # WRITE BACK: atualizar registrador
                self.regs[rd_idx] = valor
                self.saida.append(f"x{rd_idx} carregado de {addr_str} = {valor}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "sw":
                instr_obj = parse_sw(partes, self.reg_to_index)
                rs2_idx = instr_obj.rs2
                rs1_idx = instr_obj.rs1
                # EXECUTE: calcular endereço
                addr = executa_ula(self.regs[rs1_idx], instr_obj.imm, 0x0, 0x0)
                addr_str = str(addr)
                valor = self.regs[rs2_idx]
                # MEMORY ACCESS: escrever na memória
                self.memoria[addr_str] = valor
                self.saida.append(f"endereço {addr_str} armazenado = {valor}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "ecall":
                instr_obj = InstrucaoEcall()
                a0_idx = 10
                valor = self.regs[a0_idx]
                self.saida.append(f"[ECALL] Imprimir inteiro: {valor}")
                self.binarios.append(instr_obj.to_binary())

            elif op == "imprimir":
                tipo = partes[1].lower() if len(partes) > 1 else ''
                if tipo == "inteiro":
                    if len(partes) >= 3:
                        reg = partes[2]
                        valor = self.get_reg(reg)
                        self.saida.append(f"[IMPRIMIR] {reg} = {valor}")
                    else:
                        a0_idx = 10
                        valor = self.regs[a0_idx]
                        self.saida.append(f"[IMPRIMIR] a0 = {valor}")
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

        # Incrementar PC (+4 bytes, mas como cada linha é uma instrução, +1)
        self.pc += 1
        return self.pc >= len(self.instrucoes)

    def estado(self) -> Dict:
        return {
            "registradores": self.regs_to_dict(),
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
