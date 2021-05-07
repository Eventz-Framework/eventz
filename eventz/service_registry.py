from typing import Dict

from eventz.errors import ServiceNotFoundError
from eventz.protocols import ServiceProtocol, ServiceRegistryProtocol
from eventz.service import Service


class ServiceRegistry(ServiceRegistryProtocol):
    def __init__(self):
        self._services: Dict[str, Service] = {}

    def register(self, service_name: str, service: ServiceProtocol) -> None:
        if not isinstance(service, Service):
            err = "registered service must be of type `Service`"
            raise TypeError(err)
        self._services[service_name] = service

    def get_service(self, service_name: str) -> Service:
        if service_name not in self._services:
            err = f"No service registered for '{service_name}'."
            raise ServiceNotFoundError(err)
        return self._services[service_name]
