option task = { 
  name: "alert_mobility",
  every: 10s,
}



from(bucket: "lunar-mission")
  |> range(start: -1m)
  |> filter(fn: (r) => r._measurement == "mobility")
  |> filter(fn: (r) => r._field == "voltage")
  |> map(fn: (r) => ({ r with 
      _field: "battery_voltage_alert",
      level:
        if r._value < 10.0 then "CRIT"
        else if r._value < 20.0 then "WARN"
        else if r._value < 50.0 then "INFO"
        else "OK",
      message:
        if r._value < 10.0 then "CRITICAL: Battery critically low! Imminent shutdown."
        else if r._value < 20.0 then "WARNING: Battery low. Return to base recommended."
        else if r._value < 50.0 then "INFO: Battery below 50% capacity."
        else "Battery levels optimal."
    }))
  |> keep(columns: ["_time", "_measurement", "_field", "_value", "level", "message"])
  |> to(bucket: "lunar-mission", org: "esa-sic")
