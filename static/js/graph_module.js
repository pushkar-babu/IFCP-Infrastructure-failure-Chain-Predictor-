/**
 * Interdependency Graph Explorer (Canvas 2D Engine)
 * Visualizes multi-layer heterogeneous graph topology, directional dependency conduits, and dynamic percolation.
 */

class DependencyGraphExplorer {
  constructor(canvasId, onNodeSelectCallback) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.onNodeSelect = onNodeSelectCallback;
    this.topology = null;
    this.graphNodes = [];
    this.graphEdges = [];
    this.selectedNodeId = null;
    this.animFrameId = null;
    this.nodeStates = {};

    this.layerColors = {
      drainage: "#06b6d4",
      power: "#f59e0b",
      transport: "#a855f7",
      emergency: "#ef4444"
    };

    if (this.canvas) {
      this.initEvents();
    }
  }

  init(topology) {
    this.topology = topology;
    this.resize();
    this.layoutNodes();
    this.startAnimationLoop();
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  layoutNodes() {
    if (!this.topology || !this.canvas) return;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const cx = width / 2;
    const cy = height / 2;

    // Arrange nodes by layer in structured radial concentric layout
    const layerRadii = {
      drainage: Math.min(width, height) * 0.40,
      power: Math.min(width, height) * 0.32,
      transport: Math.min(width, height) * 0.22,
      emergency: Math.min(width, height) * 0.10
    };

    const layerBuckets = { drainage: [], power: [], transport: [], emergency: [] };
    this.topology.nodes.forEach(n => {
      if (layerBuckets[n.layer]) layerBuckets[n.layer].push(n);
    });

    this.graphNodes = [];
    Object.keys(layerBuckets).forEach(layer => {
      const list = layerBuckets[layer];
      const radius = layerRadii[layer];
      const step = (Math.PI * 2) / (list.length || 1);

      list.forEach((n, idx) => {
        const angle = idx * step - Math.PI / 2;
        this.graphNodes.push({
          id: n.id,
          name: n.name,
          layer: n.layer,
          x: cx + Math.cos(angle) * radius,
          y: cy + Math.sin(angle) * radius,
          radius: n.layer === 'emergency' ? 14 : 11,
          vx: 0,
          vy: 0
        });
      });
    });

    this.graphEdges = this.topology.edges.map(e => ({
      source: e.source,
      target: e.target,
      relation: e.relation,
      weight: e.weight
    }));
  }

  initEvents() {
    let isDragging = false;
    let draggedNode = null;

    this.canvas.addEventListener('mousedown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      draggedNode = this.graphNodes.find(n => {
        const dx = n.x - mx;
        const dy = n.y - my;
        return Math.sqrt(dx * dx + dy * dy) <= n.radius + 6;
      });

      if (draggedNode) {
        isDragging = true;
        this.selectedNodeId = draggedNode.id;
        if (this.onNodeSelect) this.onNodeSelect(draggedNode.id);
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging || !draggedNode) return;
      const rect = this.canvas.getBoundingClientRect();
      draggedNode.x = e.clientX - rect.left;
      draggedNode.y = e.clientY - rect.top;
    });

    window.addEventListener('mouseup', () => {
      isDragging = false;
      draggedNode = null;
    });
  }

  startAnimationLoop() {
    const render = () => {
      this.draw();
      this.animFrameId = requestAnimationFrame(render);
    };
    render();
  }

  draw() {
    if (!this.ctx || !this.canvas) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    const nodeMap = {};
    this.graphNodes.forEach(n => nodeMap[n.id] = n);

    // 1. Draw Edges
    this.graphEdges.forEach(edge => {
      const src = nodeMap[edge.source];
      const tgt = nodeMap[edge.target];
      if (!src || !tgt) return;

      const isConnectedToSelected = (src.id === this.selectedNodeId || tgt.id === this.selectedNodeId);
      const isCrossLayer = edge.relation !== 'physical_road' && edge.relation !== 'flow_downstream';

      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(tgt.x, tgt.y);

      if (isConnectedToSelected) {
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
      } else if (isCrossLayer) {
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.45)';
        ctx.lineWidth = 1.5;
      } else {
        ctx.strokeStyle = 'rgba(71, 85, 105, 0.35)';
        ctx.lineWidth = 1.0;
      }
      ctx.stroke();
    });

    // 2. Draw Nodes
    const now = Date.now() / 300;
    this.graphNodes.forEach(node => {
      const state = this.nodeStates[node.id] || { status: 'HEALTHY' };
      const status = state.status;
      const isSelected = node.id === this.selectedNodeId;

      ctx.save();
      ctx.translate(node.x, node.y);

      // Status glow if failed or degraded
      if (status === 'FAILED') {
        const pulse = Math.sin(now) * 4 + 8;
        ctx.beginPath();
        ctx.arc(0, 0, node.radius + pulse, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(239, 68, 68, 0.25)';
        ctx.fill();
      }

      // Base circle
      ctx.beginPath();
      ctx.arc(0, 0, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = status === 'FAILED' ? '#dc2626' : (status === 'DEGRADED' ? '#f97316' : this.layerColors[node.layer]);
      ctx.fill();

      // Border ring
      ctx.lineWidth = isSelected ? 3 : 1.5;
      ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.6)';
      ctx.stroke();

      // Node Label
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '10px -apple-system, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(node.id.split('_').slice(1, 3).join('_'), 0, node.radius + 12);

      ctx.restore();
    });
  }

  updateNodeStates(statesMap) {
    this.nodeStates = statesMap || {};
  }
}
