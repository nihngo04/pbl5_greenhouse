import { useEffect } from 'react';
import { useGlobalState } from './global-state';

export const useDataSync = () => {
  const syncFromAPI = useGlobalState((state: any) => state.syncFromAPI);
  const lastSync = useGlobalState((state: any) => state.lastSync);
  const isLoading = useGlobalState((state: any) => state.isLoading);

  useEffect(() => {
    console.log('🔄 Setting up API polling...');
    
    // Initial fetch
    syncFromAPI();

    // Set up polling every 10 seconds
    const interval = setInterval(() => {
      console.log('🔄 Polling API for updates...');
      syncFromAPI();
    }, 10000);
    
    return () => clearInterval(interval);
  }, [syncFromAPI]);

  return {
    lastSync,
    isLoading,
    syncMethod: 'API Polling',
    updateFrequency: '10s'
  };
};
