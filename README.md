# TrafficAccountingDocs
# MySQL db code
CREATE DATABASE traffic_accounting;  
USE traffic_accoutning;  
-- Table structure for table `users`  
DROP TABLE IF EXISTS `users`;  
CREATE TABLE `users` (  
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,  
    `src_ip` varchar(15) NOT NULL,  
    `username` varchar(30) DEFAULT NULL,  
    PRIMARY KEY (`id`),  
    UNIQUE KEY `src_ip` (`src_ip`)  
);  
  
CREATE TABLE `traffic_logs` (  
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,  
    `src_ip` varchar(15) NOT NULL,  
    `dst_ip` varchar(15) NOT NULL,  
    `ts` timestamp NULL DEFAULT NULL,  
    `packet_length` bigint NOT NULL,  
    PRIMARY KEY (`id`),  
    UNIQUE KEY `id` (`id`),  
    KEY `idx_traffic_src_ip` (`src_ip`),  
    KEY `idx_traffic_timestamp` (`ts`),  
    KEY `idx_traffic_bytes` (`packet_length`),  
    CONSTRAINT `fk_src_ip` FOREIGN KEY (`src_ip`) REFERENCES `users` (`src_ip`) ON DELETE CASCADE  
);  

# IPTables Rules  
sudo iptables -t nat -A POSTROUTING -o enp0s3 -s  192.168.1.0/24 -j MASQUERADE  
sudo iptables -A FORWARD -s <ip-adress> -j LOG --log-prefix "IPTables-Forward-In: " --log-level 4  

# Grafana installation  
Установка на клиент(Нужна возможность подключения к бд)
https://grafana.com/docs/grafana/latest/setup-grafana/installation/redhat-rhel-fedora/  
https://grafana.com/grafana/download   
Запускаем grafana-server.bat  
Запускаем Grafana в браузере по дефолту localhost:3000, логин паролль admin admin  
В Grafana в левом навбаре connections -> Data sources, справа сверху Add new datasources -> MySql, и затем настраиваем имя пользователя пароль и тд.
Далее скачиваем файл Traffic Logs.json  
В самой Grafana в левом навбаре выбираем dashboards, справа сверху New -> Import и заливаем json файл
["Импорт панели"](./grafana.png)  

# Python
sudo dnf install python3  
sudo dnf install python3-pip  
pip install mysql-connector-python
Скачать скрипт в репозитории traffic_log_processor.py  
Отредактировать в нём пароль и имя пользователя для подключения к базе данных.


# Dashboard json  

{  
  "annotations": {  
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "datasource": {
        "default": true,
        "type": "mysql",
        "uid": "edzne94d13hfke"
      },
      "description": "Confirm change username",
      "gridPos": {
        "h": 5,
        "w": 5,
        "x": 0,
        "y": 0
      },
      "id": 11,
      "options": {
        "buttons": [
          {
            "datasource": "",
            "query": "",
            "text": ""
          }
        ],
        "orientation": "horizontal"
      },
      "targets": [
        {
          "dataset": "mysql",
          "datasource": {
            "type": "mysql",
            "uid": "edzne94d13hfke"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "UPDATE users\nSET username = \"${username_textfield}\"\nWHERE src_ip = \"${ip_textfield}\";",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Apply Username",
      "type": "speakyourcode-button-panel"
    },
    {
      "datasource": {
        "default": true,
        "type": "mysql",
        "uid": "edzne94d13hfke"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
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
      "gridPos": {
        "h": 5,
        "w": 8,
        "x": 5,
        "y": 0
      },
      "id": 8,
      "options": {
        "minVizHeight": 75,
        "minVizWidth": 75,
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true,
        "sizing": "auto"
      },
      "pluginVersion": "11.2.2",
      "targets": [
        {
          "datasource": {
            "type": "mysql",
            "uid": "edzne94d13hfke"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "sELECT \n    DATE_FORMAT(ts, \"%Y-%m-%d %H:00:00\") AS hour,\n    SUM(packet_length) AS total_traffic\nFROM \n    traffic_accounting.traffic_logs\nWHERE \n    ts BETWEEN $__timeFrom() AND $__timeTo()\nGROUP BY \n    hour\nORDER BY \n    hour;",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Average Total Traffic",
      "type": "gauge"
    },
    {
      "datasource": {
        "default": true,
        "type": "mysql",
        "uid": "edzne94d13hfke"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "fillOpacity": 80,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineWidth": 1,
            "scaleDistribution": {
              "type": "linear"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
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
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 5
      },
      "id": 10,
      "options": {
        "barRadius": 0,
        "barWidth": 0.97,
        "fullHighlight": false,
        "groupWidth": 0.7,
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "orientation": "auto",
        "showValue": "auto",
        "stacking": "none",
        "tooltip": {
          "mode": "single",
          "sort": "none"
        },
        "xTickLabelRotation": 0,
        "xTickLabelSpacing": 0
      },
      "targets": [
        {
          "datasource": {
            "type": "mysql",
            "uid": "edzne94d13hfke"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT DISTINCT\n    src_ip,\n    SUM(packet_length) AS total_traffic\nFROM\n    traffic_logs t\nWHERE\n    t.ts BETWEEN $__timeFrom() AND $__timeTo()\nGROUP BY\n    src_ip\nORDER BY\n    total_traffic DESC;",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Panel Title",
      "type": "barchart"
    },
    {
      "datasource": {
        "default": true,
        "type": "mysql",
        "uid": "edzne94d13hfke"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "line",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
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
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 13
      },
      "id": 9,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "dataset": "mysql",
          "datasource": {
            "type": "mysql",
            "uid": "edzne94d13hfke"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \n    UNIX_TIMESTAMP(DATE_FORMAT(t.ts, \"%Y-%m-%d %H:00:00\")) * 1000 AS time,\n    SUM(packet_length) AS total_traffic\nFROM \n    traffic_logs t\nWHERE \n    t.ts BETWEEN $__timeFrom() AND $__timeTo()\nGROUP BY \n    time\nORDER BY \n    time;",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "type": "timeseries"
    },
    {
      "datasource": {
        "default": true,
        "type": "mysql",
        "uid": "edzne94d13hfke"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "left",
            "cellOptions": {
              "type": "auto",
              "wrapText": false
            },
            "filterable": true,
            "inspect": false,
            "minWidth": 50
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
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
      "gridPos": {
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 21
      },
      "id": 1,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "enablePagination": true,
          "fields": "",
          "reducer": [
            "sum"
          ],
          "show": false
        },
        "showHeader": true,
        "sortBy": [
          {
            "desc": true,
            "displayName": "packet_length"
          }
        ]
      },
      "pluginVersion": "11.2.2",
      "targets": [
        {
          "dataset": "mysql",
          "datasource": {
            "type": "mysql",
            "uid": "ddy1r6fn5e4n4a"
          },
          "editorMode": "code",
          "format": "table",
          "rawQuery": true,
          "rawSql": "SELECT \r\n    u.username,\r\n    t.src_ip,\r\n    t.dst_ip,\r\n    t.packet_length,\r\n    t.ts\r\nFROM \r\n    traffic_accounting.traffic_logs t\r\nLEFT JOIN\r\n     users u\r\nON\r\n    t.src_ip = u.src_ip\r\nWHERE\r\n    t.ts BETWEEN $__timeFrom()  AND  $__timeTo() ;\r\n  ",
          "refId": "A",
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Traffic Logs",
      "type": "table"
    }
  ],
  "refresh": "",
  "schemaVersion": 39,
  "tags": [],
  "templating": {
    "list": [
      {
        "current": {},
        "hide": 0,
        "label": "test",
        "name": "ip_textfield",
        "options": [],
        "query": "",
        "skipUrlSync": false,
        "type": "textbox"
      },
      {
        "current": {
          "selected": false,
          "text": "",
          "value": ""
        },
        "hide": 0,
        "name": "username_textfield",
        "options": [
          {
            "selected": true,
            "text": "",
            "value": ""
          }
        ],
        "query": "",
        "skipUrlSync": false,
        "type": "textbox"
      }
    ]
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Traffic Logs",
  "uid": "bdy1sn5z4wu0wb",
  "version": 4,
  "weekStart": ""
}
