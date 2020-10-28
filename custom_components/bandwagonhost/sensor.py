import logging

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS, 
    CONF_NAME, 
    CONF_SCAN_INTERVAL, 
    EVENT_HOMEASSISTANT_START,
    CONF_RESOURCES,
    CONF_TYPE,
    DATA_GIBIBYTES,
    DATA_MEBIBYTES,
    DATA_RATE_MEGABYTES_PER_SECOND,
    PERCENTAGE,
    STATE_OFF,
    STATE_ON,
    TEMP_CELSIUS,
    
)
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
import requests
import json

from homeassistant.core import callback
from datetime import timedelta,datetime

_Log=logging.getLogger(__name__)

REQUIREMENTS = ['requests']
DEFAULT_NAME = '搬瓦工状态'
CONF_VEID = 'veid'
CONF_API_KEY = 'api_key'

# Schema: [name, unit of measurement, icon, device class, flag if mandatory arg]
MONITORED_CONDITIONS = {
    'VPS_STATE' : ['Vps State','','mdi:cloud-search', None, False],
    'CURRENT_BANDWIDTH_USED': ['Current Bandwidth Used', DATA_GIBIBYTES,'mdi:cloud-tags', None, False],
    'CURRENT_BANDWIDTH_ALL': ['Current Bandwidth All', DATA_GIBIBYTES,'mdi:cloud-tags', None, False],
    'DISK_USED': ['DISK USED', DATA_GIBIBYTES, 'mdi:disc', None, False],
    'DISK_ALL': ['DISK All', DATA_GIBIBYTES, 'mdi:disc', None, False],
    'RAM_USED':['RAM USED', DATA_MEBIBYTES, 'mdi:responsive', None, False],
    'RAM_All':['RAM All', DATA_MEBIBYTES, 'mdi:responsive', None, False],
    'SWAP_USED':['SWAP USED', DATA_MEBIBYTES, 'mdi:responsive', None, False],
    'SWAP_All':['SWAP All', DATA_MEBIBYTES, 'mdi:responsive', None, False],
    'VPS_LOAD_1M':['VPS LOAD 1M', '', 'mdi:cpu-32-bit', None, False],
    'VPS_LOAD_5M':['VPS LOAD 5M', '', 'mdi:cpu-32-bit', None, False],
    'VPS_LOAD_15M':['VPS LOAD 15M', '', 'mdi:cpu-32-bit', None, False],
    'VPS_IP':['VPS IP', '', 'mdi:ip', None, False],
    'SSH_PORT':['SSH PORT', '', 'mdi:swap-vertical-bold', None, False],
    'HOSTNAME':['HOSTNAME', '', 'mdi:identifier', None, False],
    'OS':['OS', '', 'mdi:ubuntu', None, False],
    'NODE_LOCATION':['NODE LOCATION', '', 'mdi:map-marker', None, False],
    'DATA_NEXT_RESET':['DATA NEXT RESET', '', 'mdi:calendar-range', None, False],
}

SCAN_INTERVAL = timedelta(seconds=1200)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_VEID): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS,
                 default=list(MONITORED_CONDITIONS)):
    vol.All(cv.ensure_list, [vol.In(MONITORED_CONDITIONS)])
})


API_URL_LiveServiceInfo = "https://api.64clouds.com/v1/getLiveServiceInfo?"
API_URL_ServiceInfo = "https://api.64clouds.com/v1/getServiceInfo?"


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Setup the sensor platform."""
    veid = config.get(CONF_VEID)
    api_key = config.get(CONF_API_KEY)
    sensor_name = config.get(CONF_NAME)
    monitored_conditions = config.get(CONF_MONITORED_CONDITIONS)

    sensors = []

    for condition in monitored_conditions:

        sensors.append(BandwagonHostSensor(sensor_name, veid, api_key, condition))

    async_add_entities(sensors)


class BandwagonHostSensor(Entity):

    def __init__(self,sensor_name,veid, api_key, condition):
        
        if(sensor_name == '搬瓦工状态'):
            sensor_name = condition.replace('ATTR_','').replace('_', ' ')
        else:
            sensor_name = sensor_name
        self.attributes = {}
        self._state = None
        self._name = sensor_name
        self._condition = condition
        self._veid = veid
        self._api_key = api_key

        condition_info = MONITORED_CONDITIONS[condition]

        self._condition_name = condition_info[0]
        self._units = condition_info[1]
        self._icon = condition_info[2]


    async def async_added_to_hass(self):
        """Set initial state."""
        @callback
        def on_startup(_):
            self.async_schedule_update_ha_state(True)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, on_startup)

    @property
    def name(self):
        """Return the name of the sensor."""
        try:
            return self._name.format(self._condition_name)
        except IndexError:
            try:
                return self._name.format(
                    self.data['label'], self._condition_name)
            except (KeyError, TypeError):
                return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """返回图标."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attributes

    @property
    def unit_of_measurement(self):
        self._units

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        try:
            response = requests.get(API_URL_LiveServiceInfo + 'veid=' + self._veid + '&api_key=' + self._api_key)
            json_obj = json.loads(response.text)

            response_info = requests.get(API_URL_ServiceInfo + 'veid=' + self._veid + '&api_key=' + self._api_key)
            json_obj_info = json.loads(response_info.text)

            if self._condition == 'CURRENT_BANDWIDTH_USED':
                self._state = round(json_obj['data_counter']/1024/1024/1024,2)
            elif self._condition == 'CURRENT_BANDWIDTH_ALL':
                self._state = round(json_obj['plan_monthly_data']/1024/1024/1024,0)
            elif self._condition == 'DISK_USED':
                self._state = round(json_obj['ve_used_disk_space_b']/1024/1024/1024,2)
            elif self._condition == 'DISK_ALL':
                self._state = round(json_obj['plan_disk']/1024/1024/1024,0)
            elif self._condition == 'RAM_USED':
                 self._state = round((json_obj['plan_ram'] - json_obj['mem_available_kb']*1024)/1024/1024,0)
            elif self._condition == 'RAM_ALL':
                 self._state = round(json_obj['plan_ram']/1024/1024,0)
            elif self._condition == 'SWAP_USED':
                self._state = round((json_obj['swap_total_kb'] - json_obj['swap_available_kb'])/1024,2) 
            elif self._condition == 'SWAP_ALL':
                self._state = round(json_obj['swap_total_kb']/1024,0)
            elif self._condition == 'VPS_STATE':
                self._state = json_obj['ve_status']
            elif self._condition == 'SSH_PORT':
                self._state = json_obj['ssh_port']
            elif self._condition == 'VPS_LOAD_1M':
                self._state = json_obj['load_average'].split()[0]
            elif self._condition == 'VPS_LOAD_5M':
                self._state = json_obj['load_average'].split()[1]
            elif self._condition == 'VPS_LOAD_15M':
                self._state = json_obj['load_average'].split()[2]
            elif self._condition == 'VPS_IP':
                self._state = json_obj_info['ip_addresses'][0]
            elif self._condition == 'HOSTNAME':
                self._state = json_obj_info['hostname']
            elif self._condition == 'OS':
                self._state = json_obj_info['os']
            elif self._condition == 'NODE_LOCATION':
                self._state = json_obj_info['node_location']
            elif self._condition == 'DATA_NEXT_RESET':
                self._state = datetime.fromtimestamp(json_obj_info['data_next_reset']).strftime('%Y-%m-%d %H:%M:%S')
            else:
                self._state = "something wrong"
        except ConnectionError:
            _Log.error("搬瓦工：连接错误，请检查网络")