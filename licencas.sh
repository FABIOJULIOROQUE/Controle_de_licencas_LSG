#!/bin/bash
case "$1" in
  start) sudo systemctl start licencas ;;
  stop) sudo systemctl stop licencas ;;
  restart) sudo systemctl restart licencas ;;
  status) sudo systemctl status licencas ;;
  *) echo "Uso: $0 {start|stop|restart|status}" ;;
esac

