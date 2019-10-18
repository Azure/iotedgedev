class Constants:
    default_config_folder = "config"
    default_modules_folder = "modules"
    default_deployment_template_file = "deployment.template.json"
    default_deployment_debug_template_file = "deployment.debug.template.json"
    default_platform = "amd64"
    deployment_template_suffix = ".template.json"
    deployment_template_schema_version = "1.0.0"
    moduledir_placeholder_pattern = r'\${MODULEDIR<(.+)>(\..+)?}'
    deployment_template_schema_url = "http://json.schemastore.org/azure-iot-edge-deployment-template-2.0"
    deployment_manifest_schema_url = "http://json.schemastore.org/azure-iot-edge-deployment-2.0"
