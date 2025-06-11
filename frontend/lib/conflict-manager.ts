/**
 * Conflict Management System
 * Xử lý xung đột giữa scheduler và manual control
 */

import { create } from 'zustand';
import { useGlobalState, ConflictAlert } from './global-state';
import { autoScheduler } from './scheduler';
import { greenhouseAPI } from './api';

export interface ConflictResolution {
  conflictId: string;
  device: string;
  resolution: 'scheduler' | 'manual' | 'ask_user';
  timestamp: string;
}

interface ConflictManagerState {
  activeConflicts: ConflictAlert[];
  resolutions: ConflictResolution[];
  autoResolveMode: 'scheduler_priority' | 'manual_priority' | 'always_ask';
  
  // Actions
  handleDeviceAction: (device: string, action: any, source: 'scheduler' | 'manual') => Promise<boolean>;
  resolveConflict: (conflictId: string, resolution: 'scheduler' | 'manual') => Promise<void>;
  setAutoResolveMode: (mode: 'scheduler_priority' | 'manual_priority' | 'always_ask') => void;
}

export const useConflictManager = create<ConflictManagerState>((set, get) => ({
  activeConflicts: [],
  resolutions: [],
  autoResolveMode: 'always_ask',
  
  handleDeviceAction: async (device, action, source) => {
    const globalState = useGlobalState.getState();
    const conflictDetected = globalState.detectConflict(device, action, source);
    
    if (conflictDetected) {
      const { autoResolveMode } = get();
      
      // Auto-resolve based on mode
      if (autoResolveMode === 'scheduler_priority' && source === 'scheduler') {
        console.log(`🤖 AUTO RESOLVE: Scheduler priority for ${device}`);
        return await executeAction(device, action, source);
      } else if (autoResolveMode === 'manual_priority' && source === 'manual') {
        console.log(`👤 AUTO RESOLVE: Manual priority for ${device}`);
        return await executeAction(device, action, source);
      } else {
        // Ask user - return false to indicate conflict needs resolution
        console.log(`❓ CONFLICT: User resolution required for ${device}`);
        return false;
      }
    }
    
    // No conflict, execute normally
    return await executeAction(device, action, source);
  },
  
  resolveConflict: async (conflictId, resolution) => {
    const globalState = useGlobalState.getState();
    const conflict = globalState.conflicts.find(c => c.id === conflictId);
    
    if (!conflict) return;
    
    try {
      const action = JSON.parse(conflict.scheduledAction);
      
      if (resolution === 'scheduler') {
        console.log(`✅ CONFLICT RESOLVED: Execute scheduler action for ${conflict.device}`);
        await executeAction(conflict.device, action, 'scheduler');
      } else {
        console.log(`✅ CONFLICT RESOLVED: Keep manual control for ${conflict.device}`);
        // Do nothing, keep current manual state
      }
      
      // Record resolution
      set(state => ({
        resolutions: [...state.resolutions, {
          conflictId,
          device: conflict.device,
          resolution,
          timestamp: new Date().toISOString()
        }]
      }));
      
      // Remove conflict
      globalState.resolveConflict(conflictId, resolution === 'scheduler' ? 'allow' : 'override');
      
    } catch (error) {
      console.error('❌ Error resolving conflict:', error);
    }
  },
  
  setAutoResolveMode: (mode) => set({ autoResolveMode: mode })
}));

// Helper function để execute device actions
async function executeAction(device: string, action: any, source: 'scheduler' | 'manual'): Promise<boolean> {
  try {
    console.log(`🎯 EXECUTING: ${device} action from ${source}`, action);
    
    // Update global state với last action
    const globalState = useGlobalState.getState();
    globalState.updateScheduler({
      lastAction: {
        device,
        action: JSON.stringify(action),
        timestamp: new Date().toISOString(),
        source
      }
    });
    
    // Execute the actual device control
    let result;
    
    if (device === 'fan') {
      result = await greenhouseAPI.controlDevice('fan1', 'fan', action);
    } else if (device === 'pump') {
      result = await greenhouseAPI.controlDevice('pump1', 'pump', action);
    } else if (device === 'cover') {
      result = await greenhouseAPI.controlDevice('cover1', 'cover', action);
    }
    
    if (result?.success) {
      // Update device state
      globalState.updateDevices({
        [device]: action
      });
      
      console.log(`✅ ${device.toUpperCase()} action executed successfully`);
      return true;
    } else {
      console.error(`❌ ${device.toUpperCase()} action failed:`, result?.error);
      return false;
    }
    
  } catch (error) {
    console.error(`❌ Error executing ${device} action:`, error);
    return false;
  }
}

// Hook để override scheduler methods với conflict handling
export const useSchedulerWithConflicts = () => {
  const handleDeviceAction = useConflictManager(state => state.handleDeviceAction);
  
  // Override scheduler control methods
  const controlFanWithConflict = async (status: boolean, duration?: number) => {
    const success = await handleDeviceAction('fan', status, 'scheduler');
    
    if (success && status && duration) {
      // Schedule turn off after duration
      setTimeout(async () => {
        await handleDeviceAction('fan', false, 'scheduler');
      }, duration * 60 * 1000);
    }
    
    return success;
  };
  
  const controlPumpWithConflict = async (status: boolean, duration?: number) => {
    const success = await handleDeviceAction('pump', status, 'scheduler');
    
    if (success && status && duration) {
      setTimeout(async () => {
        await handleDeviceAction('pump', false, 'scheduler');
      }, duration * 60 * 1000);
    }
    
    return success;
  };
  
  const controlCoverWithConflict = async (position: string) => {
    return await handleDeviceAction('cover', position, 'scheduler');
  };
  
  return {
    controlFanWithConflict,
    controlPumpWithConflict,
    controlCoverWithConflict
  };
};

// Hook để manual control với conflict handling
export const useManualControlWithConflicts = () => {
  const handleDeviceAction = useConflictManager(state => state.handleDeviceAction);
  
  const manualControlDevice = async (device: string, action: any) => {
    return await handleDeviceAction(device, action, 'manual');
  };
  
  return {
    manualControlDevice
  };
};
