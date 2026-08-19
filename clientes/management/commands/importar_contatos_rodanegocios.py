import sqlite3

from django.core.management.base import BaseCommand, CommandError

from clientes.models import EmpresaCliente, Contato


class Command(BaseCommand):
    help = (
        "Importa dados de Representante (app rodanegocios) para Contato "
        "(app clientes), a partir de um arquivo db.sqlite3 externo. "
        "Requer que as empresas já tenham sido importadas antes "
        "(via importar_empresas_rodanegocios.py)."
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

        # 1) Monta o mapa id_origem -> (cnpj, nome) a partir de core_empresa,
        # para conseguirmos localizar a EmpresaCliente correspondente.
        try:
            cursor.execute("SELECT id, nome, cnpj FROM core_empresa")
        except sqlite3.OperationalError as exc:
            conn.close()
            raise CommandError(f"Erro ao consultar 'core_empresa': {exc}")

        mapa_empresas = {}
        for linha in cursor.fetchall():
            cnpj = (linha["cnpj"] or "").strip()
            nome = (linha["nome"] or "").strip()
            mapa_empresas[linha["id"]] = {"cnpj": cnpj, "nome": nome}

        # 2) Lê os representantes.
        tabela = "core_representante"
        try:
            cursor.execute(
                f"SELECT nome, cargo, email, telefone, empresa_id FROM {tabela}"
            )
        except sqlite3.OperationalError as exc:
            conn.close()
            raise CommandError(
                f"Erro ao consultar a tabela '{tabela}': {exc}\n"
                "Confira o nome real da tabela no banco de origem."
            )

        linhas = cursor.fetchall()
        conn.close()

        criados = 0
        atualizados = 0
        pulados = 0
        erros = 0

        for linha in linhas:
            nome = (linha["nome"] or "").strip()
            try:
                dados_empresa_origem = mapa_empresas.get(linha["empresa_id"])

                if not dados_empresa_origem:
                    pulados += 1
                    self.stderr.write(
                        self.style.WARNING(
                            f"Representante '{nome}': empresa_id "
                            f"{linha['empresa_id']} não encontrada em core_empresa."
                        )
                    )
                    continue

                cnpj = dados_empresa_origem["cnpj"]
                nome_empresa = dados_empresa_origem["nome"]

                # Mesma lógica de correspondência usada na importação de empresas:
                # tenta por CNPJ, cai para nome_fantasia.
                filtro_empresa = (
                    {"cnpj": cnpj} if cnpj else {"nome_fantasia": nome_empresa}
                )

                try:
                    empresa = EmpresaCliente.objects.get(**filtro_empresa)
                except EmpresaCliente.DoesNotExist:
                    pulados += 1
                    self.stderr.write(
                        self.style.WARNING(
                            f"Representante '{nome}': EmpresaCliente não "
                            f"encontrada para {filtro_empresa} "
                            "(empresa ainda não importada?)."
                        )
                    )
                    continue
                except EmpresaCliente.MultipleObjectsReturned:
                    pulados += 1
                    self.stderr.write(
                        self.style.WARNING(
                            f"Representante '{nome}': mais de uma EmpresaCliente "
                            f"encontrada para {filtro_empresa}, pulando."
                        )
                    )
                    continue

                email = (linha["email"] or "").strip()
                cargo = (linha["cargo"] or "").strip()
                telefone = (linha["telefone"] or "").strip()

                dados = {
                    "cargo": cargo,
                    "email": email,
                    "telefone": telefone,
                }

                if dry_run:
                    self.stdout.write(
                        f"[DRY-RUN] {nome} ({empresa}) -> {dados}"
                    )
                    continue

                # Usa email como chave de correspondência quando existir;
                # caso contrário, cai para nome dentro da mesma empresa.
                if email:
                    filtro_contato = {"empresa": empresa, "email": email}
                else:
                    filtro_contato = {"empresa": empresa, "nome": nome}

                obj, criado = Contato.objects.update_or_create(
                    **filtro_contato, defaults={**dados, "nome": nome}
                )
                if criado:
                    criados += 1
                else:
                    atualizados += 1

            except Exception as exc:
                erros += 1
                self.stderr.write(
                    self.style.WARNING(f"Erro ao importar '{nome}': {exc}")
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"Simulação concluída: {len(linhas)} registros lidos.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Importação concluída: {criados} criados, "
                    f"{atualizados} atualizados, {pulados} pulados, {erros} erros."
                )
            )
            