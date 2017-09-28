from asapp.common import config


ASAPP_ROOT = config.env_vars['ASAPP_ROOT']
ASAPP_PRODML_ROOT = config.env_vars['ASAPP_PRODML_ROOT']
ASAPP_MLENG_ROOT = config.env_vars['ASAPP_MLENG_ROOT']
ASAPP_SRS_ROOT = config.env_vars['ASAPP_SRS_ROOT']
ASAPP_COMCAST_SRS_ROOT = config.env_vars['ASAPP_COMCAST_SRS_ROOT']


CLIENT_FULL_NAMES = {
    'condor': 'comcast',
    'spear': 'sprint'
}
