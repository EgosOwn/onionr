import notifier


def update_event(bl):
    """Show update notification if available, return bool of if update happened"""
    if not bl.isSigner(onionrvalues.UPDATE_SIGN_KEY): raise onionrexceptions.InvalidUpdate
    onionr.notifier.notify(message="A new Onionr update is available. Stay updated to remain secure.")
