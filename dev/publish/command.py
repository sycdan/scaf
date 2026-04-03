from dataclasses import dataclass, field


@dataclass
class Publish:
  """Build and publish the package to PyPI or TestPyPI.

  Reads TWINE_REPOSITORY and TWINE_PASSWORD from .env in the project root.
  TWINE_REPOSITORY defaults to 'testpypi' if not set.
  Username is always '__token__'.
  """

  skip_build: bool = field(default=False, doc="Skip building; use existing dist/ artifacts.")

  def execute(self):
    from dev.publish.handler import handle

    return handle(self)
