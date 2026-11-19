import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from lib import markdown


class InlineTest(unittest.TestCase):
    def test_code_span_preserves_pipes(self):
        out = markdown.render_inline(r"a `x \| y` b")
        self.assertIn("<code>x \\| y</code>", out)

    def test_bold_and_italic(self):
        self.assertIn("<strong>b</strong>", markdown.render_inline("**b**"))
        self.assertIn("<em>i</em>", markdown.render_inline("*i*"))

    def test_html_is_escaped(self):
        out = markdown.render_inline("<script>alert(1)</script>")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_link_to_md_becomes_html(self):
        out = markdown.render_inline("[x](docs/a.md)")
        self.assertIn('href="docs/a.html"', out)

    def test_external_link_kept_absolute(self):
        out = markdown.render_inline("[x](https://e.example/a)")
        self.assertIn('href="https://e.example/a"', out)


class BlockTest(unittest.TestCase):
    def test_atx_headings(self):
        out = markdown.render("# A\n\n## B\n")
        self.assertIn("<h1", out)
        self.assertIn("<h2", out)

    def test_pipe_table_alignment_row_consumed(self):
        src = "| a | b |\n| --- | ---: |\n| 1 | 2 |\n"
        out = markdown.render(src)
        self.assertEqual(out.count("<table>"), 1)
        self.assertEqual(out.count("<th"), 2)
        self.assertEqual(out.count("<td"), 2)
        self.assertIn('style="text-align:right"', out)

    def test_table_with_escaped_pipe_in_code_span(self):
        src = "| a | b |\n| --- | --- |\n| `x \\| y` | z |\n"
        out = markdown.render(src)
        self.assertEqual(out.count("<td"), 2)

    def test_fenced_code_gets_language_class(self):
        out = markdown.render("```bash\nls\n```\n")
        self.assertIn('class="language-bash"', out)
        self.assertIn("ls", out)

    def test_fenced_code_content_not_parsed(self):
        out = markdown.render("```\n# not a heading\n```\n")
        self.assertNotIn("<h1", out)

    def test_unclosed_fence_does_not_swallow_following_text(self):
        out = markdown.render("```\nabc\n")
        self.assertIn("<pre", out)

    def test_evidence_class_wrapped(self):
        out = markdown.render("Claim one **F** and two [F] and three [N]\n")
        self.assertIn('class="evidence"', out)

    def test_ordered_and_unordered_lists(self):
        self.assertIn("<ul>", markdown.render("- a\n- b\n"))
        self.assertIn("<ol>", markdown.render("1. a\n2. b\n"))

    def test_blockquote(self):
        self.assertIn("<blockquote>", markdown.render("> quoted\n"))

    def test_crlf_input(self):
        out = markdown.render("# A\r\n\r\ntext\r\n")
        self.assertIn("<h1", out)

    def test_idempotent_on_empty(self):
        self.assertEqual(markdown.render(""), "")


if __name__ == "__main__":
    unittest.main()
