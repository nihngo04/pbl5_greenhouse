/**
 * Conflict Resolution UI Component
 * Hiển thị và xử lý conflicts giữa scheduler và manual control
 */

"use client"

import React from 'react';
import { AlertTriangle, Clock, Settings, User, Bot, X, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useConflictDetection } from '@/lib/global-state';
import { useConflictManager } from '@/lib/conflict-manager';

export const ConflictAlert: React.FC = () => {
  const { conflicts, hasConflicts } = useConflictDetection();
  const { resolveConflict, autoResolveMode, setAutoResolveMode } = useConflictManager();
  
  if (!hasConflicts) return null;
  
  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      {conflicts.map((conflict) => (
        <Card key={conflict.id} className="mb-2 border-orange-200 bg-orange-50 shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-orange-800 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Xung đột điều khiển thiết bị
              </CardTitle>
              <Badge variant="outline" className="text-xs">
                {conflict.device.toUpperCase()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-sm text-orange-700 mb-3">
              {conflict.message}
            </p>
            
            <div className="text-xs text-orange-600 mb-3">
              <div className="flex items-center mb-1">
                <Bot className="w-3 h-3 mr-1" />
                Hành động theo lịch: {conflict.scheduledAction}
              </div>
              <div className="flex items-center">
                <User className="w-3 h-3 mr-1" />
                Trạng thái hiện tại: {conflict.currentStatus}
              </div>
            </div>
            
            <div className="flex space-x-2">
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => resolveConflict(conflict.id, 'manual')}
                className="flex-1 text-xs"
              >
                <User className="w-3 h-3 mr-1" />
                Giữ thủ công
              </Button>
              <Button 
                size="sm"
                onClick={() => resolveConflict(conflict.id, 'scheduler')}
                className="flex-1 text-xs"
              >
                <Bot className="w-3 h-3 mr-1" />
                Theo lịch
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export const ConflictSettings: React.FC = () => {
  const { autoResolveMode, setAutoResolveMode } = useConflictManager();
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex items-center">
          <Settings className="w-4 h-4 mr-2" />
          Cài đặt xử lý xung đột
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium mb-2 block">
              Chế độ tự động xử lý:
            </label>
            <Select value={autoResolveMode} onValueChange={setAutoResolveMode}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="always_ask">
                  <div className="flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Luôn hỏi người dùng
                  </div>
                </SelectItem>
                <SelectItem value="scheduler_priority">
                  <div className="flex items-center">
                    <Bot className="w-4 h-4 mr-2" />
                    Ưu tiên lịch trình
                  </div>
                </SelectItem>
                <SelectItem value="manual_priority">
                  <div className="flex items-center">
                    <User className="w-4 h-4 mr-2" />
                    Ưu tiên điều khiển thủ công
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="text-xs text-gray-600">
            {autoResolveMode === 'always_ask' && (
              <Alert>
                <AlertTriangle className="w-4 h-4" />
                <AlertDescription>
                  Sẽ hiển thị thông báo cho mọi xung đột để người dùng quyết định
                </AlertDescription>
              </Alert>
            )}
            {autoResolveMode === 'scheduler_priority' && (
              <Alert>
                <Bot className="w-4 h-4" />
                <AlertDescription>
                  Lịch trình sẽ tự động ghi đè các điều khiển thủ công
                </AlertDescription>
              </Alert>
            )}
            {autoResolveMode === 'manual_priority' && (
              <Alert>
                <User className="w-4 h-4" />
                <AlertDescription>
                  Điều khiển thủ công sẽ tự động ghi đè lịch trình
                </AlertDescription>
              </Alert>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const ConflictHistory: React.FC = () => {
  const { resolutions } = useConflictManager();
  
  if (resolutions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Lịch sử xung đột</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">Chưa có xung đột nào được xử lý</p>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Lịch sử xử lý xung đột</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {resolutions.slice(-10).reverse().map((resolution) => (
            <div key={resolution.conflictId} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
              <div>
                <span className="font-medium">{resolution.device.toUpperCase()}</span>
                <span className="text-gray-500 ml-2">
                  {new Date(resolution.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <Badge variant={resolution.resolution === 'scheduler' ? 'default' : 'secondary'}>
                {resolution.resolution === 'scheduler' ? (
                  <><Bot className="w-3 h-3 mr-1" /> Lịch</>
                ) : (
                  <><User className="w-3 h-3 mr-1" /> Thủ công</>
                )}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
