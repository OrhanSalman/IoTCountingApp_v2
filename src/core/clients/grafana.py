import os
import json
from grafana_client import GrafanaApi
from grafana_client import GrafanaApi, HeaderAuth, TokenAuth
from settings import DEVICE_ID
from src.core.inference.names import names

# grafana-client==4.3.2


def prepare_panels(bucket, deviceLocation, deviceName, cls_name, region_name):
    # influx query builder
    query = f"""
    from(bucket: "{bucket}")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "Counts")
      |> filter(fn: (r) => r["standort"] == "{deviceLocation}")
      |> filter(fn: (r) => r["geraet"] == "{deviceName}")
      |> filter(fn: (r) => r["klasse"] == "{cls_name}")
      |> filter(fn: (r) => r["region"] == "{region_name}")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
      |> yield(name: "mean")
    """

    PANEL = {
      "id": 1,  # This will be overridden when adding to the dashboard
      "type": "timeseries",
      "title": f"{region_name} - {cls_name}",
      "gridPos": {
        "x": 0,
        "y": 0,
        "h": 8,
        "w": 12
      },
      "fieldConfig": {
        "defaults": {
          "custom": {
            "drawStyle": "line",
            "lineInterpolation": "linear",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "lineWidth": 1,
            "fillOpacity": 0,
            "gradientMode": "none",
            "spanNulls": False,
            "insertNulls": False,
            "showPoints": "auto",
            "pointSize": 5,
            "stacking": {
              "mode": "none",
              "group": "A"
            },
            "axisPlacement": "auto",
            "axisLabel": "",
            "axisColorMode": "text",
            "axisBorderShow": False,
            "scaleDistribution": {
              "type": "linear"
            },
            "axisCenteredZero": False,
            "hideFrom": {
              "tooltip": False,
              "viz": False,
              "legend": False
            },
            "thresholdsStyle": {
              "mode": "off"
            },
            "lineStyle": {
              "fill": "solid"
            }
          },
          "color": {
            "mode": "palette-classic"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "pluginVersion": "12.0.0",
      "targets": [
        {
          "datasource": {
            "type": "influxdb",
            "uid": "fem6834pg90qob"
          },
          "query": query,
          "refId": "A"
        }
      ],
      "datasource": {
        "type": "influxdb",
        "uid": "fem6834pg90qob"
      },
      "options": {
        "tooltip": {
          "mode": "single",
          "sort": "none",
          "hideZeros": False
        },
        "legend": {
          "showLegend": True,
          "displayMode": "list",
          "placement": "bottom",
          "calcs": []
        }
      }
    }
    
    PAN = json.dumps(PANEL)
    PAN = PAN.replace('True', 'true').replace('False', 'false').replace('None', 'null')
    PANEL = json.loads(PAN)
    
    return PANEL

def create_dashboard(deviceName, deviceLocation, bucket="Django"):
    PANELS = []
    try:
        G_URL = os.getenv("GRAFANA_URL", None)
        G_TOKEN = os.getenv("GRAFANA_TOKEN", None)

        if G_URL is None or G_TOKEN is None:
            raise ValueError("Grafana URL and token must be set in environment variables.")

        grafana = GrafanaApi.from_url(
            url=G_URL,
            credential=TokenAuth(token=G_TOKEN),
        )

        from settings import CONFIG_PATH
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        
        regions = []
        for roi in config.get("deviceRois", []):
            regions.append({
                "name": roi.get("roiName", ""),
                "tags": roi.get("tagsInThisRegion", [])
            })
        
        panel_index = 1
        
        # For each region, create panels based on the tags
        for region in regions:
            region_name = region["name"]
            region_tags = region["tags"]
            
            for tag in region_tags:
                try:
                    tag_key = int(tag)
                    cls_name = names.get(tag_key, str(tag))
                    
                    panel = prepare_panels(bucket, deviceLocation, deviceName, cls_name, region_name)
                    
                    #  unique ID for each panel
                    panel["id"] = panel_index
                    panel_index += 1
                    
                    row_in_region = (panel_index - 1) % 2 
                    panel["gridPos"]["x"] = row_in_region * 12
                    panel["gridPos"]["y"] = ((panel_index - 1) // 2) * 8
                    
                    PANELS.append(panel)
                except (ValueError, TypeError):
                    print(f"Skipping invalid tag: {tag}")
        
        if not PANELS:
            raise ValueError("No valid panels were created")
            
        dashboard_data = {
            "title": f"IoT Counter {deviceLocation}/{deviceName} - {DEVICE_ID}",
            "uid": f"{DEVICE_ID}",
            "tags": [f"{deviceLocation}", f"{deviceName}", DEVICE_ID],
            "timezone": "browser",
            "panels": PANELS,
            "editable": True,
            "refresh": "5s"
        }


        # Update with the original UID maintained
        dash = grafana.dashboard.update_dashboard(
            {
                "dashboard": dashboard_data,
                "overwrite": True,
                "message": f"Created/updated dashboard for device {DEVICE_ID}"
            }
        )

        print(f"Dashboard {DEVICE_ID} created/updated successfully.")
        return True

    except ValueError as e:
        print(f"Error: {e}")
        return False, str(e), {}


def get_embedded():
    try:
        G_URL = os.getenv("GRAFANA_URL", None)
        G_TOKEN = os.getenv("GRAFANA_TOKEN", None)

        if G_URL is None or G_TOKEN is None:
            raise ValueError("Grafana URL and token must be set in environment variables.")

        grafana = GrafanaApi.from_url(
            url=G_URL,
            credential=TokenAuth(token=G_TOKEN),
        )
        
        from settings import SYSTEM_SETTINGS_PATH
        with open(SYSTEM_SETTINGS_PATH, "r") as f:
            config = json.load(f)

        counts_publish_intervall = config.get("counts_publish_intervall", 5)
        
        try:
            dashboard = grafana.dashboard.get_dashboard(DEVICE_ID)
            
            panels = dashboard.get('dashboard', {}).get('panels', [])
            
            G_URL = G_URL.rstrip("/")
            
            panel_urls = {}
            for panel in panels:
                panel_id = panel.get("id")
                class_name = panel.get("title", f"panel-{panel_id}")
                panel_urls[class_name] = f"{G_URL}/d-solo/{DEVICE_ID}?orgId=1&timezone=browser&refresh={counts_publish_intervall}s&panelId={panel_id}&__feature.dashboardSceneSolo"
            
            #panel_urls["full_dashboard"] = f"{G_URL}/d/{DEVICE_ID}?orgId=1&timezone=browser&refresh=5s"
            
            return True, dashboard, panel_urls
            
        except Exception as e:
            print(f"Error retrieving dashboard: {e}")
            return False, str(e), {}
            
    except ValueError as e:
        print(f"Error: {e}")
        return False, str(e), {}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False, str(e), {}