"""Sheet modules for the Social Media Content Calendar & Analytics Planner.

* **Register modules** expose a ``NAME`` and a ``spec(cfg)`` returning a
  :class:`~social_media_spreadsheet.layout.SheetSpec`.  Some also expose
  ``decorate(sheet, fmts, cfg)`` for totals / callouts.
* **Page modules** expose a ``build(book, fmts, cfg, reg)`` function and return
  the finished :class:`~social_media_spreadsheet.writer.SheetWriter`.
"""
