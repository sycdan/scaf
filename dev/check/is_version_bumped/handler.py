import logging

from dev.check.is_version_bumped.query import IsVersionBumped

logger = logging.getLogger(__name__)


def handle(query: IsVersionBumped) -> bool:
  """Returns True if version has been bumped for main branch push."""

  try:
    from dev.bump_version.command import BumpVersion

    result = BumpVersion(dry_run=True).execute()
    if result == "NEEDS_BUMP":
      logger.error("Version bump is required before pushing to main")
      print("💡 Run dev.bump-version")
      return False
    logger.info("Version is up to date: %s", result)
    return True
  except Exception as e:
    logger.error("Version check failed: %s", e)
    return False
