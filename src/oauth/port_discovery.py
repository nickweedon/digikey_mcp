"""Docker Port Discovery for OAuth Callback Server

This module provides automatic discovery of the host port mapped to the container's
OAuth callback server port via Docker-outside-of-Docker (DOOD).
"""
import os
import logging
import socket
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PortDiscovery:
    """Discovers the host port mapped to container port via Docker API."""

    def __init__(self, container_port: int = 8139):
        self.container_port = container_port
        self._discovered_port: Optional[int] = None
        self._discovery_attempted = False

    def get_callback_port(self) -> int:
        """Get the callback port, discovering it if running in Docker.

        Returns:
            int: The host port to use for OAuth callbacks. Returns the discovered
                 ephemeral port if running in Docker with port mapping, otherwise
                 returns the configured container_port.
        """
        if not self._discovery_attempted:
            self._discovered_port = self._discover_port()
            self._discovery_attempted = True

        return self._discovered_port or self.container_port

    def _discover_port(self) -> Optional[int]:
        """Attempt to discover host port via Docker API.

        Returns:
            Optional[int]: The discovered host port, or None if discovery fails
        """
        # Check if running in Docker
        if not self._is_running_in_docker():
            logger.debug("Not running in Docker container, using configured port")
            return None

        # Get container ID
        container_id = self._get_container_id()
        if not container_id:
            logger.warning("Could not determine container ID")
            return None

        # Query Docker API
        try:
            port = self._query_docker_api(container_id)
            if port:
                logger.info(f"✓ Discovered host port {port} mapped to container port {self.container_port}")
                return port
        except Exception as e:
            logger.warning(f"Failed to discover port via Docker API: {e}")

        return None

    def _is_running_in_docker(self) -> bool:
        """Detect if running inside a Docker container.

        Returns:
            bool: True if running in Docker, False otherwise
        """
        # Check for .dockerenv file (common indicator)
        if Path('/.dockerenv').exists():
            return True

        # Check cgroup for docker
        try:
            with open('/proc/self/cgroup', 'r') as f:
                return 'docker' in f.read()
        except (FileNotFoundError, PermissionError):
            return False

    def _get_container_id(self) -> Optional[str]:
        """Extract container ID from cgroup or hostname.

        Returns:
            Optional[str]: The container ID, or None if not found
        """
        # Try from cgroup first (most reliable)
        try:
            with open('/proc/self/cgroup', 'r') as f:
                for line in f:
                    # Format: 0::/docker/<container_id>
                    if 'docker' in line:
                        parts = line.strip().split('/')
                        if len(parts) >= 3:
                            container_id = parts[-1]
                            # Remove any trailing characters after container ID
                            if len(container_id) >= 12:
                                return container_id
        except (FileNotFoundError, PermissionError):
            pass

        # Fallback to hostname (Docker uses short container ID as hostname)
        try:
            hostname = socket.gethostname()
            if len(hostname) == 12:  # Short container ID length
                return hostname
        except Exception:
            pass

        return None

    def _query_docker_api(self, container_id: str) -> Optional[int]:
        """Query Docker API via Unix socket to get port mappings.

        Args:
            container_id: The Docker container ID

        Returns:
            Optional[int]: The host port number, or None if not found
        """
        import http.client

        socket_path = '/var/run/docker.sock'
        if not Path(socket_path).exists():
            logger.warning(f"Docker socket not found at {socket_path}")
            return None

        conn = None
        try:
            # Connect to Docker Unix socket
            conn = http.client.HTTPConnection('localhost')
            conn.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            conn.sock.connect(socket_path)

            # Query container inspect endpoint (use v1.44+ API version)
            conn.request('GET', f'/v1.44/containers/{container_id}/json')
            response = conn.getresponse()

            if response.status != 200:
                logger.warning(f"Docker API returned status {response.status}")
                return None

            data = json.loads(response.read().decode('utf-8'))

            # Extract port mapping: NetworkSettings.Ports."8139/tcp"[0].HostPort
            ports = data.get('NetworkSettings', {}).get('Ports', {})
            port_key = f'{self.container_port}/tcp'

            if port_key in ports and ports[port_key]:
                host_port = ports[port_key][0].get('HostPort')
                if host_port:
                    return int(host_port)

            logger.warning(f"No port mapping found for container port {self.container_port}")
            return None

        except Exception as e:
            logger.error(f"Error querying Docker API: {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


# Global instance
port_discovery = PortDiscovery()
