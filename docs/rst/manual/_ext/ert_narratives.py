from sphinx.application import Sphinx
from pathlib import Path
import os
import sys
from docutils import nodes, statemachine
from os.path import basename
from docutils.parsers.rst import Directive
import shutil

NARRATIVE_DIR = "NARRATIVE_DIR"

TMPL = """.. datatemplate:json:: {source_path}
    :template: ert_narratives.tmpl"""


class ErtNarratives(Directive):
    """Find narratives and render them readable."""

    has_content = False

    def run(self):
        tab_width = self.options.get(
            "tab-width", self.state.document.settings.tab_width
        )
        source = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1
        )
        narrative_dir = os.getenv(NARRATIVE_DIR)
        dest_dir = Path(source).parent
        if not narrative_dir:
            return []
        try:
            p = Path(narrative_dir).glob("*.json")
            files = [x for x in p if x.is_file()]
            if not files:
                return [nodes.paragraph(text="Found no narratives.")]
            lines = []
            for file in files:
                shutil.copyfile(file, dest_dir / file.name)
                lines.extend(
                    statemachine.string2lines(
                        TMPL.format(source_path=file.name),
                        tab_width,
                        convert_whitespace=True,
                    )
                )
            self.state_machine.insert_input(lines, source)
            return []
        except Exception:
            return [
                nodes.error(
                    None,
                    nodes.paragraph(
                        text=f"Failed to produce ert_narratives in {basename(source)}:{self.lineno}:"
                    ),
                    nodes.paragraph(text=str(sys.exc_info()[1])),
                )
            ]


def setup(app: Sphinx):
    app.setup_extension("sphinxcontrib.datatemplates")
    app.add_css_file("css/narratives.css")
    app.add_directive("ert_narratives", ErtNarratives)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
