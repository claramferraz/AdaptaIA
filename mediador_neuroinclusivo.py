"""
Mediador neuroinclusivo (sem conexão com IA).

Fluxo:
    1. O usuário escreve o que precisa que a IA faça.
    2. O programa gera um prompt adequado às preferências dele.
    3. O usuário copia o prompt e envia à IA que preferir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Perfil(str, Enum):
    TDAH = "tdah"
    AUTISMO = "autismo"
    DISLEXIA = "dislexia"
    GERAL = "geral"


# Regras de formatação da resposta, escritas em 1ª pessoa (quem fala é o usuário)
REGRAS_PERFIL: dict[Perfil, list[str]] = {
    Perfil.TDAH: [
        "Comece pela resposta ou ação principal, sem introdução longa.",
        "Divida em passos numerados e pequenos.",
        "Destaque em negrito a ação mais importante.",
        "Evite blocos longos de texto.",
    ],
    Perfil.AUTISMO: [
        "Use linguagem literal e clara, sem ironia, metáforas ou expressões figuradas.",
        "Explique o que vai acontecer e por quê.",
        "Use sempre a mesma estrutura: objetivo, passos, resultado esperado.",
        "Se algo estiver ambíguo, pergunte antes de supor.",
    ],
    Perfil.DISLEXIA: [
        "Use frases curtas e palavras simples.",
        "Faça parágrafos de no máximo 3 linhas.",
        "Use listas e bastante espaçamento.",
        "Explique termos pouco comuns quando precisar usá-los.",
    ],
    Perfil.GERAL: [
        "Seja claro e objetivo.",
    ],
}


@dataclass
class Preferencias:
    perfis: list[Perfil] = field(default_factory=lambda: [Perfil.GERAL])
    max_palavras: int | None = None
    usar_listas: bool = True
    tom: str = "acolhedor"
    extras: list[str] = field(default_factory=list)   # regras livres do usuário


class MediadorNeuroInclusivo:
    def __init__(self, preferencias: Preferencias | None = None):
        self.preferencias = preferencias or Preferencias()
        self.historico: list[tuple[str, str]] = []   # (pedido, prompt)

    def _regras(self) -> list[str]:
        p = self.preferencias
        regras: list[str] = []
        for perfil in p.perfis:
            for r in REGRAS_PERFIL[perfil]:
                if r not in regras:
                    regras.append(r)
        regras.append(f"Use um tom {p.tom}.")
        if p.usar_listas:
            regras.append("Prefira listas quando isso ajudar na clareza.")
        if p.max_palavras:
            regras.append(f"Responda com no máximo {p.max_palavras} palavras.")
        regras.extend(p.extras)
        regras.append("Responda em português do Brasil.")
        return regras

    def gerar_prompt(self, pedido: str) -> str | None:
        """Transforma o pedido do usuário em um prompt pronto para enviar à IA."""
        pedido = pedido.strip()
        if not pedido:
            return None

        regras = "\n".join(f"- {r}" for r in self._regras())
        prompt = (
            "Preciso da sua ajuda com a seguinte tarefa:\n\n"
            f"{pedido}\n\n"
            "Para que a resposta seja acessível para mim, siga estas regras:\n"
            f"{regras}"
        )
        self.historico.append((pedido, prompt))
        return prompt

    def ultimo_prompt(self) -> str | None:
        return self.historico[-1][1] if self.historico else None

    def salvar_ultimo(self, caminho: str = "prompt.txt") -> None:
        prompt = self.ultimo_prompt()
        if prompt:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(prompt)

    def atualizar_preferencias(self, **kwargs) -> None:
        for chave, valor in kwargs.items():
            if hasattr(self.preferencias, chave):
                setattr(self.preferencias, chave, valor)


# ---------- uso interativo no terminal ----------
def _escolher_perfis() -> list[Perfil]:
    print("Perfis disponíveis:", ", ".join(p.value for p in Perfil))
    entrada = input("Escolha um ou mais (separados por vírgula) [geral]: ").strip().lower()
    if not entrada:
        return [Perfil.GERAL]
    escolhidos = []
    for nome in entrada.split(","):
        try:
            escolhidos.append(Perfil(nome.strip()))
        except ValueError:
            print(f"  '{nome.strip()}' não existe, ignorado.")
    return escolhidos or [Perfil.GERAL]


def main() -> None:
    perfis = _escolher_perfis()
    limite = input("Limite de palavras na resposta (Enter para sem limite): ").strip()
    mediador = MediadorNeuroInclusivo(
        Preferencias(perfis=perfis, max_palavras=int(limite) if limite.isdigit() else None)
    )

    print("\nDescreva o que você precisa pedir à IA (digite 'sair' para encerrar).\n")
    while True:
        pedido = input("> ").strip()
        if pedido.lower() == "sair":
            break
        prompt = mediador.gerar_prompt(pedido)
        if prompt:
            print("\n----- COPIE O PROMPT ABAIXO E ENVIE À IA -----\n")
            print(prompt)
            print("\n----------------------------------------------\n")


if __name__ == "__main__":
    main()