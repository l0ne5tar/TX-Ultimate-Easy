import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import select
from esphome.const import (
    CONF_ID,
    CONF_INITIAL_OPTION,
)

from .. import tx_ultimate_easy_ns

DEPENDENCIES = ["tx_ultimate_easy"]

RtttlSelect = tx_ultimate_easy_ns.class_(
    "RtttlSelect", select.Select, cg.Component
)

CONF_RTTTL_TYPE = "rtttl_type"
RTTTL_TYPE_INSTRUMENT = "instrument"
RTTTL_TYPE_TUNE = "tune"

CONFIG_SCHEMA = select.select_schema(RtttlSelect).extend({
    cv.Required(CONF_RTTTL_TYPE): cv.one_of(RTTTL_TYPE_INSTRUMENT, RTTTL_TYPE_TUNE),
    cv.Optional(CONF_INITIAL_OPTION): cv.string,
}).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    cg.add(var.set_type(config[CONF_RTTTL_TYPE]))
    cg.add(var.set_initial_option(config.get(CONF_INITIAL_OPTION, "")))
    await cg.register_component(var, config)
    await select.register_select(var, config, options=[])
