{
    "name": "Transmedical Customization",
    "version": "13.0.0.0.1",
    "summary": "Transmedical Customization",
    "description": "Transmedical Customization",
    "category": "Partners",
    "author": "PagarEsFacil, Christopher Ormaza",
    "website": "https://planproecuador.com",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "l10n_ec_niif",
        "muk_rest",
        "contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron_jobs.xml",
        "views/external_invoice_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
    },
}
