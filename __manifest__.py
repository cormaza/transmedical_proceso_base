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
        "partner_contact_birthdate",
        "l10n_ec_reports",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/groups.xml",
        "data/cron_jobs.xml",
        "data/sequence_data.xml",
        "report/medical_attention_order_report.xml",
        "report/medical_liquidation_report.xml",
        "data/mail_template_medical_liquidation.xml",
        "data/mail_template_medical_attention_order.xml",
        "data/medical_atention_order_data.xml",
        "data/medical_liquidation_data.xml",
        "views/root_menu.xml",
        "views/medical_liquidation_view.xml",
        "views/medical_attention_order_view.xml",
        "views/partner_view.xml",
        "views/external_invoice_view.xml",
        "views/medical_procedure_view.xml",
        "views/portal_medical_atention_order_template.xml",
        "views/portal_medical_liquidation_template.xml",
        "views/medical_diagnostic_view.xml",
        "views/medical_procedure_type_view.xml",
        "views/contract_contract_view.xml",
        "views/medical_beneficts_view.xml",
        "views/medical_speciality_view.xml",
        "views/medical_relationship_view.xml",
        "views/res_config_settings_view.xml",
        "views/account_move_view.xml",
        "views/product_product_view.xml",
        "views/medical_coverage_plan_view.xml",
        "views/medical_copago_limit_view.xml",
        "views/medical_liquidation_invoice_document_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "external_dependencies": {
        "python": [],
    },
}
