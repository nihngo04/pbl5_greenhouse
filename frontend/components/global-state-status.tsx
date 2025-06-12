/**
 * Global State Status Component
 * Hiển thị trạng thái đồng bộ dữ liệu và performance
 */

"use client"

import React from 'react';
import { RefreshCw, Clock, Database, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useGlobalState } from '@/lib/global-state';
import { useDataSync } from '@/lib/useDataSync';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export const GlobalStateStatus: React.FC = () => {
  const { 
    sensors, 
    devices, 
    isLoading, 
    lastSync,
    syncFromAPI 
  } = useGlobalState();
  
  const formatTime = (timestamp: string | null) => {
    if (!timestamp) return 'Chưa đồng bộ';
    const diff = Date.now() - new Date(timestamp).getTime();
    if (diff < 60000) return `${Math.floor(diff / 1000)}s trước`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m trước`;
    return new Date(timestamp).toLocaleTimeString();
  };
  
  const isDataFresh = lastSync && Date.now() - new Date(lastSync).getTime() < 10000; // 10 seconds for API polling
  
  return (
    <TooltipProvider>
      <div className="flex items-center space-x-2 text-xs">
        {/* Auto Sync Status */}
        <Tooltip>
          <TooltipTrigger>
            <Badge variant={isDataFresh ? "default" : "secondary"} className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              Auto Sync
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            {isDataFresh ? 'Đồng bộ tự động mỗi 10 giây' : 'Đang chờ đồng bộ...'}
          </TooltipContent>
        </Tooltip>
        
        {/* Data Freshness */}
        <Tooltip>
          <TooltipTrigger>
            <Badge variant={isDataFresh ? "default" : "secondary"} className="flex items-center">
              <Database className="w-3 h-3 mr-1" />
              {formatTime(lastSync)}
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            Lần đồng bộ dữ liệu cuối cùng
          </TooltipContent>
        </Tooltip>
        
        {/* Loading Status */}
        {isLoading && (
          <Badge variant="secondary" className="flex items-center">
            <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
            Đang tải
          </Badge>
        )}
        {/* Manual Sync Button */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button 
              size="sm" 
              variant="ghost" 
              onClick={() => syncFromAPI()}
              disabled={isLoading}
              className="h-6 px-2"
            >
              <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            Đồng bộ dữ liệu thủ công
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};

export const PerformanceIndicator: React.FC = () => {
  const { lastSync } = useGlobalState();
  
  // API polling takes about 2 seconds on average
  const estimatedLoadTime = lastSync ? 2 : 7;
  
  const getPerformanceColor = (time: number) => {
    if (time < 3) return 'text-green-600';
    if (time < 5) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getPerformanceIcon = (time: number) => {
    if (time < 3) return <Zap className="w-4 h-4" />;
    if (time < 5) return <Clock className="w-4 h-4" />;
    return <RefreshCw className="w-4 h-4" />;
  };
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <div className={`flex items-center space-x-1 ${getPerformanceColor(estimatedLoadTime)}`}>
            {getPerformanceIcon(estimatedLoadTime)}
            <span className="text-xs font-medium">
              ~{estimatedLoadTime}s
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <div className="text-xs">
            <div className="font-medium mb-1">Thời gian tải dữ liệu ước tính:</div>
            <div>• Với cache: ~2s (đã đồng bộ)</div>
            <div>• Không cache: ~7s (load từ API)</div>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export const DataOverview: React.FC = () => {
  const { sensors, devices } = useGlobalState();
  
  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center justify-between">
          <span>Trạng thái dữ liệu</span>
          <div className="flex items-center space-x-2">
            <PerformanceIndicator />
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="grid grid-cols-2 gap-4 text-xs">
          {/* Sensors */}
          <div>
            <h4 className="font-medium mb-2">Cảm biến</h4>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Nhiệt độ:</span>
                <span className={sensors.temperature !== null ? 'text-green-600' : 'text-gray-400'}>
                  {sensors.temperature !== null ? `${sensors.temperature}°C` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Độ ẩm:</span>
                <span className={sensors.humidity !== null ? 'text-green-600' : 'text-gray-400'}>
                  {sensors.humidity !== null ? `${sensors.humidity}%` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Độ ẩm đất:</span>
                <span className={sensors.soil_moisture !== null ? 'text-green-600' : 'text-gray-400'}>
                  {sensors.soil_moisture !== null ? `${sensors.soil_moisture}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
          
          {/* Devices */}
          <div>
            <h4 className="font-medium mb-2">Thiết bị</h4>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Quạt:</span>
                <Badge variant={devices.fan ? "default" : "secondary"}>
                  {devices.fan ? 'BẬT' : 'TẮT'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span>Bơm:</span>
                <Badge variant={devices.pump ? "default" : "secondary"}>
                  {devices.pump ? 'BẬT' : 'TẮT'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span>Mái che:</span>
                <Badge variant="outline">
                  {devices.cover}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
