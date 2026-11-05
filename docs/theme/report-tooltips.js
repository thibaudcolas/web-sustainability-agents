// Material supplies focus/hover tooltips; add Escape dismissal without moving focus.
(() => {
  const dismissed = new Map();
  const triggerSelector = ".audit-guideline";

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    for (const link of document.querySelectorAll(
      `${triggerSelector}[aria-describedby]`,
    )) {
      for (const id of link.getAttribute("aria-describedby").split(/\s+/)) {
        const tooltip = document.getElementById(id);
        if (!tooltip?.matches(".md-tooltip, .md-tooltip2")) continue;
        if (!link.matches(":hover, :focus") && !tooltip.matches(":hover"))
          continue;
        tooltip.setAttribute("data-audit-dismissed", "");
        dismissed.set(link, {
          tooltip,
          leftTrigger: !link.matches(":hover, :focus"),
        });
      }
    }
  });

  for (const event of ["pointerout", "focusout"]) {
    document.addEventListener(event, () => {
      requestAnimationFrame(() => {
        for (const [link, state] of dismissed) {
          if (!link.isConnected) dismissed.delete(link);
          else if (!link.matches(":hover, :focus")) state.leftTrigger = true;
        }
      });
    });
  }

  // Suppress the whole activation; a fresh visit to the trigger can show it again.
  for (const event of ["pointerover", "focusin"]) {
    document.addEventListener(event, (e) => {
      const link = e.target.closest?.(triggerSelector);
      const state = dismissed.get(link);
      if (!state?.leftTrigger || link.contains(e.relatedTarget)) return;
      state.tooltip.removeAttribute("data-audit-dismissed");
      dismissed.delete(link);
    });
  }
})();
