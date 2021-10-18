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
        "security/groups.xml",
        "data/cron_jobs.xml",
        "data/sequence_data.xml",
        "views/root_menu.xml",
        "views/medical_liquidation_view.xml",
        "views/medical_attention_order_view.xml",
        "views/partner_view.xml",
        "views/external_invoice_view.xml",
        "views/medical_procedure_view.xml",
        "views/medical_diagnostic_view.xml",
        "views/medical_speciality_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
    },
}
