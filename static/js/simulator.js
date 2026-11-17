/**
 * Timeline Simulation & Cascade Playback Controller
 * Handles time-lapse progression, scrubbing, event streaming, and state synchronization.
 */

class SimulationController {
  constructor(onStepChangeCallback) {
    this.onStepChange = onStepChangeCallback;
    this.simulationData = null;
    this.currentStepIdx = 0;
    this.isPlaying = false;
    this.intervalId = null;
    this.playbackSpeedMs = 1800; // 1.8s per time step
  }

  setSimulationData(data) {
    this.simulationData = data;
    this.currentStepIdx = 0;
    this.notifyStep();
  }

  play() {
    if (!this.simulationData || this.isPlaying) return;
    this.isPlaying = true;

    this.intervalId = setInterval(() => {
      if (!this.simulationData) return;
      const totalSteps = this.simulationData.timeline.length;

      if (this.currentStepIdx < totalSteps - 1) {
        this.currentStepIdx++;
        this.notifyStep();
      } else {
        this.pause();
      }
    }, this.playbackSpeedMs);
  }

  pause() {
    this.isPlaying = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  stepForward() {
    if (!this.simulationData) return;
    const totalSteps = this.simulationData.timeline.length;
    if (this.currentStepIdx < totalSteps - 1) {
      this.currentStepIdx++;
      this.notifyStep();
    }
  }

  reset() {
    this.pause();
    this.currentStepIdx = 0;
    this.notifyStep();
  }

  seek(stepIdx) {
    if (!this.simulationData) return;
    this.currentStepIdx = Math.max(0, Math.min(stepIdx, this.simulationData.timeline.length - 1));
    this.notifyStep();
  }

  notifyStep() {
    if (!this.simulationData) return;
    const snapshot = this.simulationData.timeline[this.currentStepIdx];
    if (this.onStepChange) {
      this.onStepChange(this.currentStepIdx, snapshot, this.simulationData);
    }
  }
}
