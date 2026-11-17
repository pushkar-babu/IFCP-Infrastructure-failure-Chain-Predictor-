/**
 * GIS Digital Twin Map Module (Leaflet.js)
 * Manages spatial layers, custom markers, animated cascade vectors, and interactive inspections.
 */

class GISMapManager {
  constructor(containerId, onNodeSelectCallback) {
    this.containerId = containerId;
    this.onNodeSelect = onNodeSelectCallback;
    this.map = null;
    this.markers = {};
    this.edgePolylines = [];
    this.activeLayers = {
      drainage: true,
      power: true,
      transport: true,
      emergency: true
    };
    this.topology = null;
  }

  init(topology) {
    this.topology = topology;
    const center = topology.metadata.geo_center;

    // Initialize Leaflet map
    this.map = L.map(this.containerId, {
      zoomControl: true,
      attributionControl: false
    }).setView([center.lat, center.lng], 14);

    // Dark Matter tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 18,
      subdomains: 'abcd'
    }).addTo(this.map);

    this.renderEdges();
    this.renderNodes();
  }

  setCity(topology) {
    this.topology = topology;
    const center = topology.metadata.geo_center;
    if (this.map) {
      this.map.flyTo([center.lat, center.lng], 14, { duration: 1.2 });
    }
    this.renderEdges();
    this.renderNodes();
  }

  flyToNode(nodeId, zoom = 16, duration = 1.2) {
    const marker = this.markers[nodeId];
    if (marker && this.map) {
      const latlng = marker.getLatLng();
      this.map.flyTo(latlng, zoom, { duration: duration });
      marker.openTooltip();
    }
  }

  resetView(zoom = 14) {
    if (this.topology && this.map) {
      const center = this.topology.metadata.geo_center;
      this.map.flyTo([center.lat, center.lng], zoom, { duration: 1.2 });
    }
  }

  renderNodes() {
    // Clear previous markers
    Object.values(this.markers).forEach(m => this.map.removeLayer(m));
    this.markers = {};

    this.topology.nodes.forEach(node => {
      const isVisible = this.activeLayers[node.layer];
      if (!isVisible) return;

      const iconHtml = this.createMarkerHtml(node, "HEALTHY", 0.1);
      const customIcon = L.divIcon({
        className: 'custom-leaflet-icon',
        html: iconHtml,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const marker = L.marker([node.lat, node.lng], { icon: customIcon }).addTo(this.map);
      
      marker.on('click', () => {
        if (this.onNodeSelect) {
          this.onNodeSelect(node.id);
        }
      });

      marker.bindTooltip(`
        <div style="background:#0f172a; color:#f8fafc; padding:4px 8px; border-radius:4px; font-size:11px; border:1px solid #334155;">
          <b>${node.name}</b><br/>
          Layer: <span style="text-transform:capitalize">${node.layer}</span> | Elev: ${node.elevation_m}m
        </div>
      `, { sticky: true, opacity: 0.95 });

      this.markers[node.id] = marker;
    });
  }

  renderEdges() {
    this.edgePolylines.forEach(p => this.map.removeLayer(p));
    this.edgePolylines = [];

    const nodeCoords = {};
    this.topology.nodes.forEach(n => {
      nodeCoords[n.id] = [n.lat, n.lng];
    });

    this.topology.edges.forEach(edge => {
      const srcCoord = nodeCoords[edge.source];
      const tgtCoord = nodeCoords[edge.target];
      if (!srcCoord || !tgtCoord) return;

      const isCrossLayer = edge.relation === "supplies_power" || 
                           edge.relation === "drains_surface_water" || 
                           edge.relation === "emergency_access";

      const polyline = L.polyline([srcCoord, tgtCoord], {
        color: isCrossLayer ? '#f59e0b' : '#475569',
        weight: isCrossLayer ? 2.2 : 1.2,
        opacity: isCrossLayer ? 0.75 : 0.4,
        dashArray: isCrossLayer ? '4, 4' : null
      }).addTo(this.map);

      this.edgePolylines.push(polyline);
    });
  }

  updateNodeStates(nodeStatesMap, activeEvents) {
    if (!this.topology) return;

    this.topology.nodes.forEach(node => {
      const state = nodeStatesMap[node.id];
      const marker = this.markers[node.id];
      if (!marker) return;

      const status = state ? state.status : "HEALTHY";
      const stress = state ? state.stress : 0.1;

      const newHtml = this.createMarkerHtml(node, status, stress);
      marker.setIcon(L.divIcon({
        className: 'custom-leaflet-icon',
        html: newHtml,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      }));
    });
  }

  createMarkerHtml(node, status, stress) {
    const layerColors = {
      drainage: "#06b6d4",
      power: "#f59e0b",
      transport: "#a855f7",
      emergency: "#ef4444"
    };

    let statusClass = "";
    if (status === "FAILED") statusClass = "pin-failed";
    else if (status === "DEGRADED") statusClass = "pin-degraded";

    const layerShort = {
      drainage: "💧",
      power: "⚡",
      transport: "🛣️",
      emergency: "🏥"
    }[node.layer] || "•";

    return `
      <div class="custom-pin pin-${node.layer} ${statusClass}" style="width:30px; height:30px;">
        <span>${layerShort}</span>
      </div>
    `;
  }

  toggleLayer(layerName) {
    this.activeLayers[layerName] = !this.activeLayers[layerName];
    this.renderNodes();
    return this.activeLayers[layerName];
  }
}
