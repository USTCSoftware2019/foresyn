import io
import cobra


def load_sbml(sbml_content: str) -> cobra.Model:
    sbml_file = io.StringIO(sbml_content)
    return cobra.io.read_sbml_model(sbml_file)
