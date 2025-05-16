
import splunk_ta_cisco_catalyst_center_declare

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    MultipleModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunk_aoblib.rest_migration import ConfigMigrationHandler

util.remove_http_proxy_env_vars()


fields_logging = [
    field.RestField(
        'loglevel',
        required=False,
        encrypted=False,
        default='INFO',
        validator=None
    )
]
fields_additional_parameters = [
    field.RestField(
        "ca_certs_path",
        required=False,
        encrypted=False,
        default="",
        validator=None,
    ),
    field.RestField(
        "verify_ssl",
        required=False,
        encrypted=False,
        default="",
        validator=None,
    ),
]
model_logging = RestModel(fields_logging, name='logging')
model_additional_parameters = RestModel(
    fields_additional_parameters, name="additional_parameters"
)


endpoint = MultipleModel(
    'splunk_ta_cisco_catalyst_center_settings',
    models=[
        model_logging,
        model_additional_parameters
    ],
)


if __name__ == '__main__':
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
