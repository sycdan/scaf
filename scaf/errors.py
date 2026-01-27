class ActionFailed(RuntimeError):
  def __init__(self, message: str, *, code: str, context: dict | None = None):
    super().__init__(message)
    self.code = code
    self.context = context or {}
