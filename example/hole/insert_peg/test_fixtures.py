from example.hole.insert_peg.command import InsertPeg


def _execute(payload: dict) -> InsertPeg.Result:
  """Build and execute an InsertPeg command from a raw payload dict."""
  return InsertPeg(**payload).execute()


def test_peg_fits_in_hole(payload):
  result = _execute(payload)
  assert result.success, f"peg {payload['peg']} did not fit in hole {payload['hole']}"
