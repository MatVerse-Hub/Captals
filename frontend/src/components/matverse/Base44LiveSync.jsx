import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import {
  Radio,
  Wifi,
  WifiOff,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  Upload,
  Download,
  RefreshCw,
  Zap
} from 'lucide-react';

// Base44 API Configuration
const BASE44_CONFIG = {
  apiKey: '431d90fd5dc046bea66c70686ed2a343',
  appId: '69224f836e8f58657363c48f',
  baseUrl: 'https://api.base44.com',
  entityName: 'MatVerseOS'
};

const Base44LiveSync = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [autoSync, setAutoSync] = useState(false);
  const [syncEvents, setSyncEvents] = useState([]);
  const [stats, setStats] = useState({
    totalSyncs: 0,
    successfulSyncs: 0,
    failedSyncs: 0,
    lastSync: null
  });
  const [connectionHealth, setConnectionHealth] = useState({
    latency: 0,
    status: 'checking'
  });

  const syncIntervalRef = useRef(null);
  const healthCheckRef = useRef(null);

  // Event types
  const eventTypes = {
    create: { icon: Upload, color: 'text-green-500', label: 'Created' },
    update: { icon: RefreshCw, color: 'text-blue-500', label: 'Updated' },
    delete: { icon: XCircle, color: 'text-red-500', label: 'Deleted' },
    sync: { icon: Download, color: 'text-purple-500', label: 'Synced' }
  };

  // Check connection health
  const checkConnectionHealth = async () => {
    const startTime = Date.now();
    try {
      const response = await fetch(
        `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/health`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const latency = Date.now() - startTime;

      if (response.ok) {
        setConnectionHealth({
          latency,
          status: 'healthy'
        });
        setIsConnected(true);
      } else {
        throw new Error('Health check failed');
      }
    } catch (error) {
      setConnectionHealth({
        latency: 0,
        status: 'unhealthy'
      });
      setIsConnected(false);
      console.error('Health check error:', error);
    }
  };

  // Sync data from Base44
  const syncFromBase44 = async () => {
    try {
      const response = await fetch(
        `${BASE44_CONFIG.baseUrl}/api/apps/${BASE44_CONFIG.appId}/entities/${BASE44_CONFIG.entityName}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${BASE44_CONFIG.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Sync failed: ${response.statusText}`);
      }

      const data = await response.json();

      // Add sync event
      addSyncEvent({
        type: 'sync',
        direction: 'download',
        entityCount: data.entities?.length || 0,
        success: true
      });

      // Update stats
      setStats(prev => ({
        ...prev,
        totalSyncs: prev.totalSyncs + 1,
        successfulSyncs: prev.successfulSyncs + 1,
        lastSync: new Date().toISOString()
      }));

      return data.entities;
    } catch (error) {
      console.error('Sync error:', error);

      // Add failed sync event
      addSyncEvent({
        type: 'sync',
        direction: 'download',
        success: false,
        error: error.message
      });

      // Update stats
      setStats(prev => ({
        ...prev,
        totalSyncs: prev.totalSyncs + 1,
        failedSyncs: prev.failedSyncs + 1,
        lastSync: new Date().toISOString()
      }));

      toast.error(`Sync failed: ${error.message}`);
      return null;
    }
  };

  // Add sync event to log
  const addSyncEvent = (event) => {
    const newEvent = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      ...event
    };

    setSyncEvents(prev => [newEvent, ...prev].slice(0, 50)); // Keep last 50 events
  };

  // Simulate entity changes (for demo)
  const simulateEntityChange = () => {
    const types = ['create', 'update', 'delete'];
    const type = types[Math.floor(Math.random() * types.length)];
    const entityNames = [
      'MatVerseOS Core',
      'Dual-Brain Sync',
      'IA-MetaMask Agent',
      'LUA-AutoHeal',
      'Ω-GATE Governance',
      'ClaudeCode-TURBO'
    ];

    addSyncEvent({
      type,
      entityName: entityNames[Math.floor(Math.random() * entityNames.length)],
      entityId: `entity-${Math.floor(Math.random() * 1000)}`,
      success: Math.random() > 0.1 // 90% success rate
    });

    // Update stats
    setStats(prev => ({
      ...prev,
      totalSyncs: prev.totalSyncs + 1,
      successfulSyncs: prev.successfulSyncs + (Math.random() > 0.1 ? 1 : 0),
      failedSyncs: prev.failedSyncs + (Math.random() > 0.1 ? 0 : 1),
      lastSync: new Date().toISOString()
    }));
  };

  // Start auto-sync
  const startAutoSync = () => {
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
    }

    syncIntervalRef.current = setInterval(() => {
      if (isConnected) {
        // Simulate entity changes for demo
        simulateEntityChange();

        // Real sync every 10 events
        if (syncEvents.length % 10 === 0) {
          syncFromBase44();
        }
      }
    }, 3000); // Every 3 seconds

    toast.success('Auto-sync enabled');
  };

  // Stop auto-sync
  const stopAutoSync = () => {
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
      syncIntervalRef.current = null;
    }
    toast.info('Auto-sync disabled');
  };

  // Toggle auto-sync
  const handleAutoSyncToggle = (enabled) => {
    setAutoSync(enabled);
    if (enabled) {
      startAutoSync();
    } else {
      stopAutoSync();
    }
  };

  // Manual sync trigger
  const handleManualSync = async () => {
    toast.loading('Syncing...');
    await syncFromBase44();
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const statusConfig = {
      healthy: { icon: CheckCircle, variant: 'default', color: 'text-green-500', label: 'Healthy' },
      checking: { icon: Clock, variant: 'secondary', color: 'text-yellow-500', label: 'Checking' },
      unhealthy: { icon: XCircle, variant: 'destructive', color: 'text-red-500', label: 'Unhealthy' }
    };

    const config = statusConfig[status] || statusConfig.checking;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${config.color}`} />
        {config.label}
      </Badge>
    );
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Get time ago
  const getTimeAgo = (timestamp) => {
    if (!timestamp) return 'Never';
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
  };

  // Start health checks
  useEffect(() => {
    checkConnectionHealth();
    healthCheckRef.current = setInterval(checkConnectionHealth, 10000); // Every 10s

    return () => {
      if (healthCheckRef.current) {
        clearInterval(healthCheckRef.current);
      }
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="w-full space-y-4">
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-white">
                <Radio className={`h-5 w-5 ${isConnected ? 'text-green-500 animate-pulse' : 'text-red-500'}`} />
                Base44 Live Sync
              </CardTitle>
              <CardDescription>
                Real-time synchronization with Base44 entities
              </CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                {isConnected ? (
                  <Wifi className="h-5 w-5 text-green-500" />
                ) : (
                  <WifiOff className="h-5 w-5 text-red-500" />
                )}
                {getStatusBadge(connectionHealth.status)}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Controls */}
            <div className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Switch
                    checked={autoSync}
                    onCheckedChange={handleAutoSyncToggle}
                    disabled={!isConnected}
                  />
                  <Label className="text-white">Auto-Sync</Label>
                </div>
                <Badge variant={autoSync ? 'default' : 'secondary'} className="flex items-center gap-1">
                  <Zap className={`h-3 w-3 ${autoSync ? 'animate-pulse' : ''}`} />
                  {autoSync ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualSync}
                disabled={!isConnected}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Manual Sync
              </Button>
            </div>

            {/* Connection Stats */}
            <div className="grid grid-cols-4 gap-4">
              <div className="p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <span className="text-sm text-slate-400">Latency</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {connectionHealth.latency}ms
                </div>
              </div>
              <div className="p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-slate-400">Success</span>
                </div>
                <div className="text-2xl font-bold text-green-500">
                  {stats.successfulSyncs}
                </div>
              </div>
              <div className="p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-slate-400">Failed</span>
                </div>
                <div className="text-2xl font-bold text-red-500">
                  {stats.failedSyncs}
                </div>
              </div>
              <div className="p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-4 w-4 text-purple-500" />
                  <span className="text-sm text-slate-400">Last Sync</span>
                </div>
                <div className="text-sm font-bold text-white">
                  {getTimeAgo(stats.lastSync)}
                </div>
              </div>
            </div>

            {/* Sync Events Log */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Sync Events
                </h3>
                <Badge variant="outline">{syncEvents.length} events</Badge>
              </div>
              <ScrollArea className="h-[400px] rounded-md border border-slate-800 bg-slate-950">
                <div className="p-4 space-y-2">
                  {syncEvents.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">
                      No sync events yet. Enable auto-sync to start monitoring.
                    </div>
                  ) : (
                    syncEvents.map((event) => {
                      const eventConfig = eventTypes[event.type] || eventTypes.sync;
                      const Icon = eventConfig.icon;

                      return (
                        <div
                          key={event.id}
                          className={`p-3 rounded-lg border ${
                            event.success === false
                              ? 'bg-red-950/20 border-red-900/50'
                              : 'bg-slate-800 border-slate-700'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <Icon className={`h-4 w-4 ${eventConfig.color}`} />
                              <div>
                                <div className="font-medium text-white">
                                  {eventConfig.label}
                                  {event.entityName && `: ${event.entityName}`}
                                  {event.entityCount !== undefined && ` (${event.entityCount} entities)`}
                                </div>
                                {event.error && (
                                  <div className="text-sm text-red-400 mt-1">
                                    Error: {event.error}
                                  </div>
                                )}
                                {event.entityId && (
                                  <div className="text-xs text-slate-500 mt-1">
                                    ID: {event.entityId}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {event.direction && (
                                <Badge variant="outline" className="text-xs">
                                  {event.direction === 'download' ? '↓' : '↑'}
                                </Badge>
                              )}
                              <span className="text-xs text-slate-400">
                                {formatTime(event.timestamp)}
                              </span>
                              {event.success !== undefined && (
                                event.success ? (
                                  <CheckCircle className="h-4 w-4 text-green-500" />
                                ) : (
                                  <XCircle className="h-4 w-4 text-red-500" />
                                )
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </ScrollArea>
            </div>

            {/* Success Rate */}
            <div className="p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Success Rate</span>
                <span className="text-lg font-bold text-white">
                  {stats.totalSyncs > 0
                    ? ((stats.successfulSyncs / stats.totalSyncs) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{
                    width: `${stats.totalSyncs > 0
                      ? (stats.successfulSyncs / stats.totalSyncs) * 100
                      : 0}%`
                  }}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Base44LiveSync;
