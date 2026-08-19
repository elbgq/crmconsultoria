import sqlite3

from django.core.management.base import BaseCommand, CommandError

from clientes.models import EmpresaCliente


class Command(BaseCommand):
    help = (
        "Importa dados de Empresa (app rodanegocios) para EmpresaCliente "
        "(app clientes), a partir de um arquivo db.sqlite3 externo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "caminho_db",
            type=str,
            nargs="?",
            default=r"D:\DATA\Aplicativos\Santos\rodanegocios\db.sqlite3",
            help="Caminho completo para o db.sqlite3 do projeto rodanegocios",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula a importação sem gravar nada no banco de destino",
        )

    def handle(self, *args, **options):
        caminho = options["caminho_db"]
        dry_run = options["dry_run"]

        try:
            conn = sqlite3.connect(caminho)
        except sqlite3.Error as exc:
            raise CommandError(f"Não foi possível abrir o banco de origem: {exc}")

        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Ajuste o nome da tabela se necessário. Por convenção do Django,
        # costuma ser "<app_label>_<nomemodelo minúsculo>".
        tabela = "core_empresa"

        try:
            cursor.execute(
                f"SELECT nome, cnpj, site, segmento, modalidade FROM {tabela}"
            )
        except sqlite3.OperationalError as exc:
            conn.close()
            raise CommandError(
                f"Erro ao consultar a tabela '{tabela}': {exc}\n"
                "Confira o nome real da tabela no banco de origem."
            )

        linhas = cursor.fetchall()
        conn.close()

        criadas = 0
        atualizadas = 0
        erros = 0

        for linha in linhas:
            try:
                cnpj = (linha["cnpj"] or "").strip()
                nome = (linha["nome"] or "").strip()

                dados = {
                    "razao_social": nome,      # ajuste se houver campo próprio
                    "nome_fantasia": nome,
                    "website": (linha["site"] or "").strip(),
                    "setor": (linha["segmento"] or "").strip(),
                    "modalidade": self._mapear_modalidade(linha["modalidade"]),
                }

                if dry_run:
                    self.stdout.write(f"[DRY-RUN] {cnpj or '(sem cnpj)'} -> {dados}")
                    continue

                # Usa cnpj como chave de correspondência quando existir;
                # caso contrário, cai para nome_fantasia.
                filtro = {"cnpj": cnpj} if cnpj else {"nome_fantasia": nome}

                obj, criado = EmpresaCliente.objects.update_or_create(
                    **filtro, defaults=dados
                )
                if criado:
                    criadas += 1
                else:
                    atualizadas += 1

            except Exception as exc:
                erros += 1
                self.stderr.write(
                    self.style.WARNING(f"Erro ao importar '{linha['nome']}': {exc}")
                )

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Simulação concluída: {len(linhas)} registros lidos."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Importação concluída: {criadas} criadas, {atualizadas} atualizadas, {erros} erros."
                )
            )

    def _mapear_modalidade(self, valor_origem):
        """Converte o valor de 'modalidade' da origem para as choices de EmpresaCliente."""
        if not valor_origem:
            return EmpresaCliente.Modalidade.VENDEDOR

        valor = str(valor_origem).strip().lower()

        if valor in ("comprador", "compradora", "buyer"):
            return EmpresaCliente.Modalidade.COMPRADOR
        if valor in ("vendedor", "vendedora", "seller"):
            return EmpresaCliente.Modalidade.VENDEDOR

        # valor desconhecido: mantém o padrão e avisa no console
        self.stdout.write(
            self.style.WARNING(f"Modalidade desconhecida '{valor_origem}', usando VENDEDOR")
        )
        return EmpresaCliente.Modalidade.VENDEDOR
    