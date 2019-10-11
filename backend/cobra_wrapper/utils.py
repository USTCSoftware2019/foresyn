import io
import cobra


def load_sbml(sbml_content: str) -> cobra.Model:
    sbml_file = io.StringIO(sbml_content)
    return cobra.io.read_sbml_model(sbml_file)


def dump_sbml(cobra_model: cobra.Model) -> str:
    sbml_file = io.StringIO()
    cobra.io.write_sbml_model(cobra_model, sbml_file)
    sbml_file.seek(0)
    return sbml_file.read()
