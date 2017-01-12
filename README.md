# upsconfer

upsconfer is a python library to get info and configure UPS devices.

## Supported devices

* Socomec Netys with NetVision management cards (`UpsSocomecNetys`)
* Socomec Masterys with NetVision management cards (`UpsSocomecMasterys`)
* Socomec Digys with NetVision management cards (`UpsSocomecMasterys`)
* Riello UPS with Netman 204 management cards (`UpsRielloSentinel`)

## Tested on

* Socomec NETYS RT 1/1 UPS
* Socomec MASTERYS 3/3
* Socomec DIGYS 3/3
* Riello Sentinel Dual SDH 2200 (UMO3)


## API

### Creating an ups object

```
ups = upsconfer.UpsSocomecNetys(host='myups.example.com', 'user='admin', password='mypass')
```

### ups.login()

Log into device's management interface.

On most supported devices you need to call this method before doing any other operations. 

### ups.logout()

Log out of device's management interface.

Some devices support only one concurrent management session. So it is advisable to call
this method when you're done with a device to allow other users to login immediately. 
Otherwise they would have to wait for the current management session to timeout due to
inactivity.

### ups.get_serial()

Returns a serial number of the device as a string.

### ups.get_info()

Returns a dict with device info.
```
{
    'manufacturer': 'Socomec',
    'model': 'NETYS RT 1/1 UPS',
    'serial': '123456789',
    'firmware': '1.0',
    'agent_type': 'NetVision',
    'agent_firmware': '2.0h',
    'agent_serial': 'D1111',
    'mac_address': '00:11:22:33:44:55',
    'rating_va': '2200',
    'rating_w': '1900',
    'battery_capacity_ah': '7',
}
```

### ups.get_snmp_config()

Returns a dict with SNMP configuration.
```
{
    'default': {
        'community': 'public',
        'access': 'none'
    },
    '1': {
        'ip': '10.8.7.6',
        'community': 'public',
        'access': 'ro',
    },
    '2': {
        'ip': '10.66.66.66',
        'community': 'secret1',
        'access': 'rw'
    },
}
```

* `default` key represents all other management stations.
* `ip` is the address or subnet (if supported by device) of the SNMP client.
* `access` is one of `none`, `ro` or `rw`.

### ups.set_snmp_config(new_config)

Sets SNMP configuration from new_config dict.

Optional keys that are not supported by this device type are silently ignored.

### ups.get_trap_config()

Returns SNMP Trap configuration.

```
{
    '1': {
        'ip': '10.6.8.7',
        'community': 'public',
        'version': 2,
        'severity': 'info',
        'type': 'rfc',
        'alias': 'nms.example.com'
    }
}
```

* `ip` and `community` are mandatory. Other keys are optional.
* `version` determines the version of SNMP traps that will be sent out. Should be one of 1 or 2.
* `severity` determines the level of traps that should be sent to this reciever. Should be one of: `none`, `info`, `warn`, `crit`.
* `type` specifies the MIB from which the traps will be sent out. Valid values are `rfc` or `proprietary`.
* `alias` is a user friendly display name for this trap reciever.

### ups.set_trap_config(new_config)

Sets SNMP trap configuration from new_config dict.

Optional keys that are not supported by this device type are silently ignored.

### ups.reboot()

Reboot the management interface. On some devices some configuration changes can
only be applied after a reboot.
